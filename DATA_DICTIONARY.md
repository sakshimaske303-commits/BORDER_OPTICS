# BORDER OPTICS — Data Dictionary

Column definitions for the processed datasets in `data/processed/`, added as part of the project's reproducibility package alongside `requirements.txt` and the `src/` pipeline scripts.

## `border_optics_master_villages.csv` / `border_optics_master_villages_with_distance.csv`

One row per successfully geocoded village (258 rows).

| Column | Type | Description |
|---|---|---|
| `village_id` | int | Stable integer ID assigned during `merge_geocoded.py`; the join key used across every other processed file. |
| `village` | string | Village/habitation name (from `Habitation` in the raw state lists). |
| `district` | string | District name. |
| `block` | string | Administrative block. May be blank/"unresolved" for the 19 Pithoragarh (Uttarakhand) villages documented in BO_Development_Log.md, Entry 2. |
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
| `before_image_count`, `after_image_count` | int | Number of Sentinel-2 images that went into each period's composite — present only in the summer-matched files, since this is what surfaced Sikkim's complete data loss in that window (BO_Development_Log.md, Entry 5). Not present in the full-year files; a null `ndbi_before`/`ndbi_after` is the only signal of a missing full-year composite. |
| `system:index`, `.geo` | — | Google Earth Engine export artifacts (feature index and geometry, GeoJSON-encoded). Not used downstream; harmless to ignore. |

## Compositing windows, defined precisely

| Window | Before | After |
|---|---|---|
| Full-year | 2021-01-01 to 2022-01-01 | 2025-01-01 to 2026-01-01 |
| Summer-matched | 2021-06-01 to 2021-10-01 | 2025-06-01 to 2025-10-01 |

See `src/acquisition/extract_satellite_data.py` for the exact implementation.

## `border_optics_control_villages.csv`

One row per non-VVP control village (753 rows), assembled via the OpenStreetMap Overpass API from the same 14 districts as the treated core sample, excluding any village on a VVP-I priority list. Produced by `select_control_villages.py`.

| Column | Type | Description |
|---|---|---|
| `village_id` | int | Control-group-specific integer ID (not comparable to the treated `village_id` values — the two ID spaces are separate). |
| `village`, `district`, `block`, `state`, `is_core_sample`, `latitude`, `longitude`, `distance_to_border_km` | — | Same meaning as in the master village table. |
| `village_source` | string | Always `control (non-VVP)` in this file — retained so control and treated rows can be safely concatenated for the DiD panel without losing group identity. |

## `border_optics_control_results.csv` (full-year) / `border_optics_control_results_summer.csv` (summer-matched)

Control-group villages run through the identical extraction pipeline (same 500m buffer, same NDBI/VIIRS definitions, same before/after windows) used for the treated sample. Produced by `extract_control_satellite_data.py`.

| Column | Type | Description |
|---|---|---|
| `ndbi_before`, `ndbi_after`, `ndbi_before_image_count`, `ndbi_after_image_count` | float / int | Same meaning as the treated village-results files, extracted for control villages. |
| `lights_before`, `lights_after`, `lights_before_image_count`, `lights_after_image_count` | float / int | VIIRS radiance equivalents. |

## `border_optics_did_panel_fullyear.csv` / `border_optics_did_panel_summer.csv`

The treated and control villages reshaped into a two-period panel with a treatment indicator, used to fit the district-fixed-effects Difference-in-Differences model (`ndbi ~ treatment + post + treatment×post + district FE`, clustered SEs by district). Produced by `did_model.py`.

| Column | Type | Description |
|---|---|---|
| `village_id` | int | Join key (separate ID spaces for treated vs. control, as above). |
| `treatment` | int | `1` for a treated (VVP-I priority) village, `0` for a matched non-VVP control village. |
| `ndbi`, `lights` | float | The outcome value for this village-period row (one row per village per period, not a before/after delta). |
| `post` | int | `0` for the "before" period, `1` for the "after" period. |
| `did_term` | int | `treatment × post` — the interaction term whose coefficient is the DiD estimate. |

## `border_optics_did_by_district_fullyear.csv` / `border_optics_did_by_district_summer.csv`

Per-district breakdown of the treated-vs-control gap, used for the "8 of 10 districts show a positive gap" robustness check (Section 4.6 of `BO_Research_Paper.md`).

| Column | Type | Description |
|---|---|---|
| `district` | string | District name. |
| `outcome` | string | `ndbi` or `lights`. |
| `window` | string | `full_year` or `summer`. |
| `n_treated`, `n_control` | int | Village counts with valid data in that district/window. |
| `treated_change`, `control_change` | float | Mean before/after change for each group. |
| `gap` | float | `treated_change - control_change`. |

## `border_optics_did_summary_fullyear.json` / `border_optics_did_summary_summer.json`

Top-level keys: `did` (the DiD regression coefficients, confidence intervals, and cluster-robust/HC3 p-values reported in Section 4.6), and `baseline_balance` (the 2021 Mann-Whitney baseline-imbalance check between treated and control villages, Section 4.6/6.7).

## `border_optics_multiyear_fullyear.csv` / `border_optics_multiyear_summer.csv`

One row per core-sample village with NDBI and VIIRS values extracted at all three time points (2021, 2023, 2025), used for the three-point trend extension (Section 4.7). Produced by `extract_multiyear_satellite_data.py`.

| Column | Type | Description |
|---|---|---|
| `ndbi_2021`, `ndbi_2023`, `ndbi_2025` | float | Mean NDBI at each time point. |
| `ndbi_n_2021`, `ndbi_n_2023`, `ndbi_n_2025` | int | Sentinel-2 image count behind each year's composite. |
| `lights_2021`, `lights_2023`, `lights_2025` | float | Mean VIIRS radiance at each time point. |
| `lights_n_2021`, `lights_n_2023`, `lights_n_2025` | int | VIIRS image count behind each year's composite. |

## `border_optics_multiyear_slopes_fullyear.csv` / `border_optics_multiyear_slopes_summer.csv`

Same rows as the multiyear files above, with a per-village linear trend fit across all three years added by `multiyear_trend.py`.

| Column | Type | Description |
|---|---|---|
| `ndbi_slope`, `lights_slope` | float | Least-squares slope of the value against year, per village. |
| `ndbi_trend_r2`, `lights_trend_r2` | float | R² of that per-village linear fit. |

## `border_optics_multiyear_summary_fullyear.json` / `border_optics_multiyear_summary_summer.json`

A list of summary statistics for the multi-year trend test — the aggregate Wilcoxon signed-rank test on per-village slopes, the village-fixed-effects panel regression, and the individual 2021→2023 / 2023→2025 sub-period tests referenced in Section 4.7.

## `border_optics_buffer250_summer.csv` / `border_optics_buffer1000_summer.csv`

The core-sample villages re-extracted at 250m and 1km buffer radii (summer-matched window only), for the buffer-radius robustness sweep (Section 4.8). Same columns as `border_optics_village_results_summer_analyzed.csv` (which serves as the 500m case in this comparison). Produced by `extract_buffer_sensitivity_data.py`.

## `border_optics_buffer_sensitivity_summary.json`

Top-level keys: `as_extracted` (Wilcoxon results at each radius using all villages with valid data at that radius, varying n), `coverage_note` (the archive-timing/Sentinel-2 backfill explanation for why the 250m/1km extractions picked up more villages than the original 500m pull), and `matched_subsample` (the same test restricted to the 154-village subsample with valid data at all three radii — the version actually reported as the robustness result in Section 4.8).

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
