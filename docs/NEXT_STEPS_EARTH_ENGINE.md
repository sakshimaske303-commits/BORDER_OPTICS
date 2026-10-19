# Next steps that need my own machine (Earth Engine / live APIs / manual checks)

Prepared in Development Log Entry 49, after the October 2026 forensic review. Everything that
could be done without Earth Engine or live web APIs has been done and is already in the repo
(see Entry 49). The steps below could not be run in the review environment. Do them in this
order; each one says which review item it closes and what to rerun afterwards.

Before starting: `pip install -r requirements-lock.txt`, `earthengine authenticate`, and
`EE_PROJECT` set in `.env`.

---

## 1. Same-day full-year re-extraction (review item A4) — ~2–3 h, cheap, do first

Why: the full-year treated values come from an early Code Editor export that is not in the
repo, and a Python re-extraction differs at 187/251 villages. Controls were extracted with the
Python script seven weeks later.

```bash
mkdir -p archive/data_processed
mv data/processed/border_optics_village_results.csv archive/data_processed/border_optics_village_results_PRE_ENTRY49_CODE_EDITOR_EXPORT.csv
mv data/processed/border_optics_control_results.csv archive/data_processed/border_optics_control_results_PRE_ENTRY49.csv
python src/acquisition/extract_satellite_data.py --window full_year
python src/acquisition/extract_control_satellite_data.py --window full_year
python src/analysis/analyze_results.py --window full_year
python src/analysis/did_model.py --window full_year
python src/analysis/wild_cluster_bootstrap.py
python src/analysis/sample_qa_sensitivity.py
python -m pytest tests/
```
Expected: same conclusion (the review already tested the Python values for treated villages:
full-year NDBI DiD +0.0029, p = 0.64). Update the paper's full-year numbers from the new
`border_optics_did_summary_fullyear.json`.

## 2. Settlement-targeted outcomes (review item A1) — the most important new analysis

```bash
python src/acquisition/extract_settlement_masked.py --group treated --window summer
python src/acquisition/extract_settlement_masked.py --group control --window summer
python src/acquisition/extract_settlement_masked.py --group treated --window full_year
python src/acquisition/extract_settlement_masked.py --group control --window full_year
python src/analysis/settlement_masked_did.py --bootstrap
```
This gives NDBI and Dynamic World inside each village's actual settlement footprint, Dynamic
World built-up AREA (m²) in the buffer, and cloud-filtered VIIRS, for 2019 (placebo), 2021,
2025 and summer 2026 (longer exposure). The analysis script was tested on synthetic data with
a known effect; the extraction script has not been run yet. Check the first 10–20 villages'
output by eye before letting it run through.

How to report it: make `dw_built_area_m2` (m² of built-labelled land) and `ndbi_zone` the
primary outcomes of the revised paper; the 500 m buffer means become the "original
specification" robustness row.

## 3. Archive-backfill check (review item B2) — 10 minutes

```bash
python src/acquisition/check_s2_archive_ingestion.py
```
If most Sikkim scenes were ingested before 28 July 2026, replace "archive backfill" in the
paper with "the original Code Editor export returned no scenes for Sikkim; cause undetermined
because that code was not preserved".

## 4. Control group without border-first selection (review item B9)

```bash
python src/acquisition/select_control_villages.py --selection random --seed 42 \
    --out data/processed/border_optics_control_villages_random.csv
```
Then point `extract_control_satellite_data.py` at that file (copy it over
`border_optics_control_villages.csv` only after archiving the current list) and rerun
`did_model.py` for both windows. Report as a robustness row.

## 5. Manual data tasks (no code can do these)

- **VVP-I block membership (A3).** Get the list of VVP-I's 46 blocks / 2,967 villages
  (MHA/state notifications, RS Q. 2321 annexure). Check which of the 14 districts' blocks are
  VVP blocks. If controls fall inside VVP blocks, either (a) restrict controls to non-VVP blocks,
  or (b) keep them and say clearly that the comparison is "priority vs. non-priority villages",
  not "VVP vs. non-VVP".
- **Implementation data (A3).** For as many treated villages as possible, record which VVP-I
  works were completed and when (state VVP portals, PIB releases, district news, inauguration
  reports). Even 30–50 villages with a completion date allows a "completed-works" subgroup DiD.
- **Geocode QA (A5).** Open every treated point (start with the 35 whose 500 m buffer has no
  building: `outputs/sample_qa_sensitivity_results.json` lists the variant; the village names
  are in the review) in Google Earth / Esri imagery. Move each point to the centre of the
  settlement it names, or flag it as not found. Record the old and new coordinates and the
  reason in a new `data/processed/geocode_qa_log.csv`. Resolve the 7 identical-coordinate pairs
  (keep one, or locate the second settlement). Decide whether Joshimath (block HQ town) belongs
  in a "border village" sample. Then rerun steps 1–2.
- **Ground truth (B4).** Add the source URL for the Anjaw inauguration report; check that each
  facility lies inside the 500 m buffer; try to find more confirmed works in other districts.
- **Himachal Pradesh sourcing (B13).** Note where the 7 HP village names came from.
