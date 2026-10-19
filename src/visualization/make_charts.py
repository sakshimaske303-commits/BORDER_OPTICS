"""Core figures for H1, RQ2 and H3 (rebuilt in Development Log Entry 49).

Changes from v1.7, following the forensic review:
  - no hard-coded "Figure N" in image titles (paper numbering changed; the
    file names stay stable because the dashboard loads them)
  - 01: the extreme full-year values are labelled (their 2021 NDBI is
    below -0.6, i.e. snow/water, not built-up change) and medians are drawn
  - 02: the dual-axis bar chart is replaced by a labelled scatter of budget
    against mean NDBI change for both windows (n = 3, descriptive only)
  - 03: points coloured by district, with the pooled Spearman rho and the
    within-district (stratified) rho printed on every panel, so the reader
    can see that the pooled H3 correlations are between-district patterns
    (outputs/h3_within_district_results.json)

run from the repository root:  python src/visualization/make_charts.py
"""

import json
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

os.makedirs("outputs/figures", exist_ok=True)
plt.rcParams.update({"figure.dpi": 150, "font.size": 10})
BLUE, ORANGE = "#4C72B0", "#DD8452"

full_year = pd.read_csv("data/processed/border_optics_village_results_analyzed.csv")
summer = pd.read_csv("data/processed/border_optics_village_results_summer_analyzed.csv")
distances = pd.read_csv("data/processed/border_optics_master_villages_with_distance.csv")
full_year_core = full_year[full_year["is_core_sample"] == True].copy()
summer_core = summer[summer["is_core_sample"] == True].copy()

# --- 01: NDBI change distribution, both windows -------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), sharey=True)
for ax, df, color, title in [(axes[0], full_year_core, BLUE, "Full-year composites (2021 vs 2025)"),
                             (axes[1], summer_core, ORANGE, "Summer composites, Jun–Sep (2021 vs 2025)")]:
    ch = df["ndbi_change"].dropna()
    ax.hist(ch, bins=30, color=color, edgecolor="white")
    ax.axvline(0, color="black", linestyle="--", linewidth=1)
    ax.axvline(ch.median(), color="#333333", linewidth=1.4)
    ax.text(ch.median(), ax.get_ylim()[1] * 0.95, f" median {ch.median():+.4f}", fontsize=8, va="top")
    ax.set_title(title)
    ax.set_xlabel("Change in 500 m buffer-mean NDBI (2025 − 2021)")
    ax.text(0.98, 0.80, f"n = {len(ch)}\n{100 * (ch < 0).mean():.0f}% of villages decline",
            transform=ax.transAxes, ha="right", fontsize=8)
    snow = df[(df["ndbi_before"] < -0.6) & (df["ndbi_change"].abs() > 0.15)]
    for _, r in snow.iterrows():
        ax.annotate(f"{r['village']}\n(2021 NDBI {r['ndbi_before']:.2f})", (r["ndbi_change"], 1),
                    xytext=(r["ndbi_change"], 18), fontsize=7, ha="center",
                    arrowprops=dict(arrowstyle="-", color="grey", lw=0.6))
axes[0].set_ylabel("Number of villages")
fig.suptitle("NDBI change per village, core sample (n = 251). Labelled outliers start from snow/water values, "
             "not settlement", y=1.02, fontsize=10)
fig.tight_layout()
fig.savefig("outputs/figures/01_ndbi_change_distribution.png", bbox_inches="tight")
plt.close(fig)

# --- 02: budget vs mean NDBI change, both windows (n = 3, descriptive) ---------------------
budget = {"Arunachal Pradesh": 2749.74, "Uttarakhand": 270.58, "Sikkim": 188.90}
fig, ax = plt.subplots(figsize=(7, 4.6))
for df, color, label in [(full_year_core, BLUE, "Full-year window"), (summer_core, ORANGE, "Summer window")]:
    s = df.dropna(subset=["ndbi_change"]).groupby("state")["ndbi_change"].agg(["mean", "size"])
    s = s.loc[list(budget)]
    xs = [budget[k] for k in s.index]
    ax.scatter(xs, s["mean"], s=70, color=color, label=label, zorder=3)
    for st, x, y, n in zip(s.index, xs, s["mean"], s["size"]):
        ax.annotate(f"{st} (n={n})", (x, y), textcoords="offset points", xytext=(6, 4), fontsize=8, color=color)
ax.set_xscale("log")
ax.axhline(0, color="black", linewidth=0.8)
ax.set_xlabel("Sanctioned VVP-I works, ₹ crore (log scale; parliamentary record)")
ax.set_ylabel("Mean change in 500 m buffer-mean NDBI")
ax.set_title("State budget vs mean NDBI change — 3 states, descriptive only\n"
             "(Spearman ρ = +0.5 summer, −0.5 full-year: the sign flips with the window)", fontsize=10)
ax.legend(fontsize=8, loc="lower right")
fig.tight_layout()
fig.savefig("outputs/figures/02_state_change_vs_budget.png", bbox_inches="tight")
plt.close(fig)

# --- 03: H3, coloured by district, pooled and within-district rho --------------------------
with open("outputs/h3_within_district_results.json") as f:
    h3 = json.load(f)
districts = sorted(full_year_core["district"].unique())
cmap = plt.get_cmap("tab20")
dcolor = {d: cmap(i % 20) for i, d in enumerate(districts)}

fig, axes = plt.subplots(2, 2, figsize=(12, 9))
panels = [(0, 0, full_year_core, "full_year", "ndbi_change", "NDBI change — full-year"),
          (0, 1, summer_core, "summer", "ndbi_change", "NDBI change — summer"),
          (1, 0, full_year_core, "full_year", "lights_change", "Night-light change — full-year"),
          (1, 1, summer_core, "summer", "lights_change", "Night-light change — summer")]
for r, c, df, window, outcome, title in panels:
    ax = axes[r, c]
    m = df.merge(distances[["village_id", "distance_to_border_km"]], on="village_id")
    for d, g in m.groupby("district"):
        ax.scatter(g["distance_to_border_km"], g[outcome], s=14, alpha=0.8, color=dcolor[d], label=d)
    lo, hi = m[outcome].quantile([0.01, 0.99])
    pad = 0.15 * (hi - lo)
    ax.set_ylim(lo - pad, hi + pad)
    off = int(((m[outcome] < lo - pad) | (m[outcome] > hi + pad)).sum())
    res = h3[f"{window}|{outcome}|distance_to_border_km"]
    ax.text(0.02, 0.97,
            f"pooled ρ = {res['pooled_rho']:+.2f} (p = {res['pooled_p']:.1g})\n"
            f"within-district ρ = {res['within_district_rank_corr']:+.2f} (perm. p = {res['within_district_perm_p']:.2g})",
            transform=ax.transAxes, va="top", fontsize=8,
            bbox=dict(facecolor="white", alpha=0.85, edgecolor="none"))
    if off:
        ax.text(0.98, 0.03, f"{off} point(s) beyond axis", transform=ax.transAxes, ha="right", fontsize=7, color="grey")
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_title(title, fontsize=10)
    if r == 1:
        ax.set_xlabel("Distance to nearest India boundary (km, Natural Earth; not an official LAC alignment)")
axes[0, 0].set_ylabel("NDBI change")
axes[1, 0].set_ylabel("Night-light change (nW/cm²/sr)")
handles, labels = axes[0, 0].get_legend_handles_labels()
fig.legend(handles, labels, loc="center right", fontsize=8, title="District", bbox_to_anchor=(1.10, 0.5))
fig.suptitle("Border distance vs change, coloured by district. Pooled correlations largely reflect differences "
             "between districts", y=1.0, fontsize=10)
fig.tight_layout()
fig.savefig("outputs/figures/03_h3_border_distance_vs_lights.png", bbox_inches="tight")
plt.close(fig)

print("Saved 01_ndbi_change_distribution.png, 02_state_change_vs_budget.png, 03_h3_border_distance_vs_lights.png")
