# BORDER OPTICS — Analysis Freeze

This file records the exact state this version of the study's headline results are built on: what was extracted, how, when, and which tests are primary versus secondary. Its purpose is to give a reviewer (or a future version of this project) one place to check "is this the same analysis the paper describes" without reconstructing it from commit history or scattered script defaults.

**How to use this file.** Anything computed after the date below, using different data, a different script default, or a different test than what's declared here, is an extension of this study, not a continuation of it — it should be logged as a new Development Log entry and, if it changes a headline number, treated the way Development Log Entries 21–22 treated the Sikkim archive-timing discovery: documented as a revision with a before/after table, not folded in silently. This file itself should be updated (not left to go stale) whenever a genuine re-freeze happens — e.g., once the control list is regenerated under the Entry 24 code fix and the control satellite data is re-extracted against it, or after a pre-treatment-panel extraction (both currently open, see "Known, deferred issues" below).

## Git reference point

Fill this in with the commit hash of whatever push this freeze corresponds to (`git rev-parse HEAD` from the repository root). Left blank here deliberately rather than guessed — this file was written from a working copy without direct git access to confirm the exact current hash.

Commit hash: `___________`
Date of this freeze: 2026-09-13 (re-frozen per Development Log Entry 25: the control-group contamination fix from Entry 24 was actually run against live data — control list regenerated from 735 to 732 villages, both satellite-extraction windows re-pulled against it, both DiD models and the extended robustness suite re-run)

## Data extraction

| Parameter | Value |
|---|---|
| Satellite collections | `COPERNICUS/S2_SR_HARMONIZED` (Sentinel-2 Surface Reflectance, Harmonized); `NOAA/VIIRS/DNB/MONTHLY_V1/VCMSLCFG` |
| NDBI formula | `(B11 - B8) / (B11 + B8)`, Sentinel-2 median composite per period |
| Cloud/cirrus mask | QA60 bitmask, bit 10 (opaque cloud) and bit 11 (cirrus), both required clear |
| Buffer radius (primary) | 500m, all villages (treated and control) |
| Buffer radii (sensitivity) | 250m, 1000m — summer window only, core sample only; **not extracted same-day as the 500m run** (Development Log §6.9) |
| Reduction scale | 10m (NDBI), 500m (VIIRS radiance) |
| Full-year window | before 2021-01-01–2022-01-01, after 2025-01-01–2026-01-01 |
| Summer-matched window | before 2021-06-01–2021-10-01, after 2025-06-01–2025-10-01 |
| Treated sample extraction date | Development Log Entry 22 (same-day, complete re-extraction) |
| Control sample extraction date | Development Log Entry 25 (regenerated control list, both windows re-extracted; supersedes the Entry 22 control extraction, which was against the pre-fix, contaminated 735-village list) |
| Multi-year (2023) extraction | Treated core sample only; control group has no third time point |
| Border/LAC distance (treated villages) | Geodesic, WGS84 ellipsoid, via `pyproj.Geod` (`compute_border_distance.py`) |
| Border/LAC distance (control eligibility filter) | Geodesic (`pyproj.Geod`, fixed Development Log Entry 24), and the on-disk control list was regenerated under the fix and re-verified (Development Log Entry 25). Resolved. |

## Sample sizes

| Group | n |
|---|---|
| Treated, core sample (Arunachal Pradesh + Sikkim + Uttarakhand) | 251 |
| Treated, illustrative only (Himachal Pradesh) | 7 |
| Treated, total geocoded | 258 |
| Control (non-VVP, district-restricted) | 732 (was 735 pre-Entry-25; the 50m coordinate-proximity and full official-name exclusions changed which candidates enter the pool, not a simple subtraction of the counts below) |
| District clusters | 14 |
| Control villages that were an exact-coordinate duplicate of a treated village, under a different name/script | Resolved: 0, verified independently on the regenerated 732-village list (was 20, implicating 21 treated villages — Development Log Entries 23, 25) |
| Control villages that name-collided with an ungeocoded official priority village — a narrower, non-overlapping check | Resolved: 0, verified independently on the regenerated 732-village list (was 3 — Development Log Entries 23, 25) |

## Primary estimand

The treated-only before/after change in NDBI between 2021 and 2025 across the 251-village core sample (H1), tested under both full-year and summer-matched compositing windows. This is the estimand the paper's headline conclusion (Sections 4.2, 4.9, 5, 8) is stated against. See `BO_Research_Paper.md` §3.12 for the full primary/secondary/exploratory hierarchy.

## Secondary, pre-specified robustness checks on the primary estimand

Control-group DiD (H4), buffer-radius sweep (250/500/1000m), leave-one-district-out, randomization inference (2,000 permutations, seed=42), Holm-Bonferroni correction across the 8 H1/H3 headline p-values.

## Secondary, independent research questions

Night-lights change, border-proximity correlation (H3), three-point multi-year trend (2021/2023/2025), budget-vs-outcome descriptive comparison (RQ2).

## Exploratory, unstressed finding

Summer-window H3 NDBI-border-proximity correlation (ρ = 0.291, p = 0.0000026), which emerged only after the Entry 22 data correction. Not yet leave-one-out or randomization-inference checked. Does not feed back into the primary estimand's conclusion.

## Multiple-testing family

Holm-Bonferroni correction is applied across exactly 8 tests: H1 (NDBI, lights) × 2 windows, H3 border-proximity (NDBI, lights) × 2 windows. The control-group DiD, buffer-radius sweep, leave-one-out, randomization inference, and multi-year trend are evaluated on their own terms as robustness checks on already-tested hypotheses, not as additional members of this correction family (`BO_Research_Paper.md` §4.9).

## Statistical tests used

Wilcoxon signed-rank (paired, `alternative="greater"`) for before/after change. Spearman rank correlation for RQ2 (budget) and H3 (border proximity). OLS Difference-in-Differences with district fixed effects, cluster-robust SE by district (primary), and a parallel HC3 heteroskedasticity-robust no-fixed-effects specification (comparison), both via `statsmodels`. Mann-Whitney U for baseline-balance and geocoding-coverage checks.

## Software

See `requirements.txt` for the package list. Versions are **not currently pinned** — before treating any number in this study as final for submission, run `pip freeze > requirements-lock.txt` in the environment the analysis was actually run in and commit that file alongside this one, so a future run of the same scripts against a newer library version can be told apart from a genuine data change.

## Known, deferred issues as of this freeze

1. **RESOLVED (Development Log Entry 25).** `select_control_villages.py`'s distance metric was fixed to geodesic and its exclusion logic now checks coordinate proximity (50m) and the full official priority-village name list (Entry 24) — and that fix has now actually been run against live Overpass/Nominatim/Earth Engine access on the researcher's own machine, not left as a code-only fix. The control list is regenerated (732 villages), both satellite-extraction windows re-pulled against it (732/732 valid, both windows), and every number that depends on the control group (H4 DiD, LOO, RI, log1p, baseline balance) has been re-run against the corrected data. One of those numbers changed conclusion: the full-year night-lights control-group DiD, this study's one previously-surviving significant control-group result, is now null under every specification that had found it significant (§4.6 of `BO_Research_Paper.md`).
2. **RESOLVED (Development Log Entry 25).** The contamination Entry 23 found — 20 of 735 control villages an exact-coordinate duplicate of a treated village under a different name/script (implicating 21 treated villages), plus a separate 3 of 735 matching an ungeocoded official priority-village name — is independently confirmed at zero on the regenerated 732-village list (checked directly: 0 exact-coordinate overlaps, 0 official-name matches). The lower-confidence 40.3m Jorging/Tenggo near-miss flagged in Entry 24 is resolved by construction, since the actual 50m coordinate-proximity filter used in the real rerun catches it along with every other near-duplicate, so it did not need separate manual adjudication.
3. 250m/1km buffer-radius sensitivity extracted on a different day than the 500m primary run (§6.9). Still open — unaffected by the control-group fix above (this buffer sweep is treated-only, no control group involved).
4. No genuine pre-treatment panel exists for the control group — the parallel-trends assumption rests on a single-point baseline-balance check, not a tested trend (§7.5). Still open, though as of Entry 25 that single-point baseline check is now balanced on all four outcome/window combinations (§6.7), a firmer footing than before even without a full panel.
5. New H3 summer border-proximity result not yet stress-tested the way the (now-null) primary NDBI result and the (now-null) full-year lights DiD were both stress-tested before failing (§7.6). Still open.

Any analysis that resolves one of the above should update this file's relevant section and note the resolution with a cross-reference to the Development Log entry that did it, following the same pattern Entries 21–22 used for the Sikkim archive-timing discovery.
