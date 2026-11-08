import streamlit as st
import pandas as pd
from utils.theme import inject_theme, PALETTE
from utils.data import load_data

st.set_page_config(page_title="Study Design — BORDER OPTICS", layout="wide")
inject_theme()

villages, full_year, summer = load_data()

st.markdown("<h1>STUDY DESIGN</h1>", unsafe_allow_html=True)
st.markdown(
    "<h3 style='text-align: center; font-weight: 700;'>Research Question, Design and Sample</h3>",
    unsafe_allow_html=True,
)
st.markdown("---")

st.markdown("""
### The Research Framework

**Research question:** *Did VVP-I priority villages show more satellite-observed built-up and
night-light change between 2021 and 2025 than non-priority villages in the same districts?*

The **primary analysis** answers it directly: a within-district difference-in-differences
comparing 220 geocoded priority villages with 628 non-priority villages in the same 13 districts,
with NDBI and night lights as the two outcomes fixed in advance. Two subsidiary questions follow,
exactly as in the Research Paper.
""")

st.markdown("---")

st.markdown("### Research Question and Subsidiary Questions")

st.markdown(f"""
<div class="recon-card" style="border-left: 4px solid {PALETTE['accent']}; margin-bottom: 16px;">
    <p style="color: {PALETTE['accent']}; font-weight: 800; font-size: 0.85rem; text-transform: uppercase; margin-bottom: 10px;">Research Question — Programme Effect (primary)</p>
    <p style="color: {PALETTE['text_primary']}; font-size: 0.9rem; margin: 0;">
        Did priority villages change more than non-priority villages in the same districts between
        2021 and 2025? Answered with a two-period difference-in-differences with district-by-period
        fixed effects (villages compared within their own district), district-clustered errors, t with
        12 degrees of freedom and an exact wild cluster bootstrap (13 districts). Primary outcomes: Sentinel-2 NDBI and VIIRS night lights.
        Sentinel-1 radar and Dynamic World built-up probability are triangulation outcomes.
    </p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    <div class="recon-card" style="border-left: 4px solid {PALETTE['border_up']}; min-height: 210px; margin-bottom: 16px;">
        <p style="color: {PALETTE['border_up']}; font-weight: 800; font-size: 0.85rem; text-transform: uppercase; margin-bottom: 10px;">SQ1 — Measurement: What Could Each Measure Detect?</p>
        <p style="color: {PALETTE['text_primary']}; font-size: 0.9rem; margin: 0;">
            How large a change could each satellite measure, averaged over a 500 m buffer, actually
            detect? Google Open Buildings footprints are used to convert each index into square
            metres of buildings and to compare a plausible amount of construction with the
            design's minimum detectable effect.
        </p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="recon-card" style="border-left: 4px solid {PALETTE['border_down']}; min-height: 210px; margin-bottom: 16px;">
        <p style="color: {PALETTE['border_down']}; font-weight: 800; font-size: 0.85rem; text-transform: uppercase; margin-bottom: 10px;">SQ2 — Pattern: Does Change Track Border Distance? (descriptive)</p>
        <p style="color: {PALETTE['text_primary']}; font-size: 0.9rem; margin: 0;">
            Is change related to distance from the international boundary, as a securitization
            reading of the programme would suggest? Tested pooled and within districts, so that
            differences between districts are not mistaken for a gradient.
        </p>
    </div>
    """, unsafe_allow_html=True)

st.caption(
    "Also reported, descriptively only: each priority village's own 2021→2025 change (it cannot separate "
    "programme effects from regional trends)."
)

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
            Arunachal Pradesh and Uttarakhand form the <b>core statistical sample</b> (220 villages).
            Himachal Pradesh (7 villages) is an <b>illustrative case study</b> only, and Sikkim (31 villages)
            is outside the core sample from version 2.1, because none of its comparison villages could be
            verified inside its district — see Methodology & Limitations. A district-restricted
            <b>non-VVP control group</b> of 628 villages, drawn from the identical 13 districts, benchmarks this sample's change against
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

# pulsing button next to each step, click to see the proof screenshot
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
    with st.popover("View"):
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
    st.markdown("3. **Satellite Extraction** — Sentinel-2 NDBI, VIIRS night lights, Sentinel-1 radar and Dynamic World built-up probability via Google Earth Engine, 500 m buffer means. Treated and comparison villages both get 2021 and 2025 plus a 2019 pre-treatment year; the 2023 time point and the 250 m / 1 km radii were extracted for the treated core sample only. Google Open Buildings footprints are counted in the same buffers.")
with col_m4:
    proof_popover("02_gee_extraction_vscode.png", "extract_satellite_data.py open in VS Code, running the Earth Engine NDBI/VIIRS extraction pipeline.")

st.markdown("4. **Dual Compositing Windows** — Full-year and summer-matched (Jun–Sep), to separate genuine signal from seasonal artifacts.")

col_m5, col_m6, col_m6b = st.columns([0.88, 0.06, 0.06])
with col_m5:
    st.markdown("5. **Border Distance** — GeoPandas nearest-point distance to Natural Earth's border/LAC geometry, computed geodesically (WGS84 ellipsoid) rather than via a single map-projection zone, since the study area spans roughly 20 degrees of longitude.")
with col_m6:
    proof_popover("03_border_distance_vscode.png", "compute_border_distance.py open in VS Code — the GeoPandas nearest-point distance calculation.")
with col_m6b:
    proof_popover("05_qgis_border_distance_qa.png", "QGIS — visual QA of the border/LAC line against village points, graduated by distance-to-border, to sanity-check the GeoPandas calculation.")

col_m7, col_m8 = st.columns([0.94, 0.06])
with col_m7:
    st.markdown("6. **Descriptive Tests** — Wilcoxon signed-rank for each priority village's own change and Spearman correlation for border distance (SQ2, pooled and within districts); descriptive, not the programme estimate.")
with col_m8:
    proof_popover("04_statistical_testing_vscode.png", "Statistical Validation page code open in VS Code — the Wilcoxon signed-rank and Spearman correlation tests.")

st.markdown("7. **Primary Analysis: Difference-in-Differences** — 628 non-priority villages from the same 13 districts (OpenStreetMap Overpass, each checked against a district boundary), compared with the 220 priority villages using district-by-period fixed effects, t with 12 df and an exact wild cluster bootstrap; checked with a 2019–2021 placebo, leave-one-district-out and randomization inference.")
st.markdown("8. **Detectability (SQ1)** — Open Buildings footprints convert every DiD estimate into square metres of building-equivalent surface and show what each measure could have detected. A 2023 mid-point is shown descriptively only, because the 2023 composites may be unmasked.")
st.markdown("9. **Buffer-Radius Sensitivity** — The same summer-window test re-run at 250m and 1km, all three radii pulled the same day (n=220 at every radius), to check the 500m buffer choice isn't itself driving the result.")

st.markdown("---")
st.markdown(
    "<p class='caption-text' style='text-align:center;'>BORDER OPTICS — Evaluating a Place-Based Border Programme from Space: Evidence and Indicator Limits from India's Vibrant Villages Programme</p>",
    unsafe_allow_html=True,
)