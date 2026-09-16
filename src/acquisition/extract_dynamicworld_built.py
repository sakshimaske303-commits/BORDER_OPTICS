import argparse
import os
import time

import ee
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

DW_COLLECTION = "GOOGLE/DYNAMICWORLD/V1"
BUFFER_RADIUS_M = 500  # same as extract_satellite_data.py's primary buffer

VILLAGE_PATHS = {
    "treated": "data/processed/border_optics_master_villages.csv",
    "control": "data/processed/border_optics_control_villages.csv",
}

# Same before/after date ranges as extract_satellite_data.py /
# extract_control_satellite_data.py, so this lines up exactly with the
# NDBI/lights extraction it's meant to cross-check.
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
    ("treated", "full_year"): "data/processed/border_optics_treated_dynamicworld_fullyear.csv",
    ("treated", "summer"): "data/processed/border_optics_treated_dynamicworld_summer.csv",
    ("control", "full_year"): "data/processed/border_optics_control_dynamicworld_fullyear.csv",
    ("control", "summer"): "data/processed/border_optics_control_dynamicworld_summer.csv",
}


def init_ee():
    project = os.environ.get("EE_PROJECT")
    try:
        ee.Initialize(project=project)
    except Exception:
        ee.Authenticate()
        ee.Initialize(project=project)


def built_prob_for_period(buffered_geom, start, end):
    """Mean of the per-image 'built' probability band over the period,
    median-composited first (same compositing choice as NDBI's Sentinel-2
    median, for consistency) then averaged over the buffer."""
    collection = (
        ee.ImageCollection(DW_COLLECTION)
        .filterBounds(buffered_geom)
        .filterDate(start, end)
        .select("built")
    )
    count = collection.size().getInfo()
    if count == 0:
        return None, 0

    composite = collection.median()
    stats = composite.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=buffered_geom,
        scale=10,
        maxPixels=1e9,
    ).getInfo()
    return stats.get("built"), count


def extract(group, window_key, checkpoint_every=10):
    cfg = WINDOWS[window_key]
    before_start, before_end = cfg["before"]
    after_start, after_end = cfg["after"]
    out_path = OUT_PATHS[(group, window_key)]

    outcome_cols = ["built_before", "built_after", "built_before_image_count", "built_after_image_count"]

    if os.path.exists(out_path):
        villages = pd.read_csv(out_path)
        print(f"Resuming from existing checkpoint: {out_path}")
    else:
        villages = pd.read_csv(VILLAGE_PATHS[group])

    for col in outcome_cols:
        if col not in villages.columns:
            villages[col] = None

    print(f"--- Extracting Dynamic World 'built' probability, group='{group}', window='{window_key}' ---")
    print(f"Before: {before_start} to {before_end}  |  After: {after_start} to {after_end}")
    print(f"{len(villages)} villages to process")

    for i, row in villages.iterrows():
        if all(pd.notna(row.get(c)) for c in outcome_cols):
            continue  # already extracted (resume support)

        point = ee.Geometry.Point([row["longitude"], row["latitude"]])
        buffered_geom = point.buffer(BUFFER_RADIUS_M)

        built_before, n_before = built_prob_for_period(buffered_geom, before_start, before_end)
        built_after, n_after = built_prob_for_period(buffered_geom, after_start, after_end)

        villages.at[i, "built_before"] = built_before
        villages.at[i, "built_after"] = built_after
        villages.at[i, "built_before_image_count"] = n_before
        villages.at[i, "built_after_image_count"] = n_after

        if (i + 1) % checkpoint_every == 0:
            villages.to_csv(out_path, index=False)
            print(f"  {i + 1}/{len(villages)} villages processed...")

        time.sleep(0.2)  # be polite to the Earth Engine API

    villages.to_csv(out_path, index=False)
    n_valid = villages.dropna(subset=["built_before", "built_after"]).shape[0]
    print(f"Done. {n_valid}/{len(villages)} villages have valid before/after 'built' probability.")
    print(f"Saved to {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract Dynamic World 'built' probability per village (H1/H4 triangulation check).")
    parser.add_argument("--group", choices=["treated", "control"], required=True)
    parser.add_argument("--window", choices=["full_year", "summer"], required=True)
    args = parser.parse_args()

    init_ee()
    extract(args.group, args.window)
