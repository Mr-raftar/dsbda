import pymongo
from flask import Flask, render_template, request
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

app = Flask(__name__)
CORS(app)

# MongoDB Connection
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["crawlerDB"]


def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        search = request.form.get("content")
        if not search:
            return render_template("index.html", error="Please enter a product name")

        searchString = search.replace(" ", "+")
        collection = db[searchString]

        # Return cached data if exists
        if collection.count_documents({}) > 0:
            reviews = list(collection.find({}, {"_id": 0}))
            return render_template("results.html", reviews=reviews)

        driver = get_driver()
        try:
            # 🔍 Open Flipkart
            driver.get(f"https://www.flipkart.com/search?q={searchString}")
            wait = WebDriverWait(driver, 10)

            # Get product links
            try:
                products = wait.until(EC.presence_of_all_elements_located(
                    (By.XPATH, "//a[contains(@href,'/p/') and not(contains(@href, 'login'))]")
                ))
            except:
                driver.quit()
                return render_template("index.html", error="No products found on Flipkart")

            if not products:
                driver.quit()
                return render_template("index.html", error="No products found on Flipkart")

            product_link = products[0].get_attribute("href")
            print("Product URL:", product_link)

            # Convert to review page
            if "/p/" in product_link:
                review_url = product_link.replace("/p/", "/product-reviews/")
            else:
                review_url = product_link

            driver.get(review_url)
            print("Review URL:", driver.current_url)

            # Wait for reviews to load
            time.sleep(3)

            # Scroll multiple times to trigger lazy loading
            for _ in range(4):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1.5)

            # --- ROBUST REVIEW EXTRACTION ---
            # 1. Find all star rating elements
            star_elements = driver.find_elements(By.XPATH,
                                                 "//*[contains(text(), '★') and string-length(normalize-space(text())) <= 4]")

            unique_blocks = []
            seen_texts = set()

            for star in star_elements:
                try:
                    # 2. Traverse up the DOM to find the review container
                    block = star
                    for _ in range(7):  # Max 7 levels up
                        block = block.find_element(By.XPATH, "..")
                        text = block.text
                        if text and ("Certified Buyer" in text or "ago" in text) and len(text) > 30:
                            if text not in seen_texts:
                                unique_blocks.append(text)
                                seen_texts.add(text)
                            break
                except:
                    continue

            print("Reviews Found:", len(unique_blocks))

            if len(unique_blocks) == 0:
                driver.quit()
                return render_template("index.html",
                                       error="No reviews found. Flipkart may have blocked the request or changed its layout.")

            reviews = []

            for review_text in unique_blocks[:10]:
                lines = [line.strip() for line in review_text.split('\n') if
                         line.strip() and "READ MORE" not in line.upper()]

                rating = "No Rating"
                title = "No Title"
                comment = "No Comment"
                name = "No Name"

                if lines:
                    first_line = lines[0]
                    if '★' in first_line:
                        parts = first_line.split('★', 1)
                        rating = parts[0].strip() + '★'
                        title = parts[1].strip()
                        if not title and len(lines) > 1:
                            title = lines[1]
                            comment_start_idx = 2
                        else:
                            comment_start_idx = 1
                    else:
                        title = first_line
                        comment_start_idx = 1

                    comment_lines = []
                    for i in range(comment_start_idx, len(lines)):
                        line = lines[i]
                        # Stop if we hit footer elements
                        if "Certified Buyer" in line or line.endswith("ago"):
                            if i > 0 and name == "No Name":
                                name = lines[i - 1]
                            break
                        comment_lines.append(line)

                    if comment_lines:
                        # Extract name from the last line if 'Certified Buyer' wasn't found
                        if len(comment_lines) > 1 and len(comment_lines[-1]) < 25 and name == "No Name":
                            name = comment_lines.pop()
                        comment = " ".join(comment_lines)

                data = {
                    "Product": search,
                    "Name": name,
                    "Rating": rating,
                    "CommentHead": title,
                    "Comment": comment
                }

                collection.insert_one(data)
                reviews.append(data)

            driver.quit()
            return render_template("results.html", reviews=reviews)

        except Exception as e:
            driver.quit()
            return render_template("index.html", error=f"An error occurred: {str(e)}")

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)