import pandas as pd
import numpy as np
import io

df = pd.read_csv(r"c:\Users\Kimo Store\OneDrive\Desktop\cars1.csv")

print("\n===== HEAD =====")
print(df.head(), "\n")

print("===== INFO =====")
buf = io.StringIO()
df.info(buf=buf)
print(buf.getvalue(), "\n")

print("===== SHAPE =====")
print("Rows:", df.shape[0], " | Columns:", df.shape[1], "\n")

print("===== DESCRIBE (NUMERIC) =====")
print(df.describe(), "\n")

print("===== DESCRIBE (ALL COLUMNS) =====")
print(df.describe(include='all'), "\n")

print("===== MISSING VALUES =====")
print(df.isnull().sum(), "\n")

print("===== UNIQUE COUNT =====")
print(df.nunique(), "\n")

print("===== DUPLICATES =====")
print(df.duplicated().sum(), "\n")

print("===== DATA TYPES =====")
print(df.dtypes, "\n")

print("===== CORRELATION MATRIX =====")
numeric_df = df.select_dtypes(include=['number'])
print(numeric_df.corr(), "\n")

print("===== OUTLIER DETECTION (IQR) =====")
def detect_outliers(series):
    Q1 = series.quantile(0.25)
    Q3 = series.quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR
    return ((series < lower) | (series > upper)).sum()

for col in numeric_df.columns:
    print(f"{col}: {detect_outliers(numeric_df[col])}")

print("\n===== DATA SUMMARY =====")
summary = {
    "Total Rows": df.shape[0],
    "Total Columns": df.shape[1],
    "Missing Values Total": df.isnull().sum().sum(),
    "Duplicate Rows": df.duplicated().sum(),
    "Numeric Columns": len(df.select_dtypes(include='number').columns),
    "Categorical Columns": len(df.select_dtypes(include='object').columns),
    "Memory Usage (MB)": round(df.memory_usage().sum() / (1024*1024), 3)
}

for key, val in summary.items():
    print(f"{key}: {val}")

print("\n===== SAMPLE ROW =====")
print(df.sample(1))


print("\n======== INSPECTION DONE =========")