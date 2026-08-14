"""
BORDER OPTICS — Non-VVP Control Village Selection

Builds the control group this study's own Research Paper names as its most
significant open design gap (Section 7.3): a set of villages in the same
districts as the VVP-I priority-village sample, but NOT sanctioned under
VVP-I, so the before/after satellite comparison can become a genuine
Difference-in-Differences design instead of an uncontrolled before/after.

Design choices, stated explicitly rather than left implicit:
  - Matched on DISTRICT, not exact distance-to-border, since district is the
    coarsest unit at which "same regional trend" is defensible, and pinning
    control villages to the treated sample's exact distance band would
    (a) sharply shrink the candidate pool, and (b) risk selecting only the
    handful of non-VVP villages immediately adjacent to a treated village,
    which are the *most* likely to have been excluded from VVP-I for a
    reason (e.g., smaller, less accessible) rather than by chance.
  - Distance-to-border is still used as a soft filter: candidates are kept
    only within [0, 1.5x the treated sample's max distance] for that
    district, so the control group stays "border-region" villages of a
    comparable character rather than pulling in distant lowland towns.
  - Only OpenStreetMap-named place=village/hamlet nodes are considered —
    the same category the original geocoding pipeline matches against, so
    treated and control villages are drawn from the same source population.
  - Any candidate whose name exactly matches (case-insensitive, whitespace-
    normalized) a treated village's name in the same district is dropped —
    this is almost certainly the same physical settlement showing up under
    a second OSM node, not a genuinely distinct village.
  - Per district, candidates are capped at 3x the treated village count
    (or all available candidates if fewer), to keep the control group
    large enough for a real DiD comparison without turning the downstream
    Earth Engine extraction into an unbounded job.

Requires network access to the public Overpass API (openstreetmap.org's
query backend) — run this on your own machine, the same way
geocode_villages.py already talks to Nominatim; this environment's sandbox
cannot reach either service directly.

Output: data/processed/border_optics_control_villages.csv — same schema as
border_optics_master_villages_with_distance.csv (village, district, block,
state, latitude, longitude, distance_to_border_km), plus a
`village_source` column so it's always traceable which villages are the
VVP-I treated sample and which are the added control group.
"""

import time
import unicodedata

import geopandas as gpd
import pandas as pd
import requests
from shapely.geometry import Point
from shapely.ops import nearest_points

TREATED_PATH = "data/processed/border_optics_master_villages_with_distance.csv"
BOUNDARY_PATH = "data/raw/ne_10m_admin_0_boundary_lines_land/ne_10m_admin_0_boundary_lines_land.shp"
OUT_PATH = "data/processed/border_optics_control_villages.csv"

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
OVERPASS_TIMEOUT_S = 90
REQUEST_PAUSE_S = 2.0  # be polite to the shared public Overpass instance

# Overpass rejects requests with no User-Agent (406 Not Acceptable) — same
# identifying header geocode_villages.py already sends to Nominatim
HEADERS = {"User-Agent": "border_optics_research_sakshi_maske (contact: sakshimaske303@gmail.com)"}

# The shared public Overpass instance rate-limits (429) and times out (504)
# under load, especially on the larger bounding-box queries. Same retry
# convention as geocode_villages.py, but with longer, escalating waits —
# Nominatim's per-request rate limit clears in seconds, Overpass's shared-
# instance load doesn't. MAX_RETRIES=5 with a 20/40/80/160s backoff caps a
# single stuck district at ~5 minutes before moving on.
MAX_RETRIES = 5
RETRY_WAIT_SECONDS = 20
RETRYABLE_STATUS_CODES = {429, 502, 503, 504}

MAX_DISTANCE_MULTIPLIER = 1.5   # candidate cap: up to 1.5x the treated sample's max distance
MAX_CANDIDATES_PER_DISTRICT_MULTIPLIER = 3  # cap control count at 3x treated count per district

METRIC_CRS = "EPSG:32644"  # UTM 44N — same CRS compute_border_distance.py uses


def normalize_name(name):
    name = unicodedata.normalize("NFKD", str(name)).encode("ascii", "ignore").decode()
    return " ".join(name.lower().split())


def overpass_query_for_bbox(south, west, north, east):
    """All named place=village/hamlet nodes within a bounding box.

    Retries on 429 (rate-limited) and 502/503/504 (gateway/server errors
    on the shared public instance) with escalating backoff, honoring the
    server's own Retry-After header when it sends one.
    """
    query = f"""
    [out:json][timeout:{OVERPASS_TIMEOUT_S}];
    (
      node["place"~"^(village|hamlet)$"]["name"]({south},{west},{north},{east});
    );
    out body;
    """
    last_err = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.post(
                OVERPASS_URL, data={"data": query}, headers=HEADERS, timeout=OVERPASS_TIMEOUT_S + 10,
            )
            resp.raise_for_status()
            return resp.json().get("elements", [])
        except requests.exceptions.HTTPError as e:
            last_err = e
            status = e.response.status_code if e.response is not None else None
            if status in RETRYABLE_STATUS_CODES and attempt < MAX_RETRIES:
                wait = RETRY_WAIT_SECONDS * (2 ** (attempt - 1))
                retry_after = e.response.headers.get("Retry-After") if e.response is not None else None
                if retry_after:
                    try:
                        wait = max(wait, float(retry_after))
                    except ValueError:
                        pass
                print(f"    {status} error, attempt {attempt}/{MAX_RETRIES} — waiting {wait:.0f}s before retry...")
                time.sleep(wait)
                continue
            raise
        except requests.exceptions.RequestException as e:
            last_err = e
            if attempt < MAX_RETRIES:
                wait = RETRY_WAIT_SECONDS * (2 ** (attempt - 1))
                print(f"    network error ({e}), attempt {attempt}/{MAX_RETRIES} — waiting {wait:.0f}s before retry...")
                time.sleep(wait)
                continue
            raise
    raise last_err


def load_border_union():
    boundary = gpd.read_file(BOUNDARY_PATH)
    if "ADM0_A3_1" in boundary.columns:
        india_segments = boundary[(boundary["ADM0_A3_1"] == "IND") | (boundary["ADM0_A3_2"] == "IND")]
    else:
        india_segments = boundary[(boundary["ADM0_LEFT"] == "India") | (boundary["ADM0_RIGHT"] == "India")]
    return india_segments.to_crs(METRIC_CRS).union_all()


def distance_to_border_km(lat, lon, border_union_metric):
    pt = gpd.GeoSeries([Point(lon, lat)], crs="EPSG:4326").to_crs(METRIC_CRS).iloc[0]
    nearest = nearest_points(pt, border_union_metric)[1]
    return pt.distance(nearest) / 1000


def main():
    treated = pd.read_csv(TREATED_PATH)
    # Control group is only drawn from the three core-sample states — Himachal
    # Pradesh stays an illustrative-only case study throughout this project,
    # per the scope decision already made in merge_geocoded.py.
    treated = treated[treated["is_core_sample"] == True].copy()
    treated["village_norm"] = treated["village"].apply(normalize_name)

    # Resume support: a district already saved in OUT_PATH from an earlier,
    # partially-failed run is skipped rather than re-queried — this both
    # saves time and avoids burning through the same rate limit again on
    # districts that already succeeded.
    existing_rows = []
    completed_districts = set()
    try:
        existing_df = pd.read_csv(OUT_PATH)
        existing_rows = existing_df.to_dict("records")
        completed_districts = set(zip(existing_df["state"], existing_df["district"]))
        if completed_districts:
            print(f"Resuming: {len(completed_districts)} district(s) already saved in {OUT_PATH}, will skip:")
            for state, district in sorted(completed_districts):
                print(f"  - {state} / {district}")
    except FileNotFoundError:
        pass

    print("Loading Natural Earth border geometry (same source as compute_border_distance.py)...")
    border_union = load_border_union()

    all_control_rows = list(existing_rows)

    for (state, district), group in treated.groupby(["state", "district"]):
        if (state, district) in completed_districts:
            print(f"\n--- {state} / {district}: already done, skipping (resume) ---")
            continue
        treated_names = set(group["village_norm"])
        max_dist = group["distance_to_border_km"].max()
        search_radius_deg = 0.6  # ~65km at these latitudes — generous margin around the district's villages

        south = group["latitude"].min() - search_radius_deg
        north = group["latitude"].max() + search_radius_deg
        west = group["longitude"].min() - search_radius_deg
        east = group["longitude"].max() + search_radius_deg

        print(f"\n--- {state} / {district}: {len(group)} treated villages, "
              f"querying Overpass for candidates in bbox... ---")
        try:
            elements = overpass_query_for_bbox(south, west, north, east)
        except Exception as e:
            print(f"  Overpass query failed for {district}: {e} — skipping this district, rerun later.")
            continue
        time.sleep(REQUEST_PAUSE_S)

        candidates = []
        for el in elements:
            name = el.get("tags", {}).get("name", "")
            if not name or normalize_name(name) in treated_names:
                continue
            lat, lon = el.get("lat"), el.get("lon")
            if lat is None or lon is None:
                continue
            candidates.append({
                "village": name, "district": district, "block": "Unknown",
                "state": state, "latitude": lat, "longitude": lon,
            })

        print(f"  {len(elements)} OSM place nodes found, {len(candidates)} after removing treated-name matches")

        # Distance filter + cap
        kept = []
        for c in candidates:
            d = distance_to_border_km(c["latitude"], c["longitude"], border_union)
            if d <= max_dist * MAX_DISTANCE_MULTIPLIER:
                c["distance_to_border_km"] = d
                kept.append(c)

        cap = len(group) * MAX_CANDIDATES_PER_DISTRICT_MULTIPLIER
        kept = sorted(kept, key=lambda c: c["distance_to_border_km"])[:cap]
        print(f"  {len(kept)} candidates kept after distance filter (<= {max_dist * MAX_DISTANCE_MULTIPLIER:.1f} km) "
              f"and per-district cap ({cap})")

        all_control_rows.extend(kept)

        # Checkpoint after every district, not just at the end — so a later
        # district's failure (or the run being interrupted) never loses
        # progress already made this run, on top of the resume support above.
        _save(all_control_rows)
        print(f"  checkpoint saved ({len(all_control_rows)} control villages so far)")

    if not all_control_rows:
        print("\nNo control villages found — check network access to Overpass API and rerun.")
        return

    control_df = _save(all_control_rows)
    print(f"\nSaved {len(control_df)} control villages to {OUT_PATH}")
    print(control_df.groupby(["state", "district"]).size().to_string())


def _save(rows):
    control_df = pd.DataFrame(rows)
    control_df["is_core_sample"] = True
    control_df["village_source"] = "control (non-VVP)"
    control_df["village_id"] = range(1, len(control_df) + 1)
    control_df = control_df[[
        "village_id", "village", "district", "block", "state", "is_core_sample",
        "latitude", "longitude", "distance_to_border_km", "village_source",
    ]]
    control_df.to_csv(OUT_PATH, index=False)
    return control_df


if __name__ == "__main__":
    main()
