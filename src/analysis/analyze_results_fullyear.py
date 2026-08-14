"""
BORDER OPTICS — Core Statistical Analysis, Full-Year Window
RQ1 (built-up change significance) + RQ2 (state-level budget correlation)

Full-year counterpart of analyze_results.py (which covers the summer-matched
window only) — kept as a separate script, mirroring the same logic against
the full-year extraction output, so both compositing-window results in the
paper's robustness check (BO_Research_Paper.md, Section 3.5 / 4.2) are each
reproducible from a script actually checked into this repo.
"""

import pandas as pd
from scipy import stats

df = pd.read_csv("data/processed/border_optics_village_results.csv")

# --- Derived change metrics ---
df["ndbi_change"] = df["ndbi_after"] - df["ndbi_before"]
df["lights_change"] = df["lights_after"] - df["lights_before"]

core = df[df["is_core_sample"] == True].copy()

print("=" * 60)
print("DESCRIPTIVE STATS — Core sample (Arunachal, Sikkim, Uttarakhand)")
print("FULL-YEAR COMPOSITE WINDOW")
print("=" * 60)
print(f"n = {len(core)} villages\n")

print("NDBI change (built-up index, after - before):")
print(core["ndbi_change"].describe())
print()
print("VIIRS night-light change (radiance, after - before):")
print(core["lights_change"].describe())
print()

print("By state:")
print(core.groupby("state")[["ndbi_change", "lights_change"]].agg(["mean", "median", "std"]))
print()

# --- RQ1 / H1: is the built-up change significantly positive? ---
print("=" * 60)
print("RQ1 / H1 — Wilcoxon signed-rank test on NDBI change (paired, before vs after)")
print("=" * 60)

valid_ndbi = core.dropna(subset=["ndbi_before", "ndbi_after"])
print(f"NDBI test run on {len(valid_ndbi)}/{len(core)} villages with valid data "
      f"(rest excluded — no cloud-free imagery in the full-year window)")
w_stat, w_p = stats.wilcoxon(valid_ndbi["ndbi_after"], valid_ndbi["ndbi_before"], alternative="greater")
print(f"Wilcoxon statistic = {w_stat:.2f}, p = {w_p:.6f}")
print("(alternative='greater' tests whether 'after' is significantly higher than 'before')")
print()

valid_lights = core.dropna(subset=["lights_before", "lights_after"])
print(f"Lights test run on {len(valid_lights)}/{len(core)} villages with valid data")
w_stat_l, w_p_l = stats.wilcoxon(valid_lights["lights_after"], valid_lights["lights_before"], alternative="greater")
print(f"Same test on VIIRS night-lights: statistic = {w_stat_l:.2f}, p = {w_p_l:.6f}")
print()

# --- RQ2: state-level change vs sanctioned budget (EXPLORATORY — n<=3 only) ---
print("=" * 60)
print("RQ2 — State-level mean NDBI change vs sanctioned VVP-I budget")
print("EXPLORATORY ONLY — n=3 states at most, not a statistically powered test")
print("=" * 60)

budget_data = {
    "Arunachal Pradesh": {"projects": 2082, "budget_cr": 2749.74},
    "Uttarakhand":        {"projects": 200,  "budget_cr": 270.58},
    "Sikkim":             {"projects": 63,   "budget_cr": 188.90},
}

state_summary = valid_ndbi.groupby("state")[["ndbi_change", "lights_change"]].mean().reset_index()
state_summary["projects"] = state_summary["state"].map(lambda s: budget_data[s]["projects"])
state_summary["budget_cr"] = state_summary["state"].map(lambda s: budget_data[s]["budget_cr"])
state_summary["n_villages_with_ndbi"] = state_summary["state"].map(valid_ndbi["state"].value_counts())

print(state_summary.to_string(index=False))
print()

if len(state_summary) >= 3:
    rho, p_val = stats.spearmanr(state_summary["budget_cr"], state_summary["ndbi_change"])
    print(f"Spearman correlation (budget vs mean NDBI change): rho = {rho:.3f}, p = {p_val:.3f}")
    print("NOTE: with only 3 states (or fewer, if data was missing for one), this p-value")
    print("is not meaningful on its own — report the direction/pattern descriptively.")
else:
    print(f"Only {len(state_summary)} state(s) have valid NDBI data — correlation not computable.")

# --- Save enriched dataset ---
df.to_csv("data/processed/border_optics_village_results_analyzed.csv", index=False)
print("\nSaved enriched dataset to data/processed/border_optics_village_results_analyzed.csv")
