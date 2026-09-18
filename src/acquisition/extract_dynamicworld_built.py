"""
Cross-check for H1/H4: pulls Dynamic World's "built" probability (different
algorithm than my NDBI, though same S2 imagery underneath) for the same
villages/buffers/windows. Skipped GHSL on purpose -- its future epochs are
modelled not observed, so it'd be a fake "independent" check.

Run all 4 to match extract_satellite_data.py + extract_control_satellite_data.py coverage:

python3 src/acquisition/extract_dynamicworld_built.py --group treated --window full_year
python3 src/acquisition/extract_dynamicworld_built.py --group treated --window summer
python3 src/acquisition/extract_dynamicworld_built.py --group control --window full_year
python3 src/acquisition/extract_dynamicworld_built.py --group control --window summer
"""
import argparse
import os
import time

import ee
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

DW_COLLECTION = "GOOGLE/DYNAMICWORLD/V1"
BUFFER_RADIUS_M = 500  # matches extract_satellite_data.py's buffer

VILLAGE_PATHS = {
    "treated": "data/processed/border_optics_master_villages.csv",
    "control": "data/processed/border_optics_control_villages.csv",
}

# same date ranges as the NDBI/lights extraction, so it actually lines up
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

    # village list is the source of truth (the control list can get regenerated
    # by select_control_villages.py), so always read it fresh and only pull
    # prior values from a checkpoint when its rows match by coordinate --
    # otherwise a stale checkpoint silently overrides an updated village list.
    # Same convention as extract_control_satellite_data.py; this script used to
    # just load the checkpoint outright with no mismatch check, which is what
    # let a post-district-verification-rerun run silently reuse the old
    # 732-village control checkpoint instead of the corrected 721-village list.
    villages = pd.read_csv(VILLAGE_PATHS[group])
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
            lookup = existing.copy()
            lookup["_coord_key"] = list(zip(lookup["latitude"].round(6), lookup["longitude"].round(6)))
            lookup_dict = lookup.set_index("_coord_key")[
                [c for c in outcome_cols if c in lookup.columns]
            ].to_dict("index")
            villages_keys = list(zip(villages["latitude"].round(6), villages["longitude"].round(6)))
            for i, key in zip(villages.index, villages_keys):
                values = lookup_dict.get(key)
                if values:
                    for col in outcome_cols:
                        if col in values:
                            villages.at[i, col] = values[col]
            print(f"Resuming from existing checkpoint: {out_path} (matched by coordinate, {len(existing)} rows)")
        else:
            print(f"  Checkpoint at {out_path} doesn't match current village list -- starting fresh.")

    print(f"--- Extracting Dynamic World 'built' probability, group='{group}', window='{window_key}' ---")
    print(f"Before: {before_start} to {before_end}  |  After: {after_start} to {after_end}")
    print(f"{len(villages)} villages to process")

    for i, row in villages.iterrows():
        if all(pd.notna(row.get(c)) for c in outcome_cols):
            continue

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

        time.sleep(0.2)

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
