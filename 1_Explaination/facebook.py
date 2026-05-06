import pandas as pd
import numpy as np

# -------------------------------
# 1. LOAD THE DATASET
# -------------------------------
# Read the CSV file and store it into a DataFrame
df = pd.read_csv(r"D:\Dsbda practical\Facebook Metrics of Cosmetic Brand.csv")

# Display first 5 rows of dataset to understand structure
print("Original Dataset:")
print(df.head())
print("-" * 50)


# -------------------------------
# 2. SELECT SUBSET OF COLUMNS
# -------------------------------
# Extract only important columns for analysis
subset = df[["Type", "Post Hour", "Lifetime Post Total Reach"]]

print("Data Subset (Selected Columns):")
print(subset.head())
print("-" * 50)


# -------------------------------
# 3. CREATE EXTRA DATA FOR MERGING
# -------------------------------
# Create a new DataFrame manually with content scores
extra_data = pd.DataFrame({
    "Type": ["Photo", "Status", "Video", "Link"],
    "Content Score": [80, 65, 90, 70]
})


# -------------------------------
# 4. MERGE DATASETS
# -------------------------------
# Merge original dataset with extra_data using "Type" column
# 'how=left' ensures all rows from original dataset are kept
merged_data = pd.merge(df, extra_data, on="Type", how="left")

print("Merged Data:")
print(merged_data.head())
print("-" * 50)


# -------------------------------
# 5. SORT DATA
# -------------------------------
# Sort dataset based on "Lifetime Post Total Reach" in descending order
sorted_data = df.sort_values(by="Lifetime Post Total Reach", ascending=False)

print("Sorted Data (by Lifetime Post Total Reach):")
print(sorted_data.head())
print("-" * 50)


# -------------------------------
# 6. TRANSPOSE DATA
# -------------------------------
# Convert rows into columns and columns into rows
transposed_data = df.head().T

print("Transposed Data:")
print(transposed_data)
print("-" * 50)


# -------------------------------
# 7. SHAPE OF DATASET
# -------------------------------
# Display number of rows and columns in dataset
print("Shape of Dataset:")
print(df.shape)
print("-" * 50)


# -------------------------------
# 8. NUMPY RESHAPING
# -------------------------------
# Convert "Lifetime Post Total Reach" column into NumPy array
reach_array = np.array(df["Lifetime Post Total Reach"].head(6))

# Reshape array into 2 rows and 3 columns
reshaped_array = reach_array.reshape(2, 3)

print("Reshaped Array (2x3):")
print(reshaped_array)
print("-" * 50)


# -------------------------------
# 9. CREATE PIVOT TABLE
# -------------------------------
# Create pivot table to calculate average reach
# Index = Type of post
# Columns = Post Month
# Values = Average Lifetime Post Total Reach
pivot_data = df.pivot_table(
    values="Lifetime Post Total Reach",
    index="Type",
    columns="Post Month",
    aggfunc="mean"
)

print("Pivot Table:")
print(pivot_data)
print("-" * 50)


# ============================================================
#                📘 DETAILED EXPLANATION
# ============================================================

"""
1. The dataset is loaded using pandas read_csv() function.
   It converts the CSV file into a DataFrame (table format).

2. df.head() is used to preview the first 5 rows, helping us
   understand column names and data structure.

3. A subset of columns is selected to focus only on important
   features like Type, Post Hour, and Reach.

4. A new DataFrame (extra_data) is manually created to assign
   a Content Score to each post type.

5. pd.merge() combines both datasets using the common column "Type".
   Left join ensures no data from original dataset is lost.

6. sort_values() arranges the dataset based on reach so we can
   identify top-performing posts.

7. Transpose (.T) flips the dataset (rows ↔ columns), useful for
   better visualization in some cases.

8. df.shape returns dataset size in (rows, columns) format.

9. NumPy reshape converts a 1D array into a 2D matrix.
   This is useful in machine learning and mathematical operations.

10. Pivot table summarizes data:
    - Groups data by post Type
    - Splits it by Post Month
    - Calculates average reach
    This helps in analyzing trends and patterns easily.

Overall, this program demonstrates important data preprocessing
and analysis operations used in Data Science.
"""
