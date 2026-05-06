import pandas as pd
import numpy as np

# Load dataset
df = pd.read_csv(r"D:\Dsbda practical\Facebook Metrics of Cosmetic Brand.csv")

# Display original dataset
print("Original Dataset:")
print(df.head())
print("-" * 50)

# Select subset of columns
subset = df[["Type", "Post Hour", "Lifetime Post Total Reach"]]

print("Data Subset (Selected Columns):")
print(subset.head())
print("-" * 50)

# Create extra data for merging
extra_data = pd.DataFrame({
    "Type": ["Photo", "Status", "Video", "Link"],
    "Content Score": [80, 65, 90, 70]
})

# Merge datasets
merged_data = pd.merge(df, extra_data, on="Type", how="left")

print("Merged Data:")
print(merged_data.head())
print("-" * 50)

# Sort dataset
sorted_data = df.sort_values(by="Lifetime Post Total Reach", ascending=False)

print("Sorted Data (by Lifetime Post Total Reach):")
print(sorted_data.head())
print("-" * 50)

# Transpose data
transposed_data = df.head().T

print("Transposed Data:")
print(transposed_data)
print("-" * 50)

# Shape of dataset
print("Shape of Dataset:")
print(df.shape)
print("-" * 50)

# NumPy reshaping
reach_array = np.array(df["Lifetime Post Total Reach"].head(6))
reshaped_array = reach_array.reshape(2, 3)

print("Reshaped Array (2x3):")
print(reshaped_array)
print("-" * 50)

# Pivot table
pivot_data = df.pivot_table(
    values="Lifetime Post Total Reach",
    index="Type",
    columns="Post Month",
    aggfunc="mean"
)

print("Pivot Table:")
print(pivot_data)
print("-" * 50)
