import pandas as pd

print("Loading CSV...")
df = pd.read_csv('E:/Shivam/F1/f1-ai-predictor/data/openf1_features_expanded.csv')

print("\nOriginal columns:")
print(list(df.columns))

print("\nCleaning columns...")
df.columns = df.columns.str.replace("'", "").str.replace('"', '').str.strip()

print("\nCleaned columns:")
print(list(df.columns))

print("\nChecking keys:")
print(f"gap_trend: {'gap_trend' in df.columns}")
print(f"overtakes_made: {'overtakes_made' in df.columns}")

if 'gap_trend' not in df.columns:
    print("\n⚠️  gap_trend NOT FOUND. Closest matches:")
    for c in df.columns:
        if 'gap' in c:
            print(f"  - {c}")
