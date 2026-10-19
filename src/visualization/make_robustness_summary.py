"""Summary of the treated-only (H1) and border-proximity (H3) tests, file
07_robustness_summary.png (rebuilt in Development Log Entry 49).

Changes from v1.7: H1 is plotted two-sided with the direction of change
marked (the one-sided p = 1.000 had hidden a significant full-year
*decline*); H3 is shown both pooled and within-district (stratified
Spearman, permutation p, from outputs/h3_within_district_results.json), so
the figure no longer suggests that the pooled H3 correlations are robust
proximity effects. No hard-coded figure number in the title.

run from the repository root:  python src/visualization/make_robustness_summary.py
"""

import json

import matplotlib.pyplot as plt
import pandas as pd
from scipy import stats

FY = pd.read_csv("data/processed/border_optics_village_results_analyzed.csv")
SU = pd.read_csv("data/processed/border_optics_village_results_summer_analyzed.csv")
FY, SU = FY[FY.is_core_sample == True], SU[SU.is_core_sample == True]
with open("outputs/h3_within_district_results.json") as f:
    H3 = json.load(f)

rows = []
for wlabel, wkey, df in [("Full-year", "full_year", FY), ("Summer", "summer", SU)]:
    for o, name in [("ndbi", "H1  NDBI change (Wilcoxon, two-sided)"), ("lights", "Night-light change (Wilcoxon, two-sided)")]:
        v = df.dropna(subset=[f"{o}_before", f"{o}_after"])
        p = stats.wilcoxon(v[f"{o}_after"], v[f"{o}_before"]).pvalue
        direction = "↑" if (v[f"{o}_after"] - v[f"{o}_before"]).median() > 0 else "↓"
        rows.append((name, wlabel, p, direction, "filled"))
    for o, name in [("ndbi_change", "H3  distance vs NDBI change"), ("lights_change", "H3  distance vs night-light change")]:
        r = H3[f"{wkey}|{o}|distance_to_border_km"]
        rows.append((name + " — pooled", wlabel, r["pooled_p"], "+" if r["pooled_rho"] > 0 else "−", "filled"))
        rows.append((name + " — within district", wlabel, r["within_district_perm_p"],
                     "+" if r["within_district_rank_corr"] > 0 else "−", "hollow"))
df = pd.DataFrame(rows, columns=["test", "window", "p", "sign", "style"])
df["p_plot"] = df["p"].clip(lower=1e-16)

tests = list(dict.fromkeys(df["test"]))
fig, ax = plt.subplots(figsize=(10, 6))
colors = {"Full-year": "#4C72B0", "Summer": "#DD8452"}
for w, off in [("Full-year", -0.15), ("Summer", 0.15)]:
    s = df[df.window == w]
    for _, r in s.iterrows():
        y = tests.index(r.test) + off
        face = colors[w] if r["style"] == "filled" else "white"
        ax.scatter(r.p_plot, y, s=80, facecolor=face, edgecolor=colors[w], linewidth=1.6, zorder=3,
                   label=w if r.test == tests[0] else None)
        ax.text(r.p_plot * 1.6, y, r.sign, va="center", fontsize=9, color=colors[w])
ax.axvline(0.05, color="#C44E52", linewidth=1.2)
ax.text(0.05, len(tests) - 0.55, " p = 0.05", color="#C44E52", fontsize=8)
ax.set_xscale("log")
ax.set_yticks(range(len(tests)))
ax.set_yticklabels(tests, fontsize=9)
ax.invert_yaxis()
ax.set_xlabel("p-value (log scale). Arrow / sign = direction of the median change or correlation")
ax.set_title("Treated-only and border-proximity tests, both windows\n"
             "(filled = as reported before; hollow = within-district H3)", fontsize=11)
ax.legend(loc="lower left", fontsize=8)
fig.tight_layout()
fig.savefig("outputs/figures/07_robustness_summary.png", bbox_inches="tight", dpi=150)
plt.close(fig)
print("Saved outputs/figures/07_robustness_summary.png")
print(df[["test", "window", "p", "sign"]].to_string(index=False))
