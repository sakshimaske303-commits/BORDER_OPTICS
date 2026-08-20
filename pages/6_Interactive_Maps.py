import streamlit as st
import streamlit.components.v1 as components
import os
from utils.theme import inject_theme, PALETTE
from utils.data import load_data

st.set_page_config(page_title="Interactive Maps — BORDER OPTICS", page_icon="🗺️", layout="wide")
inject_theme()

villages, full_year, summer = load_data()

st.markdown("<h1>🗺️ INTERACTIVE MAPS &amp; PLOTS</h1>", unsafe_allow_html=True)
st.markdown(
    "<h3 style='text-align: center; font-weight: 700;'>Village-Level Satellite Evidence and Headline Charts</h3>",
    unsafe_allow_html=True,
)
st.markdown("---")

st.markdown("""
Every geocoded village — plus the 753-village non-VVP control group — plotted on a live
satellite/dark basemap, plus the three headline statistical charts as hoverable, toggleable
plots instead of flat images. Hover or click any marker or data point for its exact value.
""")

st.markdown("---")

MAP_DIR = "outputs/interactive_maps/maps"
PLOT_DIR = "outputs/interactive_maps/plots"

MAP_OPTIONS = {
    "Built-Up Change — Full-Year Composite": (MAP_DIR, "village_ndbi_change_map_fullyear.html"),
    "Built-Up Change — Summer-Matched Composite": (MAP_DIR, "village_ndbi_change_map_summer.html"),
    "Night-Lights Change": (MAP_DIR, "village_lights_change_map.html"),
    "Border / LAC Proximity": (MAP_DIR, "village_border_distance_map.html"),
    "State Overview": (MAP_DIR, "village_state_overview_map.html"),
    "Treated vs. Non-VVP Control Group (H4)": (MAP_DIR, "village_treated_vs_control_map.html"),
    "2023-to-2025 Recovery (Multi-Year Trend)": (MAP_DIR, "village_recovery_2023_2025_map.html"),
    "500m Coverage Gap (Buffer-Sensitivity Diagnostic)": (MAP_DIR, "village_coverage_gap_map.html"),
    "Control-Group DiD Effect": (PLOT_DIR, "control_group_did_effect.html"),
    "Multi-Year Trend (2021 / 2023 / 2025)": (PLOT_DIR, "multiyear_trend.html"),
    "Buffer-Radius Sensitivity": (PLOT_DIR, "buffer_sensitivity.html"),
}

choice = st.selectbox("Select a map or chart", list(MAP_OPTIONS.keys()))
map_dir, map_file = MAP_OPTIONS[choice]
map_path = os.path.join(map_dir, map_file)

if os.path.exists(map_path):
    with open(map_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    components.html(html_content, height=680, scrolling=False)
else:
    st.warning(f"Missing file: `{map_path}` — check the folder path matches where your files were saved.")

st.markdown("---")

st.markdown(f"""
<div class="recon-card">
    <p style="color: {PALETTE['accent']}; font-weight: 800; font-size: 0.85rem; text-transform: uppercase; margin-bottom: 10px;">About These Maps &amp; Plots</p>
    <p style="color: {PALETTE['text_primary']}; font-size: 0.9rem; margin: 0;">
        Each map is a standalone Folium visualization with its own dark-mode and satellite
        basemap toggle. Marker color encodes the selected metric (built-up change,
        night-lights change, distance to border, treated/control group, or 500m coverage),
        and marker click reveals the underlying village name, block, district, state, and
        raw values used in the analysis. Each plot is a standalone Plotly chart — hover any
        point for its exact value, and toggle series on or off in the legend.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")
st.markdown(
    "<p class='caption-text' style='text-align:center;'>BORDER OPTICS — Maps built with Folium, plots built with Plotly</p>",
    unsafe_allow_html=True,
)