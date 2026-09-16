"""Buffers each village 500m, pulls NDBI (Sentinel-2) and VIIRS night-lights
for full_year/summer windows. Null (not zero) when a period has no
cloud-free images.
"""

import argparse
import os
import time

import ee
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

VILLAGES_PATH = "data/processed/border_optics_master_villages.csv"
BUFFER_RADIUS_M = 500

S2_COLLECTION = "COPERNICUS/S2_SR_HARMONIZED"
VIIRS_COLLECTION = "NOAA/VIIRS/DNB/MONTHLY_V1/VCMSLCFG"

WINDOWS = {
    "full_year": {
        "before": ("2021-01-01", "2022-01-01"),
        "after": ("2025-01-01", "2026-01-01"),
        "out_path": "data/processed/border_optics_village_results.csv",
    },
    "summer": {
        "before": ("2021-06-01", "2021-10-01"),
        "after": ("2025-06-01", "2025-10-01"),
        "out_path": "data/processed/border_optics_village_results_summer.csv",
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
    # QA60 bitmask: bit 10 = opaque clouds, bit 11 = cirrus
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

    # needs ee.Geometry not ee.Feature -- call .geometry() first if buffering a Feature
    stats = ndbi_image.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=buffered_geom,
        scale=10,
        maxPixels=1e9,
    ).getInfo()

    return stats.get("NDBI"), count


def lights_for_period(buffered_geom, start, end):
    collection = ee.ImageCollection(VIIRS_COLLECTION).filterBounds(buffered_geom).filterDate(start, end)
    count = collection.size().getInfo()
    if count == 0:
        return None, 0

    composite = collection.select("avg_rad").mean()
    stats = composite.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=buffered_geom,
        scale=500,
        maxPixels=1e9,
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

    # resume from checkpoint csv, not the master list, or we lose all progress
    if os.path.exists(out_path):
        villages = pd.read_csv(out_path)
        print(f"Resuming from existing checkpoint: {out_path}")
        if "latitude" not in villages.columns or "longitude" not in villages.columns:
            # old checkpoints don't have lat/lon at all -- pull them back in via village_id
            coords = pd.read_csv(VILLAGES_PATH)[["village_id", "latitude", "longitude"]]
            villages = villages.merge(coords, on="village_id", how="left")
            missing_coords = villages["latitude"].isna().sum()
            if missing_coords:
                print(f"  WARNING: {missing_coords} row(s) in the checkpoint have no matching "
                      f"village_id in {VILLAGES_PATH} — their coordinates are still missing.")
    else:
        villages = pd.read_csv(VILLAGES_PATH)

    for col in outcome_cols:
        if col not in villages.columns:
            villages[col] = None

    print(f"--- Extracting satellite data, window='{window_key}' ---")
    print(f"Before: {before_start} to {before_end}  |  After: {after_start} to {after_end}")

    for i, row in villages.iterrows():
        # only skip once every outcome + image-count col is filled in
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
            print(f"  {i + 1}/{len(villages)} villages processed...")

        time.sleep(0.2)

    villages.to_csv(out_path, index=False)

    n_valid = villages.dropna(subset=["ndbi_before", "ndbi_after"]).shape[0]
    print(f"Done. {n_valid}/{len(villages)} villages have valid before/after NDBI data.")
    print(f"Saved to {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract Sentinel-2 NDBI and VIIRS night-lights per village.")
    parser.add_argument(
        "--window", choices=["full_year", "summer"], required=True,
        help="Which compositing window to run — see module docstring.",
    )
    args = parser.parse_args()

    init_ee()
    extract_window(args.window)
