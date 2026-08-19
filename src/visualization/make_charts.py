"""
BORDER OPTICS — Core result charts
Generates the key figures for RQ1, RQ2, and H3, matching both the
full-year and summer-matched robustness-check results.
"""

import pandas as pd
import matplotlib.pyplot as plt
import os

os.makedirs("outputs/figures", exist_ok=True)

full_year = pd.read_csv("data/processed/border_optics_village_results_analyzed.csv")
summer = pd.read_csv("data/processed/border_optics_village_results_summer_analyzed.csv")
distances = pd.read_csv("data/processed/border_optics_master_villages_with_distance.csv")

full_year_core = full_year[full_year["is_core_sample"] == True]
summer_core = summer[summer["is_core_sample"] == True]

plt.rcParams.update({"figure.dpi": 150, "font.size": 10})

# --- Figure 1: NDBI change distribution, full-year vs summer-matched ---
fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), sharey=True)
axes[0].hist(full_year_core["ndbi_change"].dropna(), bins=30, color="#4C72B0", edgecolor="white")
axes[0].axvline(0, color="black", linestyle="--", linewidth=1)
axes[0].set_title("Full-year composite (2021 vs 2025)")
axes[0].set_xlabel("NDBI change (after − before)")
axes[0].set_ylabel("Number of villages")

axes[1].hist(summer_core["ndbi_change"].dropna(), bins=30, color="#DD8452", edgecolor="white")
axes[1].axvline(0, color="black", linestyle="--", linewidth=1)
axes[1].set_title("Summer-matched composite (Jun-Sep)")
axes[1].set_xlabel("NDBI change (after − before)")

fig.suptitle("Figure 1 — NDBI Change Distribution: Full-Year vs Summer-Matched Composites", y=1.03)
fig.tight_layout()
fig.savefig("outputs/figures/01_ndbi_change_distribution.png", bbox_inches="tight")
plt.close(fig)

# --- Figure 2: State-level mean NDBI change vs sanctioned budget ---
# NOTE: this must use the SUMMER-MATCHED window, not full-year. Section 4.4
# of the Research Paper reports the budget-independence finding
# (Arunachal +0.0284 vs Uttarakhand +0.0293, "nearly identical") using
# summer-matched NDBI change restricted to states with valid summer
# coverage — Sikkim has zero valid summer villages (see BO_Development_Log.md,
# Entry 5) and is excluded from that comparison. Plotting full-year data
# here previously showed a different, contradictory pattern (Arunachal
# negative, Uttarakhand strongly positive, Sikkim included) that did not
# match the text this figure sits next to.
budget_data = {
    "Arunachal Pradesh": {"projects": 2082, "budget_cr": 2749.74},
    "Uttarakhand":        {"projects": 200,  "budget_cr": 270.58},
}
summer_valid = summer_core.dropna(subset=["ndbi_change"])
state_summary = summer_valid[summer_valid["state"].isin(budget_data.keys())].groupby("state")["ndbi_change"].mean().reset_index()
state_summary["budget_cr"] = state_summary["state"].map(lambda s: budget_data[s]["budget_cr"])

fig, ax1 = plt.subplots(figsize=(7, 4.5))
ax2 = ax1.twinx()
x = range(len(state_summary))
ax1.bar([i - 0.2 for i in x], state_summary["ndbi_change"], width=0.4, color="#4C72B0", label="Mean NDBI change")
ax2.bar([i + 0.2 for i in x], state_summary["budget_cr"], width=0.4, color="#C44E52", label="Sanctioned budget (₹ cr)")
ax1.set_xticks(list(x))
ax1.set_xticklabels(state_summary["state"])
ax1.set_ylabel("Mean NDBI change")
ax2.set_ylabel("Sanctioned budget (₹ crore)")
ax1.axhline(0, color="black", linewidth=0.8)
fig.legend(loc="upper right", bbox_to_anchor=(0.9, 0.9))
ax1.set_title("Figure 2 — State-Level Built-up Change vs Sanctioned VVP-I Budget")
fig.tight_layout()
fig.savefig("outputs/figures/02_state_change_vs_budget.png", bbox_inches="tight")
plt.close(fig)

# --- Figure 3: Distance to border vs night-light change (H3), both windows ---
merged_fy = full_year.merge(distances[["village_id", "distance_to_border_km"]], on="village_id", how="inner")
merged_fy = merged_fy[merged_fy["is_core_sample"] == True]
merged_sm = summer.merge(distances[["village_id", "distance_to_border_km"]], on="village_id", how="inner")
merged_sm = merged_sm[merged_sm["is_core_sample"] == True]

fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), sharey=True)
axes[0].scatter(merged_fy["distance_to_border_km"], merged_fy["lights_change"], alpha=0.5, s=18, color="#4C72B0")
axes[0].set_title("Full-year composite")
axes[0].set_xlabel("Distance to border (km)")
axes[0].set_ylabel("Night-light change")
axes[0].axhline(0, color="black", linewidth=0.8)

axes[1].scatter(merged_sm["distance_to_border_km"], merged_sm["lights_change"], alpha=0.5, s=18, color="#DD8452")
axes[1].set_title("Summer-matched composite")
axes[1].set_xlabel("Distance to border (km)")
axes[1].axhline(0, color="black", linewidth=0.8)

fig.suptitle("Figure 3 — H3: Border Distance vs Night-Light Change (Full-Year vs Summer-Matched)", y=1.03)
fig.tight_layout()
fig.savefig("outputs/figures/03_h3_border_distance_vs_lights.png", bbox_inches="tight")
plt.close(fig)

print("Saved 3 figures to outputs/figures/")
print("  01_ndbi_change_distribution.png")
print("  02_state_change_vs_budget.png")
print("  03_h3_border_distance_vs_lights.png")