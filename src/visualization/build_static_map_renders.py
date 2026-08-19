"""
Matplotlib scatter-plot counterparts of the five interactive Folium maps
(which can't be captured in a static PDF) — for build_maps_plots_pdf.py.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt

BG = "#141414"
STATE_COLORS = {
    "Arunachal Pradesh": "#D4AF37",
    "Sikkim": "#4CAF50",
    "Uttarakhand": "#2196F3",
    "Himachal Pradesh": "#E63946",
}

plt.rcParams.update({
    "figure.facecolor": BG, "axes.facecolor": BG, "axes.edgecolor": "#555555",
    "axes.labelcolor": "#F2F2F0", "text.color": "#F2F2F0",
    "xtick.color": "#9A9A98", "ytick.color": "#9A9A98",
    "font.family": "sans-serif", "grid.color": "#2a2a2a", "grid.alpha": 0.4,
})


def draw_map(df, color_col, cmap, title, subtitle, out_path, discrete_state=False):
    valid = df.dropna(subset=[color_col, "latitude", "longitude"])
    fig, ax = plt.subplots(figsize=(9, 10))
    ax.grid(True, linewidth=0.4)

    if discrete_state:
        for state in valid["state"].unique():
            sub = valid[valid["state"] == state]
            ax.scatter(sub["longitude"], sub["latitude"], s=22, color=STATE_COLORS.get(state, "#999"),
                       label=state, edgecolor="white", linewidth=0.2, alpha=0.9)
        ax.legend(loc="upper right", facecolor="#1a1a1a", edgecolor="#555", labelcolor="#F2F2F0", fontsize=9)
    else:
        vmin, vmax = valid[color_col].quantile(0.02), valid[color_col].quantile(0.98)
        sc = ax.scatter(valid["longitude"], valid["latitude"], c=valid[color_col], cmap=cmap,
                        vmin=vmin, vmax=vmax, s=24, edgecolor="white", linewidth=0.2, alpha=0.95)
        cbar = fig.colorbar(sc, ax=ax, shrink=0.7, pad=0.02)
        cbar.set_label(color_col, color="#F2F2F0")
        cbar.ax.yaxis.set_tick_params(color="#9A9A98")
        plt.setp(cbar.ax.get_yticklabels(), color="#9A9A98")

    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title(f"{title}\n{subtitle}", fontsize=12, fontweight="bold", color="#F2F2F0", pad=14)
    fig.tight_layout()
    fig.savefig(out_path, dpi=170, facecolor=BG, bbox_inches="tight")
    plt.close(fig)
    print("Saved", out_path)


def main():
    villages = pd.read_csv("data/processed/border_optics_master_villages_with_distance.csv")
    full_year = pd.read_csv("data/processed/border_optics_village_results_analyzed.csv")
    summer = pd.read_csv("data/processed/border_optics_village_results_summer_analyzed.csv")

    merge_cols = ["village_id", "latitude", "longitude", "distance_to_border_km"]
    full_year = full_year.merge(villages[merge_cols], on="village_id", how="left")
    summer = summer.merge(villages[merge_cols], on="village_id", how="left")

    out_dir = "outputs/figures/static_map_renders"
    os.makedirs(out_dir, exist_ok=True)

    draw_map(full_year, "ndbi_change", "RdYlGn_r",
        "BORDER OPTICS — Village-Level NDBI Change",
        "Full-year composite, 2021 vs 2025 (static render of interactive map)",
        f"{out_dir}/map_ndbi_fullyear.png")

    draw_map(summer, "ndbi_change", "RdYlGn_r",
        "BORDER OPTICS — Village-Level NDBI Change",
        "Summer-matched composite (Jun-Sep), 2021 vs 2025 (static render of interactive map)",
        f"{out_dir}/map_ndbi_summer.png")

    draw_map(summer, "lights_change", "YlOrRd",
        "BORDER OPTICS — Village-Level Night-Lights Change",
        "VIIRS radiance change, summer-matched composite (static render of interactive map)",
        f"{out_dir}/map_lights_change.png")

    draw_map(summer, "distance_to_border_km", "cividis",
        "BORDER OPTICS — Village Proximity to Border/LAC",
        "Straight-line distance to nearest Natural Earth boundary segment (static render of interactive map)",
        f"{out_dir}/map_border_distance.png")

    draw_map(summer, "state", None,
        "BORDER OPTICS — Village Sample Overview",
        "All geocoded villages across 4 states, colored by state (static render of interactive map)",
        f"{out_dir}/map_state_overview.png", discrete_state=True)


if __name__ == "__main__":
    main()
