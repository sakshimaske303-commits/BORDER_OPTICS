"""
BORDER OPTICS — Merge all geocoded villages into one master table
for upload to Google Earth Engine.
"""

import pandas as pd

FILES = {
    "Arunachal Pradesh": "data/processed/arunachal_pradesh_geocoded.csv",
    "Sikkim": "data/processed/sikkim_geocoded.csv",
    "Uttarakhand": "data/processed/uttarakhand_geocoded.csv",
    "Himachal Pradesh": "data/processed/himachal_pradesh_geocoded.csv",
}

MATCHED_STATUSES = {
    "matched",
    "matched (fallback query, no block)",
    "matched via Bhuvan (district-verified)",
}

rows = []
for state, path in FILES.items():
    df = pd.read_csv(path)
    matched = df[df["geocode_status"].isin(MATCHED_STATUSES)].copy()
    matched["state"] = state
    # Himachal is just the small illustrative case study, not core sample.
    # Sikkim is outside the core sample from v2.1: none of its comparison villages
    # could be checked against a North Sikkim boundary, and 84 of the 93 lay outside it.
    matched["is_core_sample"] = state not in ("Himachal Pradesh", "Sikkim")
    rows.append(matched[["Habitation", "District", "Block", "state", "latitude", "longitude", "is_core_sample"]])

master = pd.concat(rows, ignore_index=True)
master = master.rename(columns={"Habitation": "village", "District": "district", "Block": "block"})
master["village_id"] = range(1, len(master) + 1)
master = master[["village_id", "village", "district", "block", "state", "is_core_sample", "latitude", "longitude"]]

master.to_csv("data/processed/border_optics_master_villages.csv", index=False)
print(f"Merged {len(master)} villages into data/processed/border_optics_master_villages.csv")
print(master["state"].value_counts())