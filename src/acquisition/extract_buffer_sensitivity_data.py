"""Re-runs the summer-window NDBI/VIIRS extraction at 250m and 1km buffers
to check the 500m radius isn't driving the result alone.

Same-day resume hazard (Section 6.9 / ANALYSIS_FREEZE.md item 3 -- still
open as of this note). This script's own checkpoint-resume logic will
silently do nothing useful if run again as-is: `border_optics_buffer250_summer.csv`
and `border_optics_buffer1000_summer.csv` are both already checkpointed at
251/251 villages complete (dated August 21, per Section 4.8), so a bare
re-run skips every row as "already extracted" and exits immediately without
pulling anything new -- it will NOT give you a fresh, same-day pull just
because you ran it again. The 500m primary extraction
(`extract_satellite_data.py --window summer`) has the identical problem: its
own checkpoint is complete too. Sentinel-2's archive keeps backfilling
scenes for past fixed date ranges, so any two extractions of the same
2021/2025 summer dates, run on different days, can disagree on scene counts
and composite values without either being wrong about buffer radius --
that's the actual §6.9 gap: this script's 250m/1km numbers and the primary
500m numbers were never pulled on the same day.

To actually close this gap, move all three existing checkpoints aside first
so every radius is forced to re-extract fresh, then run all three back-to-
back on the same day (same pattern Development Log Entry 22 used for its
own same-day treated/control re-pull):

    mv data/processed/border_optics_village_results_summer.csv data/processed/border_optics_village_results_summer_PRE_SAMEDAY_BUFFER_CHECK.csv
    mv data/processed/border_optics_buffer250_summer.csv data/processed/border_optics_buffer250_summer_PRE_SAMEDAY_BUFFER_CHECK.csv
    mv data/processed/border_optics_buffer1000_summer.csv data/processed/border_optics_buffer1000_summer_PRE_SAMEDAY_BUFFER_CHECK.csv
    python3 src/acquisition/extract_satellite_data.py --window summer
    python3 src/acquisition/extract_buffer_sensitivity_data.py --buffer 250
    python3 src/acquisition/extract_buffer_sensitivity_data.py --buffer 1000

Each full run takes over an hour for the 258-village sample (per Development
Log Entry 22's own timing note), so budget roughly 3+ hours run back-to-back,
not spread across days, or the same archive-timing gap this is meant to
close will just reopen. Low priority: every radius is already null on its
own (Section 4.8), so this closes a documentation/consistency gap, not an
open question about the conclusion itself.
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

    outcome_cols = [
        "ndbi_before", "ndbi_after", "ndbi_before_image_count", "ndbi_after_image_count",
        "lights_before", "lights_after", "lights_before_image_count", "lights_after_image_count",
    ]

    # Resume from the checkpointed output, not the original master list — this used
    # to always re-read VILLAGES_PATH (which never carries these columns at all), so
    # "resume support" silently reprocessed every village from scratch on every run.
    if os.path.exists(out_path):
        villages = pd.read_csv(out_path)
        print(f"Resuming from existing checkpoint: {out_path}")
    else:
        villages = pd.read_csv(VILLAGES_PATH)

    for col in outcome_cols:
        if col not in villages.columns:
            villages[col] = None

    print(f"--- Buffer-sensitivity extraction: {buffer_m}m radius, summer window ---")
    print(f"{len(villages)} villages to process")

    for i, row in villages.iterrows():
        # Skip only if ALL outcome AND image-count columns are already present —
        # checking just the four value columns would leave a row's image-count
        # columns permanently unpopulated if they were ever null on a checkpoint.
        if all(pd.notna(row.get(c)) for c in outcome_cols):
            continue  # already extracted (resume support)

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
