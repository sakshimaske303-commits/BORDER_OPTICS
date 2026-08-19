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
statistically meaningful, correlated with budget, predicted by proximity to the
border/LAC itself, and attributable to VVP-I specifically rather than a regional trend
shared by every village in these districts — benchmarked against a matched non-VVP
control group of 753 villages and a three-point 2021/2023/2025 trend.
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

st.markdown(f"""
<div class="recon-card" style="border-left: 4px solid {PALETTE['accent']}; margin-top: 16px;">
    <p style="color: {PALETTE['accent']}; font-weight: 800; font-size: 0.85rem; text-transform: uppercase; margin-bottom: 10px;">🎯 RQ5 / H4 — VVP-I-Attributable Effect</p>
    <p style="color: {PALETTE['text_primary']}; font-size: 0.9rem; margin: 0;">
        Is any detected change attributable to VVP-I specifically, or does it merely reflect
        a regional trend shared by every village in these border districts regardless of
        programme status? <b>H4:</b> VVP-I priority villages will show a significantly
        larger increase than a matched set of 753 non-VVP villages in the same 14
        districts over the same period — tested with a district-fixed-effects
        Difference-in-Differences model (see Statistical Validation).
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
            Methodology & Limitations. A matched <b>non-VVP control group</b> of 753 villages,
            drawn from the identical 14 districts, benchmarks this sample's change against
            the surrounding region's own trend over the same period.
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

# Proof-of-work popovers — pulsing button next to each methodology step, click to reveal screenshot
st.markdown(f"""
<style>
    div[data-testid="stPopover"] button {{
        animation: proof-blink 1.8s ease-in-out infinite;
        border: 3px solid {PALETTE['accent_vintage']} !important;
        width: 32px !important;
        height: 32px !important;
        border-radius: 50% !important;
        padding: 0 !important;
        min-height: unset !important;
        min-width: unset !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }}
    div[data-testid="stPopover"] button p {{
        margin: 0 !important;
        font-size: 0.95rem !important;
        line-height: 1 !important;
    }}
    @keyframes proof-blink {{
        0%, 100% {{ box-shadow: 0 0 0px rgba(255, 124, 172, 0); }}
        50% {{ box-shadow: 0 0 12px rgba(255, 124, 172, 0.85); }}
    }}
</style>
""", unsafe_allow_html=True)

import os as _os
PROOF_DIR = _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))), "outputs", "proof_screenshots")

def proof_popover(filename, caption):
    path = _os.path.join(PROOF_DIR, filename)
    with st.popover("📸"):
        if _os.path.exists(path):
            st.image(path, caption=caption, use_container_width=True)
        else:
            st.caption(f"Screenshot not added yet — save it as `outputs/proof_screenshots/{filename}`.")

st.markdown("1. **Village Acquisition** — Government portals and parliamentary annexures, cross-verified against official aggregate counts.")

col_m1, col_m2 = st.columns([0.94, 0.06])
with col_m1:
    st.markdown("2. **Geocoding** — Nominatim (primary), Bhuvan (Census-linked fallback), with manual district validation.")
with col_m2:
    proof_popover("01_village_data_excel.png", "Village dataset opened in Excel — raw geocoded village list with coordinates and border distance.")

col_m3, col_m4 = st.columns([0.94, 0.06])
with col_m3:
    st.markdown("3. **Satellite Extraction** — Sentinel-2 NDBI and VIIRS night-lights via Google Earth Engine, run identically for the treated sample and the 753-village non-VVP control group, at three time points (2021/2023/2025) and three buffer radii (250m/500m/1km), cloud-masked composites.")
with col_m4:
    proof_popover("02_gee_extraction_vscode.png", "extract_satellite_data.py open in VS Code, running the Earth Engine NDBI/VIIRS extraction pipeline.")

st.markdown("4. **Dual Compositing Windows** — Full-year and summer-matched (Jun–Sep), to separate genuine signal from seasonal artifacts.")

col_m5, col_m6, col_m6b = st.columns([0.88, 0.06, 0.06])
with col_m5:
    st.markdown("5. **Border Distance** — GeoPandas nearest-point distance to Natural Earth's border/LAC geometry, UTM-reprojected for accuracy.")
with col_m6:
    proof_popover("03_border_distance_vscode.png", "compute_border_distance.py open in VS Code — the GeoPandas nearest-point distance calculation.")
with col_m6b:
    proof_popover("05_qgis_border_distance_qa.png", "QGIS — visual QA of the border/LAC line against village points, graduated by distance-to-border, to sanity-check the GeoPandas calculation.")

col_m7, col_m8 = st.columns([0.94, 0.06])
with col_m7:
    st.markdown("6. **Statistical Testing** — Wilcoxon signed-rank (paired before/after) and Spearman correlation (RQ2, H3), with sample-size caveats disclosed throughout.")
with col_m8:
    proof_popover("04_statistical_testing_vscode.png", "Statistical Validation page code open in VS Code — the Wilcoxon signed-rank and Spearman correlation tests.")

st.markdown("7. **Control-Group DiD** — 753 non-VVP villages from the same 14 districts, via the OpenStreetMap Overpass API, compared against the treated sample with a district-fixed-effects Difference-in-Differences model (RQ5/H4).")
st.markdown("8. **Multi-Year Trend** — A third time point (2023) fit as a per-village linear trend across 2021/2023/2025, so a trend line — not a two-point difference — carries the evidentiary weight.")
st.markdown("9. **Buffer-Radius Sensitivity** — The same summer-window test re-run at 250m and 1km, on a sample-matched subset, to check the 500m buffer choice isn't itself driving the result.")

st.markdown("---")
st.markdown(
    "<p class='caption-text' style='text-align:center;'>BORDER OPTICS — Independent Geospatial Verification of VVP-I</p>",
    unsafe_allow_html=True,
)