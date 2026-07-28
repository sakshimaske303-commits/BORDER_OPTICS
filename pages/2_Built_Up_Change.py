import streamlit as st
import pandas as pd
from utils.theme import inject_theme, PALETTE
from utils.data import load_data

st.set_page_config(page_title="Built-Up Change — BORDER OPTICS", page_icon="🏗️", layout="wide")
inject_theme()

villages, full_year, summer = load_data()

st.markdown("<h1>🏗️ BUILT-UP CHANGE ANALYSIS</h1>", unsafe_allow_html=True)
st.markdown(
    "<h3 style='text-align: center; font-weight: 700;'>NDBI: 2021 → 2025</h3>",
    unsafe_allow_html=True,
)
st.markdown("---")

st.markdown("""
NDBI (Normalized Difference Built-up Index) measures the physical footprint of
construction using Sentinel-2 SWIR1/NIR reflectance. A positive change indicates new
built-up area; a negative change indicates a reduction.
""")

st.markdown("---")

# ============================================================
# COMPOSITE WINDOW TOGGLE
# ============================================================
window = st.radio("Composite window", ["Summer-Matched (Jun–Sep)", "Full-Year"], horizontal=True)
df = summer if window.startswith("Summer") else full_year
valid = df.dropna(subset=["ndbi_change"])

c1, c2, c3, c4 = st.columns(4)
c1.metric("Mean NDBI Change", f"{valid['ndbi_change'].mean():.4f}")
c2.metric("Median NDBI Change", f"{valid['ndbi_change'].median():.4f}")
c3.metric("Villages Increased", f"{(valid['ndbi_change'] > 0).mean() * 100:.1f}%")
c4.metric("Villages Decreased", f"{(valid['ndbi_change'] < 0).mean() * 100:.1f}%")

st.markdown("---")

# ============================================================
# DISTRIBUTION CHART
# ============================================================
st.markdown("### Distribution of Change")
st.image(
    "outputs/figures/01_ndbi_change_distribution.png",
    caption="Distribution of NDBI change across all geocoded villages",
    use_container_width=True,
)

st.markdown("---")

# ============================================================
# ROBUSTNESS: FULL-YEAR vs SUMMER-MATCHED
# ============================================================
st.markdown("### Robustness Check — Composite Window Comparison")

fy_valid = full_year.dropna(subset=["ndbi_change"])
sm_valid = summer.dropna(subset=["ndbi_change"])

comparison = pd.DataFrame({
    "Metric": ["Mean NDBI Change", "Median NDBI Change", "% Increased", "n (valid observations)"],
    "Full-Year": [
        f"{fy_valid['ndbi_change'].mean():.4f}",
        f"{fy_valid['ndbi_change'].median():.4f}",
        f"{(fy_valid['ndbi_change'] > 0).mean() * 100:.1f}%",
        len(fy_valid),
    ],
    "Summer-Matched": [
        f"{sm_valid['ndbi_change'].mean():.4f}",
        f"{sm_valid['ndbi_change'].median():.4f}",
        f"{(sm_valid['ndbi_change'] > 0).mean() * 100:.1f}%",
        len(sm_valid),
    ],
})

col1, col2 = st.columns([1.2, 1])
with col1:
    st.dataframe(comparison, use_container_width=True, hide_index=True)
with col2:
    st.markdown(f"""
    <div class="recon-card" style="border-left: 4px solid {PALETTE['accent']};">
        <p style="color: {PALETTE['accent']}; font-weight: 800; font-size: 0.85rem; text-transform: uppercase; margin-bottom: 10px;">Why Two Windows?</p>
        <p style="color: {PALETTE['text_primary']}; font-size: 0.88rem; margin: 0;">
            Full-year composites risk snow-cover contamination at high altitude.
            Summer-matched composites avoid snow but lose coverage to monsoon cloud cover
            in some states. Where direction or significance differs between windows, that
            instability is reported as a genuine finding — see Statistical Validation.
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ============================================================
# TOP MOVERS
# ============================================================
st.markdown("### Top Movers")

display_cols = [c for c in ["village", "district", "block", "state", "ndbi_before", "ndbi_after", "ndbi_change"] if c in valid.columns]

col_up, col_down = st.columns(2)
with col_up:
    st.markdown(f'<p style="color:{PALETTE["border_up"]}; font-family: JetBrains Mono, monospace; font-size:13px; font-weight:700;">▲ TOP 10 — INCREASE</p>', unsafe_allow_html=True)
    st.dataframe(
        valid.sort_values("ndbi_change", ascending=False)[display_cols].head(10),
        use_container_width=True, hide_index=True,
    )
with col_down:
    st.markdown(f'<p style="color:{PALETTE["border_down"]}; font-family: JetBrains Mono, monospace; font-size:13px; font-weight:700;">▼ TOP 10 — DECREASE</p>', unsafe_allow_html=True)
    st.dataframe(
        valid.sort_values("ndbi_change", ascending=True)[display_cols].head(10),
        use_container_width=True, hide_index=True,
    )

st.markdown("---")
st.markdown(
    "<p class='caption-text' style='text-align:center;'>BORDER OPTICS — Source: Sentinel-2 SR Harmonized (Google Earth Engine)</p>",
    unsafe_allow_html=True,
)