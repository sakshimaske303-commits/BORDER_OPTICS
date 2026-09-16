"""
Distance from each village to the nearest India boundary segment (Natural
Earth Admin 0 lines, so simplified in the disputed LAC sector - not a claim).
Nearest segment isn't always China - can be Nepal/Bhutan/Myanmar too.
Using geodesic distance (WGS84) instead of a single UTM zone since villages
span 77-97 deg E and a fixed zone overstated distance for the far-east ones.
"""

import geopandas as gpd
import pandas as pd
from pyproj import Geod
from shapely.ops import nearest_points

GEOD = Geod(ellps="WGS84")

# --- Load village points ---
villages = pd.read_csv("data/processed/border_optics_master_villages.csv")
villages_gdf = gpd.GeoDataFrame(
    villages,
    geometry=gpd.points_from_xy(villages["longitude"], villages["latitude"]),
    crs="EPSG:4326",
)

# --- Load boundary lines ---
boundary = gpd.read_file("data/raw/ne_10m_admin_0_boundary_lines_land/ne_10m_admin_0_boundary_lines_land.shp")

# field names vary by Natural Earth version, check columns if this filter comes up empty
print("Boundary file columns:", list(boundary.columns))
india_segments = boundary[
    (boundary.get("ADM0_A3_1") == "IND") | (boundary.get("ADM0_A3_2") == "IND")
    if "ADM0_A3_1" in boundary.columns else
    (boundary["ADM0_LEFT"] == "India") | (boundary["ADM0_RIGHT"] == "India")
].copy()
print(f"Found {len(india_segments)} India-related boundary segments")

def other_country(row):
    left, right = row.get("ADM0_LEFT"), row.get("ADM0_RIGHT")
    return right if left == "India" else left

india_segments["other_country"] = india_segments.apply(other_country, axis=1)

border_union_4326 = india_segments.union_all()

def nearest_border_km_and_country(point):
    nearest = nearest_points(point, border_union_4326)[1]
    _, _, dist_m = GEOD.inv(point.x, point.y, nearest.x, nearest.y)
    seg_idx = india_segments.distance(nearest).idxmin()
    country = india_segments.loc[seg_idx, "other_country"]
    return pd.Series({"distance_to_border_km": dist_m / 1000, "nearest_border_country": country})

nearest_info = villages_gdf.geometry.apply(nearest_border_km_and_country)

# --- Save back with the distance (+ nearest-country) column added ---
result = pd.concat([villages, nearest_info], axis=1)
result.to_csv("data/processed/border_optics_master_villages_with_distance.csv", index=False)
print(f"\nSaved {len(result)} villages with border distance to data/processed/border_optics_master_villages_with_distance.csv")
print(result["distance_to_border_km"].describe())
print("\nNearest-border-country breakdown (core sample):")
print(result.loc[result["is_core_sample"] == True, "nearest_border_country"].value_counts())
