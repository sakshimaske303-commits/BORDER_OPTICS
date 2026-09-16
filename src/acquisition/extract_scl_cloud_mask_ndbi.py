"""Section 6.10 cloud-contamination row: this study's primary NDBI pipeline
masks clouds using the QA60 bitmask (bit 10 opaque cloud, bit 11 cirrus).
QA60 is Sentinel-2's older, coarser cloud flag and is deprecated in newer
processing baselines in favor of the Scene Classification Layer (SCL) band,
a per-pixel land-cover/cloud classification that is generally considered
more accurate, especially for thin cirrus and cloud shadow that QA60 tends
to miss. This script re-extracts summer-window NDBI for the treated core
sample using an SCL-based mask instead, so the two masks' results can be
compared directly on the same villages, same buffer, same dates -- the
cross-check the paper's own Section 6.10 threats table names as "not
cross-checked against an SCL- or Cloud-Score+-based mask."

Only the summer window and only the treated group are re-extracted here:
summer is the window this study's own cloud/snow-contamination bugs (Entries
21-22) actually occurred in, and this is a mask cross-check on the primary
group, not a new control-group or full-year exercise. Requires live Earth
Engine access -- run this on the researcher's own machine, the same way
every other extraction script in this study is run, not in a sandbox
without GEE credentials.

Usage:
    python3 src/acquisition/extract_scl_cloud_mask_ndbi.py
"""

import os
import time

import ee
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

VILLAGES_PATH = "data/processed/border_optics_master_villages.csv"
BUFFER_RADIUS_M = 500
S2_COLLECTION = "COPERNICUS/S2_SR_HARMONIZED"

BEFORE = ("2021-06-01", "2021-10-01")
AFTER = ("2025-06-01", "2025-10-01")
OUT_PATH = "data/processed/border_optics_village_results_summer_sclmask.csv"

# SCL classes treated as "clear" (kept): 2 dark area, 4 vegetation,
# 5 bare soils, 6 water, 7 unclassified is EXCLUDED (ambiguous), 11 snow
# (kept -- the summer window's own date range is chosen so high-altitude
# snow should mostly be absent already; keeping it here isolates the
# cloud-detection difference between QA60 and SCL rather than introducing a
# second, unrelated masking change). Excluded (treated as cloud/invalid):
# 0 no data, 1 saturated/defective, 3 cloud shadow, 7 unclassified,
# 8 cloud medium probability, 9 cloud high probability, 10 thin cirrus.
SCL_CLEAR_CLASSES = [2, 4, 5, 6, 11]


def init_ee():
    project = os.environ.get("EE_PROJECT")
    try:
        ee.Initialize(project=project)
    except Exception:
        ee.Authenticate()
        ee.Initialize(project=project)


def mask_s2_clouds_scl(image):
    scl = image.select("SCL")
    mask = scl.eq(SCL_CLEAR_CLASSES[0])
    for c in SCL_CLEAR_CLASSES[1:]:
        mask = mask.Or(scl.eq(c))
    return image.updateMask(mask).divide(10000)


def ndbi_for_period_scl(buffered_geom, start, end):
    collection = (
        ee.ImageCollection(S2_COLLECTION)
        .filterBounds(buffered_geom)
        .filterDate(start, end)
        .map(mask_s2_clouds_scl)
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


def extract(checkpoint_every=10):
    outcome_cols = [
        "ndbi_scl_before", "ndbi_scl_after",
        "ndbi_scl_before_image_count", "ndbi_scl_after_image_count",
    ]

    if os.path.exists(OUT_PATH):
        villages = pd.read_csv(OUT_PATH)
        print(f"Resuming from existing checkpoint: {OUT_PATH}")
    else:
        villages = pd.read_csv(VILLAGES_PATH)
        villages = villages[villages["is_core_sample"] == True].reset_index(drop=True)

    for col in outcome_cols:
        if col not in villages.columns:
            villages[col] = None

    print("--- SCL-mask NDBI re-extraction, summer window, treated core sample ---")
    print(f"Before: {BEFORE[0]} to {BEFORE[1]}  |  After: {AFTER[0]} to {AFTER[1]}")

    for i, row in villages.iterrows():
        if all(pd.notna(row.get(c)) for c in outcome_cols):
            continue

        point = ee.Geometry.Point([row["longitude"], row["latitude"]])
        buffered_geom = point.buffer(BUFFER_RADIUS_M)

        ndbi_before, n_before = ndbi_for_period_scl(buffered_geom, *BEFORE)
        ndbi_after, n_after = ndbi_for_period_scl(buffered_geom, *AFTER)

        villages.at[i, "ndbi_scl_before"] = ndbi_before
        villages.at[i, "ndbi_scl_after"] = ndbi_after
        villages.at[i, "ndbi_scl_before_image_count"] = n_before
        villages.at[i, "ndbi_scl_after_image_count"] = n_after

        if (i + 1) % checkpoint_every == 0:
            villages.to_csv(OUT_PATH, index=False)
            print(f"  {i + 1}/{len(villages)} villages processed...")

        time.sleep(0.2)

    villages.to_csv(OUT_PATH, index=False)
    n_valid = villages.dropna(subset=["ndbi_scl_before", "ndbi_scl_after"]).shape[0]
    print(f"Done. {n_valid}/{len(villages)} villages have valid SCL-masked before/after NDBI.")
    print(f"Saved to {OUT_PATH}")


if __name__ == "__main__":
    init_ee()
    extract()
