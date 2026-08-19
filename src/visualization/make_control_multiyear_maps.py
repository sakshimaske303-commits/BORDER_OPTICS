"""3 new interactive maps: control group, 2023-2025 recovery, and the 500m
coverage gap.
"""

import os
import pandas as pd
import folium
import branca.colormap as cm

GOLD = "#D4AF37"

LEGEND_CSS = """
<style>
    .legend { top: auto !important; bottom: 20px !important; left: 20px !important; right: auto !important; }
</style>
"""

os.makedirs("outputs/interactive_maps/maps", exist_ok=True)


def title_html(title, subtitle):
    return f"""
    <div style="position: fixed; top: 15px; left: 60px; z-index: 9999;
        background-color: rgba(20, 20, 20, 0.9); border: 2px solid {GOLD};
        border-radius: 8px; padding: 10px 18px; color: white; font-family: 'Georgia', serif;">
        <div style="font-size: 18px; font-weight: bold; color: {GOLD};">{title}</div>
        <div style="font-size: 12px; color: #cccccc; margin-top: 3px;">{subtitle}</div>
    </div>
    """


def add_base_tiles(m):
    folium.TileLayer(tiles="CartoDB dark_matter", name="Dark Mode", control=True).add_to(m)
    folium.TileLayer(tiles="Esri.WorldImagery", name="Satellite", control=True, attr="Esri").add_to(m)


def fit_bounds(m, lat_col, lon_col, df):
    m.fit_bounds([[df[lat_col].min(), df[lon_col].min()], [df[lat_col].max(), df[lon_col].max()]])


# ---------------------------------------------------------
# MAP 6: TREATED VS. CONTROL
# ---------------------------------------------------------
def make_treated_vs_control_map():
    treated = pd.read_csv("data/processed/border_optics_village_results_summer_analyzed.csv")
    treated = treated[treated["is_core_sample"] == True].copy()
    villages = pd.read_csv("data/processed/border_optics_master_villages_with_distance.csv")
    treated = treated.merge(villages[["village_id", "latitude", "longitude"]], on="village_id", how="left")
    treated["group"] = "Treated (VVP-I)"

    control = pd.read_csv("data/processed/border_optics_control_results_summer.csv")
    control["group"] = "Control (non-VVP)"

    cols = ["village", "district", "state", "latitude", "longitude", "ndbi_before", "ndbi_after", "group"]
    both = pd.concat([treated[cols], control[cols]], ignore_index=True).dropna(subset=["latitude", "longitude"])

    m = folium.Map(location=[both["latitude"].mean(), both["longitude"].mean()], tiles=None, zoom_start=7)
    add_base_tiles(m)

    group_colors = {"Treated (VVP-I)": "#FF7CAC", "Control (non-VVP)": "#A7E1C1"}
    for _, row in both.iterrows():
        change = (row["ndbi_after"] - row["ndbi_before"]) if pd.notna(row["ndbi_before"]) and pd.notna(row["ndbi_after"]) else None
        popup_html = f"""
        <div style="font-family: Georgia, serif; font-size: 13px;">
            <b>{row['village']}</b> — {row['group']}<br>
            {row['district']}, {row['state']}<br>
            NDBI change: {f"{change:.3f}" if change is not None else "no data"}
        </div>
        """
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]], radius=5,
            color=group_colors[row["group"]], fill=True, fill_color=group_colors[row["group"]],
            fill_opacity=0.8, weight=1, popup=folium.Popup(popup_html, max_width=250),
        ).add_to(m)

    fit_bounds(m, "latitude", "longitude", both)
    legend_html = f"""
    <div style="position: fixed; bottom: 30px; left: 30px; z-index: 9999;
        background-color: rgba(20,20,20,0.9); border: 2px solid {GOLD}; border-radius: 8px;
        padding: 10px 14px; color: white; font-family: 'Georgia', serif; font-size: 12px;">
        <b style="color:{GOLD};">Group</b>
        <div style="margin-top:4px;"><span style="display:inline-block;width:12px;height:12px;
            background:{group_colors['Treated (VVP-I)']};border-radius:50%;margin-right:6px;"></span>Treated (VVP-I)</div>
        <div style="margin-top:4px;"><span style="display:inline-block;width:12px;height:12px;
            background:{group_colors['Control (non-VVP)']};border-radius:50%;margin-right:6px;"></span>Control (non-VVP)</div>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))
    folium.LayerControl(collapsed=False).add_to(m)
    m.get_root().html.add_child(folium.Element(title_html(
        "BORDER OPTICS — Treated vs. Non-VVP Control Group",
        "251 treated villages (watermelon) vs. 753 matched control villages (mint), same 14 districts",
    )))
    out_path = "outputs/interactive_maps/maps/village_treated_vs_control_map.html"
    m.save(out_path)
    print(f"Saved {out_path}")


# ---------------------------------------------------------
# MAP 7: 2023 -> 2025 RECOVERY
# ---------------------------------------------------------
def make_recovery_map():
    df = pd.read_csv("data/processed/border_optics_multiyear_summer.csv")
    core = df[df["is_core_sample"] == True].dropna(subset=["ndbi_2023", "ndbi_2025", "latitude", "longitude"]).copy()
    core["recovery_change"] = core["ndbi_2025"] - core["ndbi_2023"]

    vmin, vmax = core["recovery_change"].min(), core["recovery_change"].max()
    colormap = cm.LinearColormap(colors=["#2ecc71", "#f4f4f4", "#e74c3c"], vmin=vmin, vmax=vmax,
                                  caption="NDBI Change, 2023 -> 2025")

    m = folium.Map(location=[core["latitude"].mean(), core["longitude"].mean()], tiles=None, zoom_start=7)
    add_base_tiles(m)

    for _, row in core.iterrows():
        popup_html = f"""
        <div style="font-family: Georgia, serif; font-size: 13px;">
            <b>{row['village']}</b><br>
            {row['district']}, {row['state']}<br>
            2021: {row['ndbi_2021']:.3f} · 2023: {row['ndbi_2023']:.3f} · 2025: {row['ndbi_2025']:.3f}<br>
            <b>2023->2025 change: {row['recovery_change']:.3f}</b>
        </div>
        """
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]], radius=6,
            color=colormap(row["recovery_change"]), fill=True, fill_color=colormap(row["recovery_change"]),
            fill_opacity=0.85, weight=1, popup=folium.Popup(popup_html, max_width=250),
        ).add_to(m)

    fit_bounds(m, "latitude", "longitude", core)
    colormap.add_to(m)
    m.get_root().html.add_child(folium.Element(LEGEND_CSS))
    folium.LayerControl(collapsed=False).add_to(m)
    m.get_root().html.add_child(folium.Element(title_html(
        "BORDER OPTICS — 2023-to-2025 Recovery",
        "The sub-period driving the reported 2021-vs-2025 increase (summer window, core sample)",
    )))
    out_path = "outputs/interactive_maps/maps/village_recovery_2023_2025_map.html"
    m.save(out_path)
    print(f"Saved {out_path}")


# ---------------------------------------------------------
# MAP 8: 500M COVERAGE GAP (ARCHIVE-TIMING CONFOUND)
# ---------------------------------------------------------
def make_coverage_gap_map():
    b250 = pd.read_csv("data/processed/border_optics_buffer250_summer.csv")
    b500 = pd.read_csv("data/processed/border_optics_village_results_summer_analyzed.csv")

    core = b250[b250["is_core_sample"] == True].copy()
    valid_at_500 = set(b500[b500["is_core_sample"] == True].dropna(subset=["ndbi_before", "ndbi_after"])["village_id"])
    core["coverage"] = core["village_id"].apply(lambda v: "Valid at 500m" if v in valid_at_500 else "Only valid at 250m/1km (archive backfill)")

    m = folium.Map(location=[core["latitude"].mean(), core["longitude"].mean()], tiles=None, zoom_start=7)
    add_base_tiles(m)

    cov_colors = {"Valid at 500m": "#A7E1C1", "Only valid at 250m/1km (archive backfill)": "#FF7CAC"}
    for _, row in core.dropna(subset=["latitude", "longitude"]).iterrows():
        popup_html = f"""
        <div style="font-family: Georgia, serif; font-size: 13px;">
            <b>{row['village']}</b><br>
            {row['district']}, {row['state']}<br>
            {row['coverage']}
        </div>
        """
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]], radius=5,
            color=cov_colors[row["coverage"]], fill=True, fill_color=cov_colors[row["coverage"]],
            fill_opacity=0.8, weight=1, popup=folium.Popup(popup_html, max_width=250),
        ).add_to(m)

    fit_bounds(m, "latitude", "longitude", core.dropna(subset=["latitude", "longitude"]))
    legend_html = f"""
    <div style="position: fixed; bottom: 30px; left: 30px; z-index: 9999;
        background-color: rgba(20,20,20,0.9); border: 2px solid {GOLD}; border-radius: 8px;
        padding: 10px 14px; color: white; font-family: 'Georgia', serif; font-size: 12px;">
        <b style="color:{GOLD};">500m Coverage</b>
        <div style="margin-top:4px;"><span style="display:inline-block;width:12px;height:12px;
            background:{cov_colors['Valid at 500m']};border-radius:50%;margin-right:6px;"></span>Valid at 500m</div>
        <div style="margin-top:4px;"><span style="display:inline-block;width:12px;height:12px;
            background:{cov_colors['Only valid at 250m/1km (archive backfill)']};border-radius:50%;margin-right:6px;"></span>Only 250m/1km</div>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))
    folium.LayerControl(collapsed=False).add_to(m)
    m.get_root().html.add_child(folium.Element(title_html(
        "BORDER OPTICS — 500m Coverage Gap",
        "Villages null at 500m but valid at 250m/1km — Sentinel-2 archive backfill, not a buffer-radius effect",
    )))
    out_path = "outputs/interactive_maps/maps/village_coverage_gap_map.html"
    m.save(out_path)
    print(f"Saved {out_path}")


if __name__ == "__main__":
    make_treated_vs_control_map()
    make_recovery_map()
    make_coverage_gap_map()
