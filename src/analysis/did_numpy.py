"""
Shared NumPy implementation of the H4 DiD used by the Entry 49 follow-up
scripts (so they run without statsmodels).

Same specification as did_model.py:
    y ~ treatment + post + treatment:post + C(district)
cluster-robust (CR1) SE by district, identical small-sample factor
G/(G-1) * (N-1)/(N-K). Verified to reproduce did_model.py's committed
coefficients, SEs and p-values (border_optics_did_summary_*.json) to at least
5 decimals for all four outcome/window combinations.

Two p-values are returned: p_z (normal reference, what statsmodels reports
by default and what the paper quoted up to v1.7) and p_t (t with G-1 = 13
degrees of freedom, the more appropriate small-cluster reference and the
one the power analysis already used). Also: exact wild cluster bootstrap
(Rademacher, restricted/null-imposed, full enumeration of 2**G sign vectors),
the same algorithm as wild_cluster_bootstrap.py.
"""

import itertools

import numpy as np
import pandas as pd
from scipy import stats


def long_panel(treated, control, before_col, after_col, complete_cases=True):
    """Stack treated/control village rows into a 2-period panel with columns y, district, treatment, post."""
    rows = []
    for tr, df in [(1, treated), (0, control)]:
        df = df.copy()
        if complete_cases:
            df = df.dropna(subset=[before_col, after_col])
        for post, col in [(0, before_col), (1, after_col)]:
            part = df[["district", col]].rename(columns={col: "y"})
            part["treatment"], part["post"] = tr, post
            rows.append(part)
    panel = pd.concat(rows, ignore_index=True).dropna(subset=["y"])
    panel["did"] = panel["treatment"] * panel["post"]
    return panel.reset_index(drop=True)


def _design(panel, include_did=True):
    cols = [np.ones(len(panel)), panel["treatment"], panel["post"]]
    if include_did:
        cols.append(panel["did"])
    dummies = pd.get_dummies(panel["district"], drop_first=True).astype(float).to_numpy()
    return np.column_stack(cols + [dummies])


def _cluster_se(X, e, g, XtXi, idx):
    n, k = X.shape
    groups = np.unique(g)
    G = len(groups)
    meat = np.zeros((k, k))
    for gg in groups:
        s = X[g == gg].T @ e[g == gg]
        meat += np.outer(s, s)
    V = XtXi @ meat @ XtXi * (G / (G - 1)) * ((n - 1) / (n - k))
    return float(np.sqrt(V[idx, idx])), G


def did(panel):
    X = _design(panel)
    y = panel["y"].to_numpy(float)
    XtXi = np.linalg.pinv(X.T @ X)
    b = XtXi @ X.T @ y
    e = y - X @ b
    g = panel["district"].to_numpy()
    se, G = _cluster_se(X, e, g, XtXi, 3)
    coef = float(b[3])
    t = coef / se
    tcrit95, tcrit90 = stats.t.ppf(0.975, G - 1), stats.t.ppf(0.95, G - 1)
    return {
        "coef": coef, "se": se, "n_obs": int(len(panel)), "n_clusters": int(G),
        "p_z": float(2 * stats.norm.sf(abs(t))), "p_t": float(2 * stats.t.sf(abs(t), G - 1)),
        "ci95_t": [coef - tcrit95 * se, coef + tcrit95 * se],
        "ci90_t": [coef - tcrit90 * se, coef + tcrit90 * se],
    }


def wild_cluster_bootstrap_p(panel):
    """Exact restricted wild cluster bootstrap p-value for the DiD t-statistic."""
    X = _design(panel)
    Xr = _design(panel, include_did=False)
    y = panel["y"].to_numpy(float)
    g = panel["district"].to_numpy()
    XtXi = np.linalg.inv(X.T @ X)
    H = XtXi @ X.T
    b = H @ y
    se, G = _cluster_se(X, y - X @ b, g, XtXi, 3)
    t_obs = b[3] / se
    br = np.linalg.lstsq(Xr, y, rcond=None)[0]
    fitted, resid = Xr @ br, y - Xr @ br
    groups = sorted(np.unique(g))
    gi = np.array([groups.index(v) for v in g])
    exceed = total = 0
    for signs in itertools.product([-1.0, 1.0], repeat=len(groups)):
        ys = fitted + np.array(signs)[gi] * resid
        bs = H @ ys
        ses, _ = _cluster_se(X, ys - X @ bs, g, XtXi, 3)
        total += 1
        exceed += abs(bs[3] / ses) >= abs(t_obs)
    return exceed / total
