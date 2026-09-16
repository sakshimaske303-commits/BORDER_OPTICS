"""Same extraction logic as extract_satellite_data.py, for the non-VVP
control group; kept separate so the treated-sample run stays untouched.
"""

import argparse
import os
import time

import ee
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

VILLAGES_PATH = "data/processed/border_optics_control_villages.csv"
BUFFER_RADIUS_M = 500

S2_COLLECTION = "COPERNICUS/S2_SR_HARMONIZED"
VIIRS_COLLECTION = "NOAA/VIIRS/DNB/MONTHLY_V1/VCMSLCFG"

WINDOWS = {
    "full_year": {
        "before": ("2021-01-01", "2022-01-01"),
        "after": ("2025-01-01", "2026-01-01"),
        "out_path": "data/processed/border_optics_control_results.csv",
    },
    "summer": {
        "before": ("2021-06-01", "2021-10-01"),
        "after": ("2025-06-01", "2025-10-01"),
        "out_path": "data/processed/border_optics_control_results_summer.csv",
    },
}


def init_ee():
    # need EE_PROJECT set in .env or Initialize() fails
    project = os.environ.get("EE_PROJECT")
    try:
        ee.Initialize(project=project)
    except Exception:
        ee.Authenticate()
        ee.Initialize(project=project)


def mask_s2_clouds(image):
    qa = image.select("QA60")
    cloud_bit_mask = 1 << 10
    cirrus_bit_mask = 1 << 11
    mask = qa.bitwiseAnd(cloud_bit_mask).eq(0).And(qa.bitwiseAnd(cirrus_bit_mask).eq(0))
    return image.updateMask(mask).divide(10000)


def ndbi_for_period(buffered_geom, start, end):
    collection = (
        ee.ImageCollection(S2_COLLECTION)
        .filterBounds(buffered_geom)
        .filterDate(start, end)
        .map(mask_s2_clouds)
    )
    count = collection.size().getInfo()
    if count == 0:
        return None, 0

    composite = collection.median()
    ndbi_image = composite.normalizedDifference(["B11", "B8"]).rename("NDBI")
    stats = ndbi_image.reduceRegion(
        reducer=ee.Reducer.mean(), geometry=buffered_geom, scale=10, maxPixels=1e9,
    ).getInfo()
    return stats.get("NDBI"), count


def lights_for_period(buffered_geom, start, end):
    collection = ee.ImageCollection(VIIRS_COLLECTION).filterBounds(buffered_geom).filterDate(start, end)
    count = collection.size().getInfo()
    if count == 0:
        return None, 0

    composite = collection.select("avg_rad").mean()
    stats = composite.reduceRegion(
        reducer=ee.Reducer.mean(), geometry=buffered_geom, scale=500, maxPixels=1e9,
    ).getInfo()
    return stats.get("avg_rad"), count


def extract_window(window_key, checkpoint_every=10):
    cfg = WINDOWS[window_key]
    before_start, before_end = cfg["before"]
    after_start, after_end = cfg["after"]
    out_path = cfg["out_path"]

    outcome_cols = [
        "ndbi_before", "ndbi_after", "ndbi_before_image_count", "ndbi_after_image_count",
        "lights_before", "lights_after", "lights_before_image_count", "lights_after_image_count",
    ]

    # control village list gets fully regenerated each time (village_id isn't stable),
    # so resume by matching lat/lon coords, not village_id
    villages = pd.read_csv(VILLAGES_PATH)
    for col in outcome_cols:
        if col not in villages.columns:
            villages[col] = None

    if os.path.exists(out_path):
        existing = pd.read_csv(out_path)
        current_coords = set(zip(villages["latitude"].round(6), villages["longitude"].round(6)))
        existing_coords = (
            set(zip(existing["latitude"].round(6), existing["longitude"].round(6)))
            if {"latitude", "longitude"}.issubset(existing.columns) else set()
        )
        if existing_coords and existing_coords == current_coords:
            # both sides gotta use the same .round(6) call (Series.round, not scalar round())
            # or floating point makes a few coords mismatch even though the sets match overall
            lookup = existing.copy()
            lookup["_coord_key"] = list(zip(lookup["latitude"].round(6), lookup["longitude"].round(6)))
            lookup_dict = lookup.set_index("_coord_key")[outcome_cols].to_dict("index")
            villages_keys = list(zip(villages["latitude"].round(6), villages["longitude"].round(6)))
            missing_keys = 0
            for i, key in zip(villages.index, villages_keys):
                values = lookup_dict.get(key)
                if values is None:
                    missing_keys += 1
                    continue
                for col in outcome_cols:
                    villages.at[i, col] = values[col]
            print(f"Resuming from existing checkpoint: {out_path} (matched by coordinate, {len(existing)} rows)")
            if missing_keys:
                print(f"  NOTE: {missing_keys} row(s) had no exact coordinate match (rounding edge case) — will be re-extracted.")
        else:
            print(f"  Checkpoint at {out_path} doesn't match current village list — starting fresh.")

    print(f"--- Extracting control-group satellite data, window='{window_key}' ---")
    print(f"Before: {before_start} to {before_end}  |  After: {after_start} to {after_end}")
    print(f"{len(villages)} control villages to process")

    for i, row in villages.iterrows():
        if all(pd.notna(row.get(c)) for c in outcome_cols):
            continue

        point = ee.Geometry.Point([row["longitude"], row["latitude"]])
        buffered_geom = point.buffer(BUFFER_RADIUS_M)

        ndbi_before, ndbi_before_n = ndbi_for_period(buffered_geom, before_start, before_end)
        ndbi_after, ndbi_after_n = ndbi_for_period(buffered_geom, after_start, after_end)
        lights_before, lights_before_n = lights_for_period(buffered_geom, before_start, before_end)
        lights_after, lights_after_n = lights_for_period(buffered_geom, after_start, after_end)

        villages.at[i, "ndbi_before"] = ndbi_before
        villages.at[i, "ndbi_after"] = ndbi_after
        villages.at[i, "ndbi_before_image_count"] = ndbi_before_n
        villages.at[i, "ndbi_after_image_count"] = ndbi_after_n
        villages.at[i, "lights_before"] = lights_before
        villages.at[i, "lights_after"] = lights_after
        villages.at[i, "lights_before_image_count"] = lights_before_n
        villages.at[i, "lights_after_image_count"] = lights_after_n

        if (i + 1) % checkpoint_every == 0:
            villages.to_csv(out_path, index=False)
            print(f"  {i + 1}/{len(villages)} control villages processed...")

        time.sleep(0.2)

    villages.to_csv(out_path, index=False)
    n_valid = villages.dropna(subset=["ndbi_before", "ndbi_after"]).shape[0]
    print(f"Done. {n_valid}/{len(villages)} control villages have valid before/after NDBI data.")
    print(f"Saved to {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract Sentinel-2 NDBI and VIIRS night-lights for the control group.")
    parser.add_argument("--window", choices=["full_year", "summer"], required=True)
    args = parser.parse_args()

    init_ee()
    extract_window(args.window)
