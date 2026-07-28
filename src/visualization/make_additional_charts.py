import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np

# ============================================================
# BORDER OPTICS — Additional Static Charts (Smoky Vintage / Tech-Noir Theme)
# ============================================================
BG = "#100E0C"
CARD = "#1B1713"
TEXT = "#EDE6DA"
TEXT_DIM = "#9C9184"
TEAL = "#2FD1C5"
BRASS = "#D9A441"
CRIMSON = "#B23A48"
COPPER = "#B9863F"

plt.rcParams.update({
    "figure.facecolor": BG,
    "axes.facecolor": CARD,
    "axes.edgecolor": TEXT_DIM,
    "axes.labelcolor": TEXT,
    "text.color": TEXT,
    "xtick.color": TEXT_DIM,
    "ytick.color": TEXT_DIM,
    "font.family": "sans-serif",
    "grid.color": "#2A241E",
    "grid.alpha": 0.4,
})

# ============================================================
# LOAD DATA
# ============================================================
villages = pd.read_csv("data/processed/border_optics_master_villages_with_distance.csv")
summer = pd.read_csv("data/processed/border_optics_village_results_summer_analyzed.csv")

merge_cols = ["village_id", "latitude", "longitude", "distance_to_border_km"]
summer = summer.merge(villages[merge_cols], on="village_id", how="left")

valid = summer.dropna(subset=["ndbi_change"])

# ============================================================
# CHART 04 — STATE-WISE MEAN NDBI CHANGE
# ============================================================
state_ndbi = valid.groupby("state")["ndbi_change"].mean().sort_values()

fig, ax = plt.subplots(figsize=(9, 5.5))
bars = ax.barh(state_ndbi.index, state_ndbi.values, color=TEAL, edgecolor=BG, height=0.6)
ax.set_xlabel("Mean NDBI Change")
ax.set_title("State-Wise Mean Built-Up Area Change (Summer-Matched)", fontsize=13, fontweight="bold", color=TEXT, pad=15)
ax.axvline(0, color=TEXT_DIM, linewidth=1, linestyle="--")
for bar, val in zip(bars, state_ndbi.values):
    ax.text(val + (0.002 if val >= 0 else -0.002), bar.get_y() + bar.get_height() / 2,
            f"{val:.4f}", va="center", ha="left" if val >= 0 else "right", color=TEXT, fontsize=9, fontweight="bold")
plt.tight_layout()
plt.savefig("outputs/figures/04_state_mean_ndbi_change.png", dpi=200, facecolor=BG)
plt.close()
print("Saved outputs/figures/04_state_mean_ndbi_change.png")

# ============================================================
# CHART 05 — STATE-WISE MEAN LIGHTS CHANGE
# ============================================================
valid_lights = summer.dropna(subset=["lights_change"])
state_lights = valid_lights.groupby("state")["lights_change"].mean().sort_values()

fig, ax = plt.subplots(figsize=(9, 5.5))
bars = ax.barh(state_lights.index, state_lights.values, color=BRASS, edgecolor=BG, height=0.6)
ax.set_xlabel("Mean Night-Lights Change")
ax.set_title("State-Wise Mean Night-Lights Change (Summer-Matched)", fontsize=13, fontweight="bold", color=TEXT, pad=15)
ax.axvline(0, color=TEXT_DIM, linewidth=1, linestyle="--")
for bar, val in zip(bars, state_lights.values):
    ax.text(val + (0.002 if val >= 0 else -0.002), bar.get_y() + bar.get_height() / 2,
            f"{val:.4f}", va="center", ha="left" if val >= 0 else "right", color=TEXT, fontsize=9, fontweight="bold")
plt.tight_layout()
plt.savefig("outputs/figures/05_state_mean_lights_change.png", dpi=200, facecolor=BG)
plt.close()
print("Saved outputs/figures/05_state_mean_lights_change.png")

# ============================================================
# CHART 06 — NIGHT-LIGHTS CHANGE DISTRIBUTION
# ============================================================
fig, ax = plt.subplots(figsize=(9, 5.5))
ax.hist(valid_lights["lights_change"], bins=20, color=COPPER, edgecolor=BG)
ax.set_xlabel("Lights Change")
ax.set_ylabel("Number of Villages")
ax.set_title("Distribution of Night-Lights Change (Summer-Matched)", fontsize=13, fontweight="bold", color=TEXT, pad=15)
ax.axvline(0, color=TEXT_DIM, linewidth=1, linestyle="--")
plt.tight_layout()
plt.savefig("outputs/figures/06_lights_change_distribution.png", dpi=200, facecolor=BG)
plt.close()
print("Saved outputs/figures/06_lights_change_distribution.png")