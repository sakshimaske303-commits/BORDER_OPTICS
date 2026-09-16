"""
Checks NDBI/lights/Dynamic World against Open Buildings footprint count/area
(Section 7.2). Only one snapshot of Open Buildings exists so this is a
cross-sectional correlation, not before/after. Also checks Walong/Kaho/Musai
(confirmed new construction) against the rest.

Needs extract_building_footprints.py run for the treated group first.

Usage:
    python3 src/analysis/building_footprint_validation.py
"""
import json

import pandas as pd
from scipy import stats

TREATED_FOOTPRINTS = "data/processed/border_optics_treated_building_footprints.csv"
CONTROL_FOOTPRINTS = "data/processed/border_optics_control_building_footprints.csv"
TREATED_RESULTS_FULLYEAR = "data/processed/border_optics_village_results_analyzed.csv"
TREATED_DYNAMICWORLD_FULLYEAR = "data/processed/border_optics_treated_dynamicworld_fullyear.csv"
OUT_JSON = "outputs/building_footprint_validation.json"

CASE_STUDY_VILLAGES = ["Walong", "Kaho", "Musai"]


def cross_sectional_check():
    fp = pd.read_csv(TREATED_FOOTPRINTS)[["village_id", "village", "building_count", "building_total_area_m2"]]
    ndbi = pd.read_csv(TREATED_RESULTS_FULLYEAR)
    ndbi = ndbi[ndbi["is_core_sample"] == True][["village_id", "ndbi_after", "lights_after"]]
    dw = pd.read_csv(TREATED_DYNAMICWORLD_FULLYEAR)[["village_id", "built_after"]]

    merged = fp.merge(ndbi, on="village_id", how="inner").merge(dw, on="village_id", how="inner")
    merged = merged.dropna(subset=["building_count"])

    results = {}
    for outcome in ["ndbi_after", "lights_after", "built_after"]:
        v = merged.dropna(subset=[outcome])
        rho, p = stats.spearmanr(v["building_count"], v[outcome])
        results[f"building_count_vs_{outcome}"] = {"n": len(v), "rho": float(rho), "p": float(p)}
        print(f"Spearman(building_count, {outcome}): n={len(v)}  rho={rho:.4f}  p={p:.5f}")

    return results, merged


def case_study_check(merged):
    print("\n-- Case-study villages (Section 7.3/6.6 ground truth) --")
    sub = merged[merged["village"].isin(CASE_STUDY_VILLAGES)]
    print(sub[["village", "building_count", "building_total_area_m2", "ndbi_after", "lights_after", "built_after"]].to_string(index=False))

    comparison = merged[~merged["village"].isin(CASE_STUDY_VILLAGES)]
    print(f"\nSample-wide median building_count: {comparison['building_count'].median()}")
    return sub


def main():
    results, merged = cross_sectional_check()
    case_rows = case_study_check(merged)
    results["case_study_villages"] = case_rows.to_dict("records")
    with open(OUT_JSON, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nSaved {OUT_JSON}")


if __name__ == "__main__":
    main()
