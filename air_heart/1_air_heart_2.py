import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

# ----------------------------
# Load datasets
# ----------------------------
air = pd.read_csv(r"D:\dsbda_prac\Air Quality.csv")
heart = pd.read_csv(r"D:\dsbda_prac\heart.csv")

# ----------------------------
# Data Cleaning
# ----------------------------
# Standardize column names
air.columns = air.columns.str.strip().str.lower()
heart.columns = heart.columns.str.strip().str.lower()

# Remove duplicates
air.drop_duplicates(inplace=True)
heart.drop_duplicates(inplace=True)

# Remove completely empty columns
air.dropna(axis=1, how='all', inplace=True)
heart.dropna(axis=1, how='all', inplace=True)

# Fill missing numeric values with mean
air.fillna(air.mean(numeric_only=True), inplace=True)
heart.fillna(heart.mean(numeric_only=True), inplace=True)

# ----------------------------
# Data Integration
# ----------------------------
# Create synthetic key for merging
air["id"] = range(len(air))
heart["id"] = np.random.choice(air["id"], len(heart))

# Merge datasets
data = pd.merge(air, heart, on="id", how="left")

# Remove remaining empty columns/rows
data.dropna(axis=1, how='all', inplace=True)
data.dropna(inplace=True)

# ----------------------------
# Data Transformation
# ----------------------------
# Normalize numeric data
scaler = MinMaxScaler()
num_cols = data.select_dtypes(include=np.number).columns
data[num_cols] = scaler.fit_transform(data[num_cols])

# Encode categorical variables
data = pd.get_dummies(data, drop_first=True)

# Feature Engineering: Pollution Index
if {"co(gt)", "no2(gt)", "nox(gt)"}.issubset(data.columns):
    data["pollution_index"] = (
        data["co(gt)"] + data["no2(gt)"] + data["nox(gt)"]
    ) / 3

# ----------------------------
# Error Correction
# ----------------------------
# Remove invalid age values
if "age" in data.columns:
    data = data[data["age"] > 0]

# Fix cholesterol values (correct column = 'chol')
if "chol" in data.columns:
    data["chol"] = data["chol"].clip(0.25, 0.75)

# Remove outliers using IQR
num_cols = data.select_dtypes(include=np.number).columns
Q1 = data[num_cols].quantile(0.25)
Q3 = data[num_cols].quantile(0.75)
IQR = Q3 - Q1

data = data[
    ~((data[num_cols] < (Q1 - 1.5 * IQR)) |
      (data[num_cols] > (Q3 + 1.5 * IQR))).any(axis=1)
]

# ----------------------------
# Final Output
# ----------------------------
print("Final Dataset Shape:", data.shape)
print("\nSample Data:\n")
print(data.head())
