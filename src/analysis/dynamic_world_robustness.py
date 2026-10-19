"""
Robustness for the one significant control-group DiD in the study:
Dynamic World "built" probability (Entry 49).

Until v1.7 this result had only the standard cluster-robust p-value and a
2019 placebo. Here it gets the same small-cluster treatment the NDBI/lights
DiDs already had, plus composition checks:

  - t(13) p-value (instead of the normal approximation)
  - exact wild cluster bootstrap (2**14 = 16,384 sign vectors)
  - full-year re-estimated without Sikkim (the summer window has no valid
    Sikkim treated villages, so this shows how much the full-year result
    depends on that state)
  - full-year re-estimated on the summer window's treated/control villages,
    so the two windows can be compared on the same villages
  - leave-one-district-out (count significant at t(13) 0.05, coefficient range)
  - without the 10 control villages that are official priority villages
    written with a qualifier (see sample_qa_sensitivity.py)

run:  python src/analysis/dynamic_world_robustness.py      (~3 minutes, bootstrap)
out:  outputs/dynamic_world_robustness_results.json
"""

import json

import pandas as pd

from did_numpy import did, long_panel, wild_cluster_bootstrap_p
from sample_qa_sensitivity import suffix_matched_control_ids

P = "data/processed/"
OUT_PATH = "outputs/dynamic_world_robustness_results.json"
FILES = {
    "full_year": ("border_optics_treated_dynamicworld_fullyear.csv", "border_optics_control_dynamicworld_fullyear.csv"),
    "summer": ("border_optics_treated_dynamicworld_summer.csv", "border_optics_control_dynamicworld_summer.csv"),
}


def load(window):
    tf, cf = FILES[window]
    t = pd.read_csv(P + tf)
    t = t[t["is_core_sample"] == True].dropna(subset=["built_before", "built_after"])
    c = pd.read_csv(P + cf).dropna(subset=["built_before", "built_after"])
    return t, c


def summarize(label, t, c, bootstrap=False):
    panel = long_panel(t, c, "built_before", "built_after")
    r = did(panel)
    r.update({"n_treated": int(len(t)), "n_control": int(len(c)),
              "n_treated_districts": int(t["district"].nunique())})
    if bootstrap:
        r["wild_cluster_bootstrap_p"] = wild_cluster_bootstrap_p(panel)
    extra = f"  WCB p={r['wild_cluster_bootstrap_p']:.4f}" if bootstrap else ""
    print(f"{label:45s} coef={r['coef']:+.5f}  p_z={r['p_z']:.4f}  p_t13={r['p_t']:.4f}{extra}  "
          f"(treated {r['n_treated']} in {r['n_treated_districts']} districts / control {r['n_control']})")
    return r


def main():
    out = {}
    for window in ["full_year", "summer"]:
        t, c = load(window)
        out[f"{window}_main"] = summarize(f"{window}: all villages", t, c, bootstrap=True)
        rows = []
        for d in sorted(t["district"].unique()):
            r = did(long_panel(t[t.district != d], c[c.district != d], "built_before", "built_after"))
            rows.append({"dropped_district": d, "coef": r["coef"], "p_t": r["p_t"]})
        loo = pd.DataFrame(rows)
        out[f"{window}_leave_one_district_out"] = {
            "n_significant_t13": int((loo.p_t < 0.05).sum()), "n_reruns": int(len(loo)),
            "coef_min": float(loo.coef.min()), "coef_max": float(loo.coef.max()),
            "nonsignificant_when_dropping": loo.loc[loo.p_t >= 0.05, "dropped_district"].tolist(),
        }
        print(f"  leave-one-district-out: {out[f'{window}_leave_one_district_out']['n_significant_t13']}/{len(loo)} "
              f"significant at t(13); coef {loo.coef.min():+.5f}..{loo.coef.max():+.5f}; "
              f"non-significant when dropping {out[f'{window}_leave_one_district_out']['nonsignificant_when_dropping']}")

    t, c = load("full_year")
    out["full_year_without_sikkim"] = summarize("full_year: without Sikkim", t[t.state != "Sikkim"], c[c.state != "Sikkim"])
    ts, cs = load("summer")
    out["full_year_on_summer_villages"] = summarize(
        "full_year: restricted to summer-valid villages",
        t[t.village_id.isin(ts.village_id)], c[c.village_id.isin(cs.village_id)])

    bad = suffix_matched_control_ids()
    for window in ["full_year", "summer"]:
        t, c = load(window)
        out[f"{window}_without_suffix_matched_controls"] = summarize(
            f"{window}: without 10 suffix-matched controls", t, c[~c.village_id.isin(bad)])

    with open(OUT_PATH, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nSaved {OUT_PATH}")


if __name__ == "__main__":
    main()
