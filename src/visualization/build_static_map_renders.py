"""Static map renders (outputs/figures/static_map_renders/), rebuilt in
Development Log Entry 49 to include basic cartographic elements the earlier
versions lacked.

Each map has two regional panels (west: Uttarakhand + Himachal Pradesh;
east: Sikkim + Arunachal Pradesh), because the study villages sit in two
clusters ~800 km apart, and adds:
  - Natural Earth 1:10m India boundary lines, coloured by neighbouring
    country (cartographic only -- the LAC alignment is disputed)
  - an equal-distance aspect ratio (1 / cos(latitude)), a scale bar and a
    north arrow
  - Himachal Pradesh's 7 illustrative villages drawn as triangles, apart
    from the 251-village core sample
  - change maps on a diverging scale centred on zero, with arrows on the
    colourbar marking values clipped at the 2nd/98th percentile
  - the overview map also shows the 721 control villages
Reads the boundary through src/analysis/border_geometry.py (no geopandas
needed).

run from the repository root:  python src/visualization/build_static_map_renders.py
"""

import math
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import TwoSlopeNorm
from matplotlib.lines import Line2D

sys.path.insert(0, "src/analysis")
from border_geometry import load_india_segments  # noqa: E402

OUT_DIR = "outputs/figures/static_map_renders"
REGIONS = {"West (Uttarakhand, Himachal Pradesh)": (77.3, 81.6, 29.4, 32.5),
           "East (Sikkim, Arunachal Pradesh)": (87.8, 97.6, 26.8, 29.6)}
BORDER_COLORS = {"China": "#C0392B", "Nepal": "#7F8C8D", "Bhutan": "#7F8C8D", "Myanmar": "#7F8C8D"}
STATE_COLORS = {"Arunachal Pradesh": "#B8860B", "Sikkim": "#2E8B57", "Uttarakhand": "#1F5FA8",
                "Himachal Pradesh": "#8E44AD"}
plt.rcParams.update({"figure.dpi": 150, "font.size": 9})
SEGMENTS = load_india_segments()


def draw_borders(ax):
    for seg in SEGMENTS:
        color = BORDER_COLORS.get(seg["other_country"], "#BBBBBB")
        lw = 1.6 if seg["other_country"] == "China" else 1.0
        for part in seg["parts"]:
            ax.plot(part[:, 0], part[:, 1], color=color, linewidth=lw, zorder=1)


def scale_bar(ax, lat, km=50):
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    deg = km / (111.32 * math.cos(math.radians(lat)))
    xs, ys = x0 + 0.05 * (x1 - x0), y0 + 0.06 * (y1 - y0)
    ax.plot([xs, xs + deg], [ys, ys], color="black", linewidth=3, solid_capstyle="butt", zorder=5)
    ax.text(xs + deg / 2, ys + 0.03 * (y1 - y0), f"{km} km", ha="center", fontsize=8, zorder=5)


def north_arrow(ax):
    ax.annotate("N", xy=(0.95, 0.96), xytext=(0.95, 0.74), xycoords="axes fraction", ha="center",
                fontsize=10, fontweight="bold", arrowprops=dict(arrowstyle="-|>", color="black", lw=1.5))


def setup(ax, name, box):
    x0, x1, y0, y1 = box
    ax.set_xlim(x0, x1)
    ax.set_ylim(y0, y1)
    ax.set_aspect(1 / math.cos(math.radians((y0 + y1) / 2)))
    ax.set_title(name, fontsize=9.5)
    ax.set_xlabel("Longitude (°E)")
    ax.set_ylabel("Latitude (°N)")
    ax.grid(True, linewidth=0.3, alpha=0.5)
    draw_borders(ax)
    scale_bar(ax, (y0 + y1) / 2)
    north_arrow(ax)


def border_legend():
    return [Line2D([0], [0], color="#C0392B", lw=1.6, label="India–China boundary (Natural Earth; LAC disputed)"),
            Line2D([0], [0], color="#7F8C8D", lw=1.0, label="India–Nepal / Bhutan / Myanmar boundary")]


def value_map(df, col, label, title, path, diverging=True, cmap="RdBu_r"):
    v = df.dropna(subset=[col, "latitude", "longitude"])
    lo, hi = v[col].quantile([0.02, 0.98])
    if diverging:
        bound = max(abs(lo), abs(hi))
        norm, vmin, vmax = TwoSlopeNorm(0, -bound, bound), None, None
    else:
        norm, vmin, vmax = None, lo, hi
    fig, axes = plt.subplots(1, 2, figsize=(14, 4.6), gridspec_kw={"width_ratios": [1, 2.1]})
    sc = None
    for ax, (name, box) in zip(axes, REGIONS.items()):
        setup(ax, name, box)
        core = v[v.is_core_sample == True]
        hp = v[v.is_core_sample != True]
        sc = ax.scatter(core.longitude, core.latitude, c=core[col], cmap=cmap, norm=norm, vmin=vmin, vmax=vmax,
                        s=28, edgecolor="black", linewidth=0.3, zorder=3)
        if len(hp):
            ax.scatter(hp.longitude, hp.latitude, c=hp[col], cmap=cmap, norm=norm, vmin=vmin, vmax=vmax,
                       s=40, marker="^", edgecolor="black", linewidth=0.4, zorder=3)
    cb = fig.colorbar(sc, ax=axes, shrink=0.75, pad=0.01, extend="both")
    cb.set_label(label)
    handles = border_legend() + [Line2D([0], [0], marker="^", color="w", markerfacecolor="grey",
                                        markeredgecolor="black", markersize=7,
                                        label="Himachal Pradesh, illustrative (not in core sample)")]
    fig.legend(handles=handles, loc="lower center", ncol=3, fontsize=8, frameon=False)
    fig.suptitle(title, fontsize=11)
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print("Saved", path)


def overview(villages, controls, path):
    fig, axes = plt.subplots(1, 2, figsize=(14, 4.6), gridspec_kw={"width_ratios": [1, 2.1]})
    for ax, (name, box) in zip(axes, REGIONS.items()):
        setup(ax, name, box)
        ax.scatter(controls.longitude, controls.latitude, s=7, color="#AAAAAA", zorder=2)
        for st, g in villages.groupby("state"):
            marker = "^" if st == "Himachal Pradesh" else "o"
            ax.scatter(g.longitude, g.latitude, s=24, marker=marker, color=STATE_COLORS[st],
                       edgecolor="black", linewidth=0.3, zorder=3)
    handles = border_legend() + [
        Line2D([0], [0], marker="o", color="w", markerfacecolor=c, markeredgecolor="black", markersize=7,
               label=f"{st} — VVP-I priority village ({int((villages.state == st).sum())})")
        for st, c in STATE_COLORS.items() if st != "Himachal Pradesh"] + [
        Line2D([0], [0], marker="^", color="w", markerfacecolor=STATE_COLORS["Himachal Pradesh"],
               markeredgecolor="black", markersize=7, label="Himachal Pradesh — illustrative only (7)"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="#AAAAAA", markersize=5,
               label=f"Control village, same 14 districts ({len(controls)})")]
    fig.legend(handles=handles, loc="lower center", ncol=3, fontsize=8, frameon=False)
    fig.suptitle("Study area: 251 core VVP-I priority villages, 7 illustrative villages and 721 control villages",
                 fontsize=11)
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print("Saved", path)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    villages = pd.read_csv("data/processed/border_optics_master_villages_with_distance.csv")
    controls = pd.read_csv("data/processed/border_optics_control_villages.csv")
    fy = pd.read_csv("data/processed/border_optics_village_results_analyzed.csv").drop(
        columns=["latitude", "longitude"], errors="ignore").merge(
        villages[["village_id", "latitude", "longitude", "distance_to_border_km"]], on="village_id")
    su = pd.read_csv("data/processed/border_optics_village_results_summer_analyzed.csv").drop(
        columns=["latitude", "longitude"], errors="ignore").merge(
        villages[["village_id", "latitude", "longitude", "distance_to_border_km"]], on="village_id")

    overview(villages, controls, f"{OUT_DIR}/map_state_overview.png")
    value_map(fy, "ndbi_change", "Change in 500 m buffer-mean NDBI (red = increase)",
              "NDBI change 2021→2025, full-year composites", f"{OUT_DIR}/map_ndbi_fullyear.png")
    value_map(su, "ndbi_change", "Change in 500 m buffer-mean NDBI (red = increase)",
              "NDBI change 2021→2025, summer (Jun–Sep) composites", f"{OUT_DIR}/map_ndbi_summer.png")
    value_map(su, "lights_change", "Change in VIIRS radiance, nW/cm²/sr (red = brighter)",
              "Night-light change 2021→2025, summer composites", f"{OUT_DIR}/map_lights_change.png")
    value_map(su, "distance_to_border_km", "Distance to nearest India boundary (km)",
              "Distance from each village to the nearest India boundary line (comparative, not authoritative)",
              f"{OUT_DIR}/map_border_distance.png", diverging=False, cmap="viridis_r")


if __name__ == "__main__":
    main()
