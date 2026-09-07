"""
Paper-wise Holm-Bonferroni correction across the study's eight headline
p-values (4 core tests x 2 compositing windows), referenced in Research
Paper Section 4.9. This script didn't exist before — the paper cited
Holm-adjusted numbers without a reproducible script behind them, and
those cited numbers turned out to be the raw p-values relabeled, not
actually Holm-adjusted. This recomputes it properly from the same
result files the rest of the pipeline already produces.

Run from the repo root: python src/analysis/holm_correction.py
"""

import pandas as pd
from scipy import stats
from statsmodels.stats.multitest import multipletests

RESULT_FILES = {
    "full-year": "data/processed/border_optics_village_results_analyzed.csv",
    "summer-matched": "data/processed/border_optics_village_results_summer_analyzed.csv",
}
DISTANCES_PATH = "data/processed/border_optics_master_villages_with_distance.csv"


def wilcoxon_ndbi_lights(path):
    df = pd.read_csv(path)
    df["ndbi_change"] = df["ndbi_after"] - df["ndbi_before"]
    df["lights_change"] = df["lights_after"] - df["lights_before"]
    core = df[df["is_core_sample"] == True].copy()

    valid_ndbi = core.dropna(subset=["ndbi_before", "ndbi_after"])
    _, p_ndbi = stats.wilcoxon(valid_ndbi["ndbi_after"], valid_ndbi["ndbi_before"], alternative="greater")

    valid_lights = core.dropna(subset=["lights_before", "lights_after"])
    _, p_lights = stats.wilcoxon(valid_lights["lights_after"], valid_lights["lights_before"], alternative="greater")

    return p_ndbi, p_lights


def h3_border_proximity(path, distances):
    results = pd.read_csv(path)
    results["ndbi_change"] = results["ndbi_after"] - results["ndbi_before"]
    results["lights_change"] = results["lights_after"] - results["lights_before"]
    merged = results.merge(distances[["village_id", "distance_to_border_km"]], on="village_id", how="inner")
    merged = merged[merged["is_core_sample"] == True]

    out = {}
    for metric in ["ndbi_change", "lights_change"]:
        valid = merged.dropna(subset=[metric, "distance_to_border_km"])
        _, p = stats.spearmanr(valid["distance_to_border_km"], valid[metric])
        out[metric] = p
    return out


def main():
    distances = pd.read_csv(DISTANCES_PATH)

    tests = {}
    for window, path in RESULT_FILES.items():
        p_ndbi, p_lights = wilcoxon_ndbi_lights(path)
        tests[f"H1_ndbi_change_{window}"] = p_ndbi
        tests[f"H3_lights_change_{window}"] = p_lights

        h3 = h3_border_proximity(path, distances)
        tests[f"H3_border_proximity_ndbi_{window}"] = h3["ndbi_change"]
        tests[f"H3_border_proximity_lights_{window}"] = h3["lights_change"]

    names = list(tests.keys())
    raw_p = [tests[n] for n in names]
    reject, adj_p, _, _ = multipletests(raw_p, alpha=0.05, method="holm")

    print(f"{'test':32s} {'raw p':>14s} {'holm-adjusted p':>18s}  {'significant?'}")
    print("-" * 82)
    results_out = []
    for name, raw, adj, rej in zip(names, raw_p, adj_p, reject):
        print(f"{name:32s} {raw:14.6e} {adj:18.6e}  {'YES' if rej else 'no'}")
        results_out.append({"test": name, "raw_p": raw, "holm_adjusted_p": adj, "significant_after_holm": bool(rej)})

    out_df = pd.DataFrame(results_out)
    out_path = "outputs/holm_correction_results.csv"
    out_df.to_csv(out_path, index=False)
    print(f"\nSaved: {out_path}")


if __name__ == "__main__":
    main()
