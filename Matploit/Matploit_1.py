# Import libraries
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# ------------------ 1. LINE GRAPH ------------------
a = [1,2,3,4,5,6,5,4,3,2,1]
b = [10,20,30,40,50,60,50,40,30,20,10]

plt.plot(a, b)
plt.title("Line Graph")
plt.xlabel("Year")
plt.ylabel("Yield (tones per hectare)")
plt.show()


# ------------------ 2. SIMPLE LINE GRAPH ------------------
x = [1,2,3]
y = [10,11,12]

plt.plot(x, y)
plt.title("Simple Line Graph")
plt.xlabel("X axis")
plt.ylabel("Y axis")
plt.show()


# ------------------ 3. BAR GRAPH (Matplotlib) ------------------
df = sns.load_dataset('titanic')
df_bar = df.groupby('who')['fare'].sum().reset_index()

plt.bar(df_bar['who'], df_bar['fare'])
plt.title("Bar Chart (Matplotlib)")
plt.xlabel("Who")
plt.ylabel("Total Fare")
plt.show()


# ------------------ 4. BAR GRAPH (Seaborn) ------------------
sns.barplot(x='who', y='fare', data=df)
plt.title("Bar Chart (Seaborn)")
plt.xlabel("Who")
plt.ylabel("Fare")
plt.show()


# ------------------ 5. GROUPED BAR CHART ------------------
df_pivot = pd.pivot_table(df, values="fare", index="who", columns="class", aggfunc=np.mean)

df_pivot.plot(kind="bar")
plt.title("Grouped Bar Chart")
plt.xlabel("Who")
plt.ylabel("Average Fare")
plt.show()


# ------------------ 6. STACKED BAR CHART ------------------
data = pd.DataFrame({
    "A": ["E","F","G"],
    "B": [0,1,0],
    "C": [1,1,1],
    "D": [1,0,0]
})

data.plot.bar(x='A', y=["B","C","D"], stacked=True)
plt.title("Stacked Bar Chart")
plt.xlabel("Category")
plt.ylabel("Values")
plt.show()


# ------------------ 7. PIE CHART ------------------
cars = ['AUDI','BMW','NISSAN','TESLA','HYUNDAI','HONDA']
values = [20,15,15,14,16,20]

plt.pie(values, labels=cars, autopct='%1.1f%%')
plt.title("Pie Chart")
plt.show()


# ------------------ 8. AREA (STACKPLOT) ------------------
x = range(1,6)
y1 = [1,4,6,8,9]
y2 = [2,2,7,10,12]
y3 = [2,8,5,10,6]

plt.stackplot(x, y1, y2, y3, labels=['A','B','C'])
plt.legend(loc='upper left')
plt.title("Area Chart")
plt.xlabel("X axis")
plt.ylabel("Y axis")
plt.show()


# ------------------ 9. ANOTHER STACKPLOT ------------------
years = [1,2,3]
company_a = [6,8,10]
company_b = [4,5,9]
company_c = [3,5,7]

plt.stackplot(years, company_a, company_b, company_c,
              labels=['Company A','Company B','Company C'])
plt.legend(loc='upper left')
plt.title("Company Salary Growth")
plt.xlabel("Years of Experience")
plt.ylabel("Salary")
plt.show()
