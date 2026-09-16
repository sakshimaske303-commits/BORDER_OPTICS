"""Figures 11-12 (reading-order numbering, matching the convention
make_expanded_analysis_charts.py already uses): the SAR/Dynamic World
triangulation (Section 4.10) and the building-footprint validation
(Section 7.2), added in Development Log Entry 32/33 -- these findings
existed in the paper's prose since Entries 26 and 30 but never had a figure.
Run triangulation_analysis.py and building_footprint_validation.py first
(their JSON outputs are read here, not recomputed).
"""

import json
import os

import matplotlib.pyplot as plt
import numpy as np

os.makedirs("outputs/figures", exist_ok=True)
plt.rcParams.update({"figure.dpi": 150, "font.size": 10})

BLUE = "#4C72B0"
ORANGE = "#DD8452"
RED = "#C44E52"
GREEN = "#55A868"
GRAY = "#888888"

# ============================================================
# FIGURE 11 — SAR / Dynamic World triangulation vs. primary NDBI DiD
# ============================================================
with open("data/processed/border_optics_did_summary_fullyear.json") as f:
    did_fy = json.load(f)
with open("data/processed/border_optics_did_summary_summer.json") as f:
    did_sm = json.load(f)
with open("outputs/triangulation_results.json") as f:
    tri = json.load(f)

ndbi_fy = next(r for r in did_fy["did"] if r["outcome"] == "ndbi")
ndbi_sm = next(r for r in did_sm["did"] if r["outcome"] == "ndbi")

rows = [
    ("NDBI (primary)", "Full-Year", ndbi_fy["did_coef"], ndbi_fy["did_ci_lo"], ndbi_fy["did_ci_hi"], ndbi_fy["did_p"]),
    ("NDBI (primary)", "Summer", ndbi_sm["did_coef"], ndbi_sm["did_ci_lo"], ndbi_sm["did_ci_hi"], ndbi_sm["did_p"]),
    ("SAR VV", "Full-Year", *[tri["sar_vv_full_year"]["h4_control_group_did"][k] for k in
                               ("did_coef", "did_ci_lo", "did_ci_hi", "did_p")]),
    ("SAR VV", "Summer", *[tri["sar_vv_summer"]["h4_control_group_did"][k] for k in
                            ("did_coef", "did_ci_lo", "did_ci_hi", "did_p")]),
    ("SAR VH", "Full-Year", *[tri["sar_vh_full_year"]["h4_control_group_did"][k] for k in
                               ("did_coef", "did_ci_lo", "did_ci_hi", "did_p")]),
    ("SAR VH", "Summer", *[tri["sar_vh_summer"]["h4_control_group_did"][k] for k in
                            ("did_coef", "did_ci_lo", "did_ci_hi", "did_p")]),
    ("Dynamic World 'built'", "Full-Year", *[tri["dynamicworld_built_full_year"]["h4_control_group_did"][k] for k in
                                              ("did_coef", "did_ci_lo", "did_ci_hi", "did_p")]),
    ("Dynamic World 'built'", "Summer", *[tri["dynamicworld_built_summer"]["h4_control_group_did"][k] for k in
                                           ("did_coef", "did_ci_lo", "did_ci_hi", "did_p")]),
]

# each proxy has its own scale (NDBI ~ +/-0.01, SAR in dB ~ +/-0.1, DW probability ~ +/-0.01)
# -- plot as separate panels sharing only the "null line at 0" and significance color, not a shared x-axis
fig, axes = plt.subplots(1, 4, figsize=(13, 4), sharey=True)
proxies = ["NDBI (primary)", "SAR VV", "SAR VH", "Dynamic World 'built'"]
for ax, proxy in zip(axes, proxies):
    sub = [r for r in rows if r[0] == proxy]
    y = np.arange(len(sub))
    for yi, (_, window, coef, lo, hi, p) in zip(y, sub):
        color = RED if p < 0.05 else GRAY
        ax.errorbar(coef, yi, xerr=[[coef - lo], [hi - coef]], fmt="o", color=color,
                    ecolor=color, elinewidth=1.5, capsize=4, markersize=8)
        sig = "*" if p < 0.05 else ""
        ax.text(hi + abs(hi - lo) * 0.15, yi, f"p={p:.4f}{sig}", va="center", fontsize=7.5)
    ax.axvline(0, color="black", linewidth=1, linestyle="--")
    ax.set_yticks(list(y))
    ax.set_yticklabels([r[1] for r in sub])
    ax.invert_yaxis()
    ax.set_title(proxy, fontsize=9.5)
    ax.set_xlabel("DiD coefficient", fontsize=8)

fig.suptitle("Figure 11 — Section 4.10 Triangulation: Control-Group DiD Across Proxies\n"
             "(red = p<0.05; each proxy on its own scale -- SAR in dB, NDBI/Dynamic World on a 0-1-ish index)",
             y=1.06, fontsize=11, fontweight="bold")
fig.tight_layout()
fig.savefig("outputs/figures/11_triangulation_did.png", bbox_inches="tight")
plt.close(fig)
print("Saved outputs/figures/11_triangulation_did.png")

# ============================================================
# FIGURE 12 — Building-footprint validation (Section 7.2)
# ============================================================
with open("outputs/building_footprint_validation.json") as f:
    fp = json.load(f)

fig = plt.figure(figsize=(13, 4.5))
gs = fig.add_gridspec(1, 4, width_ratios=[1.1, 1, 1, 1])
ax_a = fig.add_subplot(gs[0, 0])
axes_b = [fig.add_subplot(gs[0, i]) for i in (1, 2, 3)]

# Panel A: Spearman rho of each proxy against independent building counts
proxies2 = [
    ("NDBI", fp["building_count_vs_ndbi_after"]["rho"], fp["building_count_vs_ndbi_after"]["p"]),
    ("Night-lights", fp["building_count_vs_lights_after"]["rho"], fp["building_count_vs_lights_after"]["p"]),
    ("Dynamic World\n'built'", fp["building_count_vs_built_after"]["rho"], fp["building_count_vs_built_after"]["p"]),
]
x = np.arange(len(proxies2))
colors_a = [BLUE, ORANGE, GREEN]
ax_a.bar(x, [r[1] for r in proxies2], color=colors_a, edgecolor="black", width=0.6)
for xi, (name, rho, p) in zip(x, proxies2):
    ax_a.text(xi, rho + 0.02, f"ρ={rho:.3f}", ha="center", fontsize=9)
ax_a.set_xticks(list(x))
ax_a.set_xticklabels([r[0] for r in proxies2], fontsize=8)
ax_a.set_ylabel("Spearman ρ vs. building-footprint count")
ax_a.set_ylim(0, 1)
ax_a.set_title("A. Correlation with\nGoogle Open Buildings\ncount (n=249-251)", fontsize=9.5)

# Panel B: case-study villages -- REAL before/after CHANGE per proxy (not the absolute
# 2025-era level, which would show baseline differences between villages rather than
# whether each proxy detected the confirmed construction). Full-year window, matching
# the numbers actually reported in Section 7.3's prose.
case_changes = {
    "NDBI": {"Kaho": -0.0566174381424472, "Musai": -0.0643190391281804, "Walong": -0.0378806202748026},
    "Night-lights": {"Kaho": 0.4196043552372992, "Musai": 0.010865608312651, "Walong": 0.9085219773018396},
    "Dynamic World": {"Kaho": 0.043966416476991704, "Musai": 0.006130502977116203, "Walong": 0.015564234710227304},
}
building_counts = {"Kaho": 78, "Musai": 108, "Walong": 524}
villages_order = ["Kaho", "Musai", "Walong"]

for ax, (proxy_name, color) in zip(axes_b, zip(case_changes.keys(), colors_a)):
    vals = [case_changes[proxy_name][v] for v in villages_order]
    bar_colors = [GREEN if v > 0 else RED for v in vals]
    ax.bar(range(3), vals, color=bar_colors, edgecolor="black", width=0.6)
    ax.axhline(0, color="black", linewidth=1)
    ax.set_xticks(range(3))
    ax.set_xticklabels([f"{v}\n({building_counts[v]} bldgs)" for v in villages_order], fontsize=8)
    ax.set_title(proxy_name, fontsize=9.5)
    if ax is axes_b[0]:
        ax.set_ylabel("Full-year before→after change")

fig.suptitle("Figure 12 — Section 7.2/7.3: Building-Footprint Validation and Ground-Truth Case Study\n"
             "(B: green = proxy detects the confirmed real construction as an increase; red = wrong direction)",
             y=1.08, fontsize=11, fontweight="bold")
fig.tight_layout()
fig.savefig("outputs/figures/12_footprint_validation.png", bbox_inches="tight")
plt.close(fig)
print("Saved outputs/figures/12_footprint_validation.png")
