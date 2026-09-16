"""
Figures 7-9 (paper calls them 7/8/9, files are named 08/09/10 -- don't get confused).
Run did_model.py, multiyear_trend.py, buffer_sensitivity.py first.
"""

import json
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

os.makedirs("outputs/figures", exist_ok=True)
plt.rcParams.update({"figure.dpi": 150, "font.size": 10})

BLUE = "#4C72B0"
ORANGE = "#DD8452"
RED = "#C44E52"
GREEN = "#55A868"

# ============================================================
# FIGURE 8 — Control-group DiD: treated-vs-control effect, both windows
# ============================================================
with open("data/processed/border_optics_did_summary_fullyear.json") as f:
    did_fy = json.load(f)
with open("data/processed/border_optics_did_summary_summer.json") as f:
    did_sm = json.load(f)

rows = []
for window_label, data in [("Full-Year", did_fy), ("Summer-Matched", did_sm)]:
    for r in data["did"]:
        rows.append({
            "outcome": "NDBI" if r["outcome"] == "ndbi" else "Night-Lights",
            "window": window_label,
            "coef": r["did_coef"], "ci_lo": r["did_ci_lo"], "ci_hi": r["did_ci_hi"],
            "p": r["did_p"],
        })
did_df = pd.DataFrame(rows)

fig, ax = plt.subplots(figsize=(8, 4.5))
labels = [f"{r.outcome}\n({r.window})" for r in did_df.itertuples()]
y = np.arange(len(did_df))
colors = [BLUE if w == "Full-Year" else ORANGE for w in did_df["window"]]
ax.errorbar(
    did_df["coef"], y,
    xerr=[did_df["coef"] - did_df["ci_lo"], did_df["ci_hi"] - did_df["coef"]],
    fmt="o", color="black", ecolor="gray", elinewidth=1.5, capsize=4, zorder=2,
)
for yi, row, c in zip(y, did_df.itertuples(), colors):
    ax.scatter(row.coef, yi, color=c, s=90, zorder=3, edgecolor="white", linewidth=0.8)
    sig = "*" if row.p < 0.05 else ""
    ax.text(row.ci_hi + (0.002 if row.coef >= 0 else -0.002), yi,
            f"p={row.p:.4f}{sig}", va="center", fontsize=8.5)

ax.axvline(0, color="black", linewidth=1, linestyle="--")
ax.set_yticks(list(y))
ax.set_yticklabels(labels)
ax.invert_yaxis()
ax.set_xlabel("DiD coefficient (treated-vs-control gap in change, district fixed effects, cluster-robust SE)")
ax.set_title("Figure 7 — Control-Group DiD: Treated-vs-Control Effect, Both Windows", fontsize=12, fontweight="bold")
fig.tight_layout()
fig.savefig("outputs/figures/08_control_group_did_effect.png", bbox_inches="tight")
plt.close(fig)
print("Saved outputs/figures/08_control_group_did_effect.png")

# ============================================================
# FIGURE 9 — Multi-year trend (2021/2023/2025), both windows, NDBI + Lights
# ============================================================
my_fy = pd.read_csv("data/processed/border_optics_multiyear_fullyear.csv")
my_sm = pd.read_csv("data/processed/border_optics_multiyear_summer.csv")
my_fy_core = my_fy[my_fy["is_core_sample"] == True]
my_sm_core = my_sm[my_sm["is_core_sample"] == True]
YEARS = [2021, 2023, 2025]

fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))

for outcome, ax, ylabel in [("ndbi", axes[0], "Mean NDBI"), ("lights", axes[1], "Mean night-lights radiance")]:
    for label, df, color in [("Full-Year", my_fy_core, BLUE), ("Summer-Matched", my_sm_core, ORANGE)]:
        means = [df[f"{outcome}_{yr}"].mean() for yr in YEARS]
        sems = [df[f"{outcome}_{yr}"].std() / np.sqrt(df[f"{outcome}_{yr}"].count()) for yr in YEARS]
        ax.errorbar(YEARS, means, yerr=sems, marker="o", capsize=4, label=label, color=color, linewidth=2)
    ax.set_xticks(YEARS)
    ax.set_xlabel("Year")
    ax.set_ylabel(ylabel)
    ax.set_title(f"{'NDBI' if outcome == 'ndbi' else 'Night-lights'} — mean ± SE, core sample (n=251)")

axes[0].legend(loc="best", fontsize=9)
fig.suptitle("Figure 8 — Three-Point Trend (2021 / 2023 / 2025), Both Compositing Windows", y=1.03, fontsize=12, fontweight="bold")
fig.tight_layout()
fig.savefig("outputs/figures/09_multiyear_trend.png", bbox_inches="tight")
plt.close(fig)
print("Saved outputs/figures/09_multiyear_trend.png")

# ============================================================
# FIGURE 10 — Buffer-radius sensitivity (250m / 500m / 1km), summer window
# all radii pulled same day now (n=251 everywhere) so it's one bar per
# radius, not the old as-extracted/matched-subsample pair
# ============================================================
with open("data/processed/border_optics_buffer_sensitivity_summary.json") as f:
    buf = json.load(f)

ndbi_p = {r["buffer_m"]: r["ndbi_wilcoxon_p"] for r in buf["as_extracted"]}
ndbi_mean_change = {r["buffer_m"]: r["ndbi_mean_change"] for r in buf["as_extracted"]}
buffers = [250, 500, 1000]

fig, ax = plt.subplots(figsize=(8, 4.5))
x = np.arange(len(buffers))
bar_colors = [BLUE if ndbi_mean_change[b] >= 0 else ORANGE for b in buffers]
bars = ax.bar(x, [max(ndbi_p[b], 1e-7) for b in buffers], width=0.5,
              color=bar_colors, edgecolor="black")
for xi, b in zip(x, buffers):
    ax.text(xi, max(ndbi_p[b], 1e-7) * 1.15, f"p={ndbi_p[b]:.4f}\n(mean chg {ndbi_mean_change[b]:+.5f})",
            ha="center", va="bottom", fontsize=8)
ax.set_yscale("log")
ax.axhline(0.05, color=RED, linewidth=1.2, linestyle="-")
ax.text(len(buffers) - 0.5, 0.05, " p = 0.05", color=RED, fontsize=9, va="bottom")
ax.set_xticks(list(x))
ax.set_xticklabels([f"{b}m" for b in buffers])
ax.set_xlabel("Buffer radius")
ax.set_ylabel("NDBI Wilcoxon p-value (log scale)")
ax.set_ylim(top=3)
ax.set_title("Figure 9 — Buffer-Radius Sensitivity: NDBI Significance, Summer Window\n"
             "(all three radii pulled the same day, n=251 at every radius)", fontsize=11, fontweight="bold")
fig.tight_layout()
fig.savefig("outputs/figures/10_buffer_sensitivity.png", bbox_inches="tight")
plt.close(fig)
print("Saved outputs/figures/10_buffer_sensitivity.png")
