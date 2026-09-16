# BORDER OPTICS — Analysis Freeze

This file records the exact state this version of the study's headline results are built on: what was extracted, how, when, and which tests are primary versus secondary. Its purpose is to give a reviewer (or a future version of this project) one place to check "is this the same analysis the paper describes" without reconstructing it from commit history or scattered script defaults.

**How to use this file.** Anything computed after the date below, using different data, a different script default, or a different test than what's declared here, is an extension of this study, not a continuation of it — it should be logged as a new Development Log entry and, if it changes a headline number, treated the way Development Log Entries 21–22 treated the Sikkim archive-timing discovery: documented as a revision with a before/after table, not folded in silently. This file itself should be updated (not left to go stale) whenever a genuine re-freeze happens — e.g., once the control list is regenerated under the Entry 24 code fix and the control satellite data is re-extracted against it, or after a pre-treatment-panel extraction (both currently open, see "Known, deferred issues" below).

## Git reference point

Fill this in with the commit hash of whatever push this freeze corresponds to (`git rev-parse HEAD` from the repository root). Left blank here deliberately rather than guessed — this file was written from a working copy without direct git access to confirm the exact current hash.

Commit hash: `a1bfe9ed140b18197480e6b923f62ee120ac93b6`
Date of this freeze: 2026-09-13 (re-frozen per Development Log Entry 25: the control-group contamination fix from Entry 24 was actually run against live data — control list regenerated from 735 to 732 villages, both satellite-extraction windows re-pulled against it, both DiD models and the extended robustness suite re-run)

## Data extraction

| Parameter | Value |
|---|---|
| Satellite collections | `COPERNICUS/S2_SR_HARMONIZED` (Sentinel-2 Surface Reflectance, Harmonized); `NOAA/VIIRS/DNB/MONTHLY_V1/VCMSLCFG` |
| NDBI formula | `(B11 - B8) / (B11 + B8)`, Sentinel-2 median composite per period |
| Cloud/cirrus mask | QA60 bitmask, bit 10 (opaque cloud) and bit 11 (cirrus), both required clear |
| Buffer radius (primary) | 500m, all villages (treated and control) |
| Buffer radii (sensitivity) | 250m, 1000m — summer window only, core sample only; extracted same-day as the 500m primary run, Development Log Entry 31 (resolves §6.9) |
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

## Statistical power (Minimum Detectable Effect)

Added after this freeze, to answer a question a clean null result doesn't answer on its own: could this design have detected a real effect if one existed? Computed by `src/analysis/power_analysis.py`, alpha=0.05 (two-sided), power=0.80, using t-quantiles at this study's own degrees of freedom (not a large-sample z approximation) — n-1=250 for the paired H1 design, and 14 districts - 1 = 13 for the cluster-robust H4 design, per Cameron & Miller (2015)'s small-cluster-count guidance.

| Test | Window | Outcome | MDE | Context |
|---|---|---|---|---|
| H1 (treated-only, paired) | Full-year | NDBI | 0.00904 | Cohen's d = 0.178 (below Cohen's own "small effect" threshold of 0.2) |
| H1 (treated-only, paired) | Full-year | Lights | 0.10246 | Cohen's d = 0.178; 23.9% of baseline mean lights |
| H1 (treated-only, paired) | Summer | NDBI | 0.00599 | Cohen's d = 0.178 |
| H1 (treated-only, paired) | Summer | Lights | 0.08001 | Cohen's d = 0.178; 19.9% of baseline mean lights |
| H4 (control-group DiD) | Full-year | NDBI | 0.01992 | Observed coefficient (+0.00667) is 34% of this threshold |
| H4 (control-group DiD) | Full-year | Lights | 0.15045 | Observed coefficient (+0.05046) is 34% of this threshold |
| H4 (control-group DiD) | Summer | NDBI | 0.01505 | Observed coefficient (-0.00357) is 24% of this threshold |
| H4 (control-group DiD) | Summer | Lights | 0.13017 | Observed coefficient (+0.03244) is 25% of this threshold |

Reading: the primary H1 design's own Cohen's-d MDE (0.178) is essentially constant across outcome/window because it depends only on n and df, not on the outcome's scale — and it sits just under the conventional "small effect" line, so H1's null is not an underpowering artifact; a real small-to-moderate effect would very likely have been caught. H4's design is less sensitive (as expected for a between-group DiD versus a paired within-village design), but every observed H4 coefficient is well below even that higher threshold (24-34% of it), so H4's null isn't a borderline "just missed it" result either.

## Software

See `requirements.txt` for the package list. Versions are **not currently pinned** — before treating any number in this study as final for submission, run `pip freeze > requirements-lock.txt` in the environment the analysis was actually run in and commit that file alongside this one, so a future run of the same scripts against a newer library version can be told apart from a genuine data change.

## Known, deferred issues as of this freeze

1. **RESOLVED (Development Log Entry 25).** `select_control_villages.py`'s distance metric was fixed to geodesic and its exclusion logic now checks coordinate proximity (50m) and the full official priority-village name list (Entry 24) — and that fix has now actually been run against live Overpass/Nominatim/Earth Engine access on the researcher's own machine, not left as a code-only fix. The control list is regenerated (732 villages), both satellite-extraction windows re-pulled against it (732/732 valid, both windows), and every number that depends on the control group (H4 DiD, LOO, RI, log1p, baseline balance) has been re-run against the corrected data. One of those numbers changed conclusion: the full-year night-lights control-group DiD, this study's one previously-surviving significant control-group result, is now null under every specification that had found it significant (§4.6 of `BO_Research_Paper.md`).
2. **RESOLVED (Development Log Entry 25).** The contamination Entry 23 found — 20 of 735 control villages an exact-coordinate duplicate of a treated village under a different name/script (implicating 21 treated villages), plus a separate 3 of 735 matching an ungeocoded official priority-village name — is independently confirmed at zero on the regenerated 732-village list (checked directly: 0 exact-coordinate overlaps, 0 official-name matches). The lower-confidence 40.3m Jorging/Tenggo near-miss flagged in Entry 24 is resolved by construction, since the actual 50m coordinate-proximity filter used in the real rerun catches it along with every other near-duplicate, so it did not need separate manual adjudication.
3. **RESOLVED (Development Log Entry 31).** 250m/500m/1km buffer-radius sensitivity re-extracted back-to-back on the same day, closing the archive-timing gap §6.9 (of `BO_Research_Paper.md`) previously flagged. The result stayed a clean null at all three radii, and closing the timing gap moved the numbers only slightly (250m: p = 0.126 → 0.1214; 500m/1km essentially unchanged at 0.436/0.899 → 0.4358/0.8976) — confirming the earlier, timing-inconsistent comparison was not masking a real effect. One honest addition the same-day pull surfaces: NDBI's mean change is not consistently signed across radii (+0.00175 at 250m, -0.00090 at 500m, -0.00293 at 1km), though none is close to significant — consistent with, not a complication of, the null.
4. **MOSTLY RESOLVED (Development Log Entry 30).** A second pre-treatment year (2019, both groups, both windows) was extracted and a 2019-to-2021 placebo DiD run against it — a period during which VVP-I could not have had an effect (not sanctioned until February 2023). 3 of 4 outcome/window combinations show no significant pre-treatment divergence between treated and control villages (full-year NDBI p=0.864, full-year lights p=0.755, summer lights p=0.968) — real evidence for, not merely an assumption behind, the parallel-trends design. Summer NDBI is a flagged, borderline exception: district-adjusted placebo DiD p=0.064 (not significant at 0.05, but close), while the raw, unadjusted Mann-Whitney comparison of the two groups' distributions is sharply significant (p=0.00001) — district composition explains most but evidently not all of a real pre-existing difference in this one combination. Reported honestly rather than rounded up to a clean pass; see `BO_Research_Paper.md` §7.5 for the full account, including that the borderline pre-period effect runs opposite in sign to the (already null) real summer NDBI DiD, so it does not appear to explain that result away.
5. **RESOLVED — and actually verified by re-running it, not just re-reported (Development Log Entry 32).** The new H3 summer NDBI border-proximity result is now stress-tested the way the (now-null) primary NDBI result and the (now-null) full-year lights DiD were both stress-tested before failing (§7.6), via `src/analysis/h3_border_proximity_robustness.py`: leave-one-district-out (14/14 reruns significant, same sign, rho range [+0.183, +0.337]) and randomization inference (2,000 permutations, p<0.001). Unlike H1 and H4, this result survives the check rather than failing it. The same script also checked the *other* Holm-significant H3 result — full-year lights-proximity (rho=-0.252) — which the paper had described as robust because it "survives as it always has" across data re-extractions, without ever actually being put through this specific check. It also survives: 14/14 leave-one-out, p<0.001 randomization inference, rho range [-0.292, -0.175]. Both null H3 combinations (full-year NDBI, summer lights) were checked too, for completeness, and behave as expected for a null (1/14 significant in leave-one-out, high randomization p). Note on how this item was actually resolved: the script this item cites had been written but never executed — `outputs/h3_robustness_results.json` did not exist on disk despite this item previously reading "RESOLVED" — until Development Log Entry 32 actually ran it and confirmed the numbers above reproduce exactly. Full results now genuinely exist in `outputs/h3_robustness_results.json`.

6. **PARTIALLY RESOLVED (Development Log Entry 26).** A Sentinel-1 SAR cross-check (`BO_Research_Paper.md` §7.1, this file's own primary-estimand note above) was pursued, alongside an unplanned second check (Google Dynamic World's "built" probability band). Both were run treated+control, both windows, against the current 258-treated/732-control sample. SAR — the genuinely sensor-independent check — is null on both bands and both windows, confirming the primary NDBI estimand's own null under this freeze. Dynamic World — algorithm-independent but not sensor-independent — disagrees: a small (+0.003 to +0.007 on a 0-1 probability scale), statistically significant increase in treated villages relative to control, in both windows, that reproduces closely between a manual-OLS check and the real `statsmodels` run and is not attributable to the extraction-completeness bug this entry also found and fixed (in a different file, the control-group summer SAR extraction). This does not change the primary estimand or its conclusion — NDBI, not Dynamic World, remains primary per the "Primary estimand" section above — but it is a genuine, unresolved disagreement between two secondary cross-checks, reported honestly in `BO_Research_Paper.md` §4.10 rather than folded into a clean triangulation claim. Full numbers in `outputs/triangulation_results.json` and Development Log Entry 26.

7. **RESOLVED (Development Log Entry 32).** Spatially-corrected significance for both Holm-significant H3 correlations, via `src/analysis/spatial_moran_and_h3_correction.py`: a SAR(1) parameter calibrated on the same k=8 nearest-neighbor weight matrix used for Moran's I (§6.11) to reproduce each outcome's own observed Moran's I, then 2,000 spatially-autocorrelated synthetic fields correlated against the real distance-to-border values to build a spatial-permutation null. Summer NDBI-proximity (rho=0.291) moves from naive p=0.0000026 to spatially-corrected p=0.02949 — still significant, but only barely. Full-year lights-proximity (rho=-0.252) moves from p=0.0000548 to p=0.00350 — robust either way. This script also re-reproduced this study's own already-published Moran's I values (I=0.346/p=0.001 summer NDBI, I=0.076/p=0.003 full-year lights) as an integrity check before building the correction on top of them; both reproduced exactly. Full results in `outputs/spatial_moran_h3_correction_results.json`.

8. **RESOLVED (Development Log Entry 32).** Wild-cluster bootstrap (Cameron, Gelbach & Miller 2008, restricted variant, full enumeration of all 2^14=16384 sign combinations, not Monte Carlo) for all four H4 control-group DiD results, via `src/analysis/wild_cluster_bootstrap.py`. Implemented with manual numpy OLS + cluster-robust sandwich SE rather than `statsmodels` (not installable in the sandbox this was run in — PyPI is policy-blocked there); the manual implementation was verified to reproduce `did_model.py`'s own already-published coefficients and standard errors to at least 10 significant figures before being trusted for the bootstrap itself. All four results remain null under the bootstrap: full-year NDBI p=0.349, full-year lights p=0.324, summer NDBI p=0.495, summer lights p=0.465 — consistent with, not a departure from, the already-null cluster-robust p-values reported in §4.6. Full results in `outputs/wild_cluster_bootstrap_results.json`.

9. **RESOLVED (Development Log Entry 32).** Village-level cross-check between Dynamic World's "built" change and SAR/NDBI's own changes, via `src/analysis/dw_sar_ndbi_village_level_check.py`, addressing whether §4.10's aggregate DW-vs-SAR/NDBI disagreement is also a village-level one. It is, more so than the aggregate comparison alone suggested: Spearman rho between Dynamic World's built-change and SAR VV/VH or NDBI's own change is small and mostly non-significant in both windows (rho range -0.13 to +0.15), and at several combinations the two proxies point the *same* direction at fewer than half the villages (31-41% same-sign in three of six combinations checked) — worse than a coin flip. This does not resolve which of §4.10's two speculative explanations for the disagreement is correct, but it does establish that Dynamic World's small aggregate DiD is not traceable to the same individual villages SAR or NDBI would flag. Full results in `outputs/dw_sar_ndbi_village_level_results.json`.

10. **RESOLVED, and NOT a clean confirmation (Development Log Entry 33).** The SCL-band-based cloud mask re-extraction (`src/acquisition/extract_scl_cloud_mask_ndbi.py`, summer window, treated core sample) has now been run on the researcher's own machine, and `src/analysis/scl_vs_qa60_comparison.py` has been run against it. The SCL-masked extraction returns valid data for only 200/258 villages (vs. QA60's 251) and, on those 200, gives a significant positive summer NDBI change (mean +0.01169, Wilcoxon p=0.0000045) — the opposite of the QA60-based null. This is NOT explained by the SCL-valid sample's skewed composition (93% Arunachal Pradesh, dropping nearly all of Uttarakhand and most of Sikkim): restricting the *QA60*-masked data to the identical 200 villages still gives a clean null (mean -0.00016, p=0.449), so the mask choice itself, holding the sample fixed, is what flips the result. Village-level agreement between the two masks is moderate (Spearman rho=0.544, n=200) — not high enough to explain the significance gap. Reported in `BO_Research_Paper.md` §6.12 as a genuine, unresolved instability in the primary measurement approach, not folded into either the null or a claimed effect. Full results in `outputs/scl_vs_qa60_comparison.json`. Neither of the two plausible explanations (QA60 under-masking, or SCL over-masking in a way that manufactures a spurious change) has been distinguished from the other; that would need a village-level visual audit or a third independent cloud-masking method (e.g., Cloud Score+), neither of which has been done.

11. **NOT THIS STUDY'S TO RESOLVE — a real-world action, not an analysis step.** The RTI application drafted in `docs/RTI_draft_HP_Ladakh_village_lists.md` for Himachal Pradesh's and Ladakh's village-wise VVP-I lists (§7.4) has not been filed. Filing it, waiting out the statutory response window, and geocoding whatever comes back are all steps only the researcher can take; nothing in this analysis pipeline can substitute for them.

Any analysis that resolves one of the above should update this file's relevant section and note the resolution with a cross-reference to the Development Log entry that did it, following the same pattern Entries 21–22 used for the Sikkim archive-timing discovery.
