import streamlit as st
import os
from utils.theme import inject_theme

st.set_page_config(page_title="Mountain Geomorphology & Climatology — BORDER OPTICS", page_icon="🏔️", layout="wide")
inject_theme()

st.markdown("<h1>🏔️ READING A VILLAGE ON A SLOPE</h1>", unsafe_allow_html=True)
st.markdown(
    "<h3 style='text-align: center; font-weight: 700;'>The Himalayan Geomorphology and Climatology Behind Border Optics' Data</h3>",
    unsafe_allow_html=True,
)
st.markdown("---")

# ============================================================
# DIAGRAM
# ============================================================
IMG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "outputs", "figures", "imgg1.png")
col_a, col_b, col_c = st.columns([0.2, 5.9, 0.2])
with col_b:
    if os.path.exists(IMG_PATH):
        st.image(IMG_PATH, use_container_width=True)
    else:
        st.warning("Diagram not found at outputs/figures/imgg1.png")
    st.markdown(
        "<p style='text-align:center;' class='caption-text'>Terrain-geometry and climatology schematic — Himalayan border belt.</p>",
        unsafe_allow_html=True,
    )

st.markdown("---")

# ============================================================
# SECTION 1 — TERRAIN GEOMETRY DISTORTS THE SIGNAL
# ============================================================
st.markdown("### High Relief Distorts What a Satellite Actually Sees")

st.markdown("""
BORDER OPTICS' 258 study villages sit across some of the steepest, highest-relief terrain any
satellite-based verification study can be run on — the Himalayan border belt of Arunachal
Pradesh, Sikkim, Uttarakhand, Himachal Pradesh, and Ladakh. That relief is not a neutral
backdrop; it actively distorts the built-up-area signal this project measures. A satellite
sensor images the ground along an oblique line of sight, not straight down, so a slope facing
away from the sensor falls into **shadow**, while a slope facing toward it appears compressed —
**foreshortening**, where a physically large slope area is mapped into a deceptively small number
of pixels. Both effects change how much "built-up" surface a village's true footprint appears to
occupy in a Sentinel-2 scene, independent of any real construction activity — a geometric
confound layered on top of the genuine NDBI signal this project is trying to isolate.
""")

st.markdown("---")

# ============================================================
# SECTION 2 — CLIMATOLOGY OF ALTITUDE
# ============================================================
st.markdown("### Altitude Is a Climate Variable, Not Just an Elevation Number")

st.markdown("""
Himalayan villages also sit across a genuine **climatological gradient with elevation**, not
just a topographic one: valley floors carry a subtropical or temperate climate, higher slopes
transition to alpine conditions, and the highest terrain holds permanent snow — a zonation
pattern driven by the roughly 6.5 °C per 1000 m environmental lapse rate. This altitudinal
climatology is precisely why the same village looks completely different across a year: a
clear, snow-free scene in one season and a partially snow- and cloud-obscured scene in another,
purely as a function of where that village sits on the altitude gradient — the "clear season vs.
snow & cloud season" comparison in the diagram above.
""")

st.markdown("---")

# ============================================================
# SECTION 3 — TIE TO THE PROJECT'S OWN METHODOLOGICAL FINDING
# ============================================================
st.markdown("### Why This Is the Physical Root of a Documented Trade-Off")

st.markdown("""
This is not an abstract concern — it is the physical mechanism behind a trade-off BORDER OPTICS
already discloses on its Methodology & Limitations page: full-year composites risk snow-cover
contamination at high altitude, while summer-matched composites avoid snow but are more exposed
to monsoon cloud, which eliminated nearly all valid observations for Sikkim in that window. Both
failure modes trace back to the same underlying cause mapped in the diagram above — Himalayan
relief drives both the imaging-geometry distortion and the altitude-driven seasonal masking that
together produce an unstable, composite-window-dependent change estimate for the highest-altitude
villages in the sample.
""")

st.markdown("---")
st.markdown(
    "<p class='caption-text' style='text-align:center;'>BORDER OPTICS — The Terrain Behind the Trade-Off</p>",
    unsafe_allow_html=True,
)
