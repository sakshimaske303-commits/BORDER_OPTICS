import streamlit as st
import pandas as pd
from scipy import stats
from utils.theme import inject_theme, PALETTE
from utils.data import load_data

st.set_page_config(page_title="Statistical Validation — BORDER OPTICS", page_icon="📊", layout="wide")
inject_theme()

villages, full_year, summer = load_data()

st.markdown("<h1>📊 STATISTICAL VALIDATION</h1>", unsafe_allow_html=True)
st.markdown(
    "<h3 style='text-align: center; font-weight: 700;'>Hypothesis Testing, Robustness, and Honest Limitations</h3>",
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
    w_stat, p_val = stats.wilcoxon(paired[before_col], paired[after_col])
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
    'This comparison is the core honesty check of the entire analysis.'
    '</p></div>'
)
st.markdown(verdict_html, unsafe_allow_html=True)

st.markdown("---")
st.markdown(
    "<p class='caption-text' style='text-align:center;'>BORDER OPTICS — Every result stress-tested, every limitation disclosed</p>",
    unsafe_allow_html=True,
)