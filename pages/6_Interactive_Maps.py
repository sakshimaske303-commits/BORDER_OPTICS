import streamlit as st
import streamlit.components.v1 as components
import os
from utils.theme import inject_theme, PALETTE
from utils.data import load_data

st.set_page_config(page_title="Interactive Maps — BORDER OPTICS", page_icon="🗺️", layout="wide")
inject_theme()

villages, full_year, summer = load_data()

st.markdown("<h1>🗺️ INTERACTIVE MAPS</h1>", unsafe_allow_html=True)
st.markdown(
    "<h3 style='text-align: center; font-weight: 700;'>Village-Level Satellite Evidence</h3>",
    unsafe_allow_html=True,
)
st.markdown("---")

st.markdown("""
Every geocoded village plotted on a live satellite/dark basemap. Hover or click any
marker for its individual before/after values.
""")

st.markdown("---")

MAP_DIR = "outputs/interactive_maps/maps"

MAP_OPTIONS = {
    "Built-Up Change — Full-Year Composite": "village_ndbi_change_map_fullyear.html",
    "Built-Up Change — Summer-Matched Composite": "village_ndbi_change_map_summer.html",
    "Night-Lights Change": "village_lights_change_map.html",
    "Border / LAC Proximity": "village_border_distance_map.html",
    "State Overview": "village_state_overview_map.html",
}

choice = st.selectbox("Select a map layer", list(MAP_OPTIONS.keys()))
map_path = os.path.join(MAP_DIR, MAP_OPTIONS[choice])

if os.path.exists(map_path):
    with open(map_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    components.html(html_content, height=680, scrolling=False)
else:
    st.warning(f"Missing map file: `{map_path}` — check the folder path matches where your maps were saved.")

st.markdown("---")

st.markdown(f"""
<div class="recon-card">
    <p style="color: {PALETTE['accent']}; font-weight: 800; font-size: 0.85rem; text-transform: uppercase; margin-bottom: 10px;">About These Maps</p>
    <p style="color: {PALETTE['text_primary']}; font-size: 0.9rem; margin: 0;">
        Each map is a standalone Folium visualization with its own dark-mode and satellite
        basemap toggle. Marker color encodes the selected metric (built-up change,
        night-lights change, or distance to border), and marker click reveals the underlying
        village name, block, district, state, and raw before/after values used in the analysis.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")
st.markdown(
    "<p class='caption-text' style='text-align:center;'>BORDER OPTICS — Maps built with Folium, dark-mode and satellite basemaps</p>",
    unsafe_allow_html=True,
)