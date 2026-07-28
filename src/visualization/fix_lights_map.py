import pandas as pd
import folium
import branca.colormap as cm

GOLD = "#D4AF37"

# --- reload data (same as main file) ---
villages = pd.read_csv("data/processed/border_optics_master_villages_with_distance.csv")
summer = pd.read_csv("data/processed/border_optics_village_results_summer_analyzed.csv")

merge_cols = ["village_id", "latitude", "longitude", "distance_to_border_km"]
summer = summer.merge(villages[merge_cols], on="village_id", how="left")

valid = summer.dropna(subset=["lights_change", "latitude", "longitude"]).copy()

# --- FIXED colors: white -> gold -> red (no more dark/black dots) ---
vmin, vmax = valid["lights_change"].min(), valid["lights_change"].max()
colormap = cm.LinearColormap(
    colors=["#FFFFFF", "#FFD700", "#FF3B30"],
    vmin=vmin, vmax=vmax,
    caption="VIIRS Night-Lights Change",
)

center_lat, center_lon = valid["latitude"].mean(), valid["longitude"].mean()
m = folium.Map(location=[center_lat, center_lon], tiles=None, zoom_start=7)

folium.TileLayer(tiles="CartoDB dark_matter", name="Dark Mode", control=True).add_to(m)
folium.TileLayer(tiles="Esri.WorldImagery", name="Satellite", control=True, attr="Esri").add_to(m)

for _, row in valid.iterrows():
    core_tag = "⭐ Core Sample" if row.get("is_core_sample", False) else ""
    popup_html = f"""
    <div style="font-family: Georgia, serif; font-size: 13px;">
        <b>{row['village']}</b> {core_tag}<br>
        {row['block']}, {row['district']}<br>
        <i>{row['state']}</i><br>
        VIIRS Night-Lights Change: {row['lights_change']:.3f}
    </div>
    """
    folium.CircleMarker(
        location=[row["latitude"], row["longitude"]],
        radius=6,
        color=colormap(row["lights_change"]),
        fill=True,
        fill_color=colormap(row["lights_change"]),
        fill_opacity=0.9,
        weight=1,
        popup=folium.Popup(popup_html, max_width=250),
    ).add_to(m)

bounds = [[valid["latitude"].min(), valid["longitude"].min()],
          [valid["latitude"].max(), valid["longitude"].max()]]
m.fit_bounds(bounds)

colormap.add_to(m)
folium.LayerControl(collapsed=False).add_to(m)

title_html = f"""
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
    <div style="font-size: 18px; font-weight: bold; color: {GOLD};">BORDER OPTICS — Night-Lights Change</div>
    <div style="font-size: 12px; color: #cccccc; margin-top: 3px;">Radiance change, 2021 vs 2025 (summer-matched composite)</div>
</div>
"""
m.get_root().html.add_child(folium.Element(title_html))

m.save("outputs/maps/village_lights_change_map.html")
print("Saved fixed lights map to outputs/maps/village_lights_change_map.html")