# BORDER OPTICS — Data Dictionary

Column definitions for the processed datasets in `data/processed/`, added as part of the project's reproducibility package alongside `requirements.txt` and the `src/` pipeline scripts.

## `border_optics_master_villages.csv` / `border_optics_master_villages_with_distance.csv`

One row per successfully geocoded village (258 rows).

| Column | Type | Description |
|---|---|---|
| `village_id` | int | Stable integer ID assigned during `merge_geocoded.py`; the join key used across every other processed file. |
| `village` | string | Village/habitation name (from `Habitation` in the raw state lists). |
| `district` | string | District name. |
| `block` | string | Administrative block. May be blank/"unresolved" for the 19 Pithoragarh (Uttarakhand) villages documented in Development_Log.md, Entry 2. |
| `state` | string | One of Arunachal Pradesh, Sikkim, Uttarakhand, Himachal Pradesh. |
| `is_core_sample` | bool | `True` for Arunachal Pradesh / Sikkim / Uttarakhand (the 251-village core statistical sample); `False` for Himachal Pradesh (7-village illustrative case study, excluded from formal hypothesis tests). |
| `latitude`, `longitude` | float | WGS84 (EPSG:4326) coordinates from the geocoding pipeline (Nominatim primary, Bhuvan fallback). |
| `distance_to_border_km` | float | Straight-line distance to the nearest India-relevant Natural Earth Admin-0 boundary segment, computed in UTM 44N (EPSG:32644) then converted to km. Added by `compute_border_distance.py`. Present only in the `_with_distance` version. |

## `border_optics_village_results.csv` / `_analyzed.csv` (full-year window) and `_summer.csv` / `_summer_analyzed.csv` (summer-matched window)

One row per village per compositing window, produced by `extract_satellite_data.py` and enriched by `analyze_results.py` / `analyze_results_fullyear.py`.

| Column | Type | Description |
|---|---|---|
| `village_id` | int | Join key back to the master village table. |
| `village`, `district`, `block`, `state`, `is_core_sample` | — | Carried through from the master table for convenience. |
| `ndbi_before` | float | Mean NDBI over the 500m village buffer, "before" period (2021). Null if zero cloud-free Sentinel-2 images were available in that window. |
| `ndbi_after` | float | Mean NDBI, "after" period (2025). Same null convention. |
| `ndbi_change` | float | `ndbi_after - ndbi_before`. Added during analysis, not part of the raw GEE export. |
| `lights_before`, `lights_after` | float | Mean VIIRS DNB monthly radiance (`avg_rad`) over the same buffer/periods. |
| `lights_change` | float | `lights_after - lights_before`. |
| `before_image_count`, `after_image_count` | int | Number of Sentinel-2 images that went into each period's composite — present only in the summer-matched files, since this is what surfaced Sikkim's complete data loss in that window (Development_Log.md, Entry 5). Not present in the full-year files; a null `ndbi_before`/`ndbi_after` is the only signal of a missing full-year composite. |
| `system:index`, `.geo` | — | Google Earth Engine export artifacts (feature index and geometry, GeoJSON-encoded). Not used downstream; harmless to ignore. |

## Compositing windows, defined precisely

| Window | Before | After |
|---|---|---|
| Full-year | 2021-01-01 to 2022-01-01 | 2025-01-01 to 2026-01-01 |
| Summer-matched | 2021-06-01 to 2021-10-01 | 2025-06-01 to 2025-10-01 |

See `src/acquisition/extract_satellite_data.py` for the exact implementation.

## Statuses used in the geocoding pipeline (`data/processed/<state>_geocoded.csv`)

| `geocode_status` value | Meaning |
|---|---|
| `matched` | Nominatim matched on the full query (habitation + block + district + state). |
| `matched (fallback query, no block)` | Nominatim matched only after dropping the block name. |
| `matched via Bhuvan (district-verified)` | Bhuvan matched, and the returned district matched the expected district. |
| `NO MATCH — Bhuvan also failed or district mismatch` | Bhuvan either found nothing or returned a same-named village in the wrong district (discarded, not accepted). |
| `NO MATCH — not in OSM (tried full + simplified query)` | Nominatim found nothing under either query form; retried against Bhuvan in the fallback pass. |
| `EXCLUDED — forest block, not an inhabited settlement` | Entry was a forest survey compartment, not a village — excluded before geocoding was attempted. |
| `FAILED AFTER RETRIES — network/timeout issue, retry later` | Transient network failure; re-running the script retries these rows specifically. |
