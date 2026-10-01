"""
Buffer-overlap sensitivity for the H4 DiD (added 2026-09-30, Development Log Entry 48).

select_control_villages.py drops control candidates within 50m of a treated
village, but every extraction uses a 500m buffer -- so a control village less
than 1km from a treated village shares pixels with that treated village's
buffer. 82 of the 721 controls are in that situation (5 of them within 200m).
Shared pixels push treated and control values toward each other, which would
bias the DiD toward zero.

This re-runs the primary district-FE, cluster-robust DiD (same spec as
did_model.py) after dropping every control village within 1km of any treated
village, for both outcomes and both windows.

run from repo root:
    python src/analysis/buffer_overlap_sensitivity.py
"""

import json

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

MASTER = "data/processed/border_optics_master_villages_with_distance.csv"
CONTROL = "data/processed/border_optics_control_villages.csv"
PANELS = {
    "full_year": "data/processed/border_optics_did_panel_fullyear.csv",
    "summer": "data/processed/border_optics_did_panel_summer.csv",
}
OVERLAP_THRESHOLD_M = 1000  # two 500m buffers overlap below this centre-to-centre distance
OUT_JSON = "outputs/buffer_overlap_sensitivity_results.json"


def nearest_treated_m(control, treated):
    r = 6371008.8
    la1 = np.radians(control["latitude"].values)[:, None]
    lo1 = np.radians(control["longitude"].values)[:, None]
    la2 = np.radians(treated["latitude"].values)[None, :]
    lo2 = np.radians(treated["longitude"].values)[None, :]
    a = np.sin((la2 - la1) / 2) ** 2 + np.cos(la1) * np.cos(la2) * np.sin((lo2 - lo1) / 2) ** 2
    return (2 * r * np.arcsin(np.sqrt(a))).min(axis=1)


def main():
    treated = pd.read_csv(MASTER)
    control = pd.read_csv(CONTROL)
    control["nearest_treated_m"] = nearest_treated_m(control, treated)
    overlapping = set(control.loc[control["nearest_treated_m"] < OVERLAP_THRESHOLD_M, "village_id"])
    print(f"{len(overlapping)} of {len(control)} control villages sit < {OVERLAP_THRESHOLD_M} m from a "
          f"treated village (buffer overlap); {(control['nearest_treated_m'] < 200).sum()} are < 200 m.")

    results = {
        "n_control_total": int(len(control)),
        "n_control_overlapping": int(len(overlapping)),
        "n_control_within_200m": int((control["nearest_treated_m"] < 200).sum()),
        "threshold_m": OVERLAP_THRESHOLD_M,
        "did_excluding_overlap": [],
    }
    for window, path in PANELS.items():
        panel = pd.read_csv(path)
        panel = panel[~((panel["treatment"] == 0) & (panel["village_id"].isin(overlapping)))]
        for outcome in ["ndbi", "lights"]:
            v = panel.dropna(subset=[outcome])
            m = smf.ols(f"{outcome} ~ treatment + post + did_term + C(district)", data=v).fit(
                cov_type="cluster", cov_kwds={"groups": v["district"]}
            )
            row = {
                "window": window, "outcome": outcome,
                "n_treated": int(v.loc[v.treatment == 1, "village_id"].nunique()),
                "n_control": int(v.loc[v.treatment == 0, "village_id"].nunique()),
                "did_coef": float(m.params["did_term"]),
                "did_se": float(m.bse["did_term"]),
                "did_p": float(m.pvalues["did_term"]),
            }
            results["did_excluding_overlap"].append(row)
            print(f"  {window:9s} {outcome:6s} controls={row['n_control']}  "
                  f"did={row['did_coef']:+.5f}  p={row['did_p']:.5f}")

    with open(OUT_JSON, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Saved {OUT_JSON}")


if __name__ == "__main__":
    main()
