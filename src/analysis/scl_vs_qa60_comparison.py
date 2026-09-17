"""Compares the QA60-masked primary summer NDBI result against the
SCL-masked re-extraction from extract_scl_cloud_mask_ndbi.py. Run this after
that extraction script has completed.
"""

import json

import pandas as pd
from scipy import stats

QA60_PATH = "data/processed/border_optics_village_results_summer_analyzed.csv"
# corrected = snow (class 11) dropped -- the old sclmask.csv file (no "_corrected"
# suffix) still exists on disk but was extracted with the buggy class list, don't use it
SCL_PATH = "data/processed/border_optics_village_results_summer_sclmask_corrected.csv"
OUT_JSON = "outputs/scl_vs_qa60_comparison.json"

ALPHA = 0.05


def main():
    qa60 = pd.read_csv(QA60_PATH)
    qa60 = qa60[qa60["is_core_sample"] == True]
    scl = pd.read_csv(SCL_PATH)
    scl["ndbi_scl_change"] = scl["ndbi_scl_after"] - scl["ndbi_scl_before"]

    merged = qa60[["village_id", "ndbi_change"]].merge(
        scl[["village_id", "ndbi_scl_before_image_count", "ndbi_scl_after_image_count", "ndbi_scl_change"]],
        on="village_id", how="inner",
    )

    valid = merged.dropna(subset=["ndbi_change", "ndbi_scl_change"])

    scl_valid = scl.dropna(subset=["ndbi_scl_before", "ndbi_scl_after"])
    w_stat_scl, w_p_scl = stats.wilcoxon(
        scl_valid["ndbi_scl_after"], scl_valid["ndbi_scl_before"], alternative="greater"
    )

    rho, p_corr = stats.spearmanr(valid["ndbi_change"], valid["ndbi_scl_change"])
    n_qa60_valid = qa60["ndbi_change"].notna().sum()
    n_scl_valid = len(scl_valid)

    # compare QA60 on the identical SCL-valid villages, not just QA60's own full sample --
    # keeps mask-choice and sample-composition effects from getting tangled together
    common_ids = set(scl_valid["village_id"])
    qa60_matched = qa60[qa60["village_id"].isin(common_ids)].dropna(subset=["ndbi_change"])
    w_stat_qa60_matched, w_p_qa60_matched = stats.wilcoxon(
        qa60_matched["ndbi_after"], qa60_matched["ndbi_before"], alternative="greater"
    )

    w_stat_qa60_full, w_p_qa60_full = stats.wilcoxon(
        qa60.dropna(subset=["ndbi_before", "ndbi_after"])["ndbi_after"],
        qa60.dropna(subset=["ndbi_before", "ndbi_after"])["ndbi_before"], alternative="greater"
    )

    qa60_sig = w_p_qa60_matched < ALPHA
    scl_sig = w_p_scl < ALPHA
    agree = qa60_sig == scl_sig

    print("=== QA60 mask vs SCL mask, summer-window NDBI, treated core sample ===\n")
    print(f"QA60-masked (primary, full n={n_qa60_valid}): mean_change={qa60['ndbi_change'].mean():+.5f}, "
          f"p={w_p_qa60_full:.6f} ({'significant' if w_p_qa60_full < ALPHA else 'not significant'})")
    print(f"SCL-masked (this check, n={n_scl_valid}): mean_change={scl_valid['ndbi_scl_change'].mean():+.5f}, "
          f"Wilcoxon p={w_p_scl:.6f} ({'significant' if scl_sig else 'not significant'})")
    print(f"\nSame-sample check (QA60 restricted to the identical {len(qa60_matched)} SCL-valid villages): "
          f"mean_change={qa60_matched['ndbi_change'].mean():+.5f}, Wilcoxon p={w_p_qa60_matched:.6f} "
          f"({'significant' if qa60_sig else 'not significant'})")

    if agree:
        print(f"--> Holding the village sample fixed, the two masks AGREE: both "
              f"{'significant' if qa60_sig else 'null'}.")
    else:
        print("--> Holding the village sample fixed, the mask choice ALONE flips the result: "
              f"{'QA60 significant, SCL null' if qa60_sig else 'QA60 null, SCL significant'}.")

    print(f"\nVillage-level agreement between the two masks' NDBI change (n={len(valid)} villages valid at both): "
          f"Spearman rho={rho:+.4f}, p={p_corr:.4g}")

    coverage_diff = n_scl_valid - n_qa60_valid
    print(f"\nCoverage: SCL mask returns valid data for {n_scl_valid}/251 core-sample villages vs "
          f"QA60's {n_qa60_valid}/251 ({'+' if coverage_diff >= 0 else ''}{coverage_diff}). "
          f"If this gap is large, check state composition separately -- don't assume it's the "
          f"same skew an earlier run had; that's exactly the kind of assumption that goes stale.")

    result = {
        "n_qa60_valid": int(n_qa60_valid), "qa60_mean_change": float(qa60["ndbi_change"].mean()),
        "qa60_wilcoxon_p_full": float(w_p_qa60_full),
        "n_scl_valid": int(n_scl_valid), "scl_mean_change": float(scl_valid["ndbi_scl_change"].mean()),
        "scl_wilcoxon_p": float(w_p_scl),
        "qa60_matched_subsample_n": int(len(qa60_matched)),
        "qa60_matched_subsample_mean_change": float(qa60_matched["ndbi_change"].mean()),
        "qa60_matched_subsample_wilcoxon_p": float(w_p_qa60_matched),
        "village_level_agreement_rho": float(rho), "village_level_agreement_p": float(p_corr),
        "n_common_valid": int(len(valid)),
        "masks_agree_on_significance": bool(agree),
        "coverage_diff": int(coverage_diff),
    }
    with open(OUT_JSON, "w") as f:
        json.dump(result, f, indent=2)
    print(f"\nSaved {OUT_JSON}")


if __name__ == "__main__":
    main()
