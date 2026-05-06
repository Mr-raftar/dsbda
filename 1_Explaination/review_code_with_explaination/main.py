# ============================================================
# FILE: main.py
# PURPOSE: Core backend — Flask web server + Selenium scraper
#          + MongoDB storage for Flipkart product reviews
# ============================================================

import pymongo                                           # MongoDB Python driver
from flask import Flask, render_template, request        # Flask web framework core
from flask_cors import CORS                              # Enables Cross-Origin requests
from selenium import webdriver                           # Browser automation
from selenium.webdriver.chrome.service import Service   # Manages ChromeDriver process
from selenium.webdriver.common.by import By             # Element locator strategies
from selenium.webdriver.support.ui import WebDriverWait # Waits for elements to appear
from selenium.webdriver.support import expected_conditions as EC  # Wait conditions
from webdriver_manager.chrome import ChromeDriverManager # Auto-downloads ChromeDriver
import time                                              # For sleep/delay between actions

# ----- APP INITIALISATION -----
app = Flask(__name__)   # Creates the Flask application; __name__ sets the root path
CORS(app)               # Allows JavaScript from other origins (ports/domains) to call this API

# ----- DATABASE CONNECTION -----
client = pymongo.MongoClient("mongodb://localhost:27017/")  # Connect to local MongoDB server
db = client["crawlerDB"]                                    # Use (or create) database named "crawlerDB"


def get_driver():
    """
    Creates and returns a Selenium Chrome WebDriver instance.
    Options are set to avoid bot-detection and start maximized.
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")  # Hides automation flag from websites
    options.add_argument("--start-maximized")                               # Opens Chrome in full-screen mode
    # ChromeDriverManager downloads the correct driver version automatically
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


@app.route("/", methods=["GET", "POST"])   # Maps "/" URL to this function for GET and POST requests
def index():
    """
    Main route handler.
    GET  → Show the search form (index.html).
    POST → Read the search term, scrape Flipkart, store in MongoDB, show results.
    """
    if request.method == "POST":
        search = request.form.get("content")    # Read the text typed in the search box
        if not search:
            return render_template("index.html", error="Please enter a product name")

        searchString = search.replace(" ", "+")     # "samsung phone" → "samsung+phone" for URL usage
        collection = db[searchString]               # Each product gets its own MongoDB collection

        # ----- CACHE CHECK -----
        # If reviews are already in MongoDB, skip scraping and return them immediately
        if collection.count_documents({}) > 0:
            reviews = list(collection.find({}, {"_id": 0}))    # Fetch all docs, exclude MongoDB "_id" field
            return render_template("results.html", reviews=reviews)

        # ----- LAUNCH BROWSER -----
        driver = get_driver()   # Open a new Chrome window controlled by Selenium
        try:
            # Navigate Chrome to Flipkart search results page
            driver.get(f"https://www.flipkart.com/search?q={searchString}")
            wait = WebDriverWait(driver, 10)    # Will wait up to 10 seconds for elements

            # ----- FIND PRODUCT LINKS -----
            try:
                # Wait until product links (containing "/p/" in href) appear on the page
                # Excludes login-related links by checking "not contains 'login'"
                products = wait.until(EC.presence_of_all_elements_located(
                    (By.XPATH, "//a[contains(@href,'/p/') and not(contains(@href, 'login'))]")
                ))
            except:
                driver.quit()
                return render_template("index.html", error="No products found on Flipkart")

            if not products:
                driver.quit()
                return render_template("index.html", error="No products found on Flipkart")

            product_link = products[0].get_attribute("href")    # Take the FIRST (most relevant) product URL
            print("Product URL:", product_link)

            # ----- BUILD REVIEW PAGE URL -----
            # Flipkart product pages use "/p/" in the URL.
            # Replacing it with "/product-reviews/" navigates to the reviews section.
            if "/p/" in product_link:
                review_url = product_link.replace("/p/", "/product-reviews/")
            else:
                review_url = product_link

            driver.get(review_url)                  # Navigate to the review page
            print("Review URL:", driver.current_url)

            # ----- WAIT AND SCROLL -----
            time.sleep(3)   # Wait 3 seconds for the review page to fully load

            # Scroll to the bottom 4 times to trigger Flipkart's lazy-loading of reviews
            for _ in range(4):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1.5)     # Pause 1.5 seconds between each scroll

            # ----- FIND REVIEW BLOCKS via STAR ELEMENTS -----
            # Locate all elements whose text contains "★" and is very short (≤4 chars).
            # These are star rating badges like "4★" or "3.5★" on each review card.
            star_elements = driver.find_elements(By.XPATH,
                "//*[contains(text(), '★') and string-length(normalize-space(text())) <= 4]")

            unique_blocks = []  # Stores raw text of each unique review block
            seen_texts = set()  # Tracks already-added blocks to avoid duplicates

            for star in star_elements:
                try:
                    block = star
                    # Walk UP the DOM tree (max 7 parent levels) from the star element
                    # to find the parent container that holds the full review text
                    for _ in range(7):
                        block = block.find_element(By.XPATH, "..")  # ".." means "parent element" in XPATH
                        text = block.text
                        # A valid review block contains "Certified Buyer" or "ago" and is long enough
                        if text and ("Certified Buyer" in text or "ago" in text) and len(text) > 30:
                            if text not in seen_texts:
                                unique_blocks.append(text)
                                seen_texts.add(text)
                            break   # Stop climbing once we find the review container
                except:
                    continue    # Skip any element that causes an error

            print("Reviews Found:", len(unique_blocks))

            if len(unique_blocks) == 0:
                driver.quit()
                return render_template("index.html",
                    error="No reviews found. Flipkart may have blocked the request or changed its layout.")

            # ----- PARSE EACH REVIEW -----
            reviews = []

            for review_text in unique_blocks[:10]:   # Process up to 10 reviews
                # Split raw text into lines; remove blank lines and "READ MORE" labels
                lines = [line.strip() for line in review_text.split('\n') if
                         line.strip() and "READ MORE" not in line.upper()]

                # Default values in case parsing cannot extract a field
                rating = "No Rating"
                title  = "No Title"
                comment = "No Comment"
                name   = "No Name"

                if lines:
                    first_line = lines[0]
                    if '★' in first_line:
                        # First line format: "4★ Great product" or "4★"
                        parts  = first_line.split('★', 1)
                        rating = parts[0].strip() + '★'     # e.g., "4★"
                        title  = parts[1].strip()            # e.g., "Great product"
                        if not title and len(lines) > 1:
                            title = lines[1]                 # Title was on the next line
                            comment_start_idx = 2
                        else:
                            comment_start_idx = 1
                    else:
                        title = first_line                   # No star on first line; treat as title
                        comment_start_idx = 1

                    comment_lines = []
                    for i in range(comment_start_idx, len(lines)):
                        line = lines[i]
                        # Stop collecting comment when we hit reviewer metadata lines
                        if "Certified Buyer" in line or line.endswith("ago"):
                            if i > 0 and name == "No Name":
                                name = lines[i - 1]     # Line just before metadata is often the reviewer name
                            break
                        comment_lines.append(line)

                    if comment_lines:
                        # If the last comment line is short (<25 chars) it is likely the reviewer's name
                        if len(comment_lines) > 1 and len(comment_lines[-1]) < 25 and name == "No Name":
                            name = comment_lines.pop()  # Remove from comment and use as name
                        comment = " ".join(comment_lines)   # Join remaining lines as the comment body

                # ----- SAVE TO MONGODB -----
                data = {
                    "Product":     search,
                    "Name":        name,
                    "Rating":      rating,
                    "CommentHead": title,
                    "Comment":     comment
                }

                collection.insert_one(data)     # Insert review document into MongoDB
                reviews.append(data)            # Also keep in local list for rendering

            driver.quit()   # Close the Chrome browser
            return render_template("results.html", reviews=reviews)     # Show results page

        except Exception as e:
            driver.quit()   # Always close the browser even if an error occurs
            return render_template("index.html", error=f"An error occurred: {str(e)}")

    return render_template("index.html")    # GET request: just show the search form


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
    # debug=True        → Shows detailed error pages; auto-reloads on code changes
    # use_reloader=False → Prevents Flask from starting a second process which would
    #                      launch a duplicate Chrome window when Selenium is used


# ======================================================================
# EXPLANATION OF main.py
# ======================================================================
#
# WHAT THIS FILE DOES:
# --------------------
# This is the heart of the entire project. It does three things:
#   1. Runs a Flask web server so users can visit the app in a browser.
#   2. Uses Selenium to open Chrome, search Flipkart, and extract reviews.
#   3. Saves those reviews to MongoDB so they don't need to be re-scraped.
#
# HOW THE ROUTE WORKS (Step-by-step):
# ------------------------------------
# When the user types a product name and clicks "Search":
#   Step 1 → Flask receives a POST request with "content" = product name
#   Step 2 → The product name is URL-encoded (spaces → "+")
#   Step 3 → MongoDB is checked: if reviews exist, return them instantly
#   Step 4 → If no cache: Chrome opens, goes to Flipkart search results
#   Step 5 → The first product link is grabbed and converted to a reviews URL
#   Step 6 → The reviews page loads; the page is scrolled to load lazy content
#   Step 7 → Star (★) elements are found; the DOM is climbed upward to get
#             the full review container text
#   Step 8 → Each review's raw text is parsed into: Rating, Title, Comment, Name
#   Step 9 → Reviews are saved to MongoDB and displayed to the user
#
# KEY DESIGN DECISIONS:
# ----------------------
# • DOM traversal (climbing ".."):  Flipkart does not use static, predictable
#   class names for review containers. Instead of a fragile CSS/class selector,
#   the code finds the reliable ★ symbol and walks UP the tree to find the
#   nearest ancestor that contains all the review metadata. This makes the
#   scraper more resilient to minor layout changes.
#
# • Caching in MongoDB:  Each unique search term gets its own collection.
#   On first search, results are stored. On repeat searches, MongoDB returns
#   the data in milliseconds — no browser launch, no scraping delay.
#
# • use_reloader=False:  Flask's hot-reloader works by forking the process.
#   When Selenium is involved, this causes Chrome to launch twice. Setting
#   use_reloader=False prevents this problem.
#
# • Time sleeps + scrolling:  Flipkart uses JavaScript to lazily load reviews
#   only when the user scrolls down. Without the scroll loop, the page would
#   appear nearly empty. The sleeps give the network time to respond.
#
# LIBRARIES USED:
# ---------------
# pymongo          → Talk to MongoDB (insert, find, count documents)
# flask            → Handle HTTP requests, render HTML templates
# flask_cors       → Allow cross-origin fetch requests (useful if frontend is separate)
# selenium         → Automate Chrome: click, scroll, read page content
# webdriver_manager → Download the right ChromeDriver version automatically
# time             → Pause execution (time.sleep) to wait for page loads
# ======================================================================
