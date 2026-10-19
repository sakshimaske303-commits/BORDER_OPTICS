"""Files 11 (cross-proxy DiD) and 12 (footprint validation + case villages),
rebuilt in Development Log Entry 49.

Changes from v1.7:
  - 11: every DiD is computed from the data with did_numpy (district FE,
    cluster-robust, 95% CI with t(13)); wild-cluster-bootstrap p-values are
    printed where they exist (NDBI from wild_cluster_bootstrap.py, Dynamic
    World from dynamic_world_robustness.py)
  - 12B: the three case-study villages are no longer coloured "detected /
    wrong direction" from the sign of their change. Each proxy's change is
    shown as a percentile of all 251 core villages' changes for that proxy
    (50 = a typical village), because most villages decline in full-year
    NDBI and a median-sized rise is not a detection
  - 12A: titled as a cross-sectional LEVEL correlation, which it is
  - no hard-coded figure numbers; case-study values are read from the data

run from the repository root:  python src/visualization/make_triangulation_and_footprint_charts.py
"""

import json
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, "src/analysis")
from did_numpy import did, long_panel  # noqa: E402

os.makedirs("outputs/figures", exist_ok=True)
plt.rcParams.update({"figure.dpi": 150, "font.size": 10})
BLUE, ORANGE, RED, GREEN, GRAY = "#4C72B0", "#DD8452", "#C44E52", "#55A868", "#888888"
P = "data/processed/"


def core(path):
    d = pd.read_csv(P + path)
    return d[d["is_core_sample"] == True] if "is_core_sample" in d.columns else d


with open("outputs/wild_cluster_bootstrap_results.json") as f:
    wcb = {(r["window"], r["outcome"]): r["wild_cluster_bootstrap_p"] for r in json.load(f)}
with open("outputs/dynamic_world_robustness_results.json") as f:
    dwr = json.load(f)
wcb[("full_year", "built")] = dwr["full_year_main"]["wild_cluster_bootstrap_p"]
wcb[("summer", "built")] = dwr["summer_main"]["wild_cluster_bootstrap_p"]

SPECS = [  # proxy label, outcome key, before, after, treated file, control file, window
    ("NDBI (500 m mean)", "ndbi", "ndbi_before", "ndbi_after",
     {"full_year": ("border_optics_village_results_analyzed.csv", "border_optics_control_results.csv"),
      "summer": ("border_optics_village_results_summer_analyzed.csv", "border_optics_control_results_summer.csv")}),
    ("SAR VV (dB)", "vv", "vv_before", "vv_after",
     {"full_year": ("border_optics_treated_sar_fullyear.csv", "border_optics_control_sar_fullyear.csv"),
      "summer": ("border_optics_treated_sar_summer.csv", "border_optics_control_sar_summer.csv")}),
    ("SAR VH (dB)", "vh", "vh_before", "vh_after",
     {"full_year": ("border_optics_treated_sar_fullyear.csv", "border_optics_control_sar_fullyear.csv"),
      "summer": ("border_optics_treated_sar_summer.csv", "border_optics_control_sar_summer.csv")}),
    ("Dynamic World 'built' probability", "built", "built_before", "built_after",
     {"full_year": ("border_optics_treated_dynamicworld_fullyear.csv", "border_optics_control_dynamicworld_fullyear.csv"),
      "summer": ("border_optics_treated_dynamicworld_summer.csv", "border_optics_control_dynamicworld_summer.csv")}),
]

# --- 11 ---------------------------------------------------------------------------------------
fig, axes = plt.subplots(1, 4, figsize=(14, 3.6), sharey=True)
for ax, (label, key, b, a, files) in zip(axes, SPECS):
    for i, window in enumerate(["full_year", "summer"]):
        tf, cf = files[window]
        t = core(tf).dropna(subset=[b, a])
        c = pd.read_csv(P + cf).dropna(subset=[b, a])
        r = did(long_panel(t, c, b, a))
        lo, hi = r["ci95_t"]
        color = RED if r["p_t"] < 0.05 else GRAY
        ax.plot([lo, hi], [i, i], color=color, linewidth=2)
        ax.scatter(r["coef"], i, color=color, s=55, zorder=3)
        txt = f"p = {r['p_t']:.3f}"
        if (window, key) in wcb:
            txt += f"\nwild bootstrap p = {wcb[(window, key)]:.3f}"
        ax.text(r["coef"], i + 0.2, txt, ha="center", va="top", fontsize=7)
    ax.axvline(0, color="black", linestyle="--", linewidth=1)
    ax.set_yticks([0, 1])
    ax.set_yticklabels(["Full-year", "Summer"])
    ax.set_ylim(-0.5, 1.7)
    ax.set_title(label, fontsize=9.5)
    ax.set_xlabel("DiD coefficient (own units)", fontsize=8)
axes[0].invert_yaxis()
fig.suptitle("Treated − control DiD across proxies (district FE; 95% CI with t, 13 df; red = p < 0.05)", fontsize=10.5)
fig.tight_layout()
fig.savefig("outputs/figures/11_triangulation_did.png", bbox_inches="tight")
plt.close(fig)
print("Saved outputs/figures/11_triangulation_did.png")

# --- 12 ---------------------------------------------------------------------------------------
with open("outputs/building_footprint_validation.json") as f:
    fp = json.load(f)
fy = core("border_optics_village_results_analyzed.csv")
dw = core("border_optics_treated_dynamicworld_fullyear.csv")
changes = {
    "NDBI": fy.set_index("village")["ndbi_after"] - fy.set_index("village")["ndbi_before"],
    "Night lights": fy.set_index("village")["lights_after"] - fy.set_index("village")["lights_before"],
    "Dynamic World": dw.set_index("village")["built_after"] - dw.set_index("village")["built_before"],
}
cases = ["Kaho", "Musai", "Walong"]

fig = plt.figure(figsize=(13, 4.4))
gs = fig.add_gridspec(1, 2, width_ratios=[1, 1.6])
ax_a, ax_b = fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1])
rows = [("NDBI", fp["building_count_vs_ndbi_after"]["rho"]), ("Night lights", fp["building_count_vs_lights_after"]["rho"]),
        ("Dynamic World", fp["building_count_vs_built_after"]["rho"])]
ax_a.bar(range(3), [r[1] for r in rows], color=[BLUE, ORANGE, GREEN], edgecolor="black", width=0.6)
for i, (_, rho) in enumerate(rows):
    ax_a.text(i, rho + 0.02, f"ρ = {rho:.2f}", ha="center", fontsize=9)
ax_a.set_xticks(range(3))
ax_a.set_xticklabels([r[0] for r in rows])
ax_a.set_ylim(0, 1)
ax_a.set_ylabel("Spearman ρ with building count")
ax_a.set_title("A. 2025 LEVEL vs Open Buildings count (n = 249–251)\n(cross-section; says nothing about detecting change)",
               fontsize=9)

width = 0.25
for j, (proxy, color) in enumerate(zip(changes, [BLUE, ORANGE, GREEN])):
    ch = changes[proxy].dropna()
    pct = [100 * (ch < ch[v]).mean() for v in cases]
    xs = np.arange(3) + (j - 1) * width
    ax_b.bar(xs, pct, width=width, color=color, edgecolor="black", label=proxy)
    for x, pv, v in zip(xs, pct, cases):
        ax_b.text(x, pv + 2, f"{ch[v]:+.3f}", ha="center", fontsize=6.5, rotation=90)
ax_b.axhline(50, color="black", linestyle="--", linewidth=1)
ax_b.text(2.45, 51, "typical village", fontsize=7, ha="right")
ax_b.set_ylim(0, 135)
ax_b.set_xticks(range(3))
ax_b.set_xticklabels(cases)
ax_b.set_ylabel("Percentile of the village's change\namong all 251 core villages")
ax_b.set_title("B. Villages with VVP-I works inaugurated Oct–Nov 2023 (Anjaw): full-year 2021→2025 change\n"
               "(numbers above bars = raw change)", fontsize=9)
ax_b.legend(fontsize=8, loc="upper center", ncol=3, frameon=False)
fig.tight_layout()
fig.savefig("outputs/figures/12_footprint_validation.png", bbox_inches="tight")
plt.close(fig)
print("Saved outputs/figures/12_footprint_validation.png")
