"""
Section 6.11 follow-through: reproduces the published Moran's I values as a
sanity check, then computes the spatially-corrected significance for H3
that was flagged as not done yet. Approach: calibrate a SAR(1) field to
match the observed Moran's I (k=8 NN weights), simulate a bunch of those,
and see how often a purely-spatial field correlates with border distance
as strongly as the real data does. Simplified version of Clifford et al./
Dutilleul's correction, not the closed-form formula itself.
"""

import json

import numpy as np
import pandas as pd
from scipy import stats

DISTANCES = "data/processed/border_optics_master_villages_with_distance.csv"
RESULT_FILES = {
    "full_year": "data/processed/border_optics_village_results_analyzed.csv",
    "summer": "data/processed/border_optics_village_results_summer_analyzed.csv",
}
K = 8
N_PERM_MORAN = 999
N_SIM_H3 = 2000
RNG_SEED = 42
OUT_JSON = "outputs/spatial_moran_h3_correction_results.json"


def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0088
    lat1, lon1, lat2, lon2 = map(np.radians, (lat1, lon1, lat2, lon2))
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    return 2 * R * np.arcsin(np.sqrt(a))


def load_core(window):
    distances = pd.read_csv(DISTANCES)
    results = pd.read_csv(RESULT_FILES[window]).drop(columns=["latitude", "longitude"], errors="ignore")
    merged = results.merge(
        distances[["village_id", "latitude", "longitude", "distance_to_border_km"]],
        on="village_id", how="inner",
    )
    return merged[merged["is_core_sample"] == True].reset_index(drop=True)


def build_knn_weights(lat, lon, k=K):
    n = len(lat)
    W = np.zeros((n, n))
    for i in range(n):
        d = haversine_km(lat[i], lon[i], lat, lon)
        d[i] = np.inf
        nn = np.argsort(d)[:k]
        W[i, nn] = 1.0
    row_sums = W.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1.0
    return W / row_sums


def morans_i(x, W):
    z = x - x.mean()
    num = z @ W @ z
    den = (z ** 2).sum()
    return num / den if den != 0 else np.nan


def morans_i_permutation_p(x, W, n_perm=N_PERM_MORAN, seed=RNG_SEED):
    rng = np.random.RandomState(seed)
    obs = morans_i(x, W)
    n = len(x)
    perm_vals = np.empty(n_perm)
    for i in range(n_perm):
        perm_vals[i] = morans_i(rng.permutation(x), W)
    p = (np.sum(np.abs(perm_vals) >= np.abs(obs)) + 1) / (n_perm + 1)
    return obs, p, perm_vals.mean(), perm_vals.std()


def calibrate_sar_phi(target_I, W, n, seed=RNG_SEED, draws_per_eval=60):
    # bisect on phi so simulated SAR(1) field's Moran's I matches target_I
    rng = np.random.RandomState(seed)
    I_n = np.eye(n)

    def mean_I_at(phi):
        M = np.linalg.inv(I_n - phi * W)
        vals = np.empty(draws_per_eval)
        for j in range(draws_per_eval):
            eps = rng.standard_normal(n)
            y = M @ eps
            vals[j] = morans_i(y, W)
        return vals.mean()

    lo, hi = 0.0, 0.97
    lo_val, hi_val = mean_I_at(lo), mean_I_at(hi)
    if target_I <= lo_val:
        return lo
    if target_I >= hi_val:
        return hi
    for _ in range(18):
        mid = (lo + hi) / 2
        mid_val = mean_I_at(mid)
        if mid_val < target_I:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def spatial_null_h3(window, metric):
    df = load_core(window).dropna(subset=[metric, "distance_to_border_km", "latitude", "longitude"])
    n = len(df)
    lat = df["latitude"].values
    lon = df["longitude"].values
    x = df[metric].values
    d = df["distance_to_border_km"].values

    W = build_knn_weights(lat, lon)
    obs_I, moran_p, perm_mean, perm_sd = morans_i_permutation_p(x, W)
    obs_rho, obs_p_naive = stats.spearmanr(d, x)

    phi = calibrate_sar_phi(obs_I, W, n)

    rng = np.random.RandomState(RNG_SEED + 1)
    I_n = np.eye(n)
    M = np.linalg.inv(I_n - phi * W)
    sim_rhos = np.empty(N_SIM_H3)
    sim_Is = np.empty(N_SIM_H3)
    for i in range(N_SIM_H3):
        eps = rng.standard_normal(n)
        y_sim = M @ eps
        sim_rhos[i] = stats.spearmanr(d, y_sim)[0]
        sim_Is[i] = morans_i(y_sim, W)

    p_spatial = (np.sum(np.abs(sim_rhos) >= np.abs(obs_rho)) + 1) / (N_SIM_H3 + 1)

    return {
        "window": window, "metric": metric, "n": n,
        "moran_i_observed": float(obs_I), "moran_i_permutation_p": float(moran_p),
        "moran_i_permutation_null_mean": float(perm_mean), "moran_i_permutation_null_sd": float(perm_sd),
        "spearman_rho": float(obs_rho), "naive_p": float(obs_p_naive),
        "calibrated_sar_phi": float(phi), "calibrated_sim_mean_moran_i": float(sim_Is.mean()),
        "spatially_corrected_p": float(p_spatial),
        "n_sim": N_SIM_H3,
    }


def main():
    print("=== Step 1: reproduce this study's own published Moran's I values (integrity check) ===\n")
    checks = [
        ("summer", "ndbi_change", "§6.11 claims I=0.346, p=0.001"),
        ("full_year", "lights_change", "§6.11 claims I=0.076, p=0.004"),
    ]
    reproduction = {}
    for window, metric, claim in checks:
        df = load_core(window).dropna(subset=[metric, "latitude", "longitude"])
        W = build_knn_weights(df["latitude"].values, df["longitude"].values)
        obs_I, p, pm, psd = morans_i_permutation_p(df[metric].values, W)
        print(f"{window}/{metric}  (published: {claim})")
        print(f"  Reproduced: I={obs_I:.3f}, permutation p={p:.4f}  (n={len(df)}, k=8 NN weights)\n")
        reproduction[f"{window}_{metric}"] = {"reproduced_I": obs_I, "reproduced_p": p, "published_claim": claim}

    print("=== Step 2: spatially-corrected significance for the two Holm-significant H3 results ===\n")
    combos = [
        ("summer", "ndbi_change", "H3 NDBI-proximity, summer (the new, flagged finding)"),
        ("full_year", "lights_change", "H3 lights-proximity, full-year (pre-existing Holm-significant result)"),
    ]
    corrections = {}
    for window, metric, desc in combos:
        r = spatial_null_h3(window, metric)
        print(f"--- {desc} ---")
        print(f"  n={r['n']}  observed rho={r['spearman_rho']:+.5f}  naive p={r['naive_p']:.3g}")
        print(f"  Moran's I of outcome = {r['moran_i_observed']:.4f} (permutation p={r['moran_i_permutation_p']:.4f})")
        print(f"  Calibrated SAR phi = {r['calibrated_sar_phi']:.4f} "
              f"(simulated fields' mean I = {r['calibrated_sim_mean_moran_i']:.4f}, target {r['moran_i_observed']:.4f})")
        print(f"  Spatially-corrected p (2000 spatially-autocorrelated null draws) = {r['spatially_corrected_p']:.5f}")
        print(f"  {'STILL significant' if r['spatially_corrected_p'] < 0.05 else 'NO LONGER significant'} "
              f"at alpha=0.05 after spatial correction\n")
        corrections[f"{window}_{metric}"] = r

    with open(OUT_JSON, "w") as f:
        json.dump({"moran_reproduction": reproduction, "h3_spatial_correction": corrections}, f, indent=2)
    print(f"Saved {OUT_JSON}")


if __name__ == "__main__":
    main()
