import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

# ----------------------------
# Load datasets
# ----------------------------
air = pd.read_csv("/home/kartik/dsbda_prac/Air Quality.csv")
heart = pd.read_csv("/home/kartik/dsbda_prac/heart.csv")



# ----------------------------
# (a) Data Cleaning
# ----------------------------
# Remove duplicates
air.drop_duplicates(inplace=True)
heart.drop_duplicates(inplace=True)

# Handle missing values (replace with mean)
air.fillna(air.mean(numeric_only=True), inplace=True)
heart.fillna(heart.mean(numeric_only=True), inplace=True)


# ----------------------------
# (b) Data Integration
# ----------------------------
# No common column → concatenate datasets column-wise
data = pd.concat([air, heart], axis=1)



# ----------------------------
# (c) Data Transformation
# ----------------------------
# Normalize numeric columns
scaler = MinMaxScaler()
num_cols = data.select_dtypes(include=np.number).columns
data[num_cols] = scaler.fit_transform(data[num_cols])

# Convert categorical to numeric (if any)
data = pd.get_dummies(data, drop_first=True)



# ----------------------------
# (d) Error Correcting
# ----------------------------
# Remove invalid age values
if "age" in data.columns:
    data = data[data["age"] > 0]

# Fix cholesterol values (column name = 'chol')
if "chol" in data.columns:
    data["chol"] = data["chol"].clip(0.25, 0.75)

# Remove outliers using IQR
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
