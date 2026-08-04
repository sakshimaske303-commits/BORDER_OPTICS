import streamlit as st
from utils.theme import inject_theme, PALETTE
from utils.data import load_data

st.set_page_config(page_title="Methodology & Limitations — BORDER OPTICS", page_icon="📖", layout="wide")
inject_theme()

villages, full_year, summer = load_data()

st.markdown("<h1>📖 METHODOLOGY & LIMITATIONS</h1>", unsafe_allow_html=True)
st.markdown(
    "<h3 style='text-align: center; font-weight: 700;'>Full Transparency and Reproducibility</h3>",
    unsafe_allow_html=True,
)
st.markdown("---")

st.markdown("### Data Sources")

col1, col2 = st.columns(2)
with col1:
    st.markdown("""
    - **Village Lists** — State VVP-I portals, Rajya Sabha / Lok Sabha Q&A annexures
    - **Geocoding** — OpenStreetMap Nominatim, ISRO Bhuvan Village Geocoding API
    - **Built-Up Index** — Sentinel-2 SR Harmonized (NDBI), Google Earth Engine
    """)
with col2:
    st.markdown("""
    - **Night-Lights** — VIIRS DNB monthly composites, Google Earth Engine
    - **Border/LAC Geometry** — Natural Earth 10m Admin-0 Boundary Lines
    - **Budget Figures** — Independently compiled from parliamentary records
    """)

st.markdown("---")

st.markdown("### Processing Pipeline")

st.markdown("""
Each village is buffered by 500m and used as the region for `reduceRegion` over
cloud-masked Sentinel-2 composites (QA60 bitmask) and VIIRS monthly composites, for both
a full-year window and a season-matched (Jun–Sep) window in 2021 and 2025. Villages with
an empty composite in either year are marked null rather than defaulted to zero, and
image-count columns are retained for quality auditing. Village coordinates and
distance-to-border are computed separately via GeoPandas (UTM 44N / EPSG:32644
reprojection, nearest-point distance to the nearest India border/LAC segment) and merged
in by village ID.
""")

st.markdown("---")

st.markdown("### Statistical Methods")

st.markdown("""
**Wilcoxon signed-rank test** (paired, non-parametric) for before/after change in NDBI
and night-lights, since normality cannot be assumed at this sample size. **Spearman
correlation** (rank-based, robust to non-linear monotonic relationships) for state-level
budget vs. change (RQ2) and distance-to-border vs. change (H3). Both correlations are
explicitly exploratory given small state and moderate village counts respectively.
""")

st.markdown("---")

st.markdown("### Known Limitations")

with st.expander("**Ladakh (UT) — Excluded from Analysis**"):
    st.markdown("""
    No publicly indexed government source with village-wise VVP-I data was found for
    Ladakh's 35 sanctioned villages, despite a deliberate search across state portals,
    parliamentary annexures, and secondary sources. Ladakh is fully excluded from this
    analysis rather than approximated. This is documented as an open gap, not silently
    omitted.
    """)

with st.expander("**Himachal Pradesh — Illustrative Only, Not Core Sample**"):
    st.markdown("""
    Of 75 priority villages under the VVP-I Action Plan (₹658.31 crore), only 51
    inhabited villages could be identified by name (32 in Kinnaur, 19 in Lahaul and
    Spiti), and only 7 of those could be reliably geocoded. Himachal Pradesh is treated
    as an illustrative case study, not part of the core statistical sample used for
    hypothesis testing.
    """)

with st.expander("**Uttarakhand — Residual Block Ambiguity**"):
    st.markdown("""
    Block-level assignment for 19 villages in Pithoragarh district carries residual
    ambiguity between Dharchula and Kanalichhina blocks, since no official village-wise
    annexure disambiguating them was found. Block confidence is tracked per-village in
    the underlying dataset.
    """)

with st.expander("**Border/LAC Geometry — A Cartographic Proxy, Not a Legal Claim**"):
    st.markdown("""
    Distance to border is computed against Natural Earth's 10m Admin-0 boundary lines.
    Along the Line of Actual Control this is a cartographic convenience for measurement
    purposes only — it is not a legal, diplomatic, or political claim. The LAC is disputed
    and is not a settled international boundary.
    """)

with st.expander("**Composite Window Trade-Off — Snow vs. Monsoon Cloud**"):
    st.markdown("""
    Full-year composites risk snow-cover contamination in high-altitude Himalayan
    terrain. Summer-matched (Jun–Sep) composites avoid snow but are vulnerable to monsoon
    cloud cover, which eliminated nearly all valid observations for Sikkim in that window.
    Where a result's direction or significance changes between the two windows, that
    instability is reported as a finding in itself — see Statistical Validation.
    """)

st.markdown("---")

st.warning("""
**Budget correlation (RQ2) is exploratory only** — with just four states in the sample,
this should not be read as a confirmatory or causal result.
""")

st.error("""
**H3 border-proximity correlation should be read alongside the LAC geometry caveat above**
— any observed relationship reflects distance to a disputed, de facto line, not a settled
legal boundary.
""")

st.markdown("---")
st.markdown(
    "<p class='caption-text' style='text-align:center;'>BORDER OPTICS — A Satellite-Based Verification Framework</p>",
    unsafe_allow_html=True,
)