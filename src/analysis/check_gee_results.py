"""
BORDER OPTICS — Quick QA on the Google Earth Engine export
"""

import pandas as pd

df = pd.read_csv("data/processed/border_optics_village_results.csv")

print(f"Total villages in export: {len(df)}")
print()

for col in ["ndbi_before", "ndbi_after", "lights_before", "lights_after"]:
    if col in df.columns:
        valid = df[col].notna().sum()
        print(f"{col}: {valid}/{len(df)} have a value ({df[col].isna().sum()} null — likely cloud cover or no imagery in that window)")
    else:
        print(f"WARNING: column '{col}' not found in the export — check the CSV's actual column names")

print()
print("Column names in file:", list(df.columns))
print()

complete_rows = df.dropna(subset=["ndbi_before", "ndbi_after", "lights_before", "lights_after"])
print(f"Villages with ALL four values present (usable for full before/after comparison): {len(complete_rows)}/{len(df)}")

df.to_csv("data/processed/border_optics_village_results.csv", index=False)  # no-op, just confirms path is right