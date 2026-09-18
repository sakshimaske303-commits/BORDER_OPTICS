"""
Checks whether geocoding success (which of the officially-listed VVP-I
priority villages made it into the geocoded, core-sample dataset) correlates
with village size (population/households) or with district -- i.e. whether
the 251-village core sample is a biased subset of the 559 officially listed
priority villages across the three core states, not just an incomplete one.

Uses only files already in this repository (data/raw/*_vvp_villages.csv,
data/processed/border_optics_master_villages_with_distance.csv) -- no new
data collection. Name matching reuses select_control_villages.py's own
normalize_name() so this check is consistent with how the rest of the
pipeline already does village-name matching.

Adds one new angle (district composition) alongside the population/household
check BO_Research_Paper.md Section 6.5 already reported.

Run: python src/analysis/geocoding_selection_bias_check.py
"""

import json

import pandas as pd
from scipy import stats

MASTER_PATH = "data/processed/border_optics_master_villages_with_distance.csv"
RAW_PATHS = {
    "Arunachal Pradesh": "data/raw/arunachal_pradesh_vvp_villages.csv",
    "Sikkim": "data/raw/sikkim_vvp_villages.csv",
    "Uttarakhand": "data/raw/uttarakhand_vvp_villages.csv",
}
OUT_JSON = "outputs/geocoding_selection_bias_check.json"
OUT_CSV = "outputs/geocoding_selection_bias_district_summary.csv"


def normalize_name(name):
    # identical to select_control_villages.py's normalize_name(), duplicated
    # here rather than imported to keep this a standalone, one-file check
    import unicodedata
    name = unicodedata.normalize("NFKD", str(name)).encode("ascii", "ignore").decode()
    return " ".join(name.lower().split())


def main():
    master = pd.read_csv(MASTER_PATH)
    master_core = master[master["is_core_sample"] == True].copy()
    master_core["village_norm"] = master_core["village"].apply(normalize_name)
    geocoded_names = set(master_core["village_norm"])

    all_rows = []
    state_summary = {}
    for state, path in RAW_PATHS.items():
        df = pd.read_csv(path)
        df["village_norm"] = df["Habitation"].apply(normalize_name)
        df["state"] = state
        df["geocoded"] = df["village_norm"].isin(geocoded_names)
        n_total = len(df)
        n_geo = int(df["geocoded"].sum())
        state_summary[state] = {
            "n_official_villages": n_total,
            "n_geocoded": n_geo,
            "n_ungeocoded": n_total - n_geo,
            "geocoded_pct": round(n_geo / n_total * 100, 1),
        }
        all_rows.append(df)

    combined = pd.concat(all_rows, ignore_index=True)

    print("=== Geocoding coverage by state ===")
    for state, s in state_summary.items():
        print(f"{state}: {s['n_official_villages']} official villages, "
              f"{s['n_geocoded']} geocoded ({s['geocoded_pct']}%), {s['n_ungeocoded']} not geocoded")

    # --- Population / households check (Arunachal Pradesh only -- Sikkim and
    # Uttarakhand's raw lists don't carry these columns; this reproduces the
    # numbers already reported in Section 6.5) ---
    ap = combined[combined["state"] == "Arunachal Pradesh"].copy()
    size_results = {}
    for col in ["Population", "Households"]:
        valid = ap.dropna(subset=[col])
        geo = valid[valid["geocoded"] == True][col]
        ungeo = valid[valid["geocoded"] == False][col]
        u_stat, p = stats.mannwhitneyu(geo, ungeo, alternative="two-sided")
        size_results[col] = {
            "geocoded_mean": float(geo.mean()), "geocoded_n": int(len(geo)),
            "ungeocoded_mean": float(ungeo.mean()), "ungeocoded_n": int(len(ungeo)),
            "mannwhitney_p": float(p),
        }
        print(f"\n{col} (Arunachal Pradesh): geocoded mean={geo.mean():.1f} (n={len(geo)}), "
              f"ungeocoded mean={ungeo.mean():.1f} (n={len(ungeo)}), Mann-Whitney p={p:.5f}")

    # --- District composition check (new angle, all three core states) ---
    print("\n=== District-level geocoding rate ===")
    district_summary = combined.groupby(["state", "District"]).agg(
        total=("geocoded", "size"), geocoded=("geocoded", "sum")
    ).reset_index()
    district_summary["geocoded"] = district_summary["geocoded"].astype(int)
    district_summary["rate_pct"] = (district_summary["geocoded"] / district_summary["total"] * 100).round(1)
    print(district_summary.sort_values(["state", "total"], ascending=[True, False]).to_string(index=False))
    district_summary.to_csv(OUT_CSV, index=False)

    district_chi2 = {}
    for state in RAW_PATHS:
        sub = combined[combined["state"] == state]
        ct = pd.crosstab(sub["District"], sub["geocoded"])
        chi2, p, dof, _ = stats.chi2_contingency(ct)
        district_chi2[state] = {
            "chi2": float(chi2), "dof": int(dof), "p": float(p), "n_districts": int(len(ct)),
        }
        print(f"\n{state} district composition: chi2={chi2:.2f}, dof={dof}, p={p:.6g}, n_districts={len(ct)}")

    result = {
        "state_summary": state_summary,
        "size_check_arunachal_pradesh": size_results,
        "district_chi_square": district_chi2,
    }
    with open(OUT_JSON, "w") as f:
        json.dump(result, f, indent=2)
    print(f"\nSaved {OUT_JSON} and {OUT_CSV}")


if __name__ == "__main__":
    main()
