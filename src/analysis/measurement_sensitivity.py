"""
What could the 500 m buffer-mean outcomes physically detect? (Entry 49.)

The power analysis (power_analysis.py) expresses sensitivity as Cohen's d,
which says nothing about whether a *plausible* amount of construction would
move a buffer-averaged index at all. This script answers that in physical
units, using data already in the repository:

1. Built-up share. Google Open Buildings footprint area per village divided by
   the 500 m buffer area (pi * 500^2 = 785,398 m^2).
2. Empirical contrast. Cross-sectional OLS (2025 level ~ building share +
   district FE, treated core + control villages pooled, district-clustered
   SE): how much buffer-mean NDBI / Dynamic World "built" rises per unit of
   building share. This is the index's own response to buildings, estimated
   from these villages rather than assumed.
3. Detectability. Implied buffer-mean change if a village added 50% / 100% of
   the median treated village's total building area, compared with the
   design's minimum detectable effects (border_optics_power_analysis.json).
4. Translation + equivalence. Each H4 DiD estimate and its t(13) 90% / 95%
   confidence bounds re-expressed as "extra building area per village" (m^2
   and multiples of the median village's building stock), and a TOST
   equivalence test against a smallest effect of interest (SESOI) of +100%
   of the median village's building area, i.e. a doubling.

run:  python src/analysis/measurement_sensitivity.py
out:  outputs/measurement_sensitivity_results.json
"""

import json

import numpy as np
import pandas as pd

from did_numpy import did, long_panel

P = "data/processed/"
BUFFER_AREA_M2 = np.pi * 500 ** 2
OUT_PATH = "outputs/measurement_sensitivity_results.json"

OUTCOMES = {
    # name: (treated file, control file, before col, after col)
    "ndbi_full_year": ("border_optics_village_results_analyzed.csv", "border_optics_control_results.csv",
                       "ndbi_before", "ndbi_after"),
    "ndbi_summer": ("border_optics_village_results_summer_analyzed.csv", "border_optics_control_results_summer.csv",
                    "ndbi_before", "ndbi_after"),
    "dw_built_full_year": ("border_optics_treated_dynamicworld_fullyear.csv", "border_optics_control_dynamicworld_fullyear.csv",
                           "built_before", "built_after"),
    "dw_built_summer": ("border_optics_treated_dynamicworld_summer.csv", "border_optics_control_dynamicworld_summer.csv",
                        "built_before", "built_after"),
}
MDE_KEYS = {"ndbi_full_year": ("full_year", "ndbi"), "ndbi_summer": ("summer", "ndbi")}


def clustered_slope(df, y, x):
    X = np.column_stack([np.ones(len(df)), df[x], pd.get_dummies(df["district"], drop_first=True).astype(float)])
    Y = df[y].to_numpy(float)
    XtXi = np.linalg.pinv(X.T @ X)
    b = XtXi @ X.T @ Y
    e = Y - X @ b
    g = df["district"].to_numpy()
    groups = np.unique(g)
    G, (n, k) = len(groups), X.shape
    meat = np.zeros((k, k))
    for gg in groups:
        s = X[g == gg].T @ e[g == gg]
        meat += np.outer(s, s)
    V = XtXi @ meat @ XtXi * (G / (G - 1)) * ((n - 1) / (n - k))
    return float(b[1]), float(np.sqrt(V[1, 1]))


def load_mdes():
    with open(P + "border_optics_power_analysis.json") as f:
        power = json.load(f)  # list of {test, window, outcome, mde, ...}
    return {(row["test"], row["window"], row["outcome"]): row["mde"] for row in power}


def main():
    ft = pd.read_csv(P + "border_optics_treated_building_footprints.csv")
    ft = ft[ft["is_core_sample"] == True]
    fc = pd.read_csv(P + "border_optics_control_building_footprints.csv")
    median_area = float(ft["building_total_area_m2"].median())
    share = ft["building_total_area_m2"] / BUFFER_AREA_M2
    results = {
        "buffer_area_m2": BUFFER_AREA_M2,
        "treated_core_n": int(len(ft)),
        "median_treated_building_area_m2": median_area,
        "median_treated_building_share_of_buffer": float(share.median()),
        "p90_treated_building_share_of_buffer": float(share.quantile(0.9)),
        "treated_core_buffers_with_zero_buildings": int((ft["building_count"] == 0).sum()),
        "sesoi_definition": "+100% of the median treated village's building area (a doubling)",
        "outcomes": {},
    }
    print(f"Median treated building area {median_area:,.0f} m^2 = {100 * share.median():.2f}% of the 500 m buffer; "
          f"{results['treated_core_buffers_with_zero_buildings']} of {len(ft)} core buffers contain no building.")

    mdes = load_mdes()
    for name, (tf, cf, before, after) in OUTCOMES.items():
        t = pd.read_csv(P + tf)
        t = t[t["is_core_sample"] == True]
        c = pd.read_csv(P + cf)
        lvl = pd.concat([
            t[["village_id", "district", after]].merge(ft[["village_id", "building_total_area_m2"]], on="village_id"),
            c[["village_id", "district", after]].merge(fc[["village_id", "building_total_area_m2"]], on="village_id"),
        ], ignore_index=True).dropna(subset=[after])
        lvl["share"] = lvl["building_total_area_m2"] / BUFFER_AREA_M2
        slope, slope_se = clustered_slope(lvl, after, "share")

        def to_m2(delta_index):
            return delta_index / slope * BUFFER_AREA_M2

        implied = {f"+{int(f * 100)}pct_median_building_area":
                   slope * f * median_area / BUFFER_AREA_M2 for f in (0.5, 1.0)}
        sesoi = implied["+100pct_median_building_area"]
        d = did(long_panel(t, c, before, after))
        lo90, hi90 = d["ci90_t"]
        equivalent = (lo90 > -sesoi) and (hi90 < sesoi)
        entry = {
            "contrast_slope_per_unit_building_share": slope, "contrast_slope_se": slope_se,
            "n_villages_for_contrast": int(len(lvl)),
            "implied_buffer_mean_change": implied,
            "did": d,
            "did_coef_as_building_area_m2": to_m2(d["coef"]),
            "did_ci95_t_as_building_area_m2": [to_m2(v) for v in d["ci95_t"]],
            "did_ci95_upper_as_multiple_of_median_village_building_stock": to_m2(d["ci95_t"][1]) / median_area,
            "tost_sesoi_index_units": sesoi,
            "tost_equivalent_at_alpha_0.05": bool(equivalent),
        }
        key = MDE_KEYS.get(name)
        if key:
            for (test, win, out), mde in mdes.items():
                if win == key[0] and out == key[1]:
                    entry[f"mde_{test}"] = mde
                    entry[f"doubling_as_fraction_of_mde_{test}"] = sesoi / mde
        results["outcomes"][name] = entry
        print(f"\n{name}: contrast {slope:.3f} (SE {slope_se:.3f}) per unit building share")
        print(f"  doubling the median village's buildings -> buffer-mean change {sesoi:+.5f}")
        print(f"  DiD {d['coef']:+.5f} (p_t13={d['p_t']:.4f}) = {to_m2(d['coef']):+,.0f} m^2 of building; "
              f"95% CI upper bound = {to_m2(d['ci95_t'][1]):+,.0f} m^2 "
              f"({entry['did_ci95_upper_as_multiple_of_median_village_building_stock']:.1f}x the median village's buildings)")
        print(f"  TOST vs +/-{sesoi:.5f}: {'EQUIVALENT' if equivalent else 'not equivalent'} "
              f"(90% CI [{lo90:+.5f}, {hi90:+.5f}])")
        for k, v in entry.items():
            if k.startswith("doubling_as_fraction_of_mde"):
                print(f"  {k} = {v:.2f}")

    with open(OUT_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved {OUT_PATH}")


if __name__ == "__main__":
    main()
