"""Distance from each village to the nearest India-China/Nepal border
segment, using Natural Earth's Admin 0 boundary lines -- a simplification
in the disputed LAC sector, not an official claim.
"""

import geopandas as gpd
import pandas as pd
from shapely.ops import nearest_points

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
]
print(f"Found {len(india_segments)} India-related boundary segments")

# --- Reproject to a metric CRS suitable for the Himalayan region (UTM 44N) ---
METRIC_CRS = "EPSG:32644"
villages_metric = villages_gdf.to_crs(METRIC_CRS)
india_segments_metric = india_segments.to_crs(METRIC_CRS)

# Merge all India boundary segments into one geometry for nearest-distance search
border_union = india_segments_metric.unary_union

# --- Compute distance from each village to the nearest point on the border ---
def distance_to_border_km(point):
    nearest = nearest_points(point, border_union)[1]
    return point.distance(nearest) / 1000  # meters -> km

villages_metric["distance_to_border_km"] = villages_metric.geometry.apply(distance_to_border_km)

# --- Save back with the distance column added ---
result = villages_metric.drop(columns="geometry")
result.to_csv("data/processed/border_optics_master_villages_with_distance.csv", index=False)
print(f"\nSaved {len(result)} villages with border distance to data/processed/border_optics_master_villages_with_distance.csv")
print(result["distance_to_border_km"].describe())