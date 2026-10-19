# BORDER OPTICS — Forensic Review, 19 October 2026

Before calling version 2.0 finished, I went through the whole project read-only, as an outside examiner would: paper, executive summary, README, Development Log, every script, every figure and every dashboard page. I re-ran eleven analysis scripts unchanged (their outputs matched the committed files) and re-implemented the core statistics in NumPy to check them independently. The arithmetic was right. The problems were in what the measures can detect, how the design was described, and how some results were interpreted.

This file lists what I found and where each item stands after the v2.0 fix round (Development Log Entry 49).

Codes: **A** = critical, **B** = important.

## Critical issues

| Code | Problem | Status after v2.0 |
|---|---|---|
| A1 | **The main outcome could not see the treatment.** Buildings cover a median 0.33% of a 500 m buffer, so doubling a village's buildings moves buffer-mean NDBI by about 0.002, 13–14% of the smallest effect the DiD can detect. The NDBI null was being read as "no change". | Detectability analysis, building-equivalent areas and an equivalence test added (`measurement_sensitivity.py`); paper reframed: the NDBI null is uninformative. Settlement-footprint outcomes prepared, not yet run (`extract_settlement_masked.py`). |
| A2 | **The border-proximity result was a between-district pattern.** Within districts the summer NDBI association disappears and the night-light association reverses. | Within-district analysis and distance to the China boundary added (`h3_within_district.py`, `compute_lac_distance.py`). The earlier "robust" claim is withdrawn. |
| A3 | **Treatment and comparison are defined only by designation.** Comparison villages may sit in VVP-I blocks, and there is no works or completion data. | Open. Needs the VVP-I block list and works data. Control selection code now supports a seeded random draw; a 2026 summer composite is prepared. |
| A4 | **Full-year treated and control values came from different extraction runs.** | Sensitivity run: swapping in the pipeline values gives full-year NDBI DiD +0.0029 (p = 0.64), so conclusions hold. A same-day re-extraction is prepared. |
| A5 | **Geocode quality is unverified.** 35 treated buffers contain no building, 7 pairs share coordinates, Joshimath is a town, Kibithoo could not be located. | Sensitivity run (`sample_qa_sensitivity.py`): no conclusion changes. Visual geocode review is still open. |
| A6 | **The paper was hard to read as a research article.** Several research questions, revision history in the body, some overclaiming. | Paper rewritten around one research question, with the DiD as the primary analysis and the revision history moved to the Development Log and Stability Table. |

## Important issues

| Code | Problem | Status after v2.0 |
|---|---|---|
| B1 | DiD not stated as the primary estimand | Done |
| B2 | Sikkim "archive backfill" explanation stated as established | Softened in the paper; test prepared (`check_s2_archive_ingestion.py`) |
| B3 | Dynamic World result under-examined | Wild cluster bootstrap (p = 0.041 / 0.008), leave-one-district-out, without-Sikkim and composition checks added (`dynamic_world_robustness.py`) |
| B4 | Case villages described as confirmed VVP works | Corrected: the press reports describe them as state model-village works; shown as percentiles, not as validation |
| B5 | Snow in the full-year window; QA60 empty for 2022–2024 | 2023 dip no longer interpreted; Cloud Score+ and snow masking in the prepared extraction |
| B6 | VIIRS low-coverage months and Joshimath | Joshimath sensitivity run; `cf_cvg` filtering in the prepared extraction |
| B7 | Border distance mixed India's other neighbours with China | China-only distance added |
| B8 | Overclaiming ("no satellite-detectable effect") | Removed |
| B9 | Border-first control selection; building-free controls | Seeded random selection option added; building-free sensitivity run |
| B10 | Normal-reference p-values with 14 clusters | t(13) and exact wild cluster bootstrap now primary |
| B11 | Several research questions and an unclear title | One research question and a new title |
| B12 | No statement of software and tools | Open |
| B13 | Source of the 7 Himachal Pradesh names undocumented | Open |
| B14 | No tests for duplicate treated locations | Three tests added (15/15 pass) |

## Still open

1. Settlement-footprint extraction and the 2026 composite (`docs/NEXT_STEPS_EARTH_ENGINE.md`).
2. Visual geocode review against high-resolution imagery.
3. VVP-I block list and works or completion data.
4. Same-day full-year re-extraction for treated and comparison villages.
5. Source documentation for the Himachal Pradesh names; software and tools statement; code licence (MIT or CC BY).
