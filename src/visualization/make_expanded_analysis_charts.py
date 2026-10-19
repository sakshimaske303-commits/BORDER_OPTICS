"""Files 08 (control-group DiD), 09 (three-point trend) and 10 (buffer
radius), rebuilt in Development Log Entry 49.

Changes from v1.7:
  - 08: 95% intervals use t with 13 df (14 district clusters) instead of the
    normal approximation, wild-cluster-bootstrap p-values are printed, and
    the NDBI rows show, as a shaded band, the change that doubling the median
    village's buildings would produce (outputs/measurement_sensitivity_results.json),
    so the reader sees how wide the interval is relative to a plausible effect
  - 09: the 2023 point is marked as possibly cloud-unmasked (QA60 band empty
    in Sentinel-2 SR Harmonized for most of 2022 to early 2024)
  - 10: mean change with 95% CI per radius instead of a bar chart of p-values
  - no hard-coded figure numbers in titles
Run did_model.py, wild_cluster_bootstrap.py, measurement_sensitivity.py first.

run from the repository root:  python src/visualization/make_expanded_analysis_charts.py
"""

import json
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, "src/analysis")
from did_numpy import did, long_panel  # noqa: E402

os.makedirs("outputs/figures", exist_ok=True)
plt.rcParams.update({"figure.dpi": 150, "font.size": 10})
BLUE, ORANGE, RED = "#4C72B0", "#DD8452", "#C44E52"
P = "data/processed/"

# --- 08: control-group DiD ------------------------------------------------------------------
with open("outputs/wild_cluster_bootstrap_results.json") as f:
    wcb = {(r["window"], r["outcome"]): r["wild_cluster_bootstrap_p"] for r in json.load(f)}
with open("outputs/measurement_sensitivity_results.json") as f:
    ms = json.load(f)["outcomes"]
sesoi = {"full_year": ms["ndbi_full_year"]["tost_sesoi_index_units"], "summer": ms["ndbi_summer"]["tost_sesoi_index_units"]}

files = {"full_year": ("border_optics_village_results_analyzed.csv", "border_optics_control_results.csv"),
         "summer": ("border_optics_village_results_summer_analyzed.csv", "border_optics_control_results_summer.csv")}
fig, axes = plt.subplots(1, 2, figsize=(11, 3.8))
for ax, outcome, xlabel in [(axes[0], "ndbi", "DiD coefficient, 500 m buffer-mean NDBI"),
                            (axes[1], "lights", "DiD coefficient, night-light radiance (nW/cm²/sr)")]:
    for i, (window, color, label) in enumerate([("full_year", BLUE, "Full-year"), ("summer", ORANGE, "Summer")]):
        tf, cf = files[window]
        t = pd.read_csv(P + tf)
        t = t[t.is_core_sample == True]
        r = did(long_panel(t, pd.read_csv(P + cf), f"{outcome}_before", f"{outcome}_after"))
        lo, hi = r["ci95_t"]
        if outcome == "ndbi":
            ax.fill_betweenx([i - 0.3, i + 0.3], -sesoi[window], sesoi[window], color="#55A868", alpha=0.25,
                             label="± effect of doubling a median village's buildings" if i == 0 else None)
        ax.plot([lo, hi], [i, i], color=color, linewidth=2)
        ax.scatter(r["coef"], i, color=color, s=60, zorder=3)
        ax.text(r["coef"], i + 0.22, f"p = {r['p_t']:.2f} (t, 13 df); wild bootstrap p = {wcb[(window, outcome)]:.2f}",
                fontsize=7.5, va="top", ha="center")
    ax.set_yticks([0, 1])
    ax.set_yticklabels(["Full-year", "Summer"])
    ax.set_ylim(-0.6, 1.8)
    ax.axvline(0, color="black", linestyle="--", linewidth=1)
    ax.set_xlabel(xlabel, fontsize=9)
    if outcome == "ndbi":
        ax.legend(fontsize=7, loc="upper left")
axes[0].invert_yaxis()
axes[1].invert_yaxis()
fig.suptitle("Treated − control difference in 2021→2025 change (district FE; 95% CI, t with 13 df; "
             "251 treated / 721 control villages)", fontsize=10)
fig.tight_layout()
fig.savefig("outputs/figures/08_control_group_did_effect.png", bbox_inches="tight")
plt.close(fig)
print("Saved outputs/figures/08_control_group_did_effect.png")

# --- 09: three-point trend ------------------------------------------------------------------
my_fy = pd.read_csv(P + "border_optics_multiyear_fullyear.csv")
my_sm = pd.read_csv(P + "border_optics_multiyear_summer.csv")
my_fy, my_sm = my_fy[my_fy.is_core_sample == True], my_sm[my_sm.is_core_sample == True]
YEARS = [2021, 2023, 2025]
fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
for outcome, ax, ylabel in [("ndbi", axes[0], "Mean 500 m buffer-mean NDBI"),
                            ("lights", axes[1], "Mean night-light radiance (nW/cm²/sr)")]:
    for label, df, color in [("Full-year", my_fy, BLUE), ("Summer", my_sm, ORANGE)]:
        means = [df[f"{outcome}_{y}"].mean() for y in YEARS]
        sems = [df[f"{outcome}_{y}"].std() / np.sqrt(df[f"{outcome}_{y}"].count()) for y in YEARS]
        ax.errorbar(YEARS, means, yerr=sems, marker="o", capsize=4, label=label, color=color, linewidth=2)
    if outcome == "ndbi":
        ax.axvspan(2022.6, 2023.4, color="grey", alpha=0.15)
        ax.text(2023, ax.get_ylim()[1], "2023 composites may be\nunmasked (QA60 gap)", ha="center", va="top", fontsize=7)
    ax.set_xticks(YEARS)
    ax.set_xlabel("Year")
    ax.set_ylabel(ylabel)
    ax.set_title(f"{'NDBI' if outcome == 'ndbi' else 'Night lights'} — mean ± SE, treated core sample (n = 251)", fontsize=10)
axes[0].legend(loc="lower right", fontsize=9)
fig.tight_layout()
fig.savefig("outputs/figures/09_multiyear_trend.png", bbox_inches="tight")
plt.close(fig)
print("Saved outputs/figures/09_multiyear_trend.png")

# --- 10: buffer radius, mean change with 95% CI -------------------------------------------------
paths = {250: "border_optics_buffer250_summer.csv", 500: "border_optics_village_results_summer.csv",
         1000: "border_optics_buffer1000_summer.csv"}
with open(P + "border_optics_buffer_sensitivity_summary.json") as f:
    pvals = {r["buffer_m"]: r["ndbi_wilcoxon_p"] for r in json.load(f)["as_extracted"]}
fig, ax = plt.subplots(figsize=(7.5, 4))
for i, (radius, fname) in enumerate(paths.items()):
    d = pd.read_csv(P + fname)
    d = d[d.is_core_sample == True]
    ch = (d.ndbi_after - d.ndbi_before).dropna()
    half = stats.t.ppf(0.975, len(ch) - 1) * ch.std() / np.sqrt(len(ch))
    ax.plot([ch.mean() - half, ch.mean() + half], [i, i], color=ORANGE, linewidth=2)
    ax.scatter(ch.mean(), i, color=ORANGE, s=60, zorder=3)
    ax.text(ch.mean() + half, i, f"  n = {len(ch)}, Wilcoxon p = {pvals[radius]:.2f}", va="center", fontsize=8)
ax.axvline(0, color="black", linestyle="--", linewidth=1)
ax.set_yticks(range(3))
ax.set_yticklabels(["250 m", "500 m", "1 km"])
ax.invert_yaxis()
ax.set_xlabel("Mean change in buffer-mean NDBI, summer window (95% CI)")
ax.set_title("Buffer radius sensitivity (all radii extracted the same day)", fontsize=10)
ax.margins(x=0.45)
fig.tight_layout()
fig.savefig("outputs/figures/10_buffer_sensitivity.png", bbox_inches="tight")
plt.close(fig)
print("Saved outputs/figures/10_buffer_sensitivity.png")
