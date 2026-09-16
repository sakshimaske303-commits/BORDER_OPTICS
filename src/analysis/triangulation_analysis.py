"""
Triangulation checks for H1/H4 using Dynamic World "built" probability and
Sentinel-1 SAR VV/VH backscatter - independent of NDBI's model/sensor.
Runs the same H1 (Wilcoxon, paired) and H4 (district-FE DiD) tests as the
main pipeline, so comparisons are apples-to-apples. Uses statsmodels since
this runs in the same env as did_model.py (unlike extended_robustness_checks.py).

Usage:
    python3 src/analysis/triangulation_analysis.py
"""
import json

import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats

WINDOWS = ["full_year", "summer"]
# these extraction scripts write "fullyear" (no underscore) in filenames
WINDOW_FILE_SUFFIX = {"full_year": "fullyear", "summer": "summer"}

# (source_label, before_col, after_col, treated_path_template, control_path_template)
SOURCES = [
    ("dynamicworld_built", "built_before", "built_after",
     "data/processed/border_optics_treated_dynamicworld_{window}.csv",
     "data/processed/border_optics_control_dynamicworld_{window}.csv"),
    ("sar_vv", "vv_before", "vv_after",
     "data/processed/border_optics_treated_sar_{window}.csv",
     "data/processed/border_optics_control_sar_{window}.csv"),
    ("sar_vh", "vh_before", "vh_after",
     "data/processed/border_optics_treated_sar_{window}.csv",
     "data/processed/border_optics_control_sar_{window}.csv"),
]

OUT_JSON = "outputs/triangulation_results.json"


def h1_test(treated_path, before_col, after_col):
    df = pd.read_csv(treated_path)
    core = df[df["is_core_sample"] == True]
    valid = core.dropna(subset=[before_col, after_col])
    if len(valid) < 5:
        return {"n": len(valid), "note": "too few valid rows to test"}
    stat, p = stats.wilcoxon(valid[after_col], valid[before_col], alternative="greater")
    return {
        "n": len(valid), "mean_before": float(valid[before_col].mean()),
        "mean_after": float(valid[after_col].mean()),
        "mean_change": float((valid[after_col] - valid[before_col]).mean()),
        "wilcoxon_stat": float(stat), "wilcoxon_p": float(p),
    }


def h4_test(treated_path, control_path, before_col, after_col):
    treated = pd.read_csv(treated_path)
    treated = treated[treated["is_core_sample"] == True].copy()
    treated["treatment"] = 1

    control = pd.read_csv(control_path)
    control["treatment"] = 0

    cols = ["village_id", "district", "treatment", before_col, after_col]
    wide = pd.concat([treated[cols], control[cols]], ignore_index=True)
    wide = wide.dropna(subset=[before_col, after_col])

    before = wide.rename(columns={before_col: "outcome"})[["village_id", "district", "treatment", "outcome"]].copy()
    before["post"] = 0
    after = wide.rename(columns={after_col: "outcome"})[["village_id", "district", "treatment", "outcome"]].copy()
    after["post"] = 1
    long = pd.concat([before, after], ignore_index=True)
    long["did_term"] = long["treatment"] * long["post"]

    n_treated = long[long.treatment == 1]["village_id"].nunique()
    n_control = long[long.treatment == 0]["village_id"].nunique()

    model = smf.ols("outcome ~ treatment + post + did_term + C(district)", data=long).fit(
        cov_type="cluster", cov_kwds={"groups": long["district"]}
    )
    coef, se, p = model.params["did_term"], model.bse["did_term"], model.pvalues["did_term"]
    ci = model.conf_int().loc["did_term"]
    return {
        "n_obs": len(long), "n_treated": int(n_treated), "n_control": int(n_control),
        "did_coef": float(coef), "did_se": float(se), "did_p": float(p),
        "did_ci_lo": float(ci[0]), "did_ci_hi": float(ci[1]),
    }


def main():
    results = {}
    for source_label, before_col, after_col, treated_tmpl, control_tmpl in SOURCES:
        for window in WINDOWS:
            file_window = WINDOW_FILE_SUFFIX[window]
            treated_path = treated_tmpl.format(window=file_window)
            control_path = control_tmpl.format(window=file_window)
            key = f"{source_label}_{window}"
            print("=" * 78)
            print(f"{source_label}  ({window})  -- H1 paired treated-only, then H4 control-group DiD")
            print("=" * 78)

            h1 = h1_test(treated_path, before_col, after_col)
            if "note" in h1:
                print(f"  H1: {h1['note']} (n={h1['n']})")
            else:
                print(f"  H1: n={h1['n']}  mean_before={h1['mean_before']:.5f}  "
                      f"mean_after={h1['mean_after']:.5f}  mean_change={h1['mean_change']:+.5f}  "
                      f"Wilcoxon p={h1['wilcoxon_p']:.5f}")

            h4 = h4_test(treated_path, control_path, before_col, after_col)
            print(f"  H4: n_obs={h4['n_obs']} (treated={h4['n_treated']}, control={h4['n_control']})  "
                  f"DiD coef={h4['did_coef']:+.5f}  SE={h4['did_se']:.5f}  "
                  f"95% CI [{h4['did_ci_lo']:+.5f}, {h4['did_ci_hi']:+.5f}]  p={h4['did_p']:.5f}")
            print()

            results[key] = {"h1_treated_only": h1, "h4_control_group_did": h4}

    with open(OUT_JSON, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Saved {OUT_JSON}")


if __name__ == "__main__":
    main()
