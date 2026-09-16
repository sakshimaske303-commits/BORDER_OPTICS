import argparse
import os
import time

import ee
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

S1_COLLECTION = "COPERNICUS/S1_GRD"
BUFFER_RADIUS_M = 500  # same as extract_satellite_data.py's primary buffer
ORBIT_PASS = "DESCENDING"  # if a run below prints 0 scenes, switch to 'ASCENDING' and re-run

VILLAGE_PATHS = {
    "treated": "data/processed/border_optics_master_villages.csv",
    "control": "data/processed/border_optics_control_villages.csv",
}

WINDOWS = {
    "full_year": {
        "before": ("2021-01-01", "2022-01-01"),
        "after": ("2025-01-01", "2026-01-01"),
    },
    "summer": {
        "before": ("2021-06-01", "2021-10-01"),
        "after": ("2025-06-01", "2025-10-01"),
    },
}

OUT_PATHS = {
    ("treated", "full_year"): "data/processed/border_optics_treated_sar_fullyear.csv",
    ("treated", "summer"): "data/processed/border_optics_treated_sar_summer.csv",
    ("control", "full_year"): "data/processed/border_optics_control_sar_fullyear.csv",
    ("control", "summer"): "data/processed/border_optics_control_sar_summer.csv",
}


def init_ee():
    project = os.environ.get("EE_PROJECT")
    try:
        ee.Initialize(project=project)
    except Exception:
        ee.Authenticate()
        ee.Initialize(project=project)


def sar_for_period(buffered_geom, start, end):
    """Mean VV and VH (dB) over the period, IW mode, one fixed orbit pass
    direction (ascending/descending backscatter geometry isn't directly
    comparable, so mixing them would add noise unrelated to any real
    change)."""
    collection = (
        ee.ImageCollection(S1_COLLECTION)
        .filterBounds(buffered_geom)
        .filterDate(start, end)
        .filter(ee.Filter.eq("instrumentMode", "IW"))
        .filter(ee.Filter.eq("orbitProperties_pass", ORBIT_PASS))
        .filter(ee.Filter.listContains("transmitterReceiverPolarisation", "VV"))
        .filter(ee.Filter.listContains("transmitterReceiverPolarisation", "VH"))
    )
    count = collection.size().getInfo()
    if count == 0:
        return None, None, 0

    composite = collection.select(["VV", "VH"]).median()
    stats = composite.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=buffered_geom,
        scale=20,  # per-field IW footprint is coarser than 10m -- see gee_extract_sar.js note
        maxPixels=1e9,
    ).getInfo()
    return stats.get("VV"), stats.get("VH"), count


def extract(group, window_key, checkpoint_every=10):
    cfg = WINDOWS[window_key]
    before_start, before_end = cfg["before"]
    after_start, after_end = cfg["after"]
    out_path = OUT_PATHS[(group, window_key)]

    outcome_cols = [
        "vv_before", "vh_before", "vv_after", "vh_after",
        "sar_before_image_count", "sar_after_image_count",
    ]

    if os.path.exists(out_path):
        villages = pd.read_csv(out_path)
        print(f"Resuming from existing checkpoint: {out_path}")
    else:
        villages = pd.read_csv(VILLAGE_PATHS[group])

    for col in outcome_cols:
        if col not in villages.columns:
            villages[col] = None

    print(f"--- Extracting Sentinel-1 SAR (VV/VH), group='{group}', window='{window_key}', "
          f"orbit_pass='{ORBIT_PASS}' ---")
    print(f"Before: {before_start} to {before_end}  |  After: {after_start} to {after_end}")
    print(f"{len(villages)} villages to process")
    print("If any village prints 0 scenes for both periods, this orbit pass may not cover "
          "this area -- try ORBIT_PASS='ASCENDING' instead and re-run.")

    for i, row in villages.iterrows():
        if all(pd.notna(row.get(c)) for c in outcome_cols):
            continue  # already extracted (resume support)

        point = ee.Geometry.Point([row["longitude"], row["latitude"]])
        buffered_geom = point.buffer(BUFFER_RADIUS_M)

        vv_before, vh_before, n_before = sar_for_period(buffered_geom, before_start, before_end)
        vv_after, vh_after, n_after = sar_for_period(buffered_geom, after_start, after_end)

        villages.at[i, "vv_before"] = vv_before
        villages.at[i, "vh_before"] = vh_before
        villages.at[i, "vv_after"] = vv_after
        villages.at[i, "vh_after"] = vh_after
        villages.at[i, "sar_before_image_count"] = n_before
        villages.at[i, "sar_after_image_count"] = n_after

        if (i + 1) % checkpoint_every == 0:
            villages.to_csv(out_path, index=False)
            print(f"  {i + 1}/{len(villages)} villages processed...")

        time.sleep(0.2)  # be polite to the Earth Engine API

    villages.to_csv(out_path, index=False)
    n_valid = villages.dropna(subset=["vv_before", "vv_after"]).shape[0]
    print(f"Done. {n_valid}/{len(villages)} villages have valid before/after SAR data.")
    print(f"Saved to {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract Sentinel-1 SAR VV/VH per village (H1/H4 sensor-independent triangulation check).")
    parser.add_argument("--group", choices=["treated", "control"], required=True)
    parser.add_argument("--window", choices=["full_year", "summer"], required=True)
    args = parser.parse_args()

    init_ee()
    extract(args.group, args.window)
