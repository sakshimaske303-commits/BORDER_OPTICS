"""
Extra robustness checks for the summer-window control-group DiD (Section 4.6):
1. leave-one-district-out, 2. randomization inference (shuffle treatment
within district), 3. log1p VIIRS sensitivity, 4. summer-window missingness
mechanism.

statsmodels wouldn't install here so did OLS + cluster-robust/HC3 by hand
with numpy - checked it reproduces did_model.py's numbers to 5 sig figs first.

Run from repo root: python src/analysis/extended_robustness_checks.py
"""

import json

import numpy as np
import pandas as pd
from scipy import stats

PANEL_PATHS = {
    "full_year": "data/processed/border_optics_did_panel_fullyear.csv",
    "summer": "data/processed/border_optics_did_panel_summer.csv",
}
TREATED_PATHS = {
    "full_year": "data/processed/border_optics_village_results_analyzed.csv",
    "summer": "data/processed/border_optics_village_results_summer_analyzed.csv",
}
OUT_JSON = "outputs/robustness_extended_results.json"
OUT_LOO_CSV = "outputs/leave_one_district_out_results.csv"
N_PERMUTATIONS = 2000
RNG_SEED = 42


# ---------------------------------------------------------------------------
# manual OLS + cluster-robust/HC3 sandwich covariance (no statsmodels)
# ---------------------------------------------------------------------------

def _ols_fit(X, y):
    XtX_inv = np.linalg.inv(X.T @ X)
    beta = XtX_inv @ (X.T @ y)
    resid = y - X @ beta
    return beta, resid, XtX_inv


def _cluster_robust_se(X, resid, XtX_inv, clusters):
    n, k = X.shape
    groups = np.unique(clusters)
    G = len(groups)
    meat = np.zeros((k, k))
    for g in groups:
        idx = clusters == g
        score = X[idx].T @ resid[idx]
        meat += np.outer(score, score)
    adj = (G / (G - 1)) * ((n - 1) / (n - k))
    V = adj * XtX_inv @ meat @ XtX_inv
    return np.sqrt(np.diag(V))


def _build_design(df, fe=True):
    n = len(df)
    cols = [np.ones(n), df["treatment"].values.astype(float),
            df["post"].values.astype(float), df["did_term"].values.astype(float)]
    names = ["const", "treatment", "post", "did_term"]
    if fe:
        districts = df["district"].astype("category")
        cats = districts.cat.categories
        for c in cats[1:]:  # drop first as reference level
            cols.append((districts == c).astype(float).values)
            names.append(f"district_{c}")
    return np.column_stack(cols), names


def run_did(df, outcome, cluster_col="district"):
    """District-FE DiD with cluster-robust SE, matches did_model.py's spec."""
    valid = df.dropna(subset=[outcome]).copy()
    y = valid[outcome].values.astype(float)
    X, names = _build_design(valid, fe=True)
    beta, resid, XtX_inv = _ols_fit(X, y)
    se = _cluster_robust_se(X, resid, XtX_inv, valid[cluster_col].values)
    idx = names.index("did_term")
    coef, coef_se = beta[idx], se[idx]
    z = coef / coef_se
    p = 2 * stats.norm.sf(np.abs(z))
    return {
        "coef": float(coef), "se": float(coef_se), "p": float(p),
        "ci_lo": float(coef - 1.96 * coef_se), "ci_hi": float(coef + 1.96 * coef_se),
        "n": len(valid), "n_districts": int(valid["district"].nunique()),
    }


# ---------------------------------------------------------------------------
# 1. Leave-one-district-out
# ---------------------------------------------------------------------------

def leave_one_district_out():
    print("=" * 70)
    print("1. LEAVE-ONE-DISTRICT-OUT (summer-window DiD, both outcomes)")
    print("=" * 70)
    df = pd.read_csv(PANEL_PATHS["summer"])
    districts = sorted(df["district"].unique())
    all_rows = []
    summary = {}
    for outcome in ["ndbi", "lights"]:
        rows = []
        for d in districts:
            r = run_did(df[df["district"] != d], outcome)
            r["outcome"] = outcome
            r["dropped_district"] = d
            r["significant"] = r["p"] < 0.05
            rows.append(r)
            print(f"  [{outcome}] drop {d:16s} coef={r['coef']:+.5f}  p={r['p']:.5f}  "
                  f"{'YES' if r['significant'] else 'no'}")
        all_rows.extend(rows)
        coefs = [r["coef"] for r in rows]
        n_sig = sum(r["significant"] for r in rows)
        summary[outcome] = {
            "coef_min": min(coefs), "coef_max": max(coefs),
            "n_significant_of_14": n_sig,
        }
        print(f"  -> {outcome}: coef range [{min(coefs):+.5f}, {max(coefs):+.5f}], "
              f"significant (p<0.05) in {n_sig}/14 district-dropped reruns\n")
    pd.DataFrame(all_rows).to_csv(OUT_LOO_CSV, index=False)
    print(f"Saved {OUT_LOO_CSV}\n")
    return summary


# ---------------------------------------------------------------------------
# 2. Randomization inference: shuffle treatment within district
# ---------------------------------------------------------------------------

def randomization_inference():
    print("=" * 70)
    print(f"2. RANDOMIZATION INFERENCE ({N_PERMUTATIONS} permutations, "
          "treatment shuffled within district)")
    print("=" * 70)
    rng = np.random.RandomState(RNG_SEED)
    results = {}
    for outcome in ["ndbi", "lights"]:
        df = pd.read_csv(PANEL_PATHS["summer"])
        observed = run_did(df, outcome)
        obs_coef = observed["coef"]

        # village_id repeats across treated/control so need treatment in the key too
        df["_key"] = df["treatment"].astype(str) + "_" + df["village_id"].astype(str)
        villages = df.drop_duplicates(subset=["_key"])[["_key", "district", "treatment"]]

        perm_coefs = []
        for _ in range(N_PERMUTATIONS):
            perm = villages.copy()
            for d, grp in perm.groupby("district"):
                perm.loc[grp.index, "treatment"] = rng.permutation(grp["treatment"].values)
            treat_map = dict(zip(perm["_key"], perm["treatment"]))
            df_p = df.copy()
            df_p["treatment"] = df_p["_key"].map(treat_map)
            df_p["did_term"] = df_p["treatment"] * df_p["post"]
            perm_coefs.append(run_did(df_p, outcome)["coef"])

        perm_coefs = np.array(perm_coefs)
        # two-sided randomization p-value (+1/+1 continuity correction)
        p_perm = (np.sum(np.abs(perm_coefs) >= np.abs(obs_coef)) + 1) / (len(perm_coefs) + 1)
        print(f"  {outcome}: observed coef={obs_coef:+.5f} | permutation mean="
              f"{perm_coefs.mean():+.5f}, SD={perm_coefs.std():.5f} | "
              f"randomization-inference p={p_perm:.5f}")
        results[outcome] = {
            "observed_coef": float(obs_coef), "n_permutations": int(len(perm_coefs)),
            "perm_mean": float(perm_coefs.mean()), "perm_sd": float(perm_coefs.std()),
            "p_randomization": float(p_perm),
        }
    print()
    return results


# ---------------------------------------------------------------------------
# 3. Log-transformed VIIRS sensitivity
# ---------------------------------------------------------------------------

def log_viirs_sensitivity():
    print("=" * 70)
    print("3. LOG-TRANSFORMED VIIRS (log1p) SENSITIVITY")
    print("=" * 70)
    treated_only = {}
    for window_label, path in [("full-year", TREATED_PATHS["full_year"]),
                                 ("summer-matched", TREATED_PATHS["summer"])]:
        df = pd.read_csv(path)
        core = df[df["is_core_sample"] == True]
        valid = core.dropna(subset=["lights_before", "lights_after"])
        _, raw_p = stats.wilcoxon(valid["lights_after"], valid["lights_before"], alternative="greater")
        log_before = np.log1p(valid["lights_before"].clip(lower=0))
        log_after = np.log1p(valid["lights_after"].clip(lower=0))
        _, log_p = stats.wilcoxon(log_after, log_before, alternative="greater")
        print(f"  Treated-only [{window_label}]: n={len(valid)}  raw p={raw_p:.6f}  log1p p={log_p:.6f}")
        treated_only[window_label] = {"n": len(valid), "raw_p": float(raw_p), "log1p_p": float(log_p)}

    did = {}
    for window in ["full_year", "summer"]:
        df = pd.read_csv(PANEL_PATHS[window])
        df["lights_log1p"] = np.log1p(df["lights"].clip(lower=0))
        r_raw = run_did(df, "lights")
        r_log = run_did(df, "lights_log1p")
        print(f"  DiD [{window}]: raw coef={r_raw['coef']:+.5f} p={r_raw['p']:.5f}  |  "
              f"log1p coef={r_log['coef']:+.5f} p={r_log['p']:.5f}")
        did[window] = {"raw": r_raw, "log1p": r_log}
    print()
    return {"treated_only": treated_only, "did": did}


# ---------------------------------------------------------------------------
# 4. Summer-window missingness mechanism
# ---------------------------------------------------------------------------

def summer_missingness():
    print("=" * 70)
    print("4. SUMMER-WINDOW MISSINGNESS MECHANISM (core sample) -- HISTORICAL")
    print("=" * 70)
    summer = pd.read_csv(TREATED_PATHS["summer"])
    core = summer[summer["is_core_sample"] == True].copy()
    core["summer_valid"] = core["ndbi_before"].notna() & core["ndbi_after"].notna()
    n_valid, n_invalid = int(core["summer_valid"].sum()), int((~core["summer_valid"]).sum())
    print(f"  n core = {len(core)}, summer-valid = {n_valid}, summer-invalid = {n_invalid}")

    if n_invalid == 0:
        # extraction's complete now (251/251) so nothing to compare against -
        # keeping this check around anyway so the old result stays reproducible
        print("  No summer-invalid villages remain (fresh, complete extraction -- see Entry 22).")
        print("  This check is now moot: nothing left to compare against. Historical result")
        print("  (154 valid / 97 invalid, chi2=71.42 p~3.1e-16, baseline NDBI Mann-Whitney p=0.00063)")
        print("  is preserved in Development Log Entry 20 and superseded Research Paper drafts.\n")
        return {
            "n_core": len(core), "n_summer_valid": n_valid, "n_summer_invalid": n_invalid,
            "moot": True, "note": "No missingness remains as of Entry 22's fresh extraction.",
        }

    tab = pd.crosstab(core["state"], core["summer_valid"])
    chi2, chi2_p, _, _ = stats.chi2_contingency(tab)
    print(f"\n  By state:\n{tab.to_string()}")
    print(f"  Chi-square (state x summer-valid): chi2={chi2:.3f}, p={chi2_p:.2e}")

    fullyear = pd.read_csv(TREATED_PATHS["full_year"])
    baseline = fullyear[fullyear["is_core_sample"] == True][["village_id", "ndbi_before"]]
    merged = core.merge(baseline, on="village_id", how="left", suffixes=("", "_fy"))
    valid_grp = merged.loc[merged["summer_valid"], "ndbi_before_fy"].dropna()
    invalid_grp = merged.loc[~merged["summer_valid"], "ndbi_before_fy"].dropna()
    u_stat, u_p = stats.mannwhitneyu(valid_grp, invalid_grp, alternative="two-sided")
    print(f"\n  Baseline (2021, full-year) NDBI: valid mean={valid_grp.mean():.5f} (n={len(valid_grp)}), "
          f"invalid mean={invalid_grp.mean():.5f} (n={len(invalid_grp)}), Mann-Whitney p={u_p:.5f}")
    print()

    return {
        "n_core": len(core), "n_summer_valid": n_valid, "n_summer_invalid": n_invalid,
        "state_chi2": float(chi2), "state_chi2_p": float(chi2_p),
        "baseline_ndbi_valid_mean": float(valid_grp.mean()),
        "baseline_ndbi_invalid_mean": float(invalid_grp.mean()),
        "baseline_ndbi_mw_p": float(u_p),
        "n_valid_baseline": int(len(valid_grp)), "n_invalid_baseline": int(len(invalid_grp)),
    }


# ---------------------------------------------------------------------------
# 5. same leave-one-out + randomization stress test, but for full-year lights
# DiD - this was the last still-significant control-group DiD result after
# Entry 22, but the control-list contamination fix in Entry 24/25 sent it to
# null too (see BO_Development_Log.md Entry 25). Kept here as a completed
# check on a now-null result, not as a check on something still significant.
# ---------------------------------------------------------------------------

def fullyear_lights_robustness():
    print("=" * 70)
    print("5. LEAVE-ONE-OUT + RANDOMIZATION INFERENCE, FULL-YEAR LIGHTS DiD")
    print("   (significant post-Entry-22; went null post-Entry-25 control-list fix -- checked here anyway)")
    print("=" * 70)
    df = pd.read_csv(PANEL_PATHS["full_year"])
    districts = sorted(df["district"].unique())
    rows = []
    for d in districts:
        r = run_did(df[df["district"] != d], "lights")
        r["dropped_district"] = d
        r["significant"] = r["p"] < 0.05
        rows.append(r)
        print(f"  drop {d:16s} coef={r['coef']:+.5f}  p={r['p']:.5f}  {'YES' if r['significant'] else 'no'}")
    n_sig = sum(r["significant"] for r in rows)
    coefs = [r["coef"] for r in rows]
    print(f"  -> coef range [{min(coefs):+.5f}, {max(coefs):+.5f}], significant (p<0.05) in "
          f"{n_sig}/{len(rows)} district-dropped reruns\n")

    rng = np.random.RandomState(RNG_SEED)
    observed = run_did(df, "lights")
    obs_coef = observed["coef"]
    df["_key"] = df["treatment"].astype(str) + "_" + df["village_id"].astype(str)
    villages = df.drop_duplicates(subset=["_key"])[["_key", "district", "treatment"]]
    perm_coefs = []
    for _ in range(N_PERMUTATIONS):
        perm = villages.copy()
        for d, grp in perm.groupby("district"):
            perm.loc[grp.index, "treatment"] = rng.permutation(grp["treatment"].values)
        treat_map = dict(zip(perm["_key"], perm["treatment"]))
        df_p = df.copy()
        df_p["treatment"] = df_p["_key"].map(treat_map)
        df_p["did_term"] = df_p["treatment"] * df_p["post"]
        perm_coefs.append(run_did(df_p, "lights")["coef"])
    perm_coefs = np.array(perm_coefs)
    p_perm = (np.sum(np.abs(perm_coefs) >= np.abs(obs_coef)) + 1) / (len(perm_coefs) + 1)
    print(f"  observed coef={obs_coef:+.5f} | permutation mean={perm_coefs.mean():+.5f}, "
          f"SD={perm_coefs.std():.5f} | randomization-inference p={p_perm:.5f}\n")

    return {
        "leave_one_out": {
            "coef_min": min(coefs), "coef_max": max(coefs), "n_significant_of_14": n_sig,
            "rows": rows,
        },
        "randomization": {
            "observed_coef": float(obs_coef), "n_permutations": int(len(perm_coefs)),
            "perm_mean": float(perm_coefs.mean()), "perm_sd": float(perm_coefs.std()),
            "p_randomization": float(p_perm),
        },
    }


def main():
    results = {
        "leave_one_district_out": leave_one_district_out(),
        "randomization_inference": randomization_inference(),
        "log_viirs": log_viirs_sensitivity(),
        "summer_missingness": summer_missingness(),
        "fullyear_lights_did_robustness": fullyear_lights_robustness(),
    }
    with open(OUT_JSON, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"Saved {OUT_JSON}")


if __name__ == "__main__":
    main()
