"""
2019 Dynamic World baseline -- the DW analogue of extract_pretreatment_baseline.py.
Anara AI's suggestion #2: since Dynamic World shows a small but significant
control-group effect (Section 6, triangulation) while NDBI doesn't, a genuine
placebo test on DW itself (not just on NDBI/lights) is worth having before
trusting that DW gap as real rather than a pre-existing trend.

Gives a 2019 DW "built" value per village, to compare against the 2021 value
already sitting in border_optics_{treated,control}_dynamicworld_{fullyear,summer}.csv
(their "built_before" column, extracted by extract_dynamicworld_built.py --
its full_year "before" window is 2021-01-01 to 2022-01-01, same as here's
full_year window's role). Both periods are pre-treatment (VVP-I wasn't
sanctioned until Feb 2023), so a genuine treated-vs-control DiD on the
2019-to-2021 DW change should come back null if the 2025 DW gap is a real
post-treatment effect and not something that was already drifting apart
beforehand.

Needs live GEE, run on my machine (same as extract_pretreatment_baseline.py
and extract_dynamicworld_built.py -- this script is a straightforward
combination of the two: extract_dynamicworld_built.py's DW collection/logic,
extract_pretreatment_baseline.py's 2019-only window and resume-by-village_id
(treated) / resume-by-coordinate (control) pattern).

Run all 4 to match dw_pretreatment_placebo_test.py's expected inputs:

python3 src/acquisition/extract_dw_pretreatment_baseline.py --group treated --window full_year
python3 src/acquisition/extract_dw_pretreatment_baseline.py --group treated --window summer
python3 src/acquisition/extract_dw_pretreatment_baseline.py --group control --window full_year
python3 src/acquisition/extract_dw_pretreatment_baseline.py --group control --window summer

Then run src/analysis/dw_pretreatment_placebo_test.py once all 4 exist.
"""
import argparse
import os
import time

import ee
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

DW_COLLECTION = "GOOGLE/DYNAMICWORLD/V1"
BUFFER_RADIUS_M = 500  # same buffer as extract_dynamicworld_built.py / everywhere else

VILLAGE_PATHS = {
    "treated": "data/processed/border_optics_master_villages.csv",
    "control": "data/processed/border_optics_control_villages.csv",
}

# single composite per village here, not before/after -- 2019 IS the "before"
# for this placebo, same convention as extract_pretreatment_baseline.py
WINDOWS = {
    "full_year": ("2019-01-01", "2020-01-01"),
    "summer": ("2019-06-01", "2019-10-01"),
}

OUT_PATHS = {
    ("treated", "full_year"): "data/processed/border_optics_treated_dw_pretreatment_fullyear.csv",
    ("treated", "summer"): "data/processed/border_optics_treated_dw_pretreatment_summer.csv",
    ("control", "full_year"): "data/processed/border_optics_control_dw_pretreatment_fullyear.csv",
    ("control", "summer"): "data/processed/border_optics_control_dw_pretreatment_summer.csv",
}

OUTCOME_COLS = ["built_2019", "built_2019_image_count"]


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
        reducer=ee.Reducer.mean(), geometry=buffered_geom, scale=10, maxPixels=1e9,
    ).getInfo()
    return stats.get("built"), count


def _load_with_resume(group, out_path):
    # identical resume convention to extract_pretreatment_baseline.py: treated
    # resumes by stable village_id, control resumes by coordinate (and refuses
    # to reuse a checkpoint whose coordinates don't match the current control
    # list, since select_control_villages.py can regenerate that list)
    villages = pd.read_csv(VILLAGE_PATHS[group])
    for col in OUTCOME_COLS:
        if col not in villages.columns:
            villages[col] = None

    if not os.path.exists(out_path):
        return villages

    existing = pd.read_csv(out_path)

    if group == "treated":
        if "village_id" in existing.columns:
            lookup = existing.set_index("village_id")[
                [c for c in OUTCOME_COLS if c in existing.columns]
            ].to_dict("index")
            for i, vid in zip(villages.index, villages["village_id"]):
                values = lookup.get(vid)
                if values:
                    for col in OUTCOME_COLS:
                        if col in values:
                            villages.at[i, col] = values[col]
            print(f"Resuming from existing checkpoint: {out_path} ({len(existing)} rows, matched by village_id)")
        return villages

    current_coords = set(zip(villages["latitude"].round(6), villages["longitude"].round(6)))
    existing_coords = (
        set(zip(existing["latitude"].round(6), existing["longitude"].round(6)))
        if {"latitude", "longitude"}.issubset(existing.columns) else set()
    )
    if not (existing_coords and existing_coords == current_coords):
        print(f"  Checkpoint at {out_path} doesn't match current control list -- starting fresh.")
        return villages

    lookup = existing.copy()
    lookup["_coord_key"] = list(zip(lookup["latitude"].round(6), lookup["longitude"].round(6)))
    lookup_dict = lookup.set_index("_coord_key")[
        [c for c in OUTCOME_COLS if c in lookup.columns]
    ].to_dict("index")
    villages_keys = list(zip(villages["latitude"].round(6), villages["longitude"].round(6)))
    for i, key in zip(villages.index, villages_keys):
        values = lookup_dict.get(key)
        if values:
            for col in OUTCOME_COLS:
                if col in values:
                    villages.at[i, col] = values[col]
    print(f"Resuming from existing checkpoint: {out_path} ({len(existing)} rows, matched by coordinate)")
    return villages


def extract(group, window_key, checkpoint_every=10):
    start, end = WINDOWS[window_key]
    out_path = OUT_PATHS[(group, window_key)]
    villages = _load_with_resume(group, out_path)

    print(f"--- Extracting {window_key} 2019 Dynamic World 'built' baseline, group='{group}' ---")
    print(f"Period: {start} to {end}")
    print(f"{len(villages)} villages to process")

    for i, row in villages.iterrows():
        if all(pd.notna(row.get(c)) for c in OUTCOME_COLS):
            continue

        point = ee.Geometry.Point([row["longitude"], row["latitude"]])
        buffered_geom = point.buffer(BUFFER_RADIUS_M)

        built, n = built_prob_for_period(buffered_geom, start, end)

        villages.at[i, "built_2019"] = built
        villages.at[i, "built_2019_image_count"] = n

        if (i + 1) % checkpoint_every == 0:
            villages.to_csv(out_path, index=False)
            print(f"  {i + 1}/{len(villages)} villages processed...")

        time.sleep(0.2)

    villages.to_csv(out_path, index=False)
    n_valid = villages.dropna(subset=["built_2019"]).shape[0]
    print(f"Done. {n_valid}/{len(villages)} villages have valid 2019 Dynamic World data.")
    print(f"Saved to {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract a 2019 Dynamic World 'built' baseline for a DW-specific parallel-pre-trends placebo test."
    )
    parser.add_argument("--group", choices=["treated", "control"], required=True)
    parser.add_argument("--window", choices=["full_year", "summer"], required=True)
    args = parser.parse_args()

    init_ee()
    extract(args.group, args.window)
