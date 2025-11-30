import numpy as np
import pandas as pd
import json

# Load CSV file
df = pd.read_csv(r"c:\Users\Kimo Store\OneDrive\Desktop\Houston_TX_minimal.csv")

print("===== BASIC OVERVIEW =====")
print("Shape:", df.shape)
print("\nInfo:")
print(df.info())
print("\nHead:")
print(df.head())


#  Check for duplicates
print("\n===== DUPLICATES CHECK =====")
print("Duplicate rows:", df.duplicated().sum())
print("Duplicate property_id:", df["property_id"].duplicated().sum())


# Convert JSON columns (description, location, branding)

json_cols = ["description", "location", "branding"]

for col in json_cols:
    df[col] = df[col].apply(json.loads)

print("\nJSON columns successfully parsed.")


#  Missing Values — Top Level

print("\n===== MISSING VALUES (TOP LEVEL) =====")
print(df.isnull().sum())


#  Missing Values Inside JSON Columns

def count_missing_in_dict_column(col):
    missing = {}
    for entry in df[col]:
        if isinstance(entry, dict):
            for k, v in entry.items():
                missing[k] = missing.get(k, 0) + (v in [None, "", [], {}])
    return missing


print("\n===== MISSING INSIDE description =====")
print(count_missing_in_dict_column("description"))

print("\n===== MISSING INSIDE location =====")
print(count_missing_in_dict_column("location"))


# For branding (list of dicts)
print("\n===== MISSING INSIDE branding =====")
branding_missing = {}

for row in df["branding"]:
    if isinstance(row, list):
        for agent in row:
            for k, v in agent.items():
                branding_missing[k] = branding_missing.get(k, 0) + (v in [None, "", [], {}])

print(branding_missing)


#  Detecting Inconsistencies

print("\n===== INCONSISTENCIES =====")

# Empty branding lists
empty_branding = (df["branding"].apply(lambda x: len(x) == 0)).sum()
print("Empty branding entries:", empty_branding)

# Missing coordinates
missing_lat = df["location"].apply(lambda x: x.get("address", {}).get("coordinate", {}).get("lat") is None).sum()
missing_lng = df["location"].apply(lambda x: x.get("address", {}).get("coordinate", {}).get("lon") is None).sum()

print("Missing latitude:", missing_lat)
print("Missing longitude:", missing_lng)


#  Outliers 


#  fun to convert str to float to calculate the outliers
def safe_float(value):
    if value in [None, "", np.nan]:
        return np.nan
    value_str = str(value).replace("+", "")   
    try:
        return float(value_str)
    except:
        return np.nan


# Execute the numbers from safe_float fun 
df["baths"] = df["description"].apply(lambda x: safe_float(x.get("baths_consolidated")))
df["beds"] = df["description"].apply(lambda x: safe_float(x.get("beds")))
df["sqft"] = df["description"].apply(lambda x: safe_float(x.get("sqft")))

print("\n===== OUTLIERS CHECK =====")
print(df[["baths", "beds", "sqft"]].describe())


# IQR method for outliers

def detect_outliers(series):
    Q1 = series.quantile(0.25)
    Q3 = series.quantile(0.75)
    IQR = Q3 - Q1
    mask = (series < (Q1 - 1.5 * IQR)) | (series > (Q3 + 1.5 * IQR))
    return mask.sum()


print("Baths outliers:", detect_outliers(df["baths"]))
print("Beds outliers:", detect_outliers(df["beds"]))
print("Sqft outliers:", detect_outliers(df["sqft"]))


print("\n===== INSPECTION DONE =====")
