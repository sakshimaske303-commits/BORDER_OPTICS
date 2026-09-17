"""
Core stats for RQ1 (built-up change) and RQ2 (state budget correlation),
run against whichever compositing window is selected.

Consolidated on 2026-09-17 from two near-duplicate scripts (analyze_results.py
and analyze_results_fullyear.py) that differed only in which window's paths
they read/wrote and their print labels -- the same class of window-consistency
bug this project's Development Log has caught before, now handled the same
way did_model.py already handles it: one script, a --window flag, and a path
dictionary per window instead of copy-pasted logic. See archive/README.md.

run:
    python src/analysis/analyze_results.py --window summer
    python src/analysis/analyze_results.py --window full_year
"""

import argparse

import pandas as pd
from scipy import stats

INPUT_PATHS = {
    "summer": "data/processed/border_optics_village_results_summer.csv",
    "full_year": "data/processed/border_optics_village_results.csv",
}
OUTPUT_PATHS = {
    "summer": "data/processed/border_optics_village_results_summer_analyzed.csv",
    "full_year": "data/processed/border_optics_village_results_analyzed.csv",
}
WINDOW_LABELS = {
    "summer": "SUMMER-MATCHED COMPOSITE WINDOW",
    "full_year": "FULL-YEAR COMPOSITE WINDOW",
}

BUDGET_DATA = {
    "Arunachal Pradesh": {"projects": 2082, "budget_cr": 2749.74},
    "Uttarakhand":        {"projects": 200,  "budget_cr": 270.58},
    "Sikkim":             {"projects": 63,   "budget_cr": 188.90},
}


def main(window):
    input_path = INPUT_PATHS[window]
    output_path = OUTPUT_PATHS[window]

    df = pd.read_csv(input_path)

    # --- Derived change metrics ---
    df["ndbi_change"] = df["ndbi_after"] - df["ndbi_before"]
    df["lights_change"] = df["lights_after"] - df["lights_before"]

    core = df[df["is_core_sample"] == True].copy()

    print("=" * 60)
    print("DESCRIPTIVE STATS — Core sample (Arunachal, Sikkim, Uttarakhand)")
    print(WINDOW_LABELS[window])
    print("=" * 60)
    print(f"n = {len(core)} villages\n")

    print("NDBI change (built-up index, after - before):")
    print(core["ndbi_change"].describe())
    print()
    print("VIIRS night-light change (radiance, after - before):")
    print(core["lights_change"].describe())
    print()

    print("By state:")
    print(core.groupby("state")[["ndbi_change", "lights_change"]].agg(["mean", "median", "std"]))
    print()

    # --- RQ1 / H1: is the built-up change significantly positive? ---
    print("=" * 60)
    print("RQ1 / H1 — Wilcoxon signed-rank test on NDBI change (paired, before vs after)")
    print("=" * 60)

    valid_ndbi = core.dropna(subset=["ndbi_before", "ndbi_after"])
    print(f"NDBI test run on {len(valid_ndbi)}/{len(core)} villages with valid data "
          f"(rest excluded — no cloud-free imagery in the {window.replace('_', '-')} window)")
    w_stat, w_p = stats.wilcoxon(valid_ndbi["ndbi_after"], valid_ndbi["ndbi_before"], alternative="greater")
    print(f"Wilcoxon statistic = {w_stat:.2f}, p = {w_p:.6f}")
    print("(alternative='greater' tests whether 'after' is significantly higher than 'before')")
    print()

    valid_lights = core.dropna(subset=["lights_before", "lights_after"])
    print(f"Lights test run on {len(valid_lights)}/{len(core)} villages with valid data")
    w_stat_l, w_p_l = stats.wilcoxon(valid_lights["lights_after"], valid_lights["lights_before"], alternative="greater")
    print(f"Same test on VIIRS night-lights: statistic = {w_stat_l:.2f}, p = {w_p_l:.6f}")
    print()

    # --- RQ2: state-level change vs sanctioned budget (EXPLORATORY — n<=3 only) ---
    print("=" * 60)
    print("RQ2 — State-level mean NDBI change vs sanctioned VVP-I budget")
    print("EXPLORATORY ONLY — n=3 states at most, not a statistically powered test")
    print("=" * 60)

    state_summary = valid_ndbi.groupby("state")[["ndbi_change", "lights_change"]].mean().reset_index()
    state_summary["projects"] = state_summary["state"].map(lambda s: BUDGET_DATA[s]["projects"])
    state_summary["budget_cr"] = state_summary["state"].map(lambda s: BUDGET_DATA[s]["budget_cr"])
    state_summary["n_villages_with_ndbi"] = state_summary["state"].map(valid_ndbi["state"].value_counts())

    print(state_summary.to_string(index=False))
    print()

    if len(state_summary) >= 3:
        rho, p_val = stats.spearmanr(state_summary["budget_cr"], state_summary["ndbi_change"])
        print(f"Spearman correlation (budget vs mean NDBI change): rho = {rho:.3f}, p = {p_val:.3f}")
        print("NOTE: with only 3 states (or fewer, if data was missing for one), this p-value")
        print("is not meaningful on its own — report the direction/pattern descriptively.")
    else:
        print(f"Only {len(state_summary)} state(s) have valid NDBI data — correlation not computable.")

    # --- Save enriched dataset ---
    # lineterminator="\r\n" matches every other CSV in data/processed/ (all
    # written CRLF originally) -- without it, pandas' Linux default (LF-only)
    # would rewrite this one file's line endings and produce a spurious
    # whole-file diff with no actual content change.
    df.to_csv(output_path, index=False, lineterminator="\r\n")
    print(f"\nSaved enriched dataset to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Core RQ1/RQ2 stats for BORDER OPTICS, run against a single compositing window."
    )
    parser.add_argument("--window", choices=["full_year", "summer"], required=True)
    args = parser.parse_args()
    main(args.window)
