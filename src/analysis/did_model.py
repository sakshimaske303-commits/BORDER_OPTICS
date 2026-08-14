"""
BORDER OPTICS — DiD: 251-village treated core sample vs. 753-village matched control.
District fixed effects, SE clustered by district.

    python src/analysis/did_model.py --window full_year
    python src/analysis/did_model.py --window summer
"""

import argparse
import json

import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats

TREATED_PATHS = {
    "full_year": "data/processed/border_optics_village_results_analyzed.csv",
    "summer": "data/processed/border_optics_village_results_summer_analyzed.csv",
}
CONTROL_PATHS = {
    "full_year": "data/processed/border_optics_control_results.csv",
    "summer": "data/processed/border_optics_control_results_summer.csv",
}
PANEL_OUT = {
    "full_year": "data/processed/border_optics_did_panel_fullyear.csv",
    "summer": "data/processed/border_optics_did_panel_summer.csv",
}
SUMMARY_OUT = {
    "full_year": "data/processed/border_optics_did_summary_fullyear.json",
    "summer": "data/processed/border_optics_did_summary_summer.json",
}
DISTRICT_OUT = {
    "full_year": "data/processed/border_optics_did_by_district_fullyear.csv",
    "summer": "data/processed/border_optics_did_by_district_summer.csv",
}


def build_panel(window):
    treated = pd.read_csv(TREATED_PATHS[window])
    # core sample only - matches control group's scope (Himachal has no control match)
    treated = treated[treated["is_core_sample"] == True].copy()
    treated["treatment"] = 1

    control = pd.read_csv(CONTROL_PATHS[window])
    control["treatment"] = 0

    cols = ["village_id", "village", "district", "state", "treatment",
            "ndbi_before", "ndbi_after", "lights_before", "lights_after"]
    wide = pd.concat([treated[cols], control[cols]], ignore_index=True)

    before = wide.rename(columns={"ndbi_before": "ndbi", "lights_before": "lights"})[
        ["village_id", "district", "state", "treatment", "ndbi", "lights"]
    ].copy()
    before["post"] = 0
    after = wide.rename(columns={"ndbi_after": "ndbi", "lights_after": "lights"})[
        ["village_id", "district", "state", "treatment", "ndbi", "lights"]
    ].copy()
    after["post"] = 1

    long = pd.concat([before, after], ignore_index=True)
    long["did_term"] = long["treatment"] * long["post"]
    return long


def run_did(long, outcome, window):
    valid = long.dropna(subset=[outcome]).copy()

    formula_fe = f"{outcome} ~ treatment + post + did_term + C(district)"
    formula_nofe = f"{outcome} ~ treatment + post + did_term"

    # primary: district FE, clustered SE by district (14 clusters - thin, usual caveat)
    model_fe = smf.ols(formula_fe, data=valid).fit(
        cov_type="cluster", cov_kwds={"groups": valid["district"]}
    )
    # comparison: no FE, HC3 robust SE
    model_nofe = smf.ols(formula_nofe, data=valid).fit(cov_type="HC3")

    n_treated = valid[valid.treatment == 1]["village_id"].nunique()
    n_control = valid[valid.treatment == 0]["village_id"].nunique()

    coef, se, p = (model_fe.params["did_term"], model_fe.bse["did_term"], model_fe.pvalues["did_term"])
    ci = model_fe.conf_int().loc["did_term"]
    coef2, p2 = model_nofe.params["did_term"], model_nofe.pvalues["did_term"]

    print(f"\n--- {outcome.upper()} DiD, window={window} ---")
    print(f"n = {len(valid)} village-period observations "
          f"({n_treated} treated villages / {n_control} control villages)")
    print("[Primary: district fixed effects, cluster-robust SE by district, 14 clusters]")
    print(f"  did_term = {coef:+.5f}  SE={se:.5f}  95% CI [{ci[0]:+.5f}, {ci[1]:+.5f}]  p={p:.5f}")
    print("[Comparison: no fixed effects, HC3 heteroskedasticity-robust SE]")
    print(f"  did_term = {coef2:+.5f}  p={p2:.5f}")

    return {
        "outcome": outcome, "window": window,
        "n_obs": len(valid), "n_treated": int(n_treated), "n_control": int(n_control),
        "did_coef": coef, "did_se": se, "did_p": p,
        "did_ci_lo": ci[0], "did_ci_hi": ci[1],
        "did_coef_nofe_hc3": coef2, "did_p_nofe_hc3": p2,
    }


def baseline_balance(long, outcome, window):
    # 2021 baseline level check - stand-in for a pre-trends placebo test, which
    # needs a multi-period pre-treatment panel the control group doesn't have
    pre = long[long["post"] == 0].dropna(subset=[outcome])
    t = pre[pre.treatment == 1][outcome]
    c = pre[pre.treatment == 0][outcome]
    u_stat, p = stats.mannwhitneyu(t, c, alternative="two-sided")
    print(f"\n--- Baseline (2021) balance check, {outcome}, window={window} ---")
    print(f"  treated mean={t.mean():.5f} (n={len(t)})   control mean={c.mean():.5f} (n={len(c)})")
    print(f"  Mann-Whitney U={u_stat:.1f}, p={p:.5f}")
    return {
        "outcome": outcome, "window": window,
        "baseline_treated_mean": t.mean(), "baseline_control_mean": c.mean(),
        "baseline_n_treated": len(t), "baseline_n_control": len(c),
        "baseline_balance_p": p,
    }


def per_district_summary(long, outcome, window):
    print(f"\n--- Per-district treated-vs-control mean change, {outcome}, window={window} ---")
    rows = []
    for district, grp in long.groupby("district"):
        t_wide = grp[grp.treatment == 1].pivot_table(index="village_id", columns="post", values=outcome)
        c_wide = grp[grp.treatment == 0].pivot_table(index="village_id", columns="post", values=outcome)
        if 0 not in t_wide.columns or 1 not in t_wide.columns or 0 not in c_wide.columns or 1 not in c_wide.columns:
            continue
        t_valid = t_wide.dropna()
        c_valid = c_wide.dropna()
        if t_valid.empty or c_valid.empty:
            continue
        t_change = (t_valid[1] - t_valid[0]).mean()
        c_change = (c_valid[1] - c_valid[0]).mean()
        print(f"  {district:16s} treated n={len(t_valid):3d} Δ={t_change:+.5f}   "
              f"control n={len(c_valid):3d} Δ={c_change:+.5f}   gap={t_change - c_change:+.5f}")
        rows.append({
            "district": district, "outcome": outcome, "window": window,
            "n_treated": len(t_valid), "n_control": len(c_valid),
            "treated_change": t_change, "control_change": c_change,
            "gap": t_change - c_change,
        })
    return rows


def main():
    parser = argparse.ArgumentParser(description="Village-level DiD: VVP-I treated vs. matched non-VVP control.")
    parser.add_argument("--window", choices=["full_year", "summer"], required=True)
    args = parser.parse_args()
    window = args.window

    long = build_panel(window)
    long.to_csv(PANEL_OUT[window], index=False)
    print(f"Panel saved to {PANEL_OUT[window]} ({len(long)} rows)")

    did_results, balance_results, district_rows = [], [], []
    for outcome in ["ndbi", "lights"]:
        did_results.append(run_did(long, outcome, window))
        balance_results.append(baseline_balance(long, outcome, window))
        district_rows.extend(per_district_summary(long, outcome, window))

    summary = {"did": did_results, "baseline_balance": balance_results}
    with open(SUMMARY_OUT[window], "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nSummary saved to {SUMMARY_OUT[window]}")

    pd.DataFrame(district_rows).to_csv(DISTRICT_OUT[window], index=False)
    print(f"Per-district breakdown saved to {DISTRICT_OUT[window]}")


if __name__ == "__main__":
    main()
