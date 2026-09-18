"""
Dynamic World parallel-pre-trends placebo test -- the DW analogue of
pretreatment_placebo_test.py. Checks 2019-to-2021 change in DW's "built"
probability, treated vs control, both pre-treatment (VVP-I wasn't sanctioned
till Feb 2023). Same motivation as the NDBI/lights placebo test, but run on
DW specifically: Section 6's triangulation already shows DW disagreeing with
NDBI on the control-group DiD (DW: small but significant effect; NDBI: null).
This test asks whether that DW gap was already there before treatment could
possibly apply -- if the 2019-to-2021 DW change is itself null, the later DW
control-group effect is not just a pre-existing DW drift picked up by chance.

Same spec as pretreatment_placebo_test.py's placebo_did(): district FE,
cluster-robust SE by district, one outcome (built) instead of two (ndbi,
lights), since Dynamic World only has the one "built" band.

Needs extract_dw_pretreatment_baseline.py run for both groups/windows first.

Usage:
    python3 src/analysis/dw_pretreatment_placebo_test.py --window full_year
    python3 src/analysis/dw_pretreatment_placebo_test.py --window summer
"""
import argparse
import json

import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats

DW_PRETREATMENT_PATHS = {
    ("treated", "full_year"): "data/processed/border_optics_treated_dw_pretreatment_fullyear.csv",
    ("treated", "summer"): "data/processed/border_optics_treated_dw_pretreatment_summer.csv",
    ("control", "full_year"): "data/processed/border_optics_control_dw_pretreatment_fullyear.csv",
    ("control", "summer"): "data/processed/border_optics_control_dw_pretreatment_summer.csv",
}
# the "2021" side of this comparison is the built_before column already
# extracted by extract_dynamicworld_built.py (its full_year "before" window is
# 2021-01-01 to 2022-01-01, matching the NDBI/lights "before" definition)
EXISTING_DW_2021_PATHS = {
    ("treated", "full_year"): "data/processed/border_optics_treated_dynamicworld_fullyear.csv",
    ("treated", "summer"): "data/processed/border_optics_treated_dynamicworld_summer.csv",
    ("control", "full_year"): "data/processed/border_optics_control_dynamicworld_fullyear.csv",
    ("control", "summer"): "data/processed/border_optics_control_dynamicworld_summer.csv",
}
SUMMARY_OUT = {
    "full_year": "outputs/dw_pretreatment_placebo_summary_fullyear.json",
    "summer": "outputs/dw_pretreatment_placebo_summary_summer.json",
}


def build_group(group, window):
    """Returns one row per village: village_id, district, treatment,
    built_2019, built_2021, built_placebo_change (=2021-2019)."""
    baseline = pd.read_csv(DW_PRETREATMENT_PATHS[(group, window)])
    existing = pd.read_csv(EXISTING_DW_2021_PATHS[(group, window)])
    if group == "treated":
        existing = existing[existing["is_core_sample"] == True]
        # treated village_id is stable across runs, safe to join on
        baseline = baseline[["village_id", "built_2019"]]
        existing = existing[["village_id", "district", "built_before"]].rename(
            columns={"built_before": "built_2021"}
        )
        merged = existing.merge(baseline, on="village_id", how="inner")
    else:
        # control village_id gets reassigned fresh every time
        # select_control_villages.py regenerates the list, so it is NOT a safe
        # join key here (same issue found and fixed in pretreatment_placebo_test.py) --
        # join on rounded coordinates instead, which are stable per village.
        baseline = baseline.copy()
        existing = existing.copy()
        baseline["_coord_key"] = list(zip(baseline["latitude"].round(6), baseline["longitude"].round(6)))
        existing["_coord_key"] = list(zip(existing["latitude"].round(6), existing["longitude"].round(6)))
        baseline = baseline[["_coord_key", "built_2019"]]
        existing = existing[["_coord_key", "village_id", "district", "built_before"]].rename(
            columns={"built_before": "built_2021"}
        )
        merged = existing.merge(baseline, on="_coord_key", how="inner").drop(columns="_coord_key")
        n_dropped = len(existing) - len(merged)
        if n_dropped:
            print(f"  NOTE: {n_dropped} control village(s) in {EXISTING_DW_2021_PATHS[(group, window)]} "
                  f"have no matching coordinate in {DW_PRETREATMENT_PATHS[(group, window)]} -- the 2019 "
                  f"DW baseline is for a different control-list vintage and should be re-extracted "
                  f"(extract_dw_pretreatment_baseline.py --group control) before trusting this result.")
    merged["treatment"] = 1 if group == "treated" else 0
    merged["built_placebo_change"] = merged["built_2021"] - merged["built_2019"]
    return merged


def placebo_did(panel, outcome_col):
    # same spec as pretreatment_placebo_test.py's placebo_did() -- outcome is
    # already the 2019-2021 change, so no 'post' term, just treated vs control
    d = panel.dropna(subset=[outcome_col]).copy()
    model = smf.ols(f"{outcome_col} ~ treatment + C(district)", data=d).fit(
        cov_type="cluster", cov_kwds={"groups": d["district"]}
    )
    coef, se, p = model.params["treatment"], model.bse["treatment"], model.pvalues["treatment"]
    ci = model.conf_int().loc["treatment"]
    u_stat, mw_p = stats.mannwhitneyu(
        d[d.treatment == 1][outcome_col], d[d.treatment == 0][outcome_col]
    )
    return {
        "n_obs": len(d),
        "n_treated": int((d.treatment == 1).sum()),
        "n_control": int((d.treatment == 0).sum()),
        "placebo_did_coef": float(coef), "placebo_did_se": float(se), "placebo_did_p": float(p),
        "placebo_did_ci_lo": float(ci[0]), "placebo_did_ci_hi": float(ci[1]),
        "mann_whitney_p": float(mw_p),
    }


def main():
    parser = argparse.ArgumentParser(description="Dynamic World parallel-pre-trends placebo test, 2019 vs 2021.")
    parser.add_argument("--window", choices=["full_year", "summer"], required=True)
    args = parser.parse_args()
    window = args.window

    treated = build_group("treated", window)
    control = build_group("control", window)
    panel = pd.concat([treated, control], ignore_index=True)

    print("=" * 78)
    print(f"DYNAMIC WORLD PARALLEL-PRE-TRENDS PLACEBO TEST -- window='{window}'")
    print("2019-to-2021 change in DW 'built' probability, treated vs. control")
    print("(both periods pre-treatment; VVP-I not sanctioned until Feb 2023)")
    print("=" * 78)

    r = placebo_did(panel, "built_placebo_change")
    print(f"\nBUILT: n={r['n_obs']} (treated={r['n_treated']}, control={r['n_control']})")
    print(f"  Placebo DiD coef={r['placebo_did_coef']:+.5f}  SE={r['placebo_did_se']:.5f}  "
          f"95% CI [{r['placebo_did_ci_lo']:+.5f}, {r['placebo_did_ci_hi']:+.5f}]  p={r['placebo_did_p']:.5f}")
    print(f"  Mann-Whitney U (raw distributions) p={r['mann_whitney_p']:.5f}")
    verdict = "PASSES (null, as hoped)" if r["placebo_did_p"] > 0.05 else "FAILS (significant -- pre-trends diverge)"
    print(f"  -> Parallel-pre-trends check: {verdict}")

    with open(SUMMARY_OUT[window], "w") as f:
        json.dump({"built": r}, f, indent=2)
    print(f"\nSaved {SUMMARY_OUT[window]}")


if __name__ == "__main__":
    main()
