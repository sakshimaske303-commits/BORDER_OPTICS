"""
H3 decomposition: is the border-proximity correlation a within-district
relationship, or only a between-district one? (Development Log Entry 49.)

The earlier H3 checks (leave-one-district-out, outcome-shuffling
randomization inference, k=8 nearest-neighbour spatial correction) all leave
the district structure intact or ignore it, so none of them can tell a
genuine proximity gradient apart from "districts that sit closer to the
border happened to change differently". This script separates the two:

  pooled          Spearman rho across all 251 core villages (as reported before)
  within-district stratified Spearman: villages ranked inside their own
                  district, ranks centred per district, then correlated,
                  with a permutation p-value that shuffles distance only
                  *inside* districts (2,000 draws, seed 42)
  district FE     OLS of rank(change) on rank(distance) + district dummies,
                  cluster-robust SE by district, t(13) p-value
  between         Spearman rho of the 14 district means (n = 14)

Run for both distance definitions: distance_to_border_km (nearest India
boundary of any kind, as before) and distance_to_china_km (China/LAC only;
from compute_lac_distance.py).

run:  python src/analysis/h3_within_district.py
out:  outputs/h3_within_district_results.json
"""

import json

import numpy as np
import pandas as pd
from scipy import stats

WINDOW_PATHS = {
    "full_year": "data/processed/border_optics_village_results_analyzed.csv",
    "summer": "data/processed/border_optics_village_results_summer_analyzed.csv",
}
LAC_PATH = "data/processed/border_optics_lac_distance.csv"
OUT_PATH = "outputs/h3_within_district_results.json"
N_PERM = 2000
SEED = 42


def demeaned_ranks(df, col):
    # stratified Spearman: rank inside each district, then centre each district's ranks
    r = df.groupby("district")[col].rank()
    return r - r.groupby(df["district"]).transform("mean")


def within_corr(df, x, y):
    rx, ry = demeaned_ranks(df, x), demeaned_ranks(df, y)
    return float(np.corrcoef(rx, ry)[0, 1])


def within_perm_p(df, x, y, observed, rng):
    exceed = 0
    groups = [idx.to_numpy() for _, idx in df.groupby("district").groups.items()]
    xs = df[x].to_numpy()
    for _ in range(N_PERM):
        shuffled = xs.copy()
        for idx in groups:
            pos = df.index.get_indexer(idx)
            shuffled[pos] = rng.permutation(shuffled[pos])
        tmp = df.assign(_x=shuffled)
        if abs(within_corr(tmp, "_x", y)) >= abs(observed):
            exceed += 1
    return (exceed + 1) / (N_PERM + 1)


def fe_rank_regression(df, x, y):
    d = df.assign(rx=df[x].rank(), ry=df[y].rank())
    X = np.column_stack([np.ones(len(d)), d["rx"], pd.get_dummies(d["district"], drop_first=True).astype(float)])
    Y = d["ry"].to_numpy()
    XtXi = np.linalg.pinv(X.T @ X)
    b = XtXi @ X.T @ Y
    e = Y - X @ b
    g = d["district"].to_numpy()
    G, (n, k) = len(np.unique(g)), X.shape
    meat = np.zeros((k, k))
    for gg in np.unique(g):
        s = X[g == gg].T @ e[g == gg]
        meat += np.outer(s, s)
    V = XtXi @ meat @ XtXi * (G / (G - 1)) * ((n - 1) / (n - k))
    se = float(np.sqrt(V[1, 1]))
    return float(b[1]), se, float(2 * stats.t.sf(abs(b[1] / se), G - 1))


def main():
    lac = pd.read_csv(LAC_PATH)
    lac = lac[lac.group == "treated"][["village_id", "distance_to_border_km", "distance_to_china_km"]]
    rng = np.random.default_rng(SEED)
    results = {}
    for window, path in WINDOW_PATHS.items():
        d = pd.read_csv(path)
        d = d[d["is_core_sample"] == True].merge(lac, on="village_id", how="left").reset_index(drop=True)
        d["ndbi_change"] = d["ndbi_after"] - d["ndbi_before"]
        d["lights_change"] = d["lights_after"] - d["lights_before"]
        for outcome in ["ndbi_change", "lights_change"]:
            for dist in ["distance_to_border_km", "distance_to_china_km"]:
                v = d.dropna(subset=[outcome, dist]).reset_index(drop=True)
                pooled = stats.spearmanr(v[dist], v[outcome])
                w = within_corr(v, dist, outcome)
                w_p = within_perm_p(v, dist, outcome, w, rng)
                b, se, fe_p = fe_rank_regression(v, dist, outcome)
                means = v.groupby("district")[[dist, outcome]].mean()
                between = stats.spearmanr(means[dist], means[outcome])
                per_district = {
                    k: round(float(stats.spearmanr(g[dist], g[outcome]).statistic), 3)
                    for k, g in v.groupby("district") if len(g) >= 8
                }
                key = f"{window}|{outcome}|{dist}"
                results[key] = {
                    "n": int(len(v)), "n_districts": int(v["district"].nunique()),
                    "pooled_rho": float(pooled.statistic), "pooled_p": float(pooled.pvalue),
                    "within_district_rank_corr": w, "within_district_perm_p": w_p,
                    "district_fe_rank_slope": b, "district_fe_se": se, "district_fe_p_t13": fe_p,
                    "between_district_rho_n14": float(between.statistic), "between_district_p": float(between.pvalue),
                    "per_district_rho_n_ge_8": per_district,
                }
                print(f"{window:9s} {outcome:13s} {dist:22s} pooled rho={pooled.statistic:+.3f} (p={pooled.pvalue:.2g}) | "
                      f"within={w:+.3f} (perm p={w_p:.4f}) | FE slope={b:+.3f} (p={fe_p:.3f}) | "
                      f"between(n=14) rho={between.statistic:+.3f} (p={between.pvalue:.3f})")
    with open(OUT_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved {OUT_PATH}")


if __name__ == "__main__":
    main()
