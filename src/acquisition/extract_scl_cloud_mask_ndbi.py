"""
SCL-mask cross-check for Section 6.10 -- redo summer NDBI (treated core sample
only) with the SCL band instead of QA60, see if the numbers hold up.

Bug caught in external review: class 11 is snow/ice, not clear ground, and
these are Himalayan villages in June-Sept, so the old class list was letting
snow through as "clear." Runs two corrected variants now instead of one --
"corrected" drops snow, "strict" also drops dark-area pixels -- so both are
on record instead of picking one. The old buggy output
(border_optics_village_results_summer_sclmask.csv, classes [2,4,5,6,11]) is
left on disk untouched as the pre-fix record, not overwritten.

Needs live GEE, run on my machine.

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

# corrected: 2 dark area, 4 vegetation, 5 bare soil, 6 water -- snow (11) dropped
# strict: same minus dark area pixels too, in case those are also iffy over villages
VARIANTS = {
    "corrected": {
        "classes": [2, 4, 5, 6],
        "out_path": "data/processed/border_optics_village_results_summer_sclmask_corrected.csv",
    },
    "strict": {
        "classes": [4, 5, 6],
        "out_path": "data/processed/border_optics_village_results_summer_sclmask_strict.csv",
    },
}


def init_ee():
    project = os.environ.get("EE_PROJECT")
    try:
        ee.Initialize(project=project)
    except Exception:
        ee.Authenticate()
        ee.Initialize(project=project)


def make_mask_fn(classes):
    def mask_s2_clouds_scl(image):
        scl = image.select("SCL")
        mask = scl.eq(classes[0])
        for c in classes[1:]:
            mask = mask.Or(scl.eq(c))
        return image.updateMask(mask).divide(10000)
    return mask_s2_clouds_scl


def ndbi_for_period_scl(buffered_geom, start, end, mask_fn):
    collection = (
        ee.ImageCollection(S2_COLLECTION)
        .filterBounds(buffered_geom)
        .filterDate(start, end)
        .map(mask_fn)
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


def extract(classes, out_path, checkpoint_every=10):
    outcome_cols = [
        "ndbi_scl_before", "ndbi_scl_after",
        "ndbi_scl_before_image_count", "ndbi_scl_after_image_count",
    ]

    if os.path.exists(out_path):
        villages = pd.read_csv(out_path)
        print(f"Resuming from existing checkpoint: {out_path}")
    else:
        villages = pd.read_csv(VILLAGES_PATH)
        villages = villages[villages["is_core_sample"] == True].reset_index(drop=True)

    for col in outcome_cols:
        if col not in villages.columns:
            villages[col] = None

    mask_fn = make_mask_fn(classes)

    print(f"--- SCL-mask NDBI re-extraction, summer window, classes={classes} ---")
    print(f"Before: {BEFORE[0]} to {BEFORE[1]}  |  After: {AFTER[0]} to {AFTER[1]}")

    for i, row in villages.iterrows():
        if all(pd.notna(row.get(c)) for c in outcome_cols):
            continue

        point = ee.Geometry.Point([row["longitude"], row["latitude"]])
        buffered_geom = point.buffer(BUFFER_RADIUS_M)

        ndbi_before, n_before = ndbi_for_period_scl(buffered_geom, *BEFORE, mask_fn)
        ndbi_after, n_after = ndbi_for_period_scl(buffered_geom, *AFTER, mask_fn)

        villages.at[i, "ndbi_scl_before"] = ndbi_before
        villages.at[i, "ndbi_scl_after"] = ndbi_after
        villages.at[i, "ndbi_scl_before_image_count"] = n_before
        villages.at[i, "ndbi_scl_after_image_count"] = n_after

        if (i + 1) % checkpoint_every == 0:
            villages.to_csv(out_path, index=False)
            print(f"  {i + 1}/{len(villages)} villages processed...")

        time.sleep(0.2)

    villages.to_csv(out_path, index=False)
    n_valid = villages.dropna(subset=["ndbi_scl_before", "ndbi_scl_after"]).shape[0]
    print(f"Done. {n_valid}/{len(villages)} villages have valid SCL-masked before/after NDBI.")
    print(f"Saved to {out_path}")


if __name__ == "__main__":
    init_ee()
    for name, cfg in VARIANTS.items():
        print(f"\n=== variant: {name} ===")
        extract(cfg["classes"], cfg["out_path"])
