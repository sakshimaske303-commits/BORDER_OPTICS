import streamlit as st
import pandas as pd
import numpy as np
from utils.theme import inject_theme, PALETTE
from utils.data import load_data

st.set_page_config(page_title="Night-Lights — BORDER OPTICS", page_icon="💡", layout="wide")
inject_theme()

villages, full_year, summer = load_data()

st.markdown("<h1>💡 NIGHT-LIGHTS ANALYSIS</h1>", unsafe_allow_html=True)
st.markdown(
    "<h3 style='text-align: center; font-weight: 700;'>VIIRS Radiance: 2021 → 2025</h3>",
    unsafe_allow_html=True,
)
st.markdown("---")

st.markdown("""
VIIRS DNB monthly night-lights radiance is used as a secondary, independent proxy for
economic activity and electrification — a rise here alongside NDBI growth strengthens
confidence that observed built-up change reflects genuine development rather than a
satellite-index artifact.
""")

st.markdown("---")

# ============================================================
# COMPOSITE WINDOW TOGGLE
# ============================================================
window = st.radio(
    "Composite window", ["Summer-Matched (Jun–Sep)", "Full-Year"],
    horizontal=True, key="lights_window",
)
df = summer if window.startswith("Summer") else full_year
valid = df.dropna(subset=["lights_change"])

c1, c2, c3, c4 = st.columns(4)
c1.metric("Mean Lights Change", f"{valid['lights_change'].mean():.4f}")
c2.metric("Median Lights Change", f"{valid['lights_change'].median():.4f}")
c3.metric("Villages Increased", f"{(valid['lights_change'] > 0).mean() * 100:.1f}%")
c4.metric("Villages Decreased", f"{(valid['lights_change'] < 0).mean() * 100:.1f}%")

st.markdown("---")

# ============================================================
# DISTRIBUTION (LIVE HISTOGRAM)
# ============================================================
st.markdown("### Distribution of Change")

counts, bin_edges = np.histogram(valid["lights_change"], bins=20)
bin_starts = [round(bin_edges[i], 2) for i in range(len(bin_edges) - 1)]
hist_df = pd.DataFrame({"lights_change_bin": bin_starts, "count": counts}).set_index("lights_change_bin")
st.bar_chart(hist_df, color=PALETTE["lights"])

st.markdown("---")

# ============================================================
# INTERPRETATION NOTE
# ============================================================
st.markdown(f"""
<div class="recon-card" style="border-left: 4px solid {PALETTE['lights']};">
    <p style="color: {PALETTE['lights']}; font-weight: 800; font-size: 0.85rem; text-transform: uppercase; margin-bottom: 10px;">Reading This Metric</p>
    <p style="color: {PALETTE['text_primary']}; font-size: 0.9rem; margin: 0;">
        VIIRS night-lights data has coarser spatial resolution (~500m) than Sentinel-2 and is
        more sensitive to cloud cover, moonlight, and sensor noise at small, remote
        settlements — many border villages register near-zero radiance in both years simply
        because they are too small or too dim for the sensor to resolve meaningful change. A
        null or non-significant result here is treated as an honest finding, not a failure —
        see Statistical Validation for the formal test.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ============================================================
# TOP MOVERS
# ============================================================
st.markdown("### Top Movers")

display_cols = [c for c in ["village", "district", "block", "state", "lights_before", "lights_after", "lights_change"] if c in valid.columns]

col_up, col_down = st.columns(2)
with col_up:
    st.markdown(f'<p style="color:{PALETTE["border_up"]}; font-family: JetBrains Mono, monospace; font-size:13px; font-weight:700;">▲ TOP 10 — INCREASE</p>', unsafe_allow_html=True)
    st.dataframe(
        valid.sort_values("lights_change", ascending=False)[display_cols].head(10),
        use_container_width=True, hide_index=True,
    )
with col_down:
    st.markdown(f'<p style="color:{PALETTE["border_down"]}; font-family: JetBrains Mono, monospace; font-size:13px; font-weight:700;">▼ TOP 10 — DECREASE</p>', unsafe_allow_html=True)
    st.dataframe(
        valid.sort_values("lights_change", ascending=True)[display_cols].head(10),
        use_container_width=True, hide_index=True,
    )

st.markdown("---")
st.markdown(
    "<p class='caption-text' style='text-align:center;'>BORDER OPTICS — Source: VIIRS DNB (Google Earth Engine)</p>",
    unsafe_allow_html=True,
)