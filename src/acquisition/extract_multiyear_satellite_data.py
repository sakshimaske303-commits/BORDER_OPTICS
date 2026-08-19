"""Adds a 2023 time point between the 2021/2025 pair so a three-point trend
can be fit instead of a single before-after difference.
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

YEARS = [2021, 2023, 2025]

WINDOW_MONTHS = {
    "full_year": {"out_path": "data/processed/border_optics_multiyear_fullyear.csv"},
    "summer": {"out_path": "data/processed/border_optics_multiyear_summer.csv"},
}


def year_range(window_key, year):
    if window_key == "full_year":
        return f"{year}-01-01", f"{year + 1}-01-01"
    else:  # summer: June 1 - Sep 30, season-matched
        return f"{year}-06-01", f"{year}-10-01"


def init_ee():
    # Recent earthengine-api versions require a Cloud project attached to
    # Initialize() — a bare browser authentication no longer implies one.
    # Set EE_PROJECT in .env (see .env.example) to your Earth Engine-enabled
    # Google Cloud project ID.
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
    out_path = WINDOW_MONTHS[window_key]["out_path"]
    villages = pd.read_csv(VILLAGES_PATH)

    for year in YEARS:
        for prefix in ["ndbi", "ndbi_n", "lights", "lights_n"]:
            col = f"{prefix}_{year}"
            if col not in villages.columns:
                villages[col] = None

    print(f"--- Multi-year extraction, window='{window_key}', years={YEARS} ---")
    print(f"{len(villages)} villages to process")

    for i, row in villages.iterrows():
        already_done = all(pd.notna(row.get(f"ndbi_{y}")) for y in YEARS)
        if already_done:
            continue

        point = ee.Geometry.Point([row["longitude"], row["latitude"]])
        buffered_geom = point.buffer(BUFFER_RADIUS_M)

        for year in YEARS:
            start, end = year_range(window_key, year)
            ndbi_val, ndbi_n = ndbi_for_period(buffered_geom, start, end)
            lights_val, lights_n = lights_for_period(buffered_geom, start, end)
            villages.at[i, f"ndbi_{year}"] = ndbi_val
            villages.at[i, f"ndbi_n_{year}"] = ndbi_n
            villages.at[i, f"lights_{year}"] = lights_val
            villages.at[i, f"lights_n_{year}"] = lights_n

        if (i + 1) % checkpoint_every == 0:
            villages.to_csv(out_path, index=False)
            print(f"  {i + 1}/{len(villages)} villages processed...")

        time.sleep(0.2)

    villages.to_csv(out_path, index=False)
    n_valid = villages.dropna(subset=[f"ndbi_{y}" for y in YEARS]).shape[0]
    print(f"Done. {n_valid}/{len(villages)} villages have valid NDBI at all {len(YEARS)} time points.")
    print(f"Saved to {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract NDBI/VIIRS at 2021, 2023, 2025 for a multi-year trend.")
    parser.add_argument("--window", choices=["full_year", "summer"], required=True)
    args = parser.parse_args()

    init_ee()
    extract_window(args.window)
