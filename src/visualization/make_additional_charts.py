"""Figures 4-6 (paper numbering) -- files are 04/05/06, same light style as
everything else (01_ndbi_change_distribution.png etc.), not the dashboard's
dark theme. Run after make_charts.py."""

import os

import pandas as pd
import matplotlib.pyplot as plt

os.makedirs("outputs/figures", exist_ok=True)
plt.rcParams.update({"figure.dpi": 150, "font.size": 10})

BLUE = "#4C72B0"
ORANGE = "#DD8452"

villages = pd.read_csv("data/processed/border_optics_master_villages_with_distance.csv")
summer = pd.read_csv("data/processed/border_optics_village_results_summer_analyzed.csv")

merge_cols = ["village_id", "latitude", "longitude", "distance_to_border_km", "is_core_sample"]
summer = summer.merge(villages[merge_cols], on="village_id", how="left")

# Core statistical sample only (251 villages) -- matches the filter pages/6_Explore_Trends.py
# already applies. Without this, the 7 illustrative Himachal villages can leak into these
# static state-wise figures even though the dashboard's own state comparison excludes them.
summer = summer[summer["is_core_sample"] == True]

valid = summer.dropna(subset=["ndbi_change"])

# ============================================================
# CHART 04 -- STATE-WISE MEAN NDBI CHANGE
# ============================================================
state_ndbi = valid.groupby("state")["ndbi_change"].mean().sort_values()

fig, ax = plt.subplots(figsize=(9, 5.5))
bars = ax.barh(state_ndbi.index, state_ndbi.values, color=BLUE, edgecolor="white", height=0.6)
ax.margins(x=0.2)
ax.set_xlabel("Mean NDBI Change")
ax.set_title("State-Wise Mean Built-Up Area Change (Summer-Matched)", fontsize=13, fontweight="bold", pad=15)
ax.axvline(0, color="black", linewidth=1, linestyle="--")
for bar, val in zip(bars, state_ndbi.values):
    ax.text(val + (0.002 if val >= 0 else -0.002), bar.get_y() + bar.get_height() / 2,
            f"{val:.4f}", va="center", ha="left" if val >= 0 else "right", fontsize=9, fontweight="bold")
plt.tight_layout()
plt.savefig("outputs/figures/04_state_mean_ndbi_change.png", bbox_inches="tight")
plt.close()
print("Saved outputs/figures/04_state_mean_ndbi_change.png")

# ============================================================
# CHART 05 -- STATE-WISE MEAN LIGHTS CHANGE
# ============================================================
valid_lights = summer.dropna(subset=["lights_change"])
state_lights = valid_lights.groupby("state")["lights_change"].mean().sort_values()

fig, ax = plt.subplots(figsize=(9, 5.5))
bars = ax.barh(state_lights.index, state_lights.values, color=ORANGE, edgecolor="white", height=0.6)
ax.margins(x=0.2)
ax.set_xlabel("Mean Night-Lights Change")
ax.set_title("State-Wise Mean Night-Lights Change (Summer-Matched)", fontsize=13, fontweight="bold", pad=15)
ax.axvline(0, color="black", linewidth=1, linestyle="--")
for bar, val in zip(bars, state_lights.values):
    ax.text(val + (0.002 if val >= 0 else -0.002), bar.get_y() + bar.get_height() / 2,
            f"{val:.4f}", va="center", ha="left" if val >= 0 else "right", fontsize=9, fontweight="bold")
plt.tight_layout()
plt.savefig("outputs/figures/05_state_mean_lights_change.png", bbox_inches="tight")
plt.close()
print("Saved outputs/figures/05_state_mean_lights_change.png")

# ============================================================
# CHART 06 -- NIGHT-LIGHTS CHANGE DISTRIBUTION
# ============================================================
fig, ax = plt.subplots(figsize=(9, 5.5))
ax.hist(valid_lights["lights_change"], bins=20, color=ORANGE, edgecolor="white")
ax.set_xlabel("Lights Change")
ax.set_ylabel("Number of Villages")
ax.set_title("Distribution of Night-Lights Change (Summer-Matched)", fontsize=13, fontweight="bold", pad=15)
ax.axvline(0, color="black", linewidth=1, linestyle="--")
plt.tight_layout()
plt.savefig("outputs/figures/06_lights_change_distribution.png", bbox_inches="tight")
plt.close()
print("Saved outputs/figures/06_lights_change_distribution.png")
