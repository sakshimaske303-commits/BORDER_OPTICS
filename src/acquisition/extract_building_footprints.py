"""
Building-footprint check (Section 7.2). Open Buildings is single-vintage, no
2021 vs 2025 to diff like NDBI, so this is just a current-state validation
check -- mainly for the Walong/Kaho/Musai ground-truth question.

Needs live GEE, run on my machine.

python3 src/acquisition/extract_building_footprints.py --group treated
python3 src/acquisition/extract_building_footprints.py --group control
"""
import argparse
import os
import time

import ee
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

OPEN_BUILDINGS_COLLECTION = "GOOGLE/Research/open-buildings/v3/polygons"
BUFFER_RADIUS_M = 500  # same buffer as everywhere else
CONFIDENCE_THRESHOLD = 0.75  # Open Buildings' default "high confidence" cutoff

VILLAGE_PATHS = {
    "treated": "data/processed/border_optics_master_villages.csv",
    "control": "data/processed/border_optics_control_villages.csv",
}
OUT_PATHS = {
    "treated": "data/processed/border_optics_treated_building_footprints.csv",
    "control": "data/processed/border_optics_control_building_footprints.csv",
}
OUTCOME_COLS = ["building_count", "building_total_area_m2", "building_mean_confidence"]


def init_ee():
    project = os.environ.get("EE_PROJECT")
    try:
        ee.Initialize(project=project)
    except Exception:
        ee.Authenticate()
        ee.Initialize(project=project)


def buildings_for_buffer(buffered_geom):
    # NOTE: filterBounds selects any building polygon that INTERSECTS the buffer, but
    # `area_in_meters` is that polygon's precomputed full area, not clipped to the buffer.
    # A building straddling the buffer edge therefore contributes its whole footprint area
    # to `total_area`, not just the portion inside the 500m region. `building_count` is
    # unaffected by this (it's a count of intersecting polygons, used for the published
    # correlations), but `building_total_area_m2` should be treated as an upper bound, not
    # an exact buffer-clipped area, until this is fixed with a `.intersection()`/clip step.
    fc = (
        ee.FeatureCollection(OPEN_BUILDINGS_COLLECTION)
        .filterBounds(buffered_geom)
        .filter(ee.Filter.gte("confidence", CONFIDENCE_THRESHOLD))
    )
    count = fc.size().getInfo()
    if count == 0:
        return 0, 0.0, None
    stats = fc.aggregate_stats("area_in_meters").getInfo()
    conf_mean = fc.aggregate_mean("confidence").getInfo()
    total_area = stats.get("sum", 0.0) if stats else 0.0
    return count, total_area, conf_mean


def extract(group, checkpoint_every=10):
    out_path = OUT_PATHS[group]

    if os.path.exists(out_path):
        villages = pd.read_csv(out_path)
        print(f"Resuming from existing checkpoint: {out_path}")
    else:
        villages = pd.read_csv(VILLAGE_PATHS[group])

    for col in OUTCOME_COLS:
        if col not in villages.columns:
            villages[col] = None

    print(f"--- Extracting Open Buildings footprint count/area, group='{group}' ---")
    print(f"Confidence threshold: >= {CONFIDENCE_THRESHOLD}")
    print(f"{len(villages)} villages to process")
    print("Note: single current-vintage snapshot, not before/after.")

    for i, row in villages.iterrows():
        if all(pd.notna(row.get(c)) for c in OUTCOME_COLS):
            continue

        point = ee.Geometry.Point([row["longitude"], row["latitude"]])
        buffered_geom = point.buffer(BUFFER_RADIUS_M)

        count, total_area, conf_mean = buildings_for_buffer(buffered_geom)

        villages.at[i, "building_count"] = count
        villages.at[i, "building_total_area_m2"] = total_area
        villages.at[i, "building_mean_confidence"] = conf_mean

        if (i + 1) % checkpoint_every == 0:
            villages.to_csv(out_path, index=False)
            print(f"  {i + 1}/{len(villages)} villages processed...")

        time.sleep(0.2)

    villages.to_csv(out_path, index=False)
    n_valid = villages.dropna(subset=["building_count"]).shape[0]
    print(f"Done. {n_valid}/{len(villages)} villages have a building-footprint count.")
    print(f"Saved to {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract Open Buildings footprint count/area per village buffer (single current snapshot; Section 7.2)."
    )
    parser.add_argument("--group", choices=["treated", "control"], required=True)
    args = parser.parse_args()

    init_ee()
    extract(args.group)
