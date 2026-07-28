import streamlit as st
import pandas as pd
from utils.theme import inject_theme, PALETTE
from utils.data import load_data

st.set_page_config(page_title="Study Design — BORDER OPTICS", page_icon="🏛️", layout="wide")
inject_theme()

villages, full_year, summer = load_data()

st.markdown("<h1>🏛️ STUDY DESIGN</h1>", unsafe_allow_html=True)
st.markdown(
    "<h3 style='text-align: center; font-weight: 700;'>Research Questions, Hypotheses, and Sample Design</h3>",
    unsafe_allow_html=True,
)
st.markdown("---")

st.markdown("""
### The Research Framework

Rather than relying on official VVP-I progress reports alone, this project measures
physical, observable change from space — built-up area expansion and night-time light
growth — at 258 individually geocoded villages, then tests whether that change is
statistically meaningful, correlated with budget, and predicted by proximity to the
border/LAC itself.
""")

st.markdown("---")

st.markdown("### Research Questions & Hypotheses")

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    <div class="recon-card" style="border-left: 4px solid {PALETTE['border_up']}; min-height: 210px; margin-bottom: 16px;">
        <p style="color: {PALETTE['border_up']}; font-weight: 800; font-size: 0.85rem; text-transform: uppercase; margin-bottom: 10px;">🏗️ RQ1 / H1 — Built-Up Change</p>
        <p style="color: {PALETTE['text_primary']}; font-size: 0.9rem; margin: 0;">
            Has physical built-up area increased in VVP-I sanctioned villages between 2021
            and 2025? <b>H1:</b> Villages will show a statistically significant increase in
            NDBI following programme sanction, measured via paired Sentinel-2 composites.
        </p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="recon-card" style="border-left: 4px solid {PALETTE['accent_vintage']}; min-height: 210px; margin-bottom: 16px;">
        <p style="color: {PALETTE['accent_vintage']}; font-weight: 800; font-size: 0.85rem; text-transform: uppercase; margin-bottom: 10px;">💰 RQ2 — Budget Correlation</p>
        <p style="color: {PALETTE['text_primary']}; font-size: 0.9rem; margin: 0;">
            Does the magnitude of observed change correlate with state-wise VVP-I budget
            allocation? Treated as <b>exploratory only</b>, given just four states in the
            sample — a directional signal, not a confirmatory test.
        </p>
    </div>
    """, unsafe_allow_html=True)

col3, col4 = st.columns(2)

with col3:
    st.markdown(f"""
    <div class="recon-card" style="border-left: 4px solid {PALETTE['lights']}; min-height: 210px;">
        <p style="color: {PALETTE['lights']}; font-weight: 800; font-size: 0.85rem; text-transform: uppercase; margin-bottom: 10px;">💡 RQ3 — Economic Activity</p>
        <p style="color: {PALETTE['text_primary']}; font-size: 0.9rem; margin: 0;">
            Has night-time light radiance (VIIRS) increased in parallel with built-up area
            growth, as a proxy for electrification and economic activity following programme
            implementation?
        </p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="recon-card" style="border-left: 4px solid {PALETTE['border_down']}; min-height: 210px;">
        <p style="color: {PALETTE['border_down']}; font-weight: 800; font-size: 0.85rem; text-transform: uppercase; margin-bottom: 10px;">📍 RQ4 / H3 — Border Proximity</p>
        <p style="color: {PALETTE['text_primary']}; font-size: 0.9rem; margin: 0;">
            Does distance to the border/LAC predict the pace of change? <b>H3:</b> Villages
            closer to the border will show greater built-up and night-lights change,
            consistent with strategic prioritization of frontier villages.
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ============================================================
# SAMPLE OVERVIEW
# ============================================================
st.markdown("### Sample Overview")

state_summary = villages.groupby("state").agg(
    villages_geocoded=("village_id", "count"),
)
if "is_core_sample" in villages.columns:
    state_summary["core_sample"] = villages.groupby("state")["is_core_sample"].sum().astype(int)
state_summary = state_summary.reset_index().rename(columns={"state": "State"})

col_a, col_b = st.columns([1.3, 1])

with col_a:
    st.dataframe(state_summary, use_container_width=True, hide_index=True)

with col_b:
    st.markdown(f"""
    <div class="recon-card">
        <p style="color: {PALETTE['accent']}; font-weight: 800; font-size: 0.85rem; text-transform: uppercase; margin-bottom: 10px;">Sample Composition</p>
        <p style="color: {PALETTE['text_primary']}; font-size: 0.9rem; margin-bottom: 10px;">
            <b>{len(villages)}</b> villages geocoded across <b>{villages['state'].nunique()}</b> border states.
        </p>
        <p style="color: {PALETTE['text_primary']}; font-size: 0.9rem; margin: 0;">
            Arunachal Pradesh, Sikkim, and Uttarakhand form the <b>core statistical sample</b>.
            Himachal Pradesh (7 villages) is an <b>illustrative case study</b> only — see
            Methodology & Limitations.
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ============================================================
# DATA ACQUISITION METHOD
# ============================================================
st.info("""
**Data Acquisition Method:** Village lists were sourced from state-level VVP-I portals,
Rajya Sabha and Lok Sabha parliamentary Q&A annexures, and cross-verified against official
aggregate village counts before acceptance. Coordinates were resolved via OpenStreetMap's
Nominatim API (primary), with ISRO's Bhuvan Village Geocoding API used as a Census-linked
fallback — each Bhuvan match manually validated against its expected district to prevent
cross-state name collisions.
""")

st.markdown("---")

st.markdown("### Methodology at a Glance")

st.markdown("""
1. **Village Acquisition** — Government portals and parliamentary annexures, cross-verified
   against official aggregate counts.

2. **Geocoding** — Nominatim (primary), Bhuvan (Census-linked fallback), with manual
   district validation.

3. **Satellite Extraction** — Sentinel-2 NDBI and VIIRS night-lights via Google Earth Engine,
   500m village buffers, cloud-masked composites.

4. **Dual Compositing Windows** — Full-year and summer-matched (Jun–Sep), to separate genuine
   signal from seasonal artifacts.

5. **Border Distance** — GeoPandas nearest-point distance to Natural Earth's border/LAC
   geometry, UTM-reprojected for accuracy.

6. **Statistical Testing** — Wilcoxon signed-rank (paired before/after) and Spearman
   correlation (RQ2, H3), with sample-size caveats disclosed throughout.
""")

st.markdown("---")
st.markdown(
    "<p class='caption-text' style='text-align:center;'>BORDER OPTICS — Independent Geospatial Verification of VVP-I</p>",
    unsafe_allow_html=True,
)