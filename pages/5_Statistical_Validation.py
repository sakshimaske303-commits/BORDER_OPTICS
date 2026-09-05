import streamlit as st
import pandas as pd
from scipy import stats
from utils.theme import inject_theme, PALETTE
from utils.data import load_data, load_expanded_results

st.set_page_config(page_title="Statistical Validation — BORDER OPTICS", page_icon="📊", layout="wide")
inject_theme()

villages, full_year, summer = load_data()
expanded = load_expanded_results()

st.markdown("<h1>📊 STATISTICAL VALIDATION</h1>", unsafe_allow_html=True)
st.markdown(
    "<h3 style='text-align: center; font-weight: 700;'>Hypothesis Testing, Robustness, and Honest Limitations</h3>",
    unsafe_allow_html=True,
)
st.markdown("---")

_checks = [
    (PALETTE['accent'], "✓", "Dual Compositing-Window Test"),
    (PALETTE['accent'], "✓", "Two Independent Metrics (NDBI + VIIRS)"),
    (PALETTE['accent'], "✓", "Wilcoxon Signed-Rank Tests"),
    (PALETTE['accent'], "✓", "Matched Non-VVP Control Group (753 villages, DiD)"),
    (PALETTE['accent'], "✓", "Three-Point Multi-Year Trend (2021/2023/2025)"),
    (PALETTE['accent'], "✓", "Buffer-Radius Sweep (250m / 500m / 1km)"),
    (PALETTE['accent'], "✓", "Cross-Checked Against Sanctioned Budget"),
    (PALETTE['accent'], "✓", "Every Data Gap Disclosed"),
    (PALETTE['warning'], "!", "NDBI Result Flagged as Window-Sensitive — Not Confirmed"),
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
Every test below is run under both composite windows. Where a result's direction or
significance flips between windows, that instability is reported explicitly rather than
resolved by discarding one window.
""")

st.markdown("---")


def run_wilcoxon(df, before_col, after_col):
    paired = df.dropna(subset=[before_col, after_col])
    if len(paired) < 2:
        return None, None, len(paired)
    w_stat, p_val = stats.wilcoxon(paired[after_col], paired[before_col], alternative="greater")
    return w_stat, p_val, len(paired)


def run_spearman(df, col_x, col_y):
    valid = df.dropna(subset=[col_x, col_y])
    if len(valid) < 3:
        return None, None, len(valid)
    rho, p_val = stats.spearmanr(valid[col_x], valid[col_y])
    return rho, p_val, len(valid)


def result_card(label, w_stat, p_val, n, border_color):
    if p_val is None:
        body = '<p style="color: ' + PALETTE["text_secondary"] + '; font-size: 0.9rem; margin: 0;">Insufficient paired observations.</p>'
    else:
        sig_text = "Significant at \u03b1 = 0.05" if p_val < 0.05 else "Not significant at \u03b1 = 0.05"
        body = (
            '<p style="color: ' + PALETTE["text_primary"] + '; font-size: 1.6rem; font-weight: 900; margin-bottom: 4px;">W = ' + f"{w_stat:.3f}" + '</p>'
            + '<p style="color: ' + PALETTE["text_secondary"] + '; font-size: 0.85rem; margin-bottom: 4px;">p = ' + f"{p_val:.4f}" + ' \u00b7 n = ' + str(n) + '</p>'
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
st.markdown("### H1 — Built-Up Area Change (Wilcoxon Signed-Rank)")

fy_w, fy_p, fy_n = run_wilcoxon(full_year, "ndbi_before", "ndbi_after")
sm_w, sm_p, sm_n = run_wilcoxon(summer, "ndbi_before", "ndbi_after")

col1, col2 = st.columns(2)
with col1:
    result_card("Full-Year", fy_w, fy_p, fy_n, PALETTE["accent"])
with col2:
    result_card("Summer-Matched", sm_w, sm_p, sm_n, PALETTE["border_up"])

st.markdown("---")

# ============================================================
# NIGHT-LIGHTS CHANGE (WILCOXON)
# ============================================================
st.markdown("### Night-Lights Change (Wilcoxon Signed-Rank)")

fy_wl, fy_pl, fy_nl = run_wilcoxon(full_year, "lights_before", "lights_after")
sm_wl, sm_pl, sm_nl = run_wilcoxon(summer, "lights_before", "lights_after")

col3, col4 = st.columns(2)
with col3:
    result_card("Full-Year", fy_wl, fy_pl, fy_nl, PALETTE["lights"])
with col4:
    result_card("Summer-Matched", sm_wl, sm_pl, sm_nl, PALETTE["accent_vintage"])

st.markdown("---")

# ============================================================
# H3 — BORDER PROXIMITY (SPEARMAN)
# ============================================================
st.markdown("### H3 — Border Proximity vs. Change (Spearman)")

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
st.dataframe(h3_table, use_container_width=True, hide_index=True)
st.caption("Exploratory — treat with caution given sample size and border-geometry caveats (see Methodology & Limitations).")

st.image(
    "outputs/figures/03_h3_border_distance_vs_lights.png",
    caption="Static export: distance-to-border vs. NDBI change and lights change, both composite windows",
    use_container_width=True,
)

st.markdown("---")

# ============================================================
# H4 — CONTROL-GROUP DIFFERENCE-IN-DIFFERENCES
# ============================================================
st.markdown("### H4 — Control-Group Difference-in-Differences")
st.markdown(
    "A treated-only before/after comparison can't tell VVP-I's own effect apart from a "
    "regional trend every village in these districts shares. This benchmarks the treated "
    "core sample against 753 matched non-VVP villages in the same 14 districts — district "
    "fixed effects, standard errors clustered by district."
)

did_col1, did_col2 = st.columns(2)
for col, window_key, window_label, border in [
    (did_col1, "did_fullyear", "Full-Year", PALETTE["accent"]),
    (did_col2, "did_summer", "Summer-Matched", PALETTE["border_up"]),
]:
    ndbi_r = next(r for r in expanded[window_key]["did"] if r["outcome"] == "ndbi")
    sig_text = "Significant at α = 0.05" if ndbi_r["did_p"] < 0.05 else "Not significant at α = 0.05"
    card_html = (
        '<div class="recon-card" style="border-left: 4px solid ' + border + '; min-height: 160px;">'
        + '<p style="color: ' + border + '; font-weight: 800; font-size: 0.85rem; text-transform: uppercase; margin-bottom: 10px;">' + window_label + ' — NDBI DiD</p>'
        + '<p style="color: ' + PALETTE["text_primary"] + '; font-size: 1.6rem; font-weight: 900; margin-bottom: 4px;">did = ' + f"{ndbi_r['did_coef']:+.4f}" + '</p>'
        + '<p style="color: ' + PALETTE["text_secondary"] + '; font-size: 0.85rem; margin-bottom: 4px;">p = ' + f"{ndbi_r['did_p']:.4f}" + ' · n = ' + str(ndbi_r['n_treated']) + ' treated / ' + str(ndbi_r['n_control']) + ' control</p>'
        + '<p style="color: ' + border + '; font-size: 0.82rem; font-weight: 700; margin: 0;">' + sig_text + '</p>'
        + '</div>'
    )
    with col:
        st.markdown(card_html, unsafe_allow_html=True)

st.image(
    "outputs/figures/08_control_group_did_effect.png",
    caption="District-fixed-effects DiD coefficient (treated-vs-control gap in change) with 95% CIs, NDBI and night-lights, both windows.",
    use_container_width=True,
)
st.caption(
    "Baseline (2021) balance check: treated villages start from a significantly lower mean NDBI "
    "than control villages in both windows — expected, given priority villages were themselves "
    "selected partly for remoteness, but a reminder this is a level-balance check, not a confirmed "
    "shared pre-trend (see Methodology & Limitations)."
)

st.markdown("---")

# ============================================================
# MULTI-YEAR TREND (2021 / 2023 / 2025)
# ============================================================
st.markdown("### Multi-Year Trend — 2021 / 2023 / 2025")
st.markdown(
    "The core comparison rests on two single years, vulnerable to either being a weather "
    "anomaly. A third time point (2023) lets a trend — not a two-point difference — carry "
    "the evidentiary weight."
)

my_summer_ndbi = next(r for r in expanded["multiyear_summer"] if r["outcome"] == "ndbi")
trend_col1, trend_col2, trend_col3 = st.columns(3)
trend_col1.metric("Overall 3-yr trend (summer)", f"p = {my_summer_ndbi['wilcoxon_p']:.3f}", "Not significant")
trend_col2.metric("2021 → 2023 change", f"{my_summer_ndbi['subperiod_2021_2023_mean_change']:+.4f}", f"p = {my_summer_ndbi['subperiod_2021_2023_p']:.3f}")
trend_col3.metric("2023 → 2025 change", f"{my_summer_ndbi['subperiod_2023_2025_mean_change']:+.4f}", f"p = {my_summer_ndbi['subperiod_2023_2025_p']:.6f}")

st.image(
    "outputs/figures/09_multiyear_trend.png",
    caption="Mean NDBI and night-lights radiance at 2021, 2023, and 2025, core sample, both windows, error bars ± 1 SE.",
    use_container_width=True,
)
st.caption(
    "The reported 2021-vs-2025 summer NDBI increase is concentrated in the 2023-to-2025 "
    "recovery, following an earlier 2021-to-2023 decline — not a steady trend since sanction."
)

st.markdown("---")

# ============================================================
# BUFFER-RADIUS SENSITIVITY
# ============================================================
st.markdown("### Buffer-Radius Sensitivity — 250m / 500m / 1km")
st.markdown(
    "The 500m extraction buffer used throughout was a fixed choice. This re-runs the "
    "summer-window NDBI test at 250m and 1km, on the subsample of villages valid at all "
    "three radii, to isolate buffer radius from an unrelated archive-coverage difference "
    "between extraction dates (see Methodology & Limitations)."
)

buf_cols = st.columns(3)
for col, r in zip(buf_cols, expanded["buffer_sensitivity"]["matched_subsample"]):
    sig_text = "Significant" if r["wilcoxon_p"] < 0.05 else "Not significant"
    col.metric(f"{r['buffer_m']}m buffer (n={r['n']})", f"p = {r['wilcoxon_p']:.6f}", sig_text)

st.image(
    "outputs/figures/10_buffer_sensitivity.png",
    caption="NDBI Wilcoxon p-value (log scale) at each buffer radius — as-extracted samples vs. the matched subsample present at all three radii.",
    use_container_width=True,
)

st.markdown("---")

# ============================================================
# ROBUSTNESS SUMMARY CHART
# ============================================================
st.markdown("### Robustness Summary — All Four Core Tests, Both Windows")

st.image(
    "outputs/figures/07_robustness_summary.png",
    caption="Significance (p-value, log scale) for every test under both compositing windows — points on opposite sides of the p = 0.05 line indicate a result that reverses conclusion depending on window choice.",
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
    'Compare the full-year and summer-matched cards above. A result that keeps the same '
    'sign and significance across both windows is treated as the more trustworthy finding. '
    'A result that flips \u2014 in direction, significance, or both \u2014 is reported as evidence '
    'of methodological instability rather than silently resolved by preferring one window. '
    'The summer-matched NDBI result is the one signal that clears significance here \u2014 and it '
    'holds up against a matched control group (H4), a buffer-radius sweep, and Holm-Bonferroni '
    'correction, while the multi-year trend shows it is concentrated in 2023\u20132025 rather than '
    'sustained since sanction. This comparison is the core honesty check of the entire analysis.'
    '</p></div>'
)
st.markdown(verdict_html, unsafe_allow_html=True)

st.markdown("---")
st.markdown(
    "<p class='caption-text' style='text-align:center;'>BORDER OPTICS — Every result stress-tested, every limitation disclosed</p>",
    unsafe_allow_html=True,
)