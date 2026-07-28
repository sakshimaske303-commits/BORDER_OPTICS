"""
BORDER OPTICS — H3 test: does proximity to the border/LAC correlate with
measured built-up or night-light change? Tested against both the full-year
and summer-matched composite results, per the robustness-check approach
already used for RQ1.
"""

import pandas as pd
from scipy import stats

distances = pd.read_csv("data/processed/border_optics_master_villages_with_distance.csv")

RESULT_FILES = {
    "full-year": "data/processed/border_optics_village_results_analyzed.csv",
    "summer-matched": "data/processed/border_optics_village_results_summer_analyzed.csv",
}

for label, path in RESULT_FILES.items():
    print("=" * 60)
    print(f"H3 — Border distance vs change ({label} composite)")
    print("=" * 60)

    results = pd.read_csv(path)

    if "village_id" not in results.columns:
        print(f"WARNING: 'village_id' not found in {path} — check its columns and merge key.")
        print("Columns available:", list(results.columns))
        continue

    merged = results.merge(
        distances[["village_id", "distance_to_border_km"]],
        on="village_id",
        how="inner",
    )
    merged = merged[merged["is_core_sample"] == True]

    print(f"Merged {len(merged)} core-sample villages with distance + change data\n")

    for metric in ["ndbi_change", "lights_change"]:
        valid = merged.dropna(subset=[metric, "distance_to_border_km"])
        if len(valid) < 5:
            print(f"{metric}: too few valid rows ({len(valid)}) to test")
            continue
        rho, p = stats.spearmanr(valid["distance_to_border_km"], valid[metric])
        print(f"{metric}: n={len(valid)}, Spearman rho={rho:.3f}, p={p:.4f}  "
              f"(negative rho = closer to border -> more change, supporting H3)")
    print()