"""
BORDER OPTICS — Buffer-radius comparison, 250m / 500m / 1km, summer window.
Also re-runs on the matched subsample valid at all three radii (see note
in matched_subsample_test() below — the 250m/1km runs picked up extra
archive coverage the 500m run didn't have, so a raw comparison isn't fair).

    python src/analysis/buffer_sensitivity.py
"""

import json

import pandas as pd
from scipy import stats

BUFFERS = {
    250: "data/processed/border_optics_buffer250_summer.csv",
    500: "data/processed/border_optics_village_results_summer_analyzed.csv",
    1000: "data/processed/border_optics_buffer1000_summer.csv",
}
SUMMARY_OUT = "data/processed/border_optics_buffer_sensitivity_summary.json"


def test_buffer(buffer_m, path):
    df = pd.read_csv(path)
    core = df[df["is_core_sample"] == True].copy()

    results = {"buffer_m": buffer_m, "n_core": len(core)}
    for outcome in ["ndbi", "lights"]:
        valid = core.dropna(subset=[f"{outcome}_before", f"{outcome}_after"])
        w_stat, w_p = stats.wilcoxon(
            valid[f"{outcome}_after"], valid[f"{outcome}_before"], alternative="greater"
        )
        change = valid[f"{outcome}_after"] - valid[f"{outcome}_before"]
        results[f"{outcome}_n_valid"] = len(valid)
        results[f"{outcome}_mean_change"] = change.mean()
        results[f"{outcome}_median_change"] = change.median()
        results[f"{outcome}_wilcoxon_stat"] = w_stat
        results[f"{outcome}_wilcoxon_p"] = w_p

    return results


def matched_subsample_test(common_ids, outcome="ndbi"):
    # 250m/1km ran later than 500m, and the Sentinel-2 archive kept
    # backfilling in between -> more usable imagery, not a buffer effect.
    # Restrict to villages valid at all three radii so the comparison is fair.
    print(f"\n=== Matched-subsample check ({outcome.upper()}, n={len(common_ids)} villages "
          f"valid at all three buffer radii) ===")
    results = []
    for buffer_m, path in BUFFERS.items():
        df = pd.read_csv(path)
        sub = df[df["village_id"].isin(common_ids)].dropna(subset=[f"{outcome}_before", f"{outcome}_after"])
        change = sub[f"{outcome}_after"] - sub[f"{outcome}_before"]
        w_stat, w_p = stats.wilcoxon(sub[f"{outcome}_after"], sub[f"{outcome}_before"], alternative="greater")
        print(f"  {buffer_m:>5d}m  n={len(sub):3d}  mean change={change.mean():+.5f}  Wilcoxon p={w_p:.6f}")
        results.append({
            "buffer_m": buffer_m, "outcome": outcome, "n": len(sub),
            "mean_change": change.mean(), "wilcoxon_p": w_p,
        })
    return results


def main():
    all_results = []
    print("=== Buffer-radius sensitivity, summer window, core sample (n=251, as extracted) ===\n")
    for buffer_m, path in BUFFERS.items():
        r = test_buffer(buffer_m, path)
        all_results.append(r)
        print(f"--- {buffer_m}m buffer ---")
        print(f"  n core-sample villages = {r['n_core']}")
        print(f"  NDBI:   n_valid={r['ndbi_n_valid']:3d}  mean change={r['ndbi_mean_change']:+.5f}  "
              f"median={r['ndbi_median_change']:+.5f}  Wilcoxon p={r['ndbi_wilcoxon_p']:.6f}")
        print(f"  Lights: n_valid={r['lights_n_valid']:3d}  mean change={r['lights_mean_change']:+.5f}  "
              f"median={r['lights_median_change']:+.5f}  Wilcoxon p={r['lights_wilcoxon_p']:.6f}")
        print()

    print("=== Summary across buffer sizes, as extracted ===")
    print(f"{'buffer':>8s}  {'NDBI p':>12s}  {'NDBI mean chg':>14s}  {'Lights p':>12s}  {'Lights mean chg':>16s}")
    for r in all_results:
        print(f"{r['buffer_m']:>7d}m  {r['ndbi_wilcoxon_p']:>12.6f}  {r['ndbi_mean_change']:>+14.5f}  "
              f"{r['lights_wilcoxon_p']:>12.6f}  {r['lights_mean_change']:>+16.5f}")

    # find villages valid at every radius vs. only some, re-run on the common set
    dfs = {b: pd.read_csv(p) for b, p in BUFFERS.items()}
    valid_sets = {}
    for b, df in dfs.items():
        core = df[df["is_core_sample"] == True]
        valid_sets[b] = set(core.dropna(subset=["ndbi_before", "ndbi_after"])["village_id"])
    common_ids = valid_sets[250] & valid_sets[500] & valid_sets[1000]
    coverage_note = {
        "n_valid_250m": len(valid_sets[250]), "n_valid_500m": len(valid_sets[500]),
        "n_valid_1000m": len(valid_sets[1000]), "n_common_all_three": len(common_ids),
    }
    print(f"\nCoverage as extracted: 250m={coverage_note['n_valid_250m']}, "
          f"500m={coverage_note['n_valid_500m']}, 1000m={coverage_note['n_valid_1000m']} "
          f"-> {coverage_note['n_common_all_three']} villages valid at all three")

    matched_results = matched_subsample_test(common_ids, "ndbi")

    all_significant_ndbi_raw = all(r["ndbi_wilcoxon_p"] < 0.05 for r in all_results)
    all_significant_ndbi_matched = all(r["wilcoxon_p"] < 0.05 for r in matched_results)
    print(f"\nNDBI significant (p<0.05) at all three buffers, as-extracted samples: {all_significant_ndbi_raw}")
    print(f"NDBI significant (p<0.05) at all three buffers, matched common sample: {all_significant_ndbi_matched}")

    with open(SUMMARY_OUT, "w") as f:
        json.dump({
            "as_extracted": all_results,
            "coverage_note": coverage_note,
            "matched_subsample": matched_results,
        }, f, indent=2)
    print(f"\nSummary saved to {SUMMARY_OUT}")


if __name__ == "__main__":
    main()
