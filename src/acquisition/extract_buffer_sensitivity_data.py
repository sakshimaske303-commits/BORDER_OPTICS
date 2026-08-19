"""Re-runs the summer-window NDBI/VIIRS extraction at 250m and 1km buffers
to check the 500m radius isn't driving the result alone.
"""

import argparse
import os
import time

import ee
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

VILLAGES_PATH = "data/processed/border_optics_master_villages.csv"

S2_COLLECTION = "COPERNICUS/S2_SR_HARMONIZED"
VIIRS_COLLECTION = "NOAA/VIIRS/DNB/MONTHLY_V1/VCMSLCFG"

# Same summer window used throughout the rest of this study
BEFORE = ("2021-06-01", "2021-10-01")
AFTER = ("2025-06-01", "2025-10-01")


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


def extract_buffer(buffer_m, checkpoint_every=10):
    out_path = f"data/processed/border_optics_buffer{buffer_m}_summer.csv"
    villages = pd.read_csv(VILLAGES_PATH)

    for col in [
        "ndbi_before", "ndbi_after", "ndbi_before_image_count", "ndbi_after_image_count",
        "lights_before", "lights_after", "lights_before_image_count", "lights_after_image_count",
    ]:
        if col not in villages.columns:
            villages[col] = None

    print(f"--- Buffer-sensitivity extraction: {buffer_m}m radius, summer window ---")
    print(f"{len(villages)} villages to process")

    for i, row in villages.iterrows():
        if pd.notna(row.get("ndbi_before")) and pd.notna(row.get("ndbi_after")):
            continue  # resume support

        point = ee.Geometry.Point([row["longitude"], row["latitude"]])
        buffered_geom = point.buffer(buffer_m)

        ndbi_before, ndbi_before_n = ndbi_for_period(buffered_geom, *BEFORE)
        ndbi_after, ndbi_after_n = ndbi_for_period(buffered_geom, *AFTER)
        lights_before, lights_before_n = lights_for_period(buffered_geom, *BEFORE)
        lights_after, lights_after_n = lights_for_period(buffered_geom, *AFTER)

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
    print(f"Done. {n_valid}/{len(villages)} villages have valid before/after NDBI data at {buffer_m}m.")
    print(f"Saved to {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract NDBI/VIIRS at an alternative buffer radius (summer window).")
    parser.add_argument("--buffer", type=int, choices=[250, 1000], required=True)
    args = parser.parse_args()

    init_ee()
    extract_buffer(args.buffer)
