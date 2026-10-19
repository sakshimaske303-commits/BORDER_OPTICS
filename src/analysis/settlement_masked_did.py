"""
DiD on the settlement-targeted outcomes from extract_settlement_masked.py
(Development Log Entry 49, fix A1). Same specification as did_model.py,
via did_numpy (cluster-robust by district, t(13) and normal p-values,
optional exact wild cluster bootstrap).

For each outcome (ndbi_zone, dw_built_zone, dw_built_area_m2, viirs_cf):
  main      2021 -> 2025, both windows
  extended  2021 -> 2026, summer window (longer exposure after Feb 2023 sanction)
  placebo   2019 -> 2021, both windows (should be null)
Villages with no Open Buildings footprint have no settlement zone; they are
dropped from the zone outcomes (and counted), but kept for dw_built_area_m2
and viirs_cf, which use the whole buffer.

run:  python src/analysis/settlement_masked_did.py [--bootstrap]
out:  outputs/settlement_masked_did_results.json
"""

import argparse
import json
import os

import pandas as pd

from did_numpy import did, long_panel, wild_cluster_bootstrap_p

P = "data/processed/"
OUT_PATH = "outputs/settlement_masked_did_results.json"
OUTCOMES = ["ndbi_zone", "dw_built_zone", "dw_built_area_m2", "viirs_cf"]
CONTRASTS = {
    "full_year": [("main", 2021, 2025), ("placebo", 2019, 2021)],
    "summer": [("main", 2021, 2025), ("extended", 2021, 2026), ("placebo", 2019, 2021)],
}


def load(window, base=P):
    t = pd.read_csv(f"{base}border_optics_treated_settlement_masked_{window}.csv")
    c = pd.read_csv(f"{base}border_optics_control_settlement_masked_{window}.csv")
    return t, c


def run(base=P, out_path=OUT_PATH, bootstrap=False):
    results = {}
    for window, contrasts in CONTRASTS.items():
        if not os.path.exists(f"{base}border_optics_treated_settlement_masked_{window}.csv"):
            print(f"{window}: extraction output not found -- run extract_settlement_masked.py first.")
            continue
        t, c = load(window, base)
        for outcome in OUTCOMES:
            for label, y0, y1 in contrasts:
                b, a = f"{outcome}_{y0}", f"{outcome}_{y1}"
                if b not in t.columns or a not in t.columns:
                    continue
                panel = long_panel(t, c, b, a)
                if panel.empty or panel["treatment"].nunique() < 2:
                    continue
                r = did(panel)
                r["n_treated_villages"] = int(t.dropna(subset=[b, a]).shape[0])
                r["n_control_villages"] = int(c.dropna(subset=[b, a]).shape[0])
                if bootstrap:
                    r["wild_cluster_bootstrap_p"] = wild_cluster_bootstrap_p(panel)
                key = f"{window}|{outcome}|{label}_{y0}_{y1}"
                results[key] = r
                extra = f" WCB p={r['wild_cluster_bootstrap_p']:.4f}" if bootstrap else ""
                print(f"{key:48s} coef={r['coef']:+.5f} p_t13={r['p_t']:.4f}{extra} "
                      f"(n={r['n_treated_villages']}/{r['n_control_villages']})")
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Saved {out_path}")
    return results


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--bootstrap", action="store_true", help="add exact wild cluster bootstrap p-values (slow)")
    run(bootstrap=ap.parse_args().bootstrap)
