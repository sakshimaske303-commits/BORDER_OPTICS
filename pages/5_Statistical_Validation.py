import json
import streamlit as st
import pandas as pd
from scipy import stats
from utils.theme import inject_theme, PALETTE
from utils.data import load_data, load_expanded_results

st.set_page_config(page_title="Statistical Validation — BORDER OPTICS", page_icon="📊", layout="wide")
inject_theme()

villages, full_year, summer = load_data()
expanded = load_expanded_results()

# H1 (Wilcoxon) and H3 (Spearman) below must run on the core statistical sample only
# (220 villages from v2.1) to match the formal tests reported in the Research Paper / dashboard
# home page -- the 7 illustrative Himachal Pradesh villages are not part of the core
# sample and must not leak into these hypothesis tests. (Fixed 2026-09-18: this page
# was previously running these tests on the full 258-village set, which flipped the
# full-year night-lights H1 result from p=0.050 (not significant, matching the paper)
# to p=0.014 (significant) -- a page-only artifact, not a real result.)
full_year = full_year[full_year["is_core_sample"] == True] if "is_core_sample" in full_year.columns else full_year
summer = summer[summer["is_core_sample"] == True] if "is_core_sample" in summer.columns else summer

st.markdown("<h1>📊 STATISTICAL VALIDATION</h1>", unsafe_allow_html=True)
st.markdown(
    "<h3 style='text-align: center; font-weight: 700;'>Hypothesis Testing, Robustness, and Honest Limitations</h3>",
    unsafe_allow_html=True,
)
st.markdown("---")

_checks = [
    (PALETTE['accent'], "✓", "Dual Compositing-Window Test"),
    (PALETTE['accent'], "✓", "Two Separate Metrics (NDBI + VIIRS)"),
    (PALETTE['accent'], "✓", "Within-District DiD, t With 12 df for 13 District Clusters"),
    (PALETTE['accent'], "✓", "District-Verified Non-VVP Control Group (628 villages, DiD)"),
    (PALETTE['accent'], "✓", "Control-Group DiD Checked Further (Leave-One-District-Out + Randomization Inference)"),
    (PALETTE['accent'], "✓", "Three-Point Multi-Year Trend (2021/2023/2025)"),
    (PALETTE['accent'], "✓", "Buffer-Radius Sweep (250m / 500m / 1km)"),
    (PALETTE['accent'], "✓", "Every Data Gap Disclosed"),
    (PALETTE['accent'], "✓", "Original Summer NDBI Signal Re-Checked Once Extraction Was Completed — Did Not Survive"),
    (PALETTE['accent'], "✓", "Border Proximity (SQ2) Tested Within Districts — Pooled Correlations Disappear or Reverse"),
    (PALETTE['accent'], "✓", "Detectability in Physical Units — NDBI Cannot See Village-Scale Construction"),
    (PALETTE['accent'], "✓", "Exact Wild Cluster Bootstrap (8,192 Sign-Flip Combinations) — DiD Null Confirmed"),
    (PALETTE['accent'], "✓", "Genuine Pre-Treatment (2019) Placebo Test — Clean, but Summer NDBI Pre-Trends Uncertain"),
    (PALETTE['warning'], "!", "Dynamic World Shows a Small Positive Summer DiD (Bootstrap p = 0.017) — Cause Not Yet Established"),
]
_badges = "".join(
    f"""<span style="display:inline-flex; align-items:center; gap:6px; background:rgba(167,225,193,0.08);
        border:1px solid rgba(167,225,193,0.3); border-radius:20px; padding:6px 14px; margin:4px;
        font-size:0.82rem; color:{PALETTE['text_primary']}; font-weight:600;">
        <span style="color:{color}; font-weight:900;">{mark}</span>{label}</span>"""
    for color, mark, label in _checks
)
st.markdown(
    f"""
    <p style="color:{PALETTE['accent_vintage']}; text-transform:uppercase; letter-spacing:1.5px;
              font-weight:800; font-size:0.85rem; margin-bottom:6px;">Robustness At a Glance</p>
    <div style="display:flex; flex-wrap:wrap; margin-bottom: 6px;">{_badges}</div>
    """,
    unsafe_allow_html=True,
)

st.markdown("---")

st.markdown("""
**How to read this page.** The programme estimate is the **difference-in-differences** (priority vs.
comparison villages, section "Primary analysis" below). The first two sections describe change in
priority villages on their own (two-sided Wilcoxon); they cannot separate a programme effect from a
regional trend and are descriptive only. Every test is run under both compositing windows.
""")

st.markdown("---")


def run_wilcoxon(df, before_col, after_col):
    paired = df.dropna(subset=[before_col, after_col])
    if len(paired) < 2:
        return None, None, len(paired), None
    w_stat, p_val = stats.wilcoxon(paired[after_col], paired[before_col], alternative="two-sided")
    return w_stat, p_val, len(paired), float((paired[after_col] - paired[before_col]).median())


def run_spearman(df, col_x, col_y):
    valid = df.dropna(subset=[col_x, col_y])
    if len(valid) < 3:
        return None, None, len(valid)
    rho, p_val = stats.spearmanr(valid[col_x], valid[col_y])
    return rho, p_val, len(valid)


def result_card(label, w_stat, p_val, n, median, border_color):
    if p_val is None:
        body = '<p style="color: ' + PALETTE["text_secondary"] + '; font-size: 0.9rem; margin: 0;">Insufficient paired observations.</p>'
    else:
        direction = "increase" if median > 0 else "decrease"
        sig_text = (f"Significant {direction} (two-sided, \u03b1 = 0.05)" if p_val < 0.05
                    else "No significant change (two-sided, \u03b1 = 0.05)")
        body = (
            '<p style="color: ' + PALETTE["text_primary"] + '; font-size: 1.6rem; font-weight: 900; margin-bottom: 4px;">W = ' + f"{w_stat:.3f}" + '</p>'
            + '<p style="color: ' + PALETTE["text_secondary"] + '; font-size: 0.85rem; margin-bottom: 4px;">' + ("p < 0.0001" if p_val < 0.0001 else f"p = {p_val:.4f}") + ' \u00b7 median change ' + f"{median:+.4f}" + ' \u00b7 n = ' + str(n) + '</p>'
            + '<p style="color: ' + border_color + '; font-size: 0.82rem; font-weight: 700; margin: 0;">' + sig_text + '</p>'
        )
    card_html = (
        '<div class="recon-card" style="border-left: 4px solid ' + border_color + '; min-height: 160px;">'
        + '<p style="color: ' + border_color + '; font-weight: 800; font-size: 0.85rem; text-transform: uppercase; margin-bottom: 10px;">' + label + '</p>'
        + body
        + '</div>'
    )
    st.markdown(card_html, unsafe_allow_html=True)


# ============================================================
# H1 — NDBI CHANGE (WILCOXON)
# ============================================================
st.markdown("### Priority Villages' Own NDBI Change (descriptive, two-sided Wilcoxon)")

fy_w, fy_p, fy_n, fy_m = run_wilcoxon(full_year, "ndbi_before", "ndbi_after")
sm_w, sm_p, sm_n, sm_m = run_wilcoxon(summer, "ndbi_before", "ndbi_after")

col1, col2 = st.columns(2)
with col1:
    result_card("Full-Year", fy_w, fy_p, fy_n, fy_m, PALETTE["accent"])
with col2:
    result_card("Summer-Matched", sm_w, sm_p, sm_n, sm_m, PALETTE["border_up"])

st.caption(
    "The full-year decline is largest where snow enters the composite; the summer window shows a small rise. "
    "Both use the primary QA60 cloud mask. An SCL-band cross-check first disagreed because the SCL mask let "
    "snow through as clear; once fixed, both masks agree on a small summer increase (one-sided test for an "
    "increase: QA60 p=0.019, SCL p=0.004, n=220). These describe priority villages only and are not programme "
    "estimates: comparison villages rose by a similar amount (see the difference-in-differences below)."
)

st.markdown("---")

# ============================================================
# NIGHT-LIGHTS CHANGE (WILCOXON)
# ============================================================
st.markdown("### Priority Villages' Own Night-Light Change (descriptive, two-sided Wilcoxon)")

fy_wl, fy_pl, fy_nl, fy_ml = run_wilcoxon(full_year, "lights_before", "lights_after")
sm_wl, sm_pl, sm_nl, sm_ml = run_wilcoxon(summer, "lights_before", "lights_after")

col3, col4 = st.columns(2)
with col3:
    result_card("Full-Year", fy_wl, fy_pl, fy_nl, fy_ml, PALETTE["lights"])
with col4:
    result_card("Summer-Matched", sm_wl, sm_pl, sm_nl, sm_ml, PALETTE["accent_vintage"])
st.caption(
    "The summer median falls; the summer mean is positive only because of one town, Joshimath (+5.97)."
)

st.markdown("---")

# ============================================================
# H3 — BORDER PROXIMITY (SPEARMAN)
# ============================================================
st.markdown("### SQ2 — Border Distance vs. Change (Spearman, pooled and within districts)")

fy_rho_n, fy_p_n, fy_n_n = run_spearman(full_year, "distance_to_border_km", "ndbi_change")
sm_rho_n, sm_p_n, sm_n_n = run_spearman(summer, "distance_to_border_km", "ndbi_change")
fy_rho_l, fy_p_l, fy_n_l = run_spearman(full_year, "distance_to_border_km", "lights_change")
sm_rho_l, sm_p_l, sm_n_l = run_spearman(summer, "distance_to_border_km", "lights_change")

h3_table = pd.DataFrame({
    "Metric vs. Distance": ["NDBI Change", "Lights Change"],
    "Full-Year (ρ)": [f"{fy_rho_n:.3f}" if fy_rho_n is not None else "—", f"{fy_rho_l:.3f}" if fy_rho_l is not None else "—"],
    "Full-Year (p)": [f"{fy_p_n:.4f}" if fy_p_n is not None else "—", f"{fy_p_l:.4f}" if fy_p_l is not None else "—"],
    "Summer (ρ)": [f"{sm_rho_n:.3f}" if sm_rho_n is not None else "—", f"{sm_rho_l:.3f}" if sm_rho_l is not None else "—"],
    "Summer (p)": [f"{sm_p_n:.4f}" if sm_p_n is not None else "—", f"{sm_p_l:.4f}" if sm_p_l is not None else "—"],
})
with open("outputs/h3_within_district_results.json") as _f:
    _h3w = json.load(_f)
_w = lambda win, out: _h3w[f"{win}|{out}|distance_to_border_km"]
h3_table["Full-Year within-district ρ (perm. p)"] = [
    f"{_w('full_year', o)['within_district_rank_corr']:+.3f} ({_w('full_year', o)['within_district_perm_p']:.4f})"
    for o in ["ndbi_change", "lights_change"]]
h3_table["Summer within-district ρ (perm. p)"] = [
    f"{_w('summer', o)['within_district_rank_corr']:+.3f} ({_w('summer', o)['within_district_perm_p']:.4f})"
    for o in ["ndbi_change", "lights_change"]]
st.dataframe(h3_table, use_container_width=True, hide_index=True)
st.caption(
    "Pooled across all villages, summer NDBI change rises with distance from the boundary and full-year "
    "night-light change falls with it. Ranked within their own districts, neither holds: the summer NDBI "
    "association disappears and the night-light association reverses (villages farther from the boundary "
    "gained more light, in both windows). The pooled correlations therefore reflect which districts lie "
    "closer to the boundary, not a proximity gradient, and earlier checks (leave-one-district-out, "
    "randomization, spatial correction) could not reveal this because none separates within- from "
    "between-district variation. Same result with distance to the China boundary only "
    "(outputs/h3_within_district_results.json)."
)

st.image(
    "outputs/figures/03_h3_border_distance_vs_lights.png",
    caption="Distance to the nearest boundary vs. change, coloured by district, with pooled and within-district ρ",
    use_container_width=True,
)

st.markdown("---")

# ============================================================
# H4 — CONTROL-GROUP DIFFERENCE-IN-DIFFERENCES
# ============================================================
st.markdown("### Primary Analysis — Priority vs. Comparison Villages (Difference-in-Differences)")
st.markdown(
    "This is the programme estimate. The 220 priority villages are compared with 628 non-priority "
    "villages in the same 13 districts: district-by-period fixed effects (each village is compared only "
    "with villages in its own district), standard errors clustered by district, p-values from t with 12 "
    "degrees of freedom and an exact wild cluster bootstrap (all 8,192 sign flips), as in Table 2 of the "
    "Research Paper. Each card also gives the leave-one-district-out and "
    "randomization-inference results."
)

with open("outputs/wild_cluster_bootstrap_results.json") as _f:
    _wcb = {(r["outcome"], r["window"]): r["wild_cluster_bootstrap_p"] for r in json.load(_f)}


def _p_t(r):
    return float(2 * stats.t.sf(abs(r["did_coef"] / r["did_se"]), 12))  # 13 district clusters (v2.1)


_loo = expanded["robustness_extended"]["leave_one_district_out"]
_rand = expanded["robustness_extended"]["randomization_inference"]
_fy_lights_robust = expanded["robustness_extended"]["fullyear_lights_did_robustness"]

did_col1, did_col2 = st.columns(2)
for col, window_key, window_label, border in [
    (did_col1, "did_fullyear", "Full-Year", PALETTE["accent"]),
    (did_col2, "did_summer", "Summer-Matched", PALETTE["border_up"]),
]:
    ndbi_r = next(r for r in expanded[window_key]["did"] if r["outcome"] == "ndbi")
    _pt = _p_t(ndbi_r); _pb = _wcb[("ndbi", "full_year" if window_key == "did_fullyear" else "summer")]
    sig_text = "Significant at α = 0.05" if _pt < 0.05 else "Not significant at α = 0.05"
    if window_key == "did_summer":
        loo_text = f"Leave-one-district-out: {_loo['ndbi']['n_significant']}/{_loo['ndbi']['n_reruns']} significant · Randomization p = {_rand['ndbi']['p_randomization']:.4f}"
    else:
        loo_text = "Leave-one-out / randomization inference not run for full-year NDBI — not significant to begin with"
    card_html = (
        '<div class="recon-card" style="border-left: 4px solid ' + border + '; min-height: 190px;">'
        + '<p style="color: ' + border + '; font-weight: 800; font-size: 0.85rem; text-transform: uppercase; margin-bottom: 10px;">' + window_label + ' — NDBI DiD</p>'
        + '<p style="color: ' + PALETTE["text_primary"] + '; font-size: 1.6rem; font-weight: 900; margin-bottom: 4px;">did = ' + f"{ndbi_r['did_coef']:+.4f}" + '</p>'
        + '<p style="color: ' + PALETTE["text_secondary"] + '; font-size: 0.85rem; margin-bottom: 4px;">p = ' + f"{_pt:.2f}" + ' (t, 12 df) · wild bootstrap p = ' + f"{_pb:.2f}" + ' · n = ' + str(ndbi_r['n_treated']) + ' treated / ' + str(ndbi_r['n_control']) + ' control</p>'
        + '<p style="color: ' + border + '; font-size: 0.82rem; font-weight: 700; margin-bottom: 6px;">' + sig_text + '</p>'
        + '<p style="color: ' + PALETTE["text_secondary"] + '; font-size: 0.75rem; margin: 0;">' + loo_text + '</p>'
        + '</div>'
    )
    with col:
        st.markdown(card_html, unsafe_allow_html=True)

st.markdown("")
did_col3, did_col4 = st.columns(2)
for col, window_key, window_label, border in [
    (did_col3, "did_fullyear", "Full-Year", PALETTE["accent"]),
    (did_col4, "did_summer", "Summer-Matched", PALETTE["border_up"]),
]:
    lights_r = next(r for r in expanded[window_key]["did"] if r["outcome"] == "lights")
    _pt = _p_t(lights_r); _pb = _wcb[("lights", "full_year" if window_key == "did_fullyear" else "summer")]
    sig_text = "Significant at α = 0.05" if _pt < 0.05 else "Not significant at α = 0.05"
    if window_key == "did_summer":
        loo_text = f"Leave-one-district-out: {_loo['lights']['n_significant']}/{_loo['lights']['n_reruns']} significant · Randomization p = {_rand['lights']['p_randomization']:.4f}"
    else:
        _fy_loo = _fy_lights_robust["leave_one_out"]
        _fy_rand = _fy_lights_robust["randomization"]
        loo_text = f"Previously this study's one surviving control-group result (contaminated control list) — now null on the corrected data: leave-one-district-out {_fy_loo['n_significant']}/{_fy_loo['n_reruns']} significant · Randomization p = {_fy_rand['p_randomization']:.4f}"
    card_html = (
        '<div class="recon-card" style="border-left: 4px solid ' + border + '; min-height: 190px;">'
        + '<p style="color: ' + border + '; font-weight: 800; font-size: 0.85rem; text-transform: uppercase; margin-bottom: 10px;">' + window_label + ' — Night-Lights DiD</p>'
        + '<p style="color: ' + PALETTE["text_primary"] + '; font-size: 1.6rem; font-weight: 900; margin-bottom: 4px;">did = ' + f"{lights_r['did_coef']:+.4f}" + '</p>'
        + '<p style="color: ' + PALETTE["text_secondary"] + '; font-size: 0.85rem; margin-bottom: 4px;">p = ' + f"{_pt:.2f}" + ' (t, 12 df) · wild bootstrap p = ' + f"{_pb:.2f}" + ' · n = ' + str(lights_r['n_treated']) + ' treated / ' + str(lights_r['n_control']) + ' control</p>'
        + '<p style="color: ' + border + '; font-size: 0.82rem; font-weight: 700; margin-bottom: 6px;">' + sig_text + '</p>'
        + '<p style="color: ' + PALETTE["text_secondary"] + '; font-size: 0.75rem; margin: 0;">' + loo_text + '</p>'
        + '</div>'
    )
    with col:
        st.markdown(card_html, unsafe_allow_html=True)
st.caption(
    "Leave-one-district-out p-values use the normal reference; randomization p-values come from 2,000 within-district "
    "permutations. Against the control group, the full-year night-light gap had briefly looked significant under district fixed effects "
    "(but not the no-fixed-effects comparison) — until the control group itself was found to contain "
    "23 villages that were physically or nominally duplicate of treated villages (Development Log "
    "Entry 23). With that fixed and the control list regenerated (Entry 25), the figure above reflects "
    "the corrected, decontaminated data and is null on every specification; see Methodology & "
    "Limitations for the full account."
)

st.image(
    "outputs/figures/08_control_group_did_effect.png",
    caption="Treated-vs-control DiD, 95% intervals (t, 12 df) and wild-bootstrap p-values. Green band: the NDBI change "
            "that doubling a typical village's buildings would produce.",
    use_container_width=True,
)
st.caption(
    "Baseline (2021) balance check on the current 628-village control list: NDBI is balanced in both "
    "windows (full year p=0.790, summer p=0.864), but night lights differ at baseline in both windows "
    "(full year p=0.019, summer p=0.008). Both night-light DiDs stay null. This is a level-balance check, not a "
    "shared pre-trend test; the 2019-2021 placebo test is on the Methodology & Limitations page."
)

st.markdown("---")

# ============================================================
# DETECTABILITY + DYNAMIC WORLD (v2.0, Development Log Entry 49)
# ============================================================
st.markdown("### What Could the Satellite Measures Detect?")
with open("outputs/measurement_sensitivity_results.json") as _f:
    _ms = json.load(_f)
with open("outputs/dynamic_world_robustness_results.json") as _f:
    _dwr = json.load(_f)
_rows = []
for _key, _label in [("ndbi_full_year", "NDBI, full year"), ("ndbi_summer", "NDBI, summer"),
                     ("dw_built_full_year", "Dynamic World, full year"), ("dw_built_summer", "Dynamic World, summer")]:
    _o = _ms["outcomes"][_key]
    _lo, _hi = _o["did_ci95_t_as_building_area_m2"]
    _rows.append({
        "Measure": _label,
        "Change from doubling a typical village's buildings": f"{_o['tost_sesoi_index_units']:+.4f}",
        "DiD estimate": f"{_o['did']['coef']:+.4f} (p = {_o['did']['p_t']:.3f})",
        "DiD as building-equivalent area": f"{_o['did_coef_as_building_area_m2']:+,.0f} m²",
        "95% CI, building-equivalent area": f"{_lo:+,.0f} to {_hi:+,.0f} m²",
    })
st.dataframe(pd.DataFrame(_rows), use_container_width=True, hide_index=True)
st.caption(
    f"Buildings cover a median {100 * _ms['median_treated_building_share_of_buffer']:.2f}% of a 500 m buffer, so a "
    "buffer-average index barely moves when a village builds. For NDBI, doubling a typical village's buildings is "
    "less than a fifth of the smallest DiD effect the design can detect: the NDBI null cannot rule out "
    "construction. Dynamic World responds three to four times more strongly to buildings. Its summer DiD "
    "corresponds to roughly 1,900 square metres of built-up surface per village (an approximate conversion; "
    f"wild-bootstrap p = {_dwr['summer_main']['wild_cluster_bootstrap_p']:.3f}) and holds in all leave-one-"
    "district-out reruns. The full-year DiD is smaller and not significant (wild-bootstrap "
    f"p = {_dwr['full_year_main']['wild_cluster_bootstrap_p']:.3f})."
)

st.markdown("---")

# ============================================================
# MULTI-YEAR TREND (2021 / 2023 / 2025)
# ============================================================
st.markdown("### Multi-Year Trend — 2021 / 2023 / 2025")
st.markdown(
    "Shown for priority villages only and descriptively. Sentinel-2's QA60 cloud band is empty for "
    "most of 2022–2024, so the 2023 composites may be effectively unmasked: the 2021→2023 dip and "
    "2023→2025 recovery are not interpreted, and the programme estimate remains the 2021–2025 "
    "difference-in-differences above."
)

my_summer_ndbi = next(r for r in expanded["multiyear_summer"] if r["outcome"] == "ndbi")
trend_col1, trend_col2, trend_col3 = st.columns(3)
trend_col1.metric("Overall 3-yr trend (summer)", f"p = {my_summer_ndbi['wilcoxon_p']:.3f}",
                  "Significant" if my_summer_ndbi['wilcoxon_p'] < 0.05 else "Not significant")
trend_col2.metric("2021 → 2023 change", f"{my_summer_ndbi['subperiod_2021_2023_mean_change']:+.4f}", f"p = {my_summer_ndbi['subperiod_2021_2023_p']:.3f}")
trend_col3.metric("2023 → 2025 change", f"{my_summer_ndbi['subperiod_2023_2025_mean_change']:+.4f}", f"p = {my_summer_ndbi['subperiod_2023_2025_p']:.6f}")

st.image(
    "outputs/figures/09_multiyear_trend.png",
    caption="Mean NDBI and night-lights radiance at 2021, 2023, and 2025, core sample, both windows, error bars ± 1 SE.",
    use_container_width=True,
)
st.caption(
    "In the summer window, a 2021-to-2023 decline is followed by a 2023-to-2025 recovery, and the net "
    "per-village trend is a small rise (one-sided Wilcoxon p=0.020; panel regression p=0.116). The full-year "
    "window is different: its per-village slopes show a significant *decline* in NDBI (panel regression "
    "p<0.001), and full-year night-lights slopes are borderline upward (one-sided Wilcoxon p=0.048). Treat the 2023 point with care: Sentinel-2's QA60 cloud band is empty for most of 2022–2024 in the harmonized collection, so the 2023 composites may be effectively unmasked and the dip should not be interpreted. See Research Paper §5.1 and §6."
)

st.markdown("---")

# ============================================================
# BUFFER-RADIUS SENSITIVITY
# ============================================================
st.markdown("### Buffer-Radius Sensitivity — 250m / 500m / 1km")
st.markdown(
    "The 500m extraction buffer used throughout was a fixed choice. This re-runs the "
    "summer-window NDBI change in priority villages at 250m and 1km (one-sided Wilcoxon test for an "
    "increase; all three radii extracted the same day, n = 220 at every radius). The small summer "
    "increase is clearest at 250m and 500m and disappears at 1km. This describes priority villages only; "
    "the difference-in-differences above shows that comparison villages changed by a similar amount."
)

buf_cols = st.columns(3)
for col, r in zip(buf_cols, expanded["buffer_sensitivity"]["matched_subsample"]):
    sig_text = "Significant" if r["wilcoxon_p"] < 0.05 else "Not significant"
    col.metric(f"{r['buffer_m']}m buffer (n={r['n']})", f"p = {r['wilcoxon_p']:.6f}", sig_text)

st.image(
    "outputs/figures/10_buffer_sensitivity.png",
    caption="NDBI Wilcoxon p-value (log scale) at each buffer radius, all three radii pulled the same day, n=220 at every radius.",
    use_container_width=True,
)

st.markdown("---")

# ============================================================
# ROBUSTNESS SUMMARY CHART
# ============================================================
st.markdown("### Descriptive Tests at a Glance — Priority-Village Change and Border Distance, Both Windows")

st.image(
    "outputs/figures/07_robustness_summary.png",
    caption="Two-sided p-values (log scale) for the descriptive tests under both windows, with the within-district border-distance tests (hollow). The programme estimate is the difference-in-differences above.",
    use_container_width=True,
)

st.markdown("---")

# ============================================================
# ROBUSTNESS VERDICT
# ============================================================
verdict_html = (
    '<div class="recon-card" style="border-left: 4px solid ' + PALETTE["accent"] + ';">'
    '<p style="color: ' + PALETTE["accent"] + '; font-weight: 800; font-size: 0.85rem; text-transform: uppercase; margin-bottom: 10px;">Robustness Verdict</p>'
    '<p style="color: ' + PALETTE["text_primary"] + '; font-size: 0.9rem; margin: 0;">'
    'NDBI, night lights and radar show no difference between priority and comparison villages under any '
    'specification: within-district, cluster-robust (t, 12 df), wild cluster bootstrap, leave-one-district-out, randomization '
    'inference, a 2019\u20132021 placebo, and sample-quality variants. That null is uninformative about construction, '
    'because buffer-mean NDBI could not have detected even a doubling of a typical village\u2019s buildings. '
    'Dynamic World\u2019s built-up probability, the most building-sensitive measure, shows a small positive '
    'difference in the summer window (bootstrap p = 0.017) that survives every check; the full-year estimate '
    'is smaller and not significant. Version 2.1 removed Sikkim, whose comparison villages lay mostly outside '
    'the district, and made the model compare villages within districts. Earlier versions reported significant NDBI and night-light results that '
    'disappeared once an incomplete extraction and a contaminated control list were fixed; the full record is '
    'in the Development Log and Results Stability Table.'
    '</p></div>'
)
st.markdown(verdict_html, unsafe_allow_html=True)

st.markdown("---")
st.markdown(
    "<p class='caption-text' style='text-align:center;'>BORDER OPTICS — every result reported with its limits</p>",
    unsafe_allow_html=True,
)