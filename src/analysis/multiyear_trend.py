"""
BORDER OPTICS — Per-village linear trend, 2021/2023/2025, core sample.
Also checks the 2021-2023 and 2023-2025 sub-periods separately.

    python src/analysis/multiyear_trend.py --window full_year
    python src/analysis/multiyear_trend.py --window summer
"""

import argparse
import json

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats

DATA_PATHS = {
    "full_year": "data/processed/border_optics_multiyear_fullyear.csv",
    "summer": "data/processed/border_optics_multiyear_summer.csv",
}
SLOPES_OUT = {
    "full_year": "data/processed/border_optics_multiyear_slopes_fullyear.csv",
    "summer": "data/processed/border_optics_multiyear_slopes_summer.csv",
}
SUMMARY_OUT = {
    "full_year": "data/processed/border_optics_multiyear_summary_fullyear.json",
    "summer": "data/processed/border_optics_multiyear_summary_summer.json",
}

YEARS = [2021, 2023, 2025]


def per_village_slope(row, outcome):
    y = np.array(YEARS, dtype=float)
    vals = np.array([row[f"{outcome}_{yr}"] for yr in YEARS], dtype=float)
    if np.isnan(vals).any():
        return None, None
    slope, intercept, r, p, se = stats.linregress(y, vals)
    return slope, r ** 2


def analyze_outcome(df, outcome, window):
    slopes, r2s = [], []
    for _, row in df.iterrows():
        slope, r2 = per_village_slope(row, outcome)
        slopes.append(slope)
        r2s.append(r2)
    df = df.copy()
    df[f"{outcome}_slope"] = slopes
    df[f"{outcome}_trend_r2"] = r2s

    valid = df.dropna(subset=[f"{outcome}_slope"])
    slope_vals = valid[f"{outcome}_slope"]

    w_stat, w_p = stats.wilcoxon(slope_vals, alternative="greater")

    print(f"\n--- {outcome.upper()} multi-year trend, window={window} ---")
    print(f"n = {len(valid)} villages with complete 2021/2023/2025 data")
    print(f"Mean per-village slope = {slope_vals.mean():+.6f} / year "
          f"(median = {slope_vals.median():+.6f}, mean trend R^2 = {valid[f'{outcome}_trend_r2'].mean():.3f})")
    print(f"Wilcoxon signed-rank (slopes vs. 0, alternative='greater'): "
          f"statistic={w_stat:.2f}, p={w_p:.6f}")

    # is the change concentrated in one half of the window, or spread across both?
    d1 = valid[f"{outcome}_2023"] - valid[f"{outcome}_2021"]
    d2 = valid[f"{outcome}_2025"] - valid[f"{outcome}_2023"]
    w1_stat, w1_p = stats.wilcoxon(d1, alternative="greater")
    w2_stat, w2_p = stats.wilcoxon(d2, alternative="greater")
    print(f"  2021->2023 sub-period: mean change={d1.mean():+.6f}, Wilcoxon p={w1_p:.6f}")
    print(f"  2023->2025 sub-period: mean change={d2.mean():+.6f}, Wilcoxon p={w2_p:.6f}")

    # panel regression, village FE, clustered SE by village - second spec for comparison
    long_rows = []
    for _, row in valid.iterrows():
        for yr in YEARS:
            long_rows.append({"village_id": row["village_id"], "year": yr, "value": row[f"{outcome}_{yr}"]})
    long = pd.DataFrame(long_rows)
    long["year_c"] = long["year"] - 2021  # centered, so the intercept is interpretable
    model = smf.ols(f"value ~ year_c + C(village_id)", data=long).fit(
        cov_type="cluster", cov_kwds={"groups": long["village_id"]}
    )
    panel_coef = model.params["year_c"]
    panel_p = model.pvalues["year_c"]
    print(f"  Panel regression (village fixed effects, clustered SE by village): "
          f"year coefficient={panel_coef:+.6f}/year, p={panel_p:.6f}")

    by_state = valid.groupby("state")[f"{outcome}_slope"].agg(["mean", "median", "count"])
    print(f"  By state:\n{by_state.to_string()}")

    return {
        "outcome": outcome, "window": window, "n_villages": len(valid),
        "mean_slope": slope_vals.mean(), "median_slope": slope_vals.median(),
        "mean_trend_r2": valid[f"{outcome}_trend_r2"].mean(),
        "wilcoxon_stat": w_stat, "wilcoxon_p": w_p,
        "subperiod_2021_2023_mean_change": d1.mean(), "subperiod_2021_2023_p": w1_p,
        "subperiod_2023_2025_mean_change": d2.mean(), "subperiod_2023_2025_p": w2_p,
        "panel_fe_year_coef": panel_coef, "panel_fe_year_p": panel_p,
    }, df


def main():
    parser = argparse.ArgumentParser(description="Fit a 2021/2023/2025 trend per village and test its significance.")
    parser.add_argument("--window", choices=["full_year", "summer"], required=True)
    args = parser.parse_args()
    window = args.window

    df = pd.read_csv(DATA_PATHS[window])
    core = df[df["is_core_sample"] == True].copy()

    results = []
    for outcome in ["ndbi", "lights"]:
        result, core = analyze_outcome(core, outcome, window)
        results.append(result)

    core.to_csv(SLOPES_OUT[window], index=False)
    print(f"\nPer-village slopes saved to {SLOPES_OUT[window]}")

    with open(SUMMARY_OUT[window], "w") as f:
        json.dump(results, f, indent=2)
    print(f"Summary saved to {SUMMARY_OUT[window]}")


if __name__ == "__main__":
    main()
