"""
Holm correction across the triangulation family (Development Log Entry 50).

The paper's primary family is the four NDBI and night-light DiDs (Holm-adjusted,
all 1.000). This script applies the same correction to the secondary family:
the six triangulation DiDs (Sentinel-1 VV, Sentinel-1 VH and Dynamic World
built-up probability, each in the full-year and summer windows), using the
t(13) p-values reported in the paper's Table 2.

Same specification as did_numpy.did(): district fixed effects, CR1
district-clustered SE, t with 13 df.

run:  python src/analysis/triangulation_holm.py
out:  outputs/triangulation_holm_results.json
"""

import json

import pandas as pd

from did_numpy import did, long_panel

P = "data/processed/"
OUT_PATH = "outputs/triangulation_holm_results.json"
TESTS = [
    ("sar", "vv", "full_year", "fullyear"), ("sar", "vv", "summer", "summer"),
    ("sar", "vh", "full_year", "fullyear"), ("sar", "vh", "summer", "summer"),
    ("dynamicworld", "built", "full_year", "fullyear"), ("dynamicworld", "built", "summer", "summer"),
]


def holm(pvals):
    order = sorted(range(len(pvals)), key=lambda i: pvals[i])
    adj, running = [0.0] * len(pvals), 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (len(pvals) - rank) * pvals[i]))
        adj[i] = running
    return adj


def main():
    rows = []
    for product, var, window, sfx in TESTS:
        t = pd.read_csv(f"{P}border_optics_treated_{product}_{sfx}.csv")
        t = t[t["is_core_sample"] == True]
        c = pd.read_csv(f"{P}border_optics_control_{product}_{sfx}.csv")
        r = did(long_panel(t, c, f"{var}_before", f"{var}_after"))
        rows.append({"outcome": var, "window": window, "coef": r["coef"], "se": r["se"],
                     "n_obs": r["n_obs"], "p_t13": r["p_t"]})
    for row, a in zip(rows, holm([r["p_t13"] for r in rows])):
        row["holm_adjusted_p"] = a
        row["significant_after_holm"] = a < 0.05
        print(f"{row['outcome']:6s} {row['window']:9s} coef={row['coef']:+.5f}  p_t13={row['p_t13']:.4f}  "
              f"Holm={a:.4f}")
    with open(OUT_PATH, "w") as f:
        json.dump({"family": "six triangulation DiDs (S1 VV, S1 VH, Dynamic World; both windows)",
                   "inference": "t with 13 df, district-clustered CR1 SE", "tests": rows}, f, indent=2)
    print(f"Saved {OUT_PATH}")


if __name__ == "__main__":
    main()
