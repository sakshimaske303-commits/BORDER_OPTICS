"""
Figure 7 — horizontal dot-and-line chart, one row per test, one point per
compositing window, p-value on a log x-axis with the p=0.05 line. Points on
opposite sides of the line = not robust.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

villages = pd.read_csv("data/processed/border_optics_master_villages_with_distance.csv")
full_year = pd.read_csv("data/processed/border_optics_village_results_analyzed.csv")
summer = pd.read_csv("data/processed/border_optics_village_results_summer_analyzed.csv")

merge_cols = ["village_id", "latitude", "longitude", "distance_to_border_km"]
full_year = full_year.merge(villages[merge_cols], on="village_id", how="left")
summer = summer.merge(villages[merge_cols], on="village_id", how="left")

full_year_core = full_year[full_year["is_core_sample"] == True]
summer_core = summer[summer["is_core_sample"] == True]


def wilcoxon_p(df, before_col, after_col):
    paired = df.dropna(subset=[before_col, after_col])
    _, p = stats.wilcoxon(paired[after_col], paired[before_col], alternative="greater")
    return p, len(paired)


def spearman_p(df, col_x, col_y):
    valid = df.dropna(subset=[col_x, col_y])
    _, p = stats.spearmanr(valid[col_x], valid[col_y])
    return p, len(valid)


tests = []

p, n = wilcoxon_p(full_year_core, "ndbi_before", "ndbi_after")
tests.append(("H1 — Built-Up Change\n(NDBI, Wilcoxon)", "Full-Year", p, n))
p, n = wilcoxon_p(summer_core, "ndbi_before", "ndbi_after")
tests.append(("H1 — Built-Up Change\n(NDBI, Wilcoxon)", "Summer-Matched", p, n))

p, n = wilcoxon_p(full_year_core, "lights_before", "lights_after")
tests.append(("Night-Lights Change\n(Wilcoxon)", "Full-Year", p, n))
p, n = wilcoxon_p(summer_core, "lights_before", "lights_after")
tests.append(("Night-Lights Change\n(Wilcoxon)", "Summer-Matched", p, n))

p, n = spearman_p(full_year_core, "distance_to_border_km", "ndbi_change")
tests.append(("H3 — Border Proximity\nvs. NDBI Change (Spearman)", "Full-Year", p, n))
p, n = spearman_p(summer_core, "distance_to_border_km", "ndbi_change")
tests.append(("H3 — Border Proximity\nvs. NDBI Change (Spearman)", "Summer-Matched", p, n))

p, n = spearman_p(full_year_core, "distance_to_border_km", "lights_change")
tests.append(("H3 — Border Proximity\nvs. Lights Change (Spearman)", "Full-Year", p, n))
p, n = spearman_p(summer_core, "distance_to_border_km", "lights_change")
tests.append(("H3 — Border Proximity\nvs. Lights Change (Spearman)", "Summer-Matched", p, n))

df = pd.DataFrame(tests, columns=["test", "window", "p_value", "n"])
df["p_plot"] = df["p_value"].clip(lower=1e-7)  # avoid log(0) for p ~ 0

test_labels = df["test"].unique().tolist()
y_pos = {label: i for i, label in enumerate(test_labels)}

fig, ax = plt.subplots(figsize=(9, 5.5))

colors = {"Full-Year": "#4C72B0", "Summer-Matched": "#DD8452"}
offsets = {"Full-Year": 0.12, "Summer-Matched": -0.12}

for window in ["Full-Year", "Summer-Matched"]:
    sub = df[df["window"] == window]
    ys = [y_pos[t] + offsets[window] for t in sub["test"]]
    ax.scatter(sub["p_plot"], ys, s=90, color=colors[window], label=window, zorder=3, edgecolor="white", linewidth=0.8)

# connecting lines between the two windows per test
for t in test_labels:
    sub = df[df["test"] == t]
    fy_p = sub[sub["window"] == "Full-Year"]["p_plot"].values[0]
    sm_p = sub[sub["window"] == "Summer-Matched"]["p_plot"].values[0]
    ax.plot([fy_p, sm_p], [y_pos[t] + offsets["Full-Year"], y_pos[t] + offsets["Summer-Matched"]],
            color="#999999", linewidth=1, zorder=1, linestyle="--")

ax.axvline(0.05, color="#C44E52", linewidth=1.2, linestyle="-", zorder=2)
ax.text(0.05, len(test_labels) - 0.35, " p = 0.05", color="#C44E52", fontsize=9, va="bottom")

ax.set_xscale("log")
ax.set_yticks(list(y_pos.values()))
ax.set_yticklabels(list(y_pos.keys()))
ax.set_xlabel("p-value (log scale)")
ax.set_title("Figure 7 — Robustness Summary: Significance Across Both Compositing Windows", fontsize=12, fontweight="bold")
ax.legend(loc="lower right", frameon=True)
ax.set_ylim(-0.6, len(test_labels) - 0.4)
ax.invert_yaxis()

fig.tight_layout()
fig.savefig("outputs/figures/07_robustness_summary.png", bbox_inches="tight", dpi=150)
plt.close(fig)

print("Saved outputs/figures/07_robustness_summary.png")
print()
print(df[["test", "window", "n", "p_value"]].to_string(index=False))
