import json

import numpy as np
import pandas as pd
from scipy import stats

ALPHA = 0.05          # two-sided
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


def mde_multiplier(df):
    """(t-crit for alpha/2) + (t-crit for power), at the given degrees of
    freedom -- the standard textbook MDE formula (e.g. Duflo, Glennerster &
    Kremer 2007, "Using Randomization in Development Economics Research"),
    with the usual normal-quantile shortcut replaced by t-quantiles at this
    study's own (thin) df rather than assumed-large-sample z values."""
    t_alpha = stats.t.ppf(1 - ALPHA / 2, df)
    t_power = stats.t.ppf(POWER, df)
    return t_alpha + t_power


def h1_mde(window):
    """Primary estimand: paired treated-only before/after MDE, core sample."""
    df = pd.read_csv(TREATED_PATHS[window])
    core = df[df["is_core_sample"] == True]
    baseline_lights = core["lights_before"].mean()
    rows = []
    for outcome in ["ndbi_change", "lights_change"]:
        s = core[outcome].dropna()
        n = len(s)
        sd = s.std()
        dof = n - 1
        mult = mde_multiplier(dof)
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
    """Control-group DiD MDE, from the already-fitted cluster-robust SE."""
    with open(DID_SUMMARY_PATHS[window]) as f:
        summ = json.load(f)
    dof = N_DISTRICTS - 1
    mult = mde_multiplier(dof)
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

    print(f"\nMinimum Detectable Effect -- alpha={ALPHA} (two-sided), power={POWER}\n")
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
