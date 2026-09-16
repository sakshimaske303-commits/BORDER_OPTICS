"""
Minimum Detectable Effect for H1 and H4, since both came back null and I
want to report "no effect bigger than X is detectable" not just "p>0.05".
H1 uses paired-design MDE (df=n-1), H4 uses the cluster-robust SE from
did_model.py with df = 14 districts - 1 (Cameron & Miller 2015 for thin clusters).

Usage:
    python3 src/analysis/power_analysis.py
"""
import json

import numpy as np
import pandas as pd
from scipy import stats

ALPHA = 0.05          # nominal alpha; sidedness is set per-test below to match the
                      # actual inferential test each MDE is calibrated against
POWER = 0.80
N_DISTRICTS = 14

TREATED_PATHS = {
    "full_year": "data/processed/border_optics_village_results_analyzed.csv",
    "summer": "data/processed/border_optics_village_results_summer_analyzed.csv",
}
DID_SUMMARY_PATHS = {
    "full_year": "data/processed/border_optics_did_summary_fullyear.json",
    "summer": "data/processed/border_optics_did_summary_summer.json",
}
OUT_PATH = "data/processed/border_optics_power_analysis.json"


def mde_multiplier(df, alternative="two-sided"):
    # standard MDE formula, using t-quantiles instead of z since df is thin here.
    # alternative="two-sided" matches H4's cluster-robust DiD test (did_model.py uses
    # statsmodels' default two-sided p-values). alternative="one-sided" matches H1's
    # actual test (analyze_results.py / did_model.py call stats.wilcoxon(...,
    # alternative="greater")) -- using two-sided alpha there would understate power
    # relative to the test actually run.
    t_alpha = stats.t.ppf(1 - ALPHA / 2, df) if alternative == "two-sided" else stats.t.ppf(1 - ALPHA, df)
    t_power = stats.t.ppf(POWER, df)
    return t_alpha + t_power


def h1_mde(window):
    """Primary estimand: paired treated-only before/after MDE, core sample.
    One-sided, matching the actual H1 test (alternative='greater')."""
    df = pd.read_csv(TREATED_PATHS[window])
    core = df[df["is_core_sample"] == True]
    baseline_lights = core["lights_before"].mean()
    rows = []
    for outcome in ["ndbi_change", "lights_change"]:
        s = core[outcome].dropna()
        n = len(s)
        sd = s.std()
        dof = n - 1
        mult = mde_multiplier(dof, alternative="one-sided")
        mde = mult * sd / np.sqrt(n)
        row = {
            "test": "H1_treated_only", "window": window,
            "outcome": outcome.replace("_change", ""),
            "n": n, "sd_of_change": sd, "df": dof,
            "mde": mde, "mde_as_cohens_d": mde / sd,
        }
        if outcome == "lights_change":
            row["mde_pct_of_baseline"] = 100 * mde / baseline_lights
        rows.append(row)
    return rows


def h4_mde(window):
    """Control-group DiD MDE, from the already-fitted cluster-robust SE.
    Two-sided, matching the actual H4 test (did_model.py's cluster-robust OLS p-values
    and the two-sided Mann-Whitney check)."""
    with open(DID_SUMMARY_PATHS[window]) as f:
        summ = json.load(f)
    dof = N_DISTRICTS - 1
    mult = mde_multiplier(dof, alternative="two-sided")
    rows = []
    for r in summ["did"]:
        se = r["did_se"]
        mde = mult * se
        rows.append({
            "test": "H4_control_group_DiD", "window": window,
            "outcome": r["outcome"],
            "n_obs": r["n_obs"], "se": se, "df": dof,
            "mde": mde, "observed_coef": r["did_coef"], "observed_p": r["did_p"],
            "observed_as_fraction_of_mde": abs(r["did_coef"]) / mde,
        })
    return rows


def main():
    all_rows = []
    for window in ["full_year", "summer"]:
        all_rows.extend(h1_mde(window))
        all_rows.extend(h4_mde(window))

    print(f"\nMinimum Detectable Effect -- alpha={ALPHA}, power={POWER}")
    print("(H1 one-sided, matching alternative='greater'; H4 two-sided, matching the cluster-robust DiD test)\n")
    for r in all_rows:
        if r["test"] == "H1_treated_only":
            extra = f"  ({r['mde_pct_of_baseline']:.1f}% of baseline)" if "mde_pct_of_baseline" in r else ""
            print(f"[H1 {r['window']:>9s} {r['outcome']:7s}] n={r['n']:3d}  "
                  f"MDE = {r['mde']:.5f}  (Cohen's d = {r['mde_as_cohens_d']:.3f}){extra}")
        else:
            print(f"[H4 {r['window']:>9s} {r['outcome']:7s}]        "
                  f"MDE = {r['mde']:.5f}  observed coef = {r['observed_coef']:+.5f}  "
                  f"(observed effect is {r['observed_as_fraction_of_mde']*100:.0f}% of the detectable threshold)")

    with open(OUT_PATH, "w") as f:
        json.dump(all_rows, f, indent=2)
    print(f"\nSaved {OUT_PATH}")


if __name__ == "__main__":
    main()
