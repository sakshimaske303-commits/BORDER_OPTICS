"""Section 4.10 follow-through: Section 4.10 leaves the SAR/Dynamic World
disagreement as two competing, unresolved speculative explanations (an
atmospheric-correction/imagery-tier difference between Dynamic World's L1C
pull and NDBI's SR-Harmonized pull, versus a deep-learning classifier simply
being more sensitive to a small real change than a two-band index or SAR's
coarser effective resolution). This does not resolve that question -- doing
so properly would need a same-tier Dynamic World re-extraction, which needs
live Earth Engine access this sandbox does not have -- but it adds one piece
of evidence current data can actually answer: at the individual-village
level, does Dynamic World's "built" change at least point the same direction
as SAR and NDBI's own changes, or is the aggregate DiD disagreement also a
village-level disagreement?
"""

import json

import pandas as pd
from scipy import stats

DW_PATHS = {
    "full_year": "data/processed/border_optics_treated_dynamicworld_fullyear.csv",
    "summer": "data/processed/border_optics_treated_dynamicworld_summer.csv",
}
SAR_PATHS = {
    "full_year": "data/processed/border_optics_treated_sar_fullyear.csv",
    "summer": "data/processed/border_optics_treated_sar_summer.csv",
}
NDBI_PATHS = {
    "full_year": "data/processed/border_optics_village_results_analyzed.csv",
    "summer": "data/processed/border_optics_village_results_summer_analyzed.csv",
}
OUT_JSON = "outputs/dw_sar_ndbi_village_level_results.json"


def load_window(window):
    dw = pd.read_csv(DW_PATHS[window])
    dw["built_change"] = dw["built_after"] - dw["built_before"]
    sar = pd.read_csv(SAR_PATHS[window])
    sar["vv_change"] = sar["vv_after"] - sar["vv_before"]
    sar["vh_change"] = sar["vh_after"] - sar["vh_before"]
    ndbi = pd.read_csv(NDBI_PATHS[window])

    merged = dw[["village_id", "state", "district", "is_core_sample", "built_change"]].merge(
        sar[["village_id", "vv_change", "vh_change"]], on="village_id", how="inner"
    ).merge(
        ndbi[["village_id", "ndbi_change"]], on="village_id", how="inner"
    )
    return merged[merged["is_core_sample"] == True]


def main():
    all_results = {}
    for window in ["full_year", "summer"]:
        df = load_window(window)
        print("=" * 78)
        print(f"Village-level cross-checks, {window} window (n up to {len(df)} core-sample villages)")
        print("=" * 78)

        window_results = {"n_total_core": len(df)}
        pairs = [
            ("built_change", "vv_change", "Dynamic World built-change vs SAR VV-change"),
            ("built_change", "vh_change", "Dynamic World built-change vs SAR VH-change"),
            ("built_change", "ndbi_change", "Dynamic World built-change vs NDBI-change"),
            ("vv_change", "ndbi_change", "SAR VV-change vs NDBI-change"),
        ]
        for a, b, desc in pairs:
            valid = df.dropna(subset=[a, b])
            if len(valid) < 3:
                continue
            rho, p = stats.spearmanr(valid[a], valid[b])
            same_sign_pct = (valid[a] * valid[b] > 0).mean() * 100
            print(f"  {desc}: n={len(valid)}  rho={rho:+.4f}  p={p:.4g}  "
                  f"same-sign at {same_sign_pct:.1f}% of villages")
            window_results[f"{a}_vs_{b}"] = {
                "n": len(valid), "rho": float(rho), "p": float(p), "same_sign_pct": float(same_sign_pct),
            }

        print("\n  Dynamic World built-change by state (mean, n):")
        state_summary = df.dropna(subset=["built_change"]).groupby("state")["built_change"].agg(["mean", "count"])
        print(state_summary.to_string())
        window_results["built_change_by_state"] = state_summary.reset_index().to_dict(orient="records")

        all_results[window] = window_results
        print()

    with open(OUT_JSON, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"Saved {OUT_JSON}")


if __name__ == "__main__":
    main()
