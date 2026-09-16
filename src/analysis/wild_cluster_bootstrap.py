"""
Wild cluster bootstrap for the H4 DiD results (14 clusters is too few for
normal asymptotics). Did OLS + cluster-robust SE by hand since statsmodels
wouldn't install here - checked it matches did_model.py's numbers first.
Full enumeration of all 2**14=16384 sign flips (exact, not Monte Carlo,
since that's small enough to just do directly).
"""

import itertools
import json

import numpy as np
import pandas as pd

PANEL_PATHS = {
    "full_year": "data/processed/border_optics_did_panel_fullyear.csv",
    "summer": "data/processed/border_optics_did_panel_summer.csv",
}
OUT_JSON = "outputs/wild_cluster_bootstrap_results.json"


def manual_ols(y, X):
    XtX_inv = np.linalg.inv(X.T @ X)
    beta = XtX_inv @ X.T @ y
    resid = y - X @ beta
    fitted = X @ beta
    return beta, resid, fitted, XtX_inv


def cluster_robust_se(X, resid, clusters, XtX_inv):
    groups = pd.unique(clusters)
    G = len(groups)
    N, K = X.shape
    B = np.zeros((K, K))
    for g in groups:
        idx = clusters == g
        Xg = X[idx]
        ug = resid[idx]
        score = Xg.T @ ug
        B += np.outer(score, score)
    corr = (G / (G - 1)) * ((N - 1) / (N - K))
    V = XtX_inv @ (corr * B) @ XtX_inv
    return np.sqrt(np.diag(V))


def build_design(df, outcome):
    valid = df.dropna(subset=[outcome]).copy()
    y = valid[outcome].values.astype(float)
    district_dummies = pd.get_dummies(valid["district"], drop_first=True, prefix="district")
    X_full = pd.concat([
        pd.Series(1.0, index=valid.index, name="const"),
        valid[["treatment", "post", "did_term"]],
        district_dummies,
    ], axis=1).astype(float)
    cols = list(X_full.columns)
    X_restricted = X_full.drop(columns=["did_term"]).values
    clusters = valid["district"].values
    return y, X_full.values, cols, X_restricted, clusters


def wild_cluster_bootstrap(outcome, window):
    df = pd.read_csv(PANEL_PATHS[window])
    y, X_full, cols, X_restricted, clusters = build_design(df, outcome)
    did_idx = cols.index("did_term")

    beta_real, resid_real, _, XtX_inv_real = manual_ols(y, X_full)
    se_real = cluster_robust_se(X_full, resid_real, clusters, XtX_inv_real)
    real_coef = beta_real[did_idx]
    real_se = se_real[did_idx]
    real_t = real_coef / real_se

    beta_res, resid_res, fitted_res, _ = manual_ols(y, X_restricted)

    unique_districts = sorted(pd.unique(clusters))
    n_clusters = len(unique_districts)
    district_idx = {d: i for i, d in enumerate(unique_districts)}
    row_cluster_idx = np.array([district_idx[d] for d in clusters])

    n_combos = 2 ** n_clusters
    print(f"\n--- Wild cluster bootstrap, {outcome.upper()}, window={window} ---")
    print(f"n_obs={len(y)}  n_clusters={n_clusters}  full enumeration = {n_combos} sign combinations")
    print(f"Real fit: did_term={real_coef:+.5f}  cluster-robust SE={real_se:.5f}  t={real_t:+.3f}")

    boot_t = []
    for combo in itertools.product([-1, 1], repeat=n_clusters):
        signs = np.array(combo)[row_cluster_idx]
        y_star = fitted_res + signs * resid_res
        beta_b, resid_b, _, XtXinv_b = manual_ols(y_star, X_full)
        se_b = cluster_robust_se(X_full, resid_b, clusters, XtXinv_b)[did_idx]
        if se_b <= 0 or not np.isfinite(se_b):
            continue
        boot_t.append(beta_b[did_idx] / se_b)
    boot_t = np.array(boot_t)

    p_wcb = np.mean(np.abs(boot_t) >= np.abs(real_t))

    print(f"Wild-cluster-bootstrap p-value (full enumeration, {len(boot_t)}/{n_combos} valid draws) = {p_wcb:.5f}")
    print(f"  bootstrap t distribution: mean={boot_t.mean():+.3f}  SD={boot_t.std():.3f}  "
          f"[{np.percentile(boot_t, 2.5):+.3f}, {np.percentile(boot_t, 97.5):+.3f}]")

    return {
        "outcome": outcome, "window": window, "n_obs": len(y), "n_clusters": n_clusters,
        "real_did_coef": float(real_coef), "real_cluster_se": float(real_se), "real_t": float(real_t),
        "n_bootstrap_draws": int(len(boot_t)), "n_combinations_total": n_combos,
        "wild_cluster_bootstrap_p": float(p_wcb),
        "boot_t_mean": float(boot_t.mean()), "boot_t_sd": float(boot_t.std()),
    }


def main():
    all_results = []
    for window in ["full_year", "summer"]:
        for outcome in ["ndbi", "lights"]:
            all_results.append(wild_cluster_bootstrap(outcome, window))

    with open(OUT_JSON, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\nSaved {OUT_JSON}")


if __name__ == "__main__":
    main()
