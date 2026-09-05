import os
import pandas as pd
import folium
import branca.colormap as cm

# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------
GOLD = "#D4AF37"

STATE_COLORS = {
    "Arunachal Pradesh": "#D4AF37",   # gold
    "Sikkim": "#4CAF50",              # green
    "Uttarakhand": "#2196F3",         # blue
    "Himachal Pradesh": "#E63946",    # red
}

LEGEND_REPOSITION_CSS = """
<style>
    .legend {
        top: auto !important;
        bottom: 20px !important;
        left: 20px !important;
        right: auto !important;
    }
</style>
"""

# ---------------------------------------------------------
# LOAD + MERGE DATA
# (GEE exports don't carry latitude/longitude/distance -> pull from master file)
# ---------------------------------------------------------
villages = pd.read_csv("data/processed/border_optics_master_villages_with_distance.csv")

full_year = pd.read_csv("data/processed/border_optics_village_results_analyzed.csv")
summer = pd.read_csv("data/processed/border_optics_village_results_summer_analyzed.csv")

merge_cols = ["village_id", "latitude", "longitude", "distance_to_border_km"]

full_year = full_year.merge(villages[merge_cols], on="village_id", how="left")
summer = summer.merge(villages[merge_cols], on="village_id", how="left")

os.makedirs("outputs/interactive_maps/maps", exist_ok=True)


# ---------------------------------------------------------
# TITLE CARD HTML (shared gold-themed style)
# ---------------------------------------------------------
def title_html(title, subtitle):
    return f"""
    <div style="
        position: fixed;
        top: 15px; left: 60px;
        z-index: 9999;
        background-color: rgba(20, 20, 20, 0.9);
        border: 2px solid {GOLD};
        border-radius: 8px;
        padding: 10px 18px;
        color: white;
        font-family: 'Georgia', serif;
    ">
        <div style="font-size: 18px; font-weight: bold; color: {GOLD};">{title}</div>
        <div style="font-size: 12px; color: #cccccc; margin-top: 3px;">{subtitle}</div>
    </div>
    """


def add_base_tiles(m):
    folium.TileLayer(
        tiles="CartoDB dark_matter",
        name="Dark Mode",
        control=True,
    ).add_to(m)
    folium.TileLayer(
        tiles="Esri.WorldImagery",
        name="Satellite",
        control=True,
        attr="Esri",
    ).add_to(m)


# ---------------------------------------------------------
# MAP 1 & 2: NDBI CHANGE MAPS (full-year / summer-matched)
# ---------------------------------------------------------
def make_map(df, title, subtitle, out_path):
    valid = df.dropna(subset=["ndbi_change", "latitude", "longitude"]).copy()

    vmin, vmax = valid["ndbi_change"].min(), valid["ndbi_change"].max()
    colormap = cm.LinearColormap(
        colors=["#2ecc71", "#f4f4f4", "#e74c3c"],
        vmin=vmin, vmax=vmax,
        caption="NDBI Change (Built-up Index)",
    )

    center_lat, center_lon = valid["latitude"].mean(), valid["longitude"].mean()
    m = folium.Map(location=[center_lat, center_lon], tiles=None, zoom_start=7)
    add_base_tiles(m)

    for _, row in valid.iterrows():
        radius = 4 + min(abs(row["ndbi_change"]) * 40, 12)
        core_tag = "⭐ Core Sample" if row.get("is_core_sample", False) else ""
        popup_html = f"""
        <div style="font-family: Georgia, serif; font-size: 13px;">
            <b>{row['village']}</b> {core_tag}<br>
            {row['block']}, {row['district']}<br>
            <i>{row['state']}</i><br>
            NDBI before: {row['ndbi_before']:.3f}<br>
            NDBI after: {row['ndbi_after']:.3f}<br>
            <b>Change: {row['ndbi_change']:.3f}</b>
        </div>
        """
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=radius,
            color=colormap(row["ndbi_change"]),
            fill=True,
            fill_color=colormap(row["ndbi_change"]),
            fill_opacity=0.85,
            weight=1,
            popup=folium.Popup(popup_html, max_width=250),
        ).add_to(m)

    bounds = [[valid["latitude"].min(), valid["longitude"].min()],
              [valid["latitude"].max(), valid["longitude"].max()]]
    m.fit_bounds(bounds)

    colormap.add_to(m)
    m.get_root().html.add_child(folium.Element(LEGEND_REPOSITION_CSS))
    folium.LayerControl(collapsed=False).add_to(m)
    m.get_root().html.add_child(folium.Element(title_html(title, subtitle)))

    m.save(out_path)
    print(f"Saved interactive map to {out_path}")


# ---------------------------------------------------------
# GENERIC METRIC MAP (lights change / border distance / state overview)
# ---------------------------------------------------------
def make_metric_map(df, metric_col, colors, caption, title, subtitle, out_path, discrete_by_state=False):
    valid = df.dropna(subset=[metric_col, "latitude", "longitude"]).copy()

    colormap = None
    if not discrete_by_state:
        vmin, vmax = valid[metric_col].min(), valid[metric_col].max()
        colormap = cm.LinearColormap(colors=colors, vmin=vmin, vmax=vmax, caption=caption)

    center_lat, center_lon = valid["latitude"].mean(), valid["longitude"].mean()
    m = folium.Map(location=[center_lat, center_lon], tiles=None, zoom_start=7)
    add_base_tiles(m)

    for _, row in valid.iterrows():
        core_tag = "⭐ Core Sample" if row.get("is_core_sample", False) else ""

        if discrete_by_state:
            marker_color = STATE_COLORS.get(row["state"], "#999999")
        else:
            marker_color = colormap(row[metric_col])

        popup_html = f"""
        <div style="font-family: Georgia, serif; font-size: 13px;">
            <b>{row['village']}</b> {core_tag}<br>
            {row['block']}, {row['district']}<br>
            <i>{row['state']}</i><br>
            {caption}: {row[metric_col]:.3f}
        </div>
        """
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=6,
            color=marker_color,
            fill=True,
            fill_color=marker_color,
            fill_opacity=0.85,
            weight=1,
            popup=folium.Popup(popup_html, max_width=250),
        ).add_to(m)

    bounds = [[valid["latitude"].min(), valid["longitude"].min()],
              [valid["latitude"].max(), valid["longitude"].max()]]
    m.fit_bounds(bounds)

    if colormap is not None:
        colormap.add_to(m)
        m.get_root().html.add_child(folium.Element(LEGEND_REPOSITION_CSS))
    else:
        # discrete legend for state-overview map (already positioned bottom-left, no clash)
        legend_items = "".join(
            f'<div style="margin-top:4px;"><span style="display:inline-block;width:12px;height:12px;'
            f'background:{color};border-radius:50%;margin-right:6px;"></span>{state}</div>'
            for state, color in STATE_COLORS.items()
            if state in valid["state"].unique()
        )
        legend_html = f"""
        <div style="
            position: fixed;
            bottom: 30px; left: 30px;
            z-index: 9999;
            background-color: rgba(20, 20, 20, 0.9);
            border: 2px solid {GOLD};
            border-radius: 8px;
            padding: 10px 14px;
            color: white;
            font-family: 'Georgia', serif;
            font-size: 12px;
        ">
            <b style="color:{GOLD};">State</b>
            {legend_items}
        </div>
        """
        m.get_root().html.add_child(folium.Element(legend_html))

    folium.LayerControl(collapsed=False).add_to(m)
    m.get_root().html.add_child(folium.Element(title_html(title, subtitle)))

    m.save(out_path)
    print(f"Saved interactive map to {out_path}")


# ---------------------------------------------------------
# GENERATE ALL MAPS
# ---------------------------------------------------------

# 1 & 2: NDBI change maps
make_map(
    full_year,
    "BORDER OPTICS — NDBI Change (Full-Year Composite)",
    "NDBI change (built-up-surface proxy), 2021 vs 2025 (annual composite)",
    "outputs/interactive_maps/maps/village_ndbi_change_map_fullyear.html",
)

make_map(
    summer,
    "BORDER OPTICS — NDBI Change (Summer-Matched Composite)",
    "NDBI change (built-up-surface proxy), 2021 vs 2025 (Jun–Sep composite, season-matched)",
    "outputs/interactive_maps/maps/village_ndbi_change_map_summer.html",
)

# 3: Night-lights change map (summer-matched dataset)
make_metric_map(
    summer,
    metric_col="lights_change",
    colors=["#FFFFFF", "#FFD700", "#FF3B30"],
    caption="VIIRS Night-Lights Change",
    title="BORDER OPTICS — Night-Lights Change",
    subtitle="Radiance change, 2021 vs 2025 (summer-matched composite)",
    out_path="outputs/interactive_maps/maps/village_lights_change_map.html",
)

# 4: Border-distance map (uses master villages file directly)
make_metric_map(
    summer,
    metric_col="distance_to_border_km",
    colors=["#f4d35e", "#003049"],
    caption="Distance to Border/LAC (km)",
    title="BORDER OPTICS — Village Proximity to Border/LAC",
    subtitle="Straight-line distance to nearest Natural Earth boundary segment",
    out_path="outputs/interactive_maps/maps/village_border_distance_map.html",
)

# 5: State overview map (discrete coloring by state)
make_metric_map(
    summer,
    metric_col="ndbi_change",
    colors=[],
    caption="State",
    title="BORDER OPTICS — Village Sample Overview",
    subtitle="All geocoded villages across 4 states, colored by state",
    out_path="outputs/interactive_maps/maps/village_state_overview_map.html",
    discrete_by_state=True,
)