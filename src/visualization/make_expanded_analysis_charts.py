"""
BORDER OPTICS — Figures 8-10: control-group DiD, multi-year trend, buffer
sensitivity. Matches the light academic style of Figures 1/3/7.
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
ax.set_title("Figure 8 — Control-Group DiD: Treated-vs-Control Effect, Both Windows", fontsize=12, fontweight="bold")
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
fig.suptitle("Figure 9 — Three-Point Trend (2021 / 2023 / 2025), Both Compositing Windows", y=1.03, fontsize=12, fontweight="bold")
fig.tight_layout()
fig.savefig("outputs/figures/09_multiyear_trend.png", bbox_inches="tight")
plt.close(fig)
print("Saved outputs/figures/09_multiyear_trend.png")

# ============================================================
# FIGURE 10 — Buffer-radius sensitivity (250m / 500m / 1km), summer window
# ============================================================
with open("data/processed/border_optics_buffer_sensitivity_summary.json") as f:
    buf = json.load(f)

as_extracted = {r["buffer_m"]: r["ndbi_wilcoxon_p"] for r in buf["as_extracted"]}
matched = {r["buffer_m"]: r["wilcoxon_p"] for r in buf["matched_subsample"]}
buffers = [250, 500, 1000]

fig, ax = plt.subplots(figsize=(8, 4.5))
x = np.arange(len(buffers))
width = 0.35
bars1 = ax.bar(x - width / 2, [max(as_extracted[b], 1e-7) for b in buffers], width,
               label="As extracted (varying n, archive-timing confounded)", color="#B0B0B0", edgecolor="black")
bars2 = ax.bar(x + width / 2, [max(matched[b], 1e-7) for b in buffers], width,
               label="Matched subsample (n=154, buffer radius isolated)", color=GREEN, edgecolor="black")
ax.set_yscale("log")
ax.axhline(0.05, color=RED, linewidth=1.2, linestyle="-")
ax.text(len(buffers) - 0.5, 0.05, " p = 0.05", color=RED, fontsize=9, va="bottom")
ax.set_xticks(list(x))
ax.set_xticklabels([f"{b}m" for b in buffers])
ax.set_xlabel("Buffer radius")
ax.set_ylabel("NDBI Wilcoxon p-value (log scale)")
ax.set_title("Figure 10 — Buffer-Radius Sensitivity: NDBI Significance, Summer Window", fontsize=12, fontweight="bold")
ax.legend(loc="upper left", fontsize=8.5, frameon=True)
fig.tight_layout()
fig.savefig("outputs/figures/10_buffer_sensitivity.png", bbox_inches="tight")
plt.close(fig)
print("Saved outputs/figures/10_buffer_sensitivity.png")
