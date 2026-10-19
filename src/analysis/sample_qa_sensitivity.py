"""
Sample-quality sensitivity for the headline tests (Entry 49).

The forensic review found four data-quality issues that the robustness suite
never touched. None can be *fixed* without new geocoding or a new Earth
Engine run, but all can be *bounded* with data already in the repository:

  1. 7 pairs of treated villages share identical coordinates (14 rows, 7
     duplicated locations; e.g. Kitpi / Kitpi II, Pekong x2), so their
     500 m buffers -- and every satellite value -- are identical.
     Variant: keep the first row of each identical-coordinate group.
  2. 35 of 251 core treated buffers (and 61 of 721 control buffers) contain
     no Google Open Buildings footprint at all, a sign that the geocoded
     point may not sit on the settlement (e.g. Lachung).
     Variant: drop treated and control villages with zero buildings.
  3. Joshimath (a block-headquarters town, ~17,000 people) is in the
     treated list via the secondary Uttarakhand source and dominates the
     night-lights means.  Variant: drop Joshimath.
  5. 10 control villages are official VVP-I priority villages written with a
     qualifier the exact-name exclusion missed (e.g. "Sawa" vs official
     "Sawa H.Q.", "Bomdir" vs "Bomdir Basti"). Variant: drop them, using the
     same core_name() rule now in select_control_villages.py.
  4. Full-year treated NDBI/lights come from an earlier Earth Engine
     Code Editor export that is not in the repository; controls come from
     extract_control_satellite_data.py. The treated villages were later
     re-extracted with the repository's own Python pipeline for 2021 and
     2025 inside border_optics_multiyear_fullyear.csv.
     Variant: full-year DiD with treated 2021/2025 values taken from that
     Python extraction (pipeline-consistent with the controls).

Tests re-run under each variant: H1 treated-only Wilcoxon (one-sided
'greater' and two-sided), and the H4 DiD (cluster-robust, t(13)).

run:  python src/analysis/sample_qa_sensitivity.py
out:  outputs/sample_qa_sensitivity_results.json
"""

import json
import re
import unicodedata

import pandas as pd
from scipy import stats

from did_numpy import did, long_panel

P = "data/processed/"
OUT_PATH = "outputs/sample_qa_sensitivity_results.json"
WINDOWS = {
    "full_year": ("border_optics_village_results_analyzed.csv", "border_optics_control_results.csv"),
    "summer": ("border_optics_village_results_summer_analyzed.csv", "border_optics_control_results_summer.csv"),
}


_SUFFIX_RE = re.compile(r"\b(h\s*\.?\s*q\.?|hq|village|basti|camp|gaon|old|new|iii|ii|i)\b")


def core_name(name):
    """Identical to select_control_villages.core_name (kept here so this script needs no geopandas)."""
    s = unicodedata.normalize("NFKD", str(name)).encode("ascii", "ignore").decode()
    s = " ".join(s.lower().split())
    s = re.sub(r"\(.*?\)", " ", s)
    s = _SUFFIX_RE.sub(" ", s)
    s = re.sub(r"[^a-z]", "", s)
    return s if len(s) >= 4 else None


def suffix_matched_control_ids():
    official = {}
    for state, f in [("Arunachal Pradesh", "arunachal_pradesh"), ("Sikkim", "sikkim"), ("Uttarakhand", "uttarakhand")]:
        official[state] = {k for k in map(core_name, pd.read_csv(f"data/raw/{f}_vvp_villages.csv")["Habitation"]) if k}
    c = pd.read_csv(P + "border_optics_control_villages.csv")
    return set(c.loc[[core_name(v) in official.get(st, set()) for v, st in zip(c.village, c.state)], "village_id"])


def load(window):
    tf, cf = WINDOWS[window]
    t = pd.read_csv(P + tf)
    t = t[t["is_core_sample"] == True].copy()
    master = pd.read_csv(P + "border_optics_master_villages_with_distance.csv")[["village_id", "latitude", "longitude"]]
    if "latitude" not in t.columns:
        t = t.merge(master, on="village_id", how="left")
    c = pd.read_csv(P + cf)
    bt = pd.read_csv(P + "border_optics_treated_building_footprints.csv")[["village_id", "building_count"]]
    bc = pd.read_csv(P + "border_optics_control_building_footprints.csv")[["village_id", "building_count"]]
    return t.merge(bt, on="village_id", how="left"), c.merge(bc, on="village_id", how="left")


def variants(t, c):
    dedup = t.drop_duplicates(subset=["latitude", "longitude"], keep="first")
    nozero_t, nozero_c = t[t.building_count > 0], c[c.building_count > 0]
    no_josh = t[t.village != "Joshimath"]
    combined_t = dedup[(dedup.building_count > 0) & (dedup.village != "Joshimath")]
    bad = suffix_matched_control_ids()
    clean_c = c[~c.village_id.isin(bad)]
    return {
        "baseline": (t, c),
        "dedup_identical_coordinates": (dedup, c),
        "drop_zero_building_buffers": (nozero_t, nozero_c),
        "drop_joshimath": (no_josh, c),
        "drop_suffix_matched_controls": (t, clean_c),
        "all_combined": (combined_t, nozero_c[~nozero_c.village_id.isin(bad)]),
    }


def run_tests(t, c, outcome, before=None, after=None):
    before = before or f"{outcome}_before"
    after = after or f"{outcome}_after"
    v = t.dropna(subset=[before, after])
    change = v[after] - v[before]
    d = did(long_panel(t, c, before, after))
    return {
        "n_treated": int(len(v)), "n_control": int(c.dropna(subset=[before, after]).shape[0]),
        "mean_change": float(change.mean()), "median_change": float(change.median()),
        "h1_p_greater": float(stats.wilcoxon(v[after], v[before], alternative="greater").pvalue),
        "h1_p_two_sided": float(stats.wilcoxon(v[after], v[before]).pvalue),
        "did_coef": d["coef"], "did_p_t13": d["p_t"], "did_p_z": d["p_z"],
    }


def main():
    out = {}
    for window in WINDOWS:
        t, c = load(window)
        for name, (tv, cv) in variants(t, c).items():
            for outcome in ["ndbi", "lights"]:
                r = run_tests(tv, cv, outcome)
                out[f"{window}|{outcome}|{name}"] = r
                print(f"{window:9s} {outcome:6s} {name:30s} n={r['n_treated']}/{r['n_control']}  "
                      f"median chg={r['median_change']:+.4f} mean chg={r['mean_change']:+.4f}  "
                      f"H1 p(>)={r['h1_p_greater']:.4f} p(2s)={r['h1_p_two_sided']:.2g}  "
                      f"DiD={r['did_coef']:+.5f} p_t13={r['did_p_t13']:.3f}")

    # 4. pipeline-consistent full-year treated values
    t, c = load("full_year")
    py = pd.read_csv(P + "border_optics_multiyear_fullyear.csv")[
        ["village_id", "ndbi_2021", "ndbi_2025", "lights_2021", "lights_2025"]]
    tp = t.merge(py, on="village_id", how="left")
    for outcome in ["ndbi", "lights"]:
        r = run_tests(tp, c.rename(columns={f"{outcome}_before": f"{outcome}_2021", f"{outcome}_after": f"{outcome}_2025"}),
                      outcome, before=f"{outcome}_2021", after=f"{outcome}_2025")
        diff = (tp[f"{outcome}_2021"] - tp[f"{outcome}_before"]).abs()
        r["n_villages_2021_value_differs_by_gt_0.01"] = int((diff > 0.01).sum())
        out[f"full_year|{outcome}|python_pipeline_treated_values"] = r
        print(f"full_year {outcome:6s} {'python_pipeline_treated_values':30s} n={r['n_treated']}/{r['n_control']}  "
              f"median chg={r['median_change']:+.4f}  H1 p(>)={r['h1_p_greater']:.4f} p(2s)={r['h1_p_two_sided']:.2g}  "
              f"DiD={r['did_coef']:+.5f} p_t13={r['did_p_t13']:.3f}  "
              f"(2021 values differ >0.01 at {r['n_villages_2021_value_differs_by_gt_0.01']} villages)")

    with open(OUT_PATH, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nSaved {OUT_PATH}")


if __name__ == "__main__":
    main()
