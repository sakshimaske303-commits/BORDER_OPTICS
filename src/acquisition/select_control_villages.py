"""Builds the non-VVP control group for the DiD design: matched on district
(verified against the district's real Nominatim boundary polygon, not just
the Overpass search bbox), soft filter at 1.5x treated max border-distance,
capped at 3x treated count per district.
"""

import time
import unicodedata

import geopandas as gpd
import pandas as pd
import requests
from shapely.geometry import Point, shape
from shapely.ops import nearest_points

TREATED_PATH = "data/processed/border_optics_master_villages_with_distance.csv"
BOUNDARY_PATH = "data/raw/ne_10m_admin_0_boundary_lines_land/ne_10m_admin_0_boundary_lines_land.shp"
OUT_PATH = "data/processed/border_optics_control_villages.csv"

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
OVERPASS_TIMEOUT_S = 90
REQUEST_PAUSE_S = 2.0  # be polite to the shared public Overpass instance

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
NOMINATIM_PAUSE_S = 1.0  # Nominatim's usage policy asks for max 1 req/sec

# Overpass rejects requests with no User-Agent (406 Not Acceptable) — same
# identifying header geocode_villages.py already sends to Nominatim
HEADERS = {"User-Agent": "border_optics_research_sakshi_maske (contact: sakshimaske303@gmail.com)"}

# Overpass rate-limits (429) / times out (504) under load — 5 retries with
# 20/40/80/160s backoff caps a stuck district at ~5 min before moving on.
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


def fetch_district_polygon(district, state):
    """Looks up the district's real administrative boundary via Nominatim
    (polygon_geojson=1).

    The candidate search below queries Overpass for a rectangular bounding
    box around the treated villages and then labeled every result found in
    that box as belonging to the treated district — a village just across
    the district line, still inside the bbox margin, got assigned the
    treated district's name with nothing checking it was actually inside
    that district's boundary. This fetches the real polygon so candidates
    can be tested for actual membership instead.

    Returns a shapely (Multi)Polygon, or None if Nominatim didn't resolve a
    usable boundary for this name (caller falls back to bbox-only matching
    and marks those rows as unverified rather than guessing).
    """
    params = {"q": f"{district}, {state}, India", "format": "json", "polygon_geojson": 1, "limit": 1}
    try:
        resp = requests.get(NOMINATIM_URL, params=params, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        results = resp.json()
    except requests.exceptions.RequestException as e:
        print(f"  Nominatim boundary lookup failed for {district}, {state}: {e}")
        return None

    if not results or "geojson" not in results[0]:
        return None
    geom = results[0]["geojson"]
    if geom.get("type") not in ("Polygon", "MultiPolygon"):
        return None
    return shape(geom)


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
    # Core-sample states only — Himachal Pradesh stays illustrative-only (see merge_geocoded.py)
    treated = treated[treated["is_core_sample"] == True].copy()
    treated["village_norm"] = treated["village"].apply(normalize_name)

    # Resume support: skip districts already saved from an earlier run.
    #
    # This used to add EVERY (state, district) already present in the output
    # file to completed_districts and skip it unconditionally on resume —
    # including districts saved before the polygon-membership check existed,
    # whose rows are now marked district_verified=False specifically so they
    # get looked at again. That flag was being set and then completely
    # ignored: a resume run always skipped every already-present district
    # regardless of whether it had ever actually been polygon-verified, so
    # the boundary check below could never fix a district that already had
    # (unverified, bbox-only) rows in the file. Now a district is only
    # treated as "done" if ALL of its existing rows are verified; anything
    # else gets its old rows dropped and rebuilt fresh this run.
    existing_rows = []
    completed_districts = set()
    try:
        existing_df = pd.read_csv(OUT_PATH)
        if "district_verified" not in existing_df.columns:
            existing_df["district_verified"] = False

        verified_per_district = existing_df.groupby(["state", "district"])["district_verified"].all()
        completed_districts = set(verified_per_district[verified_per_district].index)
        stale_districts = set(zip(existing_df["state"], existing_df["district"])) - completed_districts

        keep_mask = list(zip(existing_df["state"], existing_df["district"]))
        keep_mask = [pair in completed_districts for pair in keep_mask]
        existing_rows = existing_df[keep_mask].to_dict("records")

        if completed_districts:
            print(f"Resuming: {len(completed_districts)} fully-verified district(s) already saved in {OUT_PATH}, will skip:")
            for state, district in sorted(completed_districts):
                print(f"  - {state} / {district}")
        if stale_districts:
            print(f"Re-processing {len(stale_districts)} district(s) with unverified/bbox-only rows from an earlier run "
                  f"(their old rows are dropped and rebuilt with the polygon check below):")
            for state, district in sorted(stale_districts):
                print(f"  - {state} / {district}")
    except FileNotFoundError:
        pass

    print("Loading Natural Earth border geometry (same source as compute_border_distance.py)...")
    border_union = load_border_union()

    all_control_rows = list(existing_rows)
    # Coordinates already claimed by a kept (verified) row, anywhere — used below
    # to stop the SAME physical OSM point being re-added under a different
    # district just because it also fell inside that district's search bbox
    # (adjacent districts' 0.6°-margin bboxes overlap by design).
    claimed_coords = {(round(r["latitude"], 6), round(r["longitude"], 6)) for r in existing_rows}

    for (state, district), group in treated.groupby(["state", "district"]):
        if (state, district) in completed_districts:
            print(f"\n--- {state} / {district}: already done and verified, skipping (resume) ---")
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

        district_polygon = fetch_district_polygon(district, state)
        if district_polygon is None:
            print(f"  WARNING: could not resolve a real boundary polygon for {state}/{district} — "
                  f"falling back to bbox-only matching. These rows will be marked district_verified=False; "
                  f"candidates outside the true district (but inside the bbox) will NOT be filtered out.")
        time.sleep(NOMINATIM_PAUSE_S)

        # Distance filter + district-polygon membership check + cross-district
        # coordinate dedup + cap
        dupe_skipped = 0
        kept = []
        for c in candidates:
            coord_key = (round(c["latitude"], 6), round(c["longitude"], 6))
            if coord_key in claimed_coords:
                # Same physical OSM point already claimed by another district this
                # run (or a verified earlier run) — adjacent districts' bboxes
                # overlap, so the same village can otherwise be pulled in twice
                # under two different district labels.
                dupe_skipped += 1
                continue

            d = distance_to_border_km(c["latitude"], c["longitude"], border_union)
            if d > max_dist * MAX_DISTANCE_MULTIPLIER:
                continue
            if district_polygon is not None:
                if not district_polygon.contains(Point(c["longitude"], c["latitude"])):
                    continue  # bbox candidate that isn't actually inside this district
                c["district_verified"] = True
            else:
                c["district_verified"] = False
            c["distance_to_border_km"] = d
            c["_coord_key"] = coord_key
            kept.append(c)
            # NOT claiming coord_key here — this candidate might still get cut by
            # the per-district cap below, and a coordinate that never actually
            # makes it into the saved dataset must not block a legitimate
            # candidate at the same physical point in a later district.

        cap = len(group) * MAX_CANDIDATES_PER_DISTRICT_MULTIPLIER
        kept = sorted(kept, key=lambda c: c["distance_to_border_km"])[:cap]
        # Only coordinates that survive the cap and are actually kept this run
        # get claimed — claiming earlier (before the cap) let a coordinate the
        # cap discarded still block the same physical village from being picked
        # up by a later, legitimately-matching district.
        for c in kept:
            claimed_coords.add(c.pop("_coord_key"))
        print(f"  {len(kept)} candidates kept after distance filter (<= {max_dist * MAX_DISTANCE_MULTIPLIER:.1f} km), "
              f"district-boundary check, cross-district dedup ({dupe_skipped} duplicate coordinates skipped), "
              f"and per-district cap ({cap})")

        all_control_rows.extend(kept)

        # Checkpoint after every district so an interruption doesn't lose progress
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
    if "district_verified" not in control_df.columns:
        control_df["district_verified"] = False
    control_df = control_df[[
        "village_id", "village", "district", "block", "state", "is_core_sample",
        "latitude", "longitude", "distance_to_border_km", "village_source", "district_verified",
    ]]
    control_df.to_csv(OUT_PATH, index=False)
    return control_df


if __name__ == "__main__":
    main()
