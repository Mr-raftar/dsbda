import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

# ----------------------------
# 1. LOAD DATASETS
# ----------------------------
# Load Air Quality dataset
air = pd.read_csv("/home/kartik/dsbda_prac/Air Quality.csv")

# Load Heart dataset
heart = pd.read_csv("/home/kartik/dsbda_prac/heart.csv")


# ----------------------------
# 2. DATA CLEANING
# ----------------------------

# Remove duplicate rows from both datasets
air.drop_duplicates(inplace=True)
heart.drop_duplicates(inplace=True)

# Handle missing values by replacing them with column mean (only numeric columns)
air.fillna(air.mean(numeric_only=True), inplace=True)
heart.fillna(heart.mean(numeric_only=True), inplace=True)


# ----------------------------
# 3. DATA INTEGRATION
# ----------------------------

# Since there is no common column, we concatenate both datasets column-wise
# axis=1 → joins columns side by side
data = pd.concat([air, heart], axis=1)


# ----------------------------
# 4. DATA TRANSFORMATION
# ----------------------------

# Normalize numeric columns using Min-Max Scaling (values between 0 and 1)
scaler = MinMaxScaler()

# Select only numeric columns
num_cols = data.select_dtypes(include=np.number).columns

# Apply normalization
data[num_cols] = scaler.fit_transform(data[num_cols])

# Convert categorical columns into numeric using one-hot encoding
# drop_first=True avoids dummy variable trap
data = pd.get_dummies(data, drop_first=True)


# ----------------------------
# 5. ERROR CORRECTION
# ----------------------------

# Remove invalid age values (age should be positive)
if "age" in data.columns:
    data = data[data["age"] > 0]

# Fix cholesterol values (ensure values are within reasonable range)
if "chol" in data.columns:
    data["chol"] = data["chol"].clip(0.25, 0.75)

# Remove outliers using IQR (Interquartile Range) method
Q1 = data[num_cols].quantile(0.25)   # First quartile
Q3 = data[num_cols].quantile(0.75)   # Third quartile
IQR = Q3 - Q1                        # Interquartile range

# Keep only rows within valid range
data = data[
    ~((data[num_cols] < (Q1 - 1.5 * IQR)) |
      (data[num_cols] > (Q3 + 1.5 * IQR))).any(axis=1)
]


# ----------------------------
# 6. FINAL OUTPUT
# ----------------------------

# Display final dataset shape
print("Final Dataset Shape:", data.shape)

# Display sample records
print("\nSample Data:\n")
print(data.head())


# ============================================================
#                📘 DETAILED EXPLANATION
# ============================================================

"""
1. Data Loading:
   Two datasets (Air Quality and Heart) are loaded using pandas read_csv().
   These datasets are stored as DataFrames for further processing.

2. Data Cleaning:
   - Duplicate rows are removed using drop_duplicates().
   - Missing values are replaced with the mean of each column.
     This ensures no null values affect analysis.

3. Data Integration:
   - Since both datasets have no common column, they are combined
     column-wise using pd.concat().
   - This results in a single dataset containing all features.

4. Data Transformation:
   - MinMaxScaler is used to normalize numeric values between 0 and 1.
     This is important for machine learning algorithms.
   - Categorical variables are converted into numeric form using
     one-hot encoding (pd.get_dummies()).

5. Error Correction:
   - Invalid values are handled:
       • Age must be positive
       • Cholesterol values are restricted within a fixed range
   - Outliers are removed using the IQR method:
       • Q1 (25th percentile) and Q3 (75th percentile) are calculated
       • Values outside (Q1 - 1.5*IQR) and (Q3 + 1.5*IQR) are removed

6. Final Output:
   - The cleaned and processed dataset is displayed
   - Shape shows number of rows and columns after preprocessing

Overall:
This program demonstrates complete data preprocessing pipeline:
✔ Data Cleaning
✔ Data Integration
✔ Data Transformation
✔ Error Handling

These steps are essential in Data Science before applying
Machine Learning models.
"""
