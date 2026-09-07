"""Distance from each village to the nearest India international-boundary
segment, using Natural Earth's Admin 0 boundary lines -- a simplification
in the disputed LAC sector, not an official claim. Note: "nearest India
boundary segment" is not always China/LAC -- it can be Nepal, Bhutan, or
Myanmar depending on the village's location (see the per-village
nearest_border_country column and Development Log Entry 18 for exactly how
many core-sample villages that affects).

Distance itself is computed geodesically (WGS84 ellipsoid, via pyproj's
Geod), not by projecting into a single UTM zone. A single UTM zone (44N
was used originally) is only accurate near its own central meridian
(81 deg E); this study's villages span roughly 77-97 deg E, so the old
method systematically overstated distance for villages far from 81 deg E
-- up to ~3% for Arunachal Pradesh's easternmost villages, negligible for
Uttarakhand. Geodesic distance has no such zone dependency. See
Development Log Entry 18 for the before/after comparison.
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

# Filter to segments involving India (field names can vary by Natural Earth version —
# print the columns first if this filter comes back empty, and adjust)
print("Boundary file columns:", list(boundary.columns))
india_segments = boundary[
    (boundary.get("ADM0_A3_1") == "IND") | (boundary.get("ADM0_A3_2") == "IND")
    if "ADM0_A3_1" in boundary.columns else
    (boundary["ADM0_LEFT"] == "India") | (boundary["ADM0_RIGHT"] == "India")
].copy()
print(f"Found {len(india_segments)} India-related boundary segments")

# Track which country is on the other side of each segment, so we can report
# per-village which country's boundary actually ended up nearest (it is not
# always China) rather than silently collapsing that information away.
def other_country(row):
    left, right = row.get("ADM0_LEFT"), row.get("ADM0_RIGHT")
    return right if left == "India" else left

india_segments["other_country"] = india_segments.apply(other_country, axis=1)

# --- Find the nearest boundary point in unprojected lon/lat space (adequate for
# identifying *which* point is nearest at these scales), then compute the actual
# distance geodesically on the WGS84 ellipsoid so there is no map-projection
# distortion in the reported number regardless of how far a village sits from
# any single zone's central meridian. ---
border_union_4326 = india_segments.union_all()

def nearest_border_km_and_country(point):
    nearest = nearest_points(point, border_union_4326)[1]
    _, _, dist_m = GEOD.inv(point.x, point.y, nearest.x, nearest.y)
    # which segment produced this nearest point, to attribute a country
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
