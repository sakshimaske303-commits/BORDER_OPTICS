import json

import numpy as np
import pandas as pd
from scipy import stats

DISTANCES = "data/processed/border_optics_master_villages_with_distance.csv"
RESULT_FILES = {
    "full_year": "data/processed/border_optics_village_results_analyzed.csv",
    "summer": "data/processed/border_optics_village_results_summer_analyzed.csv",
}
N_PERMUTATIONS = 2000
RNG_SEED = 42
OUT_JSON = "outputs/h3_robustness_results.json"


def load_merged(window):
    distances = pd.read_csv(DISTANCES)
    results = pd.read_csv(RESULT_FILES[window])
    merged = results.merge(
        distances[["village_id", "distance_to_border_km"]], on="village_id", how="inner"
    )
    return merged[merged["is_core_sample"] == True]


def full_sample_rho(window, metric):
    df = load_merged(window).dropna(subset=[metric, "distance_to_border_km"])
    rho, p = stats.spearmanr(df["distance_to_border_km"], df[metric])
    return rho, p, len(df)


def leave_one_district_out(window, metric, full_rho):
    df = load_merged(window)
    districts = sorted(df["district"].unique())
    rows = []
    for d in districts:
        sub = df[df["district"] != d].dropna(subset=[metric, "distance_to_border_km"])
        rho, p = stats.spearmanr(sub["distance_to_border_km"], sub[metric])
        rows.append({
            "dropped_district": d, "n": len(sub), "rho": float(rho), "p": float(p),
            "significant": bool(p < 0.05),
            "same_sign_as_full_sample": bool(np.sign(rho) == np.sign(full_rho)),
        })
    n_sig = sum(r["significant"] for r in rows)
    n_same_sign = sum(r["same_sign_as_full_sample"] for r in rows)
    rhos = [r["rho"] for r in rows]
    return {
        "rows": rows, "n_significant_of_14": n_sig, "n_same_sign_of_14": n_same_sign,
        "rho_min": min(rhos), "rho_max": max(rhos),
    }


def randomization_inference(window, metric, full_rho):
    # permutation test on the correlation - shuffle one var, see how extreme
    # observed rho is. No treatment label here to reassign like H1/H4, so
    # this is just "could this rho happen from an unstructured shuffle."
    df = load_merged(window).dropna(subset=[metric, "distance_to_border_km"])
    x = df["distance_to_border_km"].values
    y = df[metric].values
    rng = np.random.RandomState(RNG_SEED)
    perm_rhos = np.empty(N_PERMUTATIONS)
    for i in range(N_PERMUTATIONS):
        perm_rhos[i] = stats.spearmanr(x, rng.permutation(y))[0]
    p_perm = (np.sum(np.abs(perm_rhos) >= np.abs(full_rho)) + 1) / (N_PERMUTATIONS + 1)
    return {
        "n_permutations": N_PERMUTATIONS, "perm_rho_mean": float(perm_rhos.mean()),
        "perm_rho_sd": float(perm_rhos.std()), "p_randomization": float(p_perm),
    }


def main():
    combos = [
        ("summer", "ndbi_change", "H3 NDBI-proximity, summer window (the flagged, unstressed finding)"),
        ("full_year", "lights_change", "H3 lights-proximity, full-year window (Holm-significant, NOT previously flagged for this check)"),
        ("full_year", "ndbi_change", "H3 NDBI-proximity, full-year window (already null -- checked anyway, for completeness)"),
        ("summer", "lights_change", "H3 lights-proximity, summer window (already null -- checked anyway, for completeness)"),
    ]

    all_results = {}
    for window, metric, description in combos:
        key = f"{window}_{metric}"
        rho, p, n = full_sample_rho(window, metric)
        print("=" * 78)
        print(description)
        print(f"Full sample: n={n}  rho={rho:+.5f}  p={p:.6g}")
        print("=" * 78)

        loo = leave_one_district_out(window, metric, rho)
        print(f"  Leave-one-district-out: rho range [{loo['rho_min']:+.5f}, {loo['rho_max']:+.5f}], "
              f"significant (p<0.05) in {loo['n_significant_of_14']}/14 reruns, "
              f"same sign as full sample in {loo['n_same_sign_of_14']}/14")

        rand = randomization_inference(window, metric, rho)
        print(f"  Randomization inference ({rand['n_permutations']} shuffles): "
              f"permutation rho mean={rand['perm_rho_mean']:+.5f} SD={rand['perm_rho_sd']:.5f} | "
              f"randomization-inference p={rand['p_randomization']:.6g}")
        print()

        all_results[key] = {
            "description": description, "full_sample": {"rho": rho, "p": p, "n": n},
            "leave_one_district_out": loo, "randomization_inference": rand,
        }

    with open(OUT_JSON, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"Saved {OUT_JSON}")


if __name__ == "__main__":
    main()
