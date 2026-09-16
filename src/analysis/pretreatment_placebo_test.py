import argparse
import json

import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats

PRETREATMENT_PATHS = {
    ("treated", "full_year"): "data/processed/border_optics_treated_pretreatment_fullyear.csv",
    ("treated", "summer"): "data/processed/border_optics_treated_pretreatment_summer.csv",
    ("control", "full_year"): "data/processed/border_optics_control_pretreatment_fullyear.csv",
    ("control", "summer"): "data/processed/border_optics_control_pretreatment_summer.csv",
}
EXISTING_2021_PATHS = {
    ("treated", "full_year"): "data/processed/border_optics_village_results_analyzed.csv",
    ("treated", "summer"): "data/processed/border_optics_village_results_summer_analyzed.csv",
    ("control", "full_year"): "data/processed/border_optics_control_results.csv",
    ("control", "summer"): "data/processed/border_optics_control_results_summer.csv",
}
SUMMARY_OUT = {
    "full_year": "outputs/pretreatment_placebo_summary_fullyear.json",
    "summer": "outputs/pretreatment_placebo_summary_summer.json",
}


def build_group(group, window):
    """Returns one row per village: village_id, district, treatment,
    ndbi_2019, ndbi_2021, ndbi_placebo_change (=2021-2019), same for lights."""
    baseline = pd.read_csv(PRETREATMENT_PATHS[(group, window)])[
        ["village_id", "ndbi_2019", "lights_2019"]
    ]
    existing = pd.read_csv(EXISTING_2021_PATHS[(group, window)])
    if group == "treated":
        existing = existing[existing["is_core_sample"] == True]
    existing = existing[["village_id", "district", "ndbi_before", "lights_before"]].rename(
        columns={"ndbi_before": "ndbi_2021", "lights_before": "lights_2021"}
    )
    merged = existing.merge(baseline, on="village_id", how="inner")
    merged["treatment"] = 1 if group == "treated" else 0
    merged["ndbi_placebo_change"] = merged["ndbi_2021"] - merged["ndbi_2019"]
    merged["lights_placebo_change"] = merged["lights_2021"] - merged["lights_2019"]
    return merged


def placebo_did(panel, outcome_col):
    """Same specification as did_model.py's H4: outcome ~ treatment, district
    fixed effects, cluster-robust SE by district. Here 'outcome' is already
    the 2019-to-2021 CHANGE (not a before/after long panel), since both
    periods are pre-treatment there is no 'post' term to speak of -- this is
    a single cross-sectional comparison of one pre-treatment trend between
    two groups, which is what a parallel-pre-trends placebo actually is."""
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
    parser = argparse.ArgumentParser(description="Parallel-pre-trends placebo test, 2019 vs 2021 (Section 7.5).")
    parser.add_argument("--window", choices=["full_year", "summer"], required=True)
    args = parser.parse_args()
    window = args.window

    treated = build_group("treated", window)
    control = build_group("control", window)
    panel = pd.concat([treated, control], ignore_index=True)

    print("=" * 78)
    print(f"PARALLEL-PRE-TRENDS PLACEBO TEST -- window='{window}'")
    print("2019-to-2021 change, treated vs. control (both periods pre-treatment; VVP-I not sanctioned until Feb 2023)")
    print("=" * 78)

    results = {}
    for outcome, col in [("ndbi", "ndbi_placebo_change"), ("lights", "lights_placebo_change")]:
        r = placebo_did(panel, col)
        results[outcome] = r
        print(f"\n{outcome.upper()}: n={r['n_obs']} (treated={r['n_treated']}, control={r['n_control']})")
        print(f"  Placebo DiD coef={r['placebo_did_coef']:+.5f}  SE={r['placebo_did_se']:.5f}  "
              f"95% CI [{r['placebo_did_ci_lo']:+.5f}, {r['placebo_did_ci_hi']:+.5f}]  p={r['placebo_did_p']:.5f}")
        print(f"  Mann-Whitney U (raw distributions) p={r['mann_whitney_p']:.5f}")
        verdict = "PASSES (null, as hoped)" if r["placebo_did_p"] > 0.05 else "FAILS (significant -- pre-trends diverge)"
        print(f"  -> Parallel-pre-trends check: {verdict}")

    with open(SUMMARY_OUT[window], "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved {SUMMARY_OUT[window]}")


if __name__ == "__main__":
    main()
