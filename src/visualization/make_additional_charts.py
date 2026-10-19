"""State-level and night-light distribution figures (files 04/05/06), rebuilt in
Development Log Entry 49.

Changes from v1.7, following the forensic review:
  - titles say "NDBI" rather than "built-up area" (NDBI is a spectral proxy)
  - state charts show median AND mean with a 95% bootstrap interval for the
    median, sample size per state, and both windows, instead of bare means
  - night-light charts report medians first (the summer median change is
    negative while the mean is positive) and mark Joshimath, a block-
    headquarters town whose radiance jump alone flips the sign of the
    summer mean
Core statistical sample only (251 villages).

run from the repository root:  python src/visualization/make_additional_charts.py
"""

import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

os.makedirs("outputs/figures", exist_ok=True)
plt.rcParams.update({"figure.dpi": 150, "font.size": 10})
BLUE, ORANGE = "#4C72B0", "#DD8452"
rng = np.random.default_rng(42)

windows = {
    "Full-year": pd.read_csv("data/processed/border_optics_village_results_analyzed.csv"),
    "Summer (Jun–Sep)": pd.read_csv("data/processed/border_optics_village_results_summer_analyzed.csv"),
}
for k in windows:
    windows[k] = windows[k][windows[k]["is_core_sample"] == True]


def median_ci(x, n_boot=2000):
    x = np.asarray(x)
    boots = np.median(rng.choice(x, (n_boot, len(x)), replace=True), axis=1)
    return np.percentile(boots, [2.5, 97.5])


def state_panel(outcome, label, fname, title):
    states = ["Arunachal Pradesh", "Sikkim", "Uttarakhand"]
    fig, ax = plt.subplots(figsize=(9, 4.8))
    for j, (wname, df) in enumerate(windows.items()):
        color = BLUE if j == 0 else ORANGE
        for i, st in enumerate(states):
            v = df.loc[df.state == st, outcome].dropna()
            y = i + (0.18 if j == 0 else -0.18)
            lo, hi = median_ci(v)
            ax.plot([lo, hi], [y, y], color=color, linewidth=2)
            ax.scatter(v.median(), y, color=color, s=45, zorder=3, label=f"{wname}: median, 95% CI" if i == 0 else None)
            ax.scatter(v.mean(), y, color=color, marker="x", s=40, zorder=3, label=f"{wname}: mean" if i == 0 else None)
    ns = [int(windows["Full-year"].loc[lambda d: d.state == st, outcome].notna().sum()) for st in states]
    ax.set_yticks(range(len(states)))
    ax.set_yticklabels([f"{st}\n(n={n})" for st, n in zip(states, ns)])
    ax.axvline(0, color="black", linestyle="--", linewidth=1)
    ax.set_xlabel(label)
    ax.set_title(title, fontsize=11)
    ax.legend(fontsize=7, loc="best")
    fig.tight_layout()
    fig.savefig(f"outputs/figures/{fname}", bbox_inches="tight")
    plt.close(fig)
    print(f"Saved outputs/figures/{fname}")


state_panel("ndbi_change", "Change in 500 m buffer-mean NDBI (2025 − 2021)", "04_state_mean_ndbi_change.png",
            "NDBI change by state, both compositing windows")
state_panel("lights_change", "Change in VIIRS night-light radiance (nW/cm²/sr, 2025 − 2021)",
            "05_state_mean_lights_change.png",
            "Night-light change by state, both windows (Uttarakhand mean is pulled up by Joshimath)")

# --- 06: night-light change distribution, summer window ------------------------------------
df = windows["Summer (Jun–Sep)"]
ch = df["lights_change"].dropna()
lo, hi = ch.quantile([0.0, 0.98])
fig, ax = plt.subplots(figsize=(9, 5))
ax.hist(ch.clip(upper=hi), bins=40, color=ORANGE, edgecolor="white")
ax.axvline(0, color="black", linestyle="--", linewidth=1)
ax.axvline(ch.median(), color="#333333", linewidth=1.4)
ax.text(ch.median(), ax.get_ylim()[1] * 0.95, f" median {ch.median():+.3f}", fontsize=8, va="top")
ax.text(0.98, 0.85, f"n = {len(ch)}\nmean {ch.mean():+.3f}\n{100 * (ch < 0).mean():.0f}% of villages decline\n"
        f"{int((ch >= hi).sum())} values ≥ {hi:.2f} drawn in the last bin",
        transform=ax.transAxes, ha="right", fontsize=8)
josh = df.loc[df.village == "Joshimath", "lights_change"]
if len(josh):
    ax.annotate(f"Joshimath (town): {josh.iloc[0]:+.2f}", (hi, 1), xytext=(hi * 0.62, 8), fontsize=8,
                arrowprops=dict(arrowstyle="->", color="grey"))
ax.set_xlabel("Change in VIIRS night-light radiance, summer window (nW/cm²/sr)")
ax.set_ylabel("Number of villages")
ax.set_title("Night-light change per village, summer window", fontsize=11)
fig.tight_layout()
fig.savefig("outputs/figures/06_lights_change_distribution.png", bbox_inches="tight")
plt.close(fig)
print("Saved outputs/figures/06_lights_change_distribution.png")
