# Satellite Verification of India's Vibrant Villages Programme: A Compositing-Window Robustness Assessment of Border-Village Development

**Sakshi D. Maske**
Independent Geospatial Researcher

## Abstract

The Vibrant Villages Programme (VVP-I) is the Government of India's flagship border-area development scheme, sanctioning approximately ₹4,800 crore across 2,967 villages in five Himalayan border states/union territories since 2022–23, with 662 designated "priority" villages for Phase 1 development. A government reply on parliamentary record states that no impact assessment has ever been carried out for this programme. This study addresses that gap directly, independently testing whether VVP-I priority villages show measurable physical development using Sentinel-2 built-up-index (NDBI) and VIIRS night-lights data at 258 individually geocoded villages across three core states (Arunachal Pradesh, Sikkim, Uttarakhand) plus a small illustrative sample from a fourth (Himachal Pradesh), comparing a pre-sanction baseline (2021) against the present (2025) under two independent compositing windows, against a matched non-VVP control group of 753 villages drawn from the same 14 districts. A full-year composite showed no significant increase in built-up area (Wilcoxon signed-rank, p = 1.000); a season-matched (June–September) composite on the same villages showed the opposite result (p < 0.000001) — a reversal traced to snow-cover contamination in the full-year window and monsoon cloud cover eliminating Sikkim's data entirely in the summer window. A district-fixed-effects difference-in-differences model against the matched control group reproduces this same window-sensitivity pattern rather than resolving it: the summer-matched treated-vs-control gap is significant (did coefficient = +0.0377, cluster-robust p = 0.0021) while the full-year gap is not (p = 0.215), indicating the summer NDBI signal is attributable to VVP-I villages specifically and not merely a regional trend shared by every village in these districts. A three-point extension of the same summer-matched villages (2021, 2023, 2025) complicates this finding rather than simply confirming it: the change is not a steady trend but a decline from 2021 to 2023 followed by a recovery from 2023 to 2025, so the reported 2021-vs-2025 difference should be read as concentrated in the second half of the study window, not as sustained multi-year growth. A buffer-radius sweep (250m, 500m, 1km) shows the significant NDBI result holds at every radius once sample composition is matched across buffers (all p < 0.002), and is not, on its own, an artifact of the 500m radius chosen throughout the rest of this study. VIIRS night-lights, tested identically under both windows, showed no significant increase in either (p = 0.050 full-year; p = 0.9999 summer-matched), making it the more temporally stable — and more trustworthy — proxy. Descriptively — an illustrative two-state pattern, not a formal statistical test — Arunachal Pradesh's sanctioned budget (₹2,749.74 crore) was roughly ten times Uttarakhand's (₹270.58 crore), yet the two states' mean measured built-up-area change was nearly identical (+0.0284 vs. +0.0293), consistent with budget scale not translating proportionally into physical change. Border-proximity effects (H3) showed a stable null for built-up change (ρ = 0.043–0.037, both non-significant) and an unstable result for night-lights (significant only in the full-year window). Rather than resolving this instability by selectively citing the more favourable result, this study reports the instability itself as the central finding: VVP-I's claimed development is not currently demonstrable with confidence from satellite evidence, precisely the accountability gap the programme's own parliamentary record identifies — though where a treated-vs-control comparison, a multi-year trend, and a buffer-radius sweep can all be brought to bear on the one signal that does clear significance, that signal survives each of them.

**Keywords**: Vibrant Villages Programme, border development, securitization theory, satellite verification, NDBI, VIIRS night-lights, remote sensing, robustness testing, difference-in-differences

---

## 1. Introduction

India's border villages have historically been framed in policy discourse as security liabilities — remote, under-populated, and vulnerable to depopulation toward a contested frontier. The Vibrant Villages Programme (VVP-I), approved by the Union Cabinet in February 2023, reframes them instead as development priorities, sanctioning infrastructure and livelihood investment across 2,967 villages in Arunachal Pradesh, Sikkim, Uttarakhand, Himachal Pradesh, and Ladakh. What the programme has not received, in more than two years since sanction, is an independent, evidence-based accounting of whether the development it promised has actually occurred on the ground. Asked directly in Parliament whether any impact assessment has been carried out for VVP, the Ministry of Home Affairs answered without qualification: "No impact assessment has been carried out" (Lok Sabha Unstarred Question No. 508, 3 February 2026).

This study addresses that gap directly, using multi-temporal satellite imagery — built-up area indices and night-time light radiance — to test, village by village, whether physical development detectable from space has occurred since programme sanction, whether its magnitude tracks each state's sanctioned budget, and whether its distribution is better explained by border proximity than by developmental need, consistent with securitization theory's prediction that border infrastructure functions as a geopolitical signal as much as a welfare intervention.

Specifically, this study tests five research questions: (RQ1) whether priority villages show statistically detectable built-up area growth since programme sanction; (RQ2) whether the magnitude of that change correlates with each state's sanctioned budget; (RQ3) whether night-time light trends corroborate the built-up area findings; (RQ4) whether development is spatially concentrated by border proximity rather than developmental need; and (RQ5) whether any detected change is attributable to VVP-I specifically, or merely reflects a regional development trend shared by every village in these border districts regardless of VVP-I status. Correspondingly, four hypotheses are tested: **H1** predicts a statistically significant post-sanction increase in built-up area; **H2** predicts that the size of this change will not be uniformly proportional to sanctioned budget, with some high-budget states showing comparatively muted physical change; **H3** predicts that villages nearer the border/LAC will show disproportionately faster change than villages farther back within the same state, consistent with securitization theory's prediction that border proximity — not developmental need — drives priority; and **H4** predicts that VVP-I priority villages will show a significantly larger increase than a matched set of non-VVP villages in the same districts over the same period, isolating a programme-attributable effect from the general regional trend.

## 2. Literature Review

### 2.1 Securitization Theory and Border Development

Securitization theory (Buzan, Wæver, & de Wilde, 1998) argues that framing an issue as a matter of security — rather than ordinary politics — justifies extraordinary measures and resource allocation that would not otherwise be politically available. Border-area development programmes sit naturally within this frame: investment is justified simultaneously as civilian welfare and as strategic infrastructure along a contested frontier, and the two justifications are rarely disentangled in either policy design or public reporting. This study treats VVP-I as a direct empirical test case for that theory — specifically, whether the spatial distribution of measurable development is better predicted by border proximity than by conventional developmental indicators such as population or existing infrastructure gaps.

### 2.2 The Vibrant Villages Programme: Policy Context and the Accountability Gap

VVP-I's sanctioned scope is documented across multiple government sources: a Rajya Sabha Unstarred Question reply (Question No. 2321, Ministry of Home Affairs, 9 August 2023) provides Sikkim's full village-wise annexure; Lok Sabha Question No. 2104 (2023) and Rajya Sabha Question No. 401 (2025) confirm Himachal Pradesh's 75 priority villages without a name-level annexure; and Lok Sabha Question No. 4360 (2025) confirms Ladakh's 35 sanctioned villages, again without a published village list. Most directly relevant to this study's premise, Lok Sabha Unstarred Question No. 508 (3 February 2026) asked the Ministry of Home Affairs specifically whether VVP's impact had been assessed; the Ministry's answer was unqualified: "No impact assessment has been carried out." No government source identified in the course of this study's data-acquisition process provides an independent, satellite-verified accounting of physical progress against this sanctioned scope — the absence this study is designed to address.

### 2.3 Remote Sensing Approaches to Built-Up Area and Economic Activity Detection

The Normalized Difference Built-up Index (NDBI), computed from short-wave infrared and near-infrared reflectance, is an established proxy for built-up surface extent in multi-temporal satellite comparison (Zha, Gao, & Ni, 2003). VIIRS Day/Night Band night-time radiance is a complementary, independent proxy for economic and electrification activity, with documented advantages over older DMSP-OLS night-lights products in dynamic range and spatial resolution (Elvidge, Baugh, Zhizhin, Hsu, & Ghosh, 2017). This study uses both indices in parallel specifically because they are subject to different confounds — NDBI to vegetation phenology and snow cover, VIIRS to cloud cover and sensor saturation at very low radiance — so that agreement between the two carries more evidentiary weight than either alone.

### 2.4 Compositing-Window Sensitivity in Multi-Temporal Satellite Analysis

Seasonal compositing choices are known to materially affect spectral-index-based change detection in high-relief terrain, where snow cover and cloud frequency both vary systematically by season and elevation. This study treats compositing-window sensitivity not as a nuisance parameter to be tuned away, but as a testable property of the result itself: a finding that reverses direction between two independently defensible compositing windows is, on its own terms, evidence that a single-window result should not be reported as confirmatory.

## 3. Data and Methodology

### 3.1 Study Design

This study covers VVP-I priority villages across five Himalayan border states/union territories, restricting the core statistical sample to the three states with complete, officially-sourced village-wise identification — Arunachal Pradesh, Sikkim, and Uttarakhand (251 villages) — while carrying Himachal Pradesh's 7 confirmed villages as a separately labelled illustrative case study and excluding Ladakh from village-level analysis entirely, pending resolution of a documented data-availability gap. Each treated village's before/after change is benchmarked against a matched non-VVP control group of 753 villages drawn from the identical 14 districts, so that a district-fixed-effects Difference-in-Differences specification can isolate a VVP-I-attributable effect from whatever regional development trend every village in these districts shares regardless of programme status (H4). The two-year (2021 vs. 2025) comparison used throughout is extended with a third, independent time point (2023) for the same core sample, so a three-point trend — not a single before/after difference — carries the evidentiary weight for the study's central finding, and the fixed 500m extraction buffer used throughout is additionally tested at 250m and 1km radii to establish whether that choice, like the compositing window, materially changes the result.

### 3.2 Data Sources

| Variable | Source | Temporal Coverage |
|---|---|---|
| Village identification | State VVP-I portals; Rajya Sabha/Lok Sabha Q&A annexures | 2023–2025 |
| Village coordinates | OpenStreetMap Nominatim; ISRO Bhuvan Village Geocoding API | Current |
| Non-VVP control village identification | OpenStreetMap Overpass API, district-matched to treated sample | Current |
| Built-up index (NDBI) | Sentinel-2 SR Harmonized | 2021, 2023, 2025 |
| Night-lights radiance | VIIRS DNB monthly composites | 2021, 2023, 2025 |
| Border/LAC geometry | Natural Earth 10m Admin-0 Boundary Lines | Current |
| Budget/project counts | State-wise VVP-I sanction figures (parliamentary record) | 2023 |

### 3.3 Village-Level Dataset Compilation and Geocoding

Village lists were cross-verified against officially reported aggregate counts before acceptance, then geocoded via Nominatim (primary) with Bhuvan used as a Census-linked fallback, subject to manual district validation after a direct test confirmed Bhuvan does not filter by state (a query for "Kharman," an Arunachal Pradesh village, initially returned an unrelated same-named village in Haryana). Of 559 villages attempted across the four named states, 258 were successfully geocoded (Arunachal Pradesh 186/455, Sikkim 31/46, Uttarakhand 34/51, Himachal Pradesh 7/7).

### 3.4 Satellite Change Detection

For each geocoded village, a 500m buffer was used to extract mean NDBI and VIIRS night-lights radiance via Google Earth Engine, comparing a 2021 baseline against 2025.

NDBI was computed using Sentinel-2 Level-2A Surface Reflectance Harmonized bands B11 (SWIR1) and B8 (NIR), with cloud masking applied via the QA60 band. Night-lights radiance was drawn from the VIIRS Day/Night Band monthly composite product (NOAA/VIIRS/DNB/MONTHLY_V1/VCMSLCFG).

### 3.5 Compositing-Window Robustness Testing

Both metrics were computed under two independent compositing windows — a full calendar year, and a season-matched June–September window — to isolate genuine change from seasonal artifacts (snow cover in the full-year window; monsoon cloud cover in the summer window), with any village lacking a valid composite in either window marked null rather than defaulted to zero.

### 3.6 Border-Proximity Analysis

Distance from each village to the nearest segment of Natural Earth's Admin-0 boundary line was computed via GeoPandas (UTM 44N reprojection, nearest-point distance), restricted to India-relevant boundary segments. This distance is explicitly a cartographic approximation: India's boundary with China in this region, commonly referenced as the Line of Actual Control, is disputed and has no single internationally agreed alignment, so all distance figures should be read as relative and comparative rather than as an authoritative statement of the boundary's legal position.

### 3.7 Non-VVP Control Group and Difference-in-Differences Design

A treated-only before/after comparison cannot distinguish a VVP-I-attributable effect from a general trend affecting every village in these border districts over the same 2021–2025 period — infrastructure spending unrelated to VVP-I, broader state development schemes, or simple regrowth after a low year could all produce an apparent "after minus before" increase with no connection to the programme itself. To address this directly, a non-VVP control group of 753 villages was assembled via the OpenStreetMap Overpass API, restricted to the identical 14 districts that contain the treated core sample and explicitly excluded from any VVP-I priority-village list, then run through the same extraction pipeline (identical 500m buffer, identical NDBI/VIIRS definitions, identical before/after windows) used for the treated sample. Village-level results were reshaped into a two-period panel (before/after) with a treatment indicator, and tested with

ndbi (or lights) ~ treatment + post + treatment×post + district fixed effects

with standard errors clustered by district (14 clusters). The treatment×post coefficient — the DiD estimate — measures the treated group's change in excess of the control group's own change over the same period; district fixed effects absorb any baseline difference in development trajectory between districts, so the estimate reflects a treated-vs-control gap within the same district, not a cross-district comparison. A heteroskedasticity-robust (HC3) specification without district fixed effects is reported in parallel for comparability, given the standard caution around cluster-robust inference with a moderate cluster count (14, below the usual 30–40+ guidance for the asymptotic theory to be fully trustworthy). A genuine parallel-pre-trends placebo test — checking that treated and control villages moved together before programme sanction, as this project's own prior control-group DiD work on a different study does with a multi-period pre-treatment panel — was not possible here, since the control group's satellite extraction covers only the same single before/after pair as the treated sample rather than a multi-year pre-period; a baseline (2021) level-balance check (Mann-Whitney U) is reported in its place as a partial, explicitly weaker substitute.

### 3.8 Multi-Year Trend Extraction

The core comparison rests on two single years (2021, 2025), a design vulnerable to either year being a genuine weather anomaly — an unusually early snowmelt, an unusually heavy or light monsoon — that could produce or erase an apparent change independent of any true development. A third, independent time point (2023), roughly midway between the two, was extracted for the same 251-village core sample under both compositing windows, yielding one NDBI/VIIRS value per village per year rather than another before/after delta. A per-village linear trend was fit across all three years (least-squares slope), tested in aggregate against zero with a one-sided Wilcoxon signed-rank test on the per-village slopes, and cross-checked against a village-fixed-effects panel regression (value ~ year, clustered SE by village) as a second, model-based specification. Each two-year sub-period (2021→2023, 2023→2025) was also tested individually, to distinguish a genuinely sustained trend from a change concentrated in one half of the four-year window.

### 3.9 Buffer-Radius Robustness Testing

The 500m extraction buffer used throughout this study was a fixed methodological choice, not itself tested against alternatives elsewhere in this design. The same summer-window NDBI/VIIRS extraction was additionally run at 250m and 1km radii for the same core sample, and the same Wilcoxon signed-rank test applied at each radius. Because the 250m and 1km extractions were run at a later date than the original 500m extraction — against the identical fixed 2021/2025 date ranges, but a Sentinel-2 archive that continues to backfill scenes close to the present — a direct village-count comparison across the three buffer radii is confounded by that archive-timing difference rather than isolating buffer radius alone; the comparison is therefore also run on the subsample of villages with valid data at all three radii, which holds sample composition fixed and isolates buffer radius as the only variable changing between tests.

### 3.10 Statistical Testing

Before/after change was tested using the Wilcoxon signed-rank test (Wilcoxon, 1945), a paired non-parametric test appropriate given the sample's non-normal distribution. Budget-correlation (RQ2, descriptive only given n=2 states with sufficient valid data) and border-proximity correlation (H3) used Spearman's rank correlation (Spearman, 1904), robust to non-linear monotonic relationships. The control-group comparison (H4) used a Difference-in-Differences OLS specification (Section 3.7) with both cluster-robust and heteroskedasticity-robust standard errors reported in parallel.

## 4. Results

### 4.1 Village Coverage and Sample Composition

The geocoding pipeline resolved 258 of 559 attempted villages. Inspection of unmatched Arunachal Pradesh entries showed many are not civilian revenue villages but Border Roads Task Force camps, army staging huts, and labour-camp designations — inhabited points along the frontier absent from every available civilian geospatial database, a direct illustration of what "village-level development" consists of on a securitized border rather than merely a data gap.

### 4.2 Built-Up Area Change: A Compositing-Window-Sensitive Result

![Figure 1](outputs/figures/01_ndbi_change_distribution.png)

**Figure 1.** Distribution of NDBI change across all geocoded villages, full-year and summer-matched composites.

Under the full-year composite, mean NDBI change across the 251-village core sample showed no significant increase (Wilcoxon signed-rank, p = 1.000), trending slightly negative at the median. Under the season-matched (June–September) composite, the same test on the same villages (n = 154 with valid data after seasonal dropout) showed a highly significant increase (p < 0.000001) — the opposite conclusion. This reversal is attributed to snow-cover contamination varying between the 2021 and 2025 full-year composites at high altitude, a confound the summer window was designed to avoid; the summer window in turn eliminated Sikkim's data entirely, since all 31 of its geocoded villages returned zero cloud-free imagery in at least one period of that window — Sikkim sits in the peak-monsoon zone during exactly the months chosen to avoid snow.

![Figure 2](outputs/figures/04_state_mean_ndbi_change.png)

**Figure 2.** State-wise mean built-up-area change (summer-matched composite), by state.

### 4.3 Night-Lights Change: A Stable Null

![Figure 3](outputs/figures/06_lights_change_distribution.png)

**Figure 3.** Distribution of VIIRS night-lights change (summer-matched composite).

VIIRS night-lights, tested identically under both compositing windows, showed no significant increase in either (full-year p = 0.050, borderline; summer-matched p = 0.9999). Because night-lights radiance is not subject to the same vegetation/snow phenology confound as a spectral built-up index, its consistency across both windows is read as the more trustworthy signal of the two — and that signal does not support a confirmed increase in night-time economic activity following programme sanction.

![Figure 4](outputs/figures/05_state_mean_lights_change.png)

**Figure 4.** State-wise mean night-lights change (summer-matched composite), by state.

### 4.4 Budget Independence (RQ2)

![Figure 5](outputs/figures/02_state_change_vs_budget.png)

**Figure 5.** State-level mean built-up-area change plotted against sanctioned VVP-I budget.

Restricting to states with sufficient valid summer-window NDBI coverage left two comparable data points: Arunachal Pradesh (120 villages, mean NDBI change +0.0284; ₹2,749.74 crore sanctioned, 2,082 projects) and Uttarakhand (34 villages, mean NDBI change +0.0293; ₹270.58 crore sanctioned, 200 projects). Despite a roughly tenfold difference in sanctioned budget and project count, the two states' mean measured built-up change is nearly identical. Two data points cannot support a formal statistical claim, but this pattern is descriptively consistent with H2: budget scale is not translating proportionally into a correspondingly larger physical development signal.

### 4.5 Border-Proximity Testing (H3)

![Figure 6](outputs/figures/03_h3_border_distance_vs_lights.png)

**Figure 6.** Distance-to-border versus NDBI change and night-lights change, both compositing windows.

Distance to the border/LAC ranged from 0.1 km to 69.4 km across the sample (mean 27.3 km). NDBI change showed no relationship with border proximity in either compositing window (full-year ρ = 0.043, p = 0.497; summer-matched ρ = 0.037, p = 0.650) — a stable non-finding. Night-lights change showed a significant relationship in the full-year window (ρ = -0.259, p < 0.0001, consistent with H3's prediction that closer villages change more) but not in the summer-matched window (ρ = -0.076, p = 0.233) — the same window-sensitivity pattern documented in Section 4.2, and reported with the same caution rather than as a confirmed result.

### 4.6 Control-Group Difference-in-Differences: Isolating a VVP-I-Attributable Effect (H4)

![Figure 8](outputs/figures/08_control_group_did_effect.png)

**Figure 8.** District-fixed-effects DiD coefficient (treated-vs-control gap in change) with 95% confidence intervals, NDBI and night-lights, both compositing windows.

Against the matched 753-village non-VVP control group, the summer-matched NDBI DiD coefficient is positive and significant (did coefficient = +0.0377, 95% CI [+0.0137, +0.0617], cluster-robust p = 0.0021; HC3 no-fixed-effects comparison spec: +0.0287, p = 0.0116) — the treated group's summer NDBI increase exceeds the control group's own change over the same period, by an amount unlikely to be regional-trend noise. The full-year DiD coefficient is not significant (+0.0082, p = 0.2153), reproducing the same window-sensitivity pattern documented in Section 4.2 in a design that additionally controls for the regional trend. Night-lights showed no significant DiD effect in either window (full-year p = 0.7229; summer p = 0.8485). A baseline (2021) balance check found treated villages start from a significantly lower mean NDBI level than control villages in both windows (e.g. summer: treated mean = -0.246 vs. control mean = -0.185, Mann-Whitney p < 0.00001) — expected, given VVP-I priority villages were themselves selected partly for remoteness and security proximity, but a reminder that this comparison rests on a level difference at baseline rather than a directly confirmed shared pre-trend, since a genuine multi-period pre-treatment panel was not extracted for the control group (Section 3.7). A per-district breakdown (14 districts) shows the treated-vs-control gap is directionally positive in 8 of 10 districts with adequate NDBI coverage in the summer window, not concentrated in one or two outlier districts.

### 4.7 Multi-Year Trend: A Non-Monotonic Recovery Pattern

![Figure 9](outputs/figures/09_multiyear_trend.png)

**Figure 9.** Mean NDBI and night-lights radiance at 2021, 2023, and 2025, core sample, both compositing windows, error bars ± 1 SE.

Extending the core sample to a third time point (2023) shows the 2021-vs-2025 comparison rests on a change that is not monotonic across the four-year window. In the summer-matched window, mean NDBI declines from 2021 to 2023 (mean change = -0.0231, Wilcoxon p = 1.000, i.e. not a significant increase — a decline) and then rises from 2023 to 2025 (mean change = +0.0222, p < 0.000001); the overall three-point linear trend across all three years is not itself significant (mean per-village slope = -0.0002/year, Wilcoxon p = 0.442; village-fixed-effects panel regression, p = 0.728). The full-year window shows the identical shape (2021→2023 decline, 2023→2025 significant increase, p = 0.000001; overall trend not significant, p = 1.000 by Wilcoxon, p = 0.000001 by the panel regression — the two specifications disagree here, a discrepancy attributable to the panel regression's greater sensitivity to the larger 2023→2025 recovery outweighing the earlier decline in a way the more conservative per-village-slope Wilcoxon test does not register). Read together, this means the significant 2021-vs-2025 summer-matched result reported as this study's central finding (Section 4.2) is better described as a 2023-to-2025 recovery than as steady multi-year growth, and the earlier decline should not be assumed away when interpreting the headline two-point comparison.

### 4.8 Buffer-Radius Sensitivity: A Stable Result Once Sample Composition Is Matched

![Figure 10](outputs/figures/10_buffer_sensitivity.png)

**Figure 10.** NDBI Wilcoxon p-value (log scale) at 250m, 500m, and 1km buffer radii, summer window — as-extracted samples (grey, varying n) vs. the matched subsample present at all three radii (green, fixed n=154).

Compared directly "as extracted," the significant 500m NDBI result (n=154, p < 0.000001) does not replicate at 250m (n=251, p = 0.126) or 1km (n=251, p = 0.899) — but this comparison is confounded by a large coverage difference: the 250m and 1km extractions, run at a later date, picked up complete data for 97 core-sample villages (66 Arunachal Pradesh, 31 Sikkim) that were null at 500m, a signature of Sentinel-2 archive backfill in the time between extractions rather than a true buffer-radius effect (Section 3.9). Restricting all three buffer radii to the 154-village subsample with valid data at every radius isolates buffer radius as the only variable changing between tests: on this matched subsample, the NDBI result is significant and directionally consistent at all three radii (250m: p = 0.000009; 500m: p < 0.000001; 1km: p = 0.001471). The significant summer NDBI finding is therefore not an artifact of the specific 500m buffer chosen throughout this study.

### 4.9 Robustness Summary

![Figure 7](outputs/figures/07_robustness_summary.png)

**Figure 7.** Significance (p-value, log scale) for all four core tests under both compositing windows, with a reference line at p = 0.05. A test whose two points fall on opposite sides of the line reverses conclusion depending on which window is used.

Read together, the four core tests split into two distinct patterns rather than one. H1 (built-up change) and the H3 night-lights correlation both cross the p = 0.05 line between windows — full-year non-significant, summer-matched significant for H1 (and the reverse for H3 night-lights) — the signature of a compositing-window-sensitive result. The H3 NDBI-proximity test, by contrast, stays non-significant in both windows (p = 0.497 full-year, p = 0.650 summer-matched): a genuinely stable null, not merely a result that happened not to flip. This distinction matters for how each finding should be read — the unstable results are reported as open questions, not as confirmed effects in either direction, while the stable null is reported with more confidence precisely because it did not depend on which window was chosen. The three checks in Sections 4.6–4.8 add a further layer to this picture specifically for the summer-matched NDBI result: it survives a matched-control-group comparison (H4), a buffer-radius sweep once sample composition is held fixed, and is attributable mainly to the second half of the study window rather than the first — three independent stress tests that narrow, rather than resolve, exactly what the significant result represents.

Across the eight core tests reported in this section (four tests × two windows), no multiple-testing correction was applied to the headline p-values, since each test addresses a distinct research question rather than one hypothesis tested eight ways. As a conservative check, applying a Holm-Bonferroni correction across all eight simultaneously (family-wise α = 0.05) leaves the paper's two significant results intact — H1 summer-matched NDBI (p = 9.3 × 10⁻¹⁵) and H3 full-year night-lights (p = 3.2 × 10⁻⁵) both clear even the strictest step in the correction — while every result already treated as non-significant in this paper remains non-significant. The correction does not change any conclusion; it confirms that the two significant results are not artifacts of running several tests. The Sections 4.6–4.8 robustness checks were designed and reported after this correction, as targeted follow-up tests on the one signal that cleared it, rather than as additional draws from the same multiple-testing family.

## 5. Discussion

The central finding of this study is not a confirmed increase or decrease in physical development, but a demonstrated instability in the only metric that produced a "significant" result at all — and, where that instability can be stress-tested with a matched control group, a multi-year trend, and a buffer-radius sweep, a more precise picture of what the surviving signal actually represents. A single-date, single-window spectral comparison in high-relief Himalayan terrain is not, on its own, sufficient grounds for a confident claim about built-up change — precisely because snow cover and monsoon cloud cover both vary by season in ways that can flip a result's sign independent of any true change on the ground. Night-lights, the more temporally stable proxy available, shows no confirmed increase under either window, and where budget and change can be directly compared, a tenfold difference in sanctioned investment did not correspond to a proportionally larger measured effect.

The summer-matched NDBI increase is the one result in this study that clears significance and holds up under three independent stress tests rather than one: it is significantly larger than the change observed in a matched non-VVP control group in the same districts (H4, Section 4.6), it is not an artifact of the specific 500m buffer radius used throughout the rest of this study (Section 4.8), and Holm-Bonferroni correction for multiple testing does not eliminate it (Section 4.9). None of that, however, makes it a simple confirmation of steady VVP-I-driven growth. The three-point trend extension (Section 4.7) shows the 2021-to-2025 change is concentrated in a 2023-to-2025 recovery following an earlier 2021-to-2023 decline — a shape more consistent with a late-window acceleration than a programme producing steady, sustained development from the point of sanction onward, and a pattern this study cannot, from satellite evidence alone, attribute to any specific cause (a genuinely late-starting rollout, a weather-driven dip in the earlier years, or something else). The control-group comparison, meanwhile, strengthens the claim that the surviving signal is VVP-I-attributable rather than a shared regional trend, but its own baseline check found treated and control villages started from measurably different NDBI levels in 2021 — expected, given VVP-I priority villages were themselves selected in part for remoteness, but a reason to treat the DiD estimate as suggestive of a real, isolable effect rather than as a fully clean natural experiment.

Read together with the border-proximity results — a stable null for built-up change and an unstable, window-sensitive result for night-lights — this study's evidence does not support a confident claim that VVP-I's sanctioned investment has produced measurable, verifiable development at the pace or scale its budget would imply, nor that its distribution is confidently explained by border-proximity-driven prioritization over developmental need. What it does support, more precisely than the two-window comparison alone could, is a narrower and more defensible claim: a real, control-group-verified, buffer-radius-stable increase in built-up area is detectable at VVP-I priority villages, but it is concentrated in the more recent half of the study period rather than sustained since sanction, and the programme has still never been the subject of an official impact assessment that could explain why. This is precisely the accountability gap the programme's own parliamentary record identifies: a scheme of this scale, framed simultaneously as welfare and as strategic signal, has never been independently assessed, and this study's own results — including the layers of nuance the robustness checks add rather than remove — illustrate why that gap is consequential rather than resolving it with a convenient answer in either direction.

## 6. Limitations

### 6.1 Village Coverage Gaps

Ladakh (35 sanctioned villages) is fully excluded from village-level analysis; no publicly indexed source names its villages, and closing this gap would require an RTI request not pursued within this study's scope. Himachal Pradesh (7 of 51 inhabited priority villages identified) is carried only as an illustrative case study, not the core statistical sample. Nineteen of Uttarakhand's Pithoragarh villages have confirmed names but unresolved block assignment.

### 6.2 Border Geometry as Cartographic Approximation

Distance-to-border figures rely on Natural Earth's cartographic boundary line, a simplification of a disputed Line of Actual Control with no single internationally agreed alignment, and should be read as relative rather than authoritative.

### 6.3 Budget-Correlation Scope and Ecological Inference (RQ2)

The RQ2 budget-correlation observation rests on only two states with sufficient valid data and is reported descriptively rather than as a statistically confirmatory result; it also compares a state-level sanctioned budget against a village-level sampled mean, an ecological-inference gap — the budget figure describes spending across the whole state's VVP-I portfolio, not specifically the villages this study happened to geocode, so the comparison is suggestive rather than a clean like-for-like test.

### 6.4 Compositing-Window Sensitivity

Most centrally, the built-up-area and border-proximity findings are compositing-window-sensitive rather than stable, and this instability is reported as a limitation of single-date spectral comparison in this terrain, not resolved by preferring whichever result looks cleanest.

### 6.5 Geocoding Coverage and Selection Bias

Only 258 of 559 attempted villages (46%) were successfully geocoded, and the drop-off is uneven — Arunachal Pradesh alone lost 269 of 455 (Section 4.1). A village that fails to geocode against OpenStreetMap or Bhuvan could plausibly be smaller, more remote, or less administratively documented than one that succeeds, which would bias the analyzed sample toward already-more-accessible villages. This was tested directly rather than assumed away: for Arunachal Pradesh, where Census 2011 population and household counts are available for every village in the raw list regardless of geocoding outcome, a Mann-Whitney U test found no significant difference between geocoded and non-geocoded villages in either population (matched mean 135.0 vs. unmatched 145.7; p = 0.310) or households (matched mean 25.8 vs. unmatched 28.8; p = 0.540). Geocoding success in this dataset is not detectably associated with village size, which weighs against — though cannot fully rule out — a size-driven selection bias in the analyzed sample. Sikkim and Uttarakhand's raw village lists do not carry population or household fields, so this check could not be extended to them.

### 6.6 No Ground-Truth Validation

This study is satellite-only: no known-completed VVP-I project (e.g., one confirmed by a dated press release) was used as a positive control to verify that NDBI and VIIRS are sensitive enough, at 500m resolution, to detect development at the scale VVP-I typically funds (a village road, a school building, a handful of homes). A search for a specific, by-name, dated positive control during this study's review did not turn up a completed project that also appears in the 258-village geocoded sample, so this check could not be completed with real data rather than a placeholder; it is carried forward as a concrete item in Future Work rather than skipped silently.

### 6.7 Baseline Imbalance in the Control-Group Comparison

The H4 control-group comparison (Section 4.6) found treated and control villages start from significantly different mean NDBI levels in 2021, and a genuine parallel-pre-trends placebo test could not be run because the control group's satellite extraction covers only the same single before/after pair as the treated sample, not a multi-year pre-treatment panel. District fixed effects address baseline differences at the district level, not village-level selection into the treated group itself, so the DiD estimate should be read as a control-group-adjusted result, not as evidence from a fully clean natural experiment.

### 6.8 Non-Monotonic Multi-Year Pattern

The three-point trend extension (Section 4.7) shows the reported 2021-vs-2025 summer NDBI increase is concentrated in a 2023-to-2025 recovery following an earlier 2021-to-2023 decline, rather than reflecting steady growth across the full window. This study's satellite-only evidence cannot distinguish between several possible explanations for that shape (a late-starting rollout, a weather-driven dip earlier in the window, or some combination), and this limitation should be read alongside Section 4.7 rather than treating the two-point 2021-vs-2025 comparison as if it were a steady trend.

### 6.9 Archive-Timing Confound in the Buffer-Radius Comparison

The 250m and 1km buffer extractions (Section 4.8) were run at a later date than the original 500m extraction, and picked up complete data for 97 core-sample villages that were null at 500m — a Sentinel-2 archive-backfill effect, not a buffer-radius effect, diagnosed directly rather than reported as if it were a genuine finding about buffer size. The matched-subsample comparison in Section 4.8 controls for this, but the underlying asymmetry means the three buffer extractions are not perfectly reproducible snapshots of the same archive state, and a fully clean re-run would require re-extracting all three radii on the same date.

## 7. Future Work

The following are concrete extensions identified during this study's own review process, not yet implemented, and deliberately kept separate from the Discussion and Limitations sections above so that what was actually done is never conflated with what remains open.

### 7.1 SAR-Based Change Detection

Sentinel-1 Synthetic Aperture Radar (VV/VH backscatter or coherence change) is not affected by cloud cover or the optical snow-contamination confound that motivated this study's compositing-window robustness check in the first place. Radar-based change detection would not resolve the debate between the full-year and summer-matched optical results — it would provide a genuinely independent third measurement, immune to both of this study's identified confounds, which could help determine whether either optical result is closer to the truth.

### 7.2 Building-Footprint or Sub-500m Structural Analysis

NDBI at a 500m buffer averages a mix of built-up surface, bare rock, agricultural land, and natural vegetation in a single value — a coarse proxy for what VVP-I actually funds at the village level (individual roads, buildings, small installations). High-resolution optical imagery (PlanetScope) or open building-footprint datasets (e.g., Google/Microsoft building footprints) could support structure-level change detection instead of an area-averaged index.

### 7.3 Ground-Truth Positive-Control Validation

As noted in Limitations, no by-name, dated, independently-confirmed completed VVP-I project was identified during this study that also falls within the 258-village geocoded sample. Identifying even two or three such villages — for instance from a dated press release or news report confirming a specific completed road or building — and checking whether their individual NDBI/VIIRS signal is detectable would directly test this study's implicit assumption that the chosen indices and resolution are sensitive enough to detect the scale of development VVP-I typically funds.

### 7.4 RTI Follow-Through for Himachal Pradesh and Ladakh

Development_Log.md records a deliberate decision not to file Right to Information requests for the two states' missing village-wise annexures, given this study's timeline. Filing those requests remains open and would close the two largest documented coverage gaps with primary-source data rather than the illustrative/excluded treatment used here.

### 7.5 A Genuine Pre-Treatment Panel for the Control Group

The current control-group comparison (Section 3.7, 4.6, 6.7) rests on a single before/after pair rather than a genuine multi-period pre-treatment panel, so a proper parallel-pre-trends placebo test — of the kind this study's own multi-year extension makes possible for the treated sample — could not be run. Extracting 2019 and 2020 values for the same 753-village control group (and, ideally, matching pre-2021 years for the treated sample) would close this gap directly.

## 8. Conclusion

This study finds that India's Vibrant Villages Programme (VVP-I), sanctioned at a scale of approximately ₹4,800 crore across five border states/union territories, cannot currently be shown, with confidence, to have produced measurable, verifiable physical development at its priority villages at the pace or on the steady trajectory its budget and framing would imply — not because no change is detectable, but because the one metric that shows a significant increase does so in only one of two equally defensible measurement windows, while the more temporally stable available proxy shows no increase under either. Subjecting that one significant result to three further, independent stress tests narrows rather than resolves this picture: a district-fixed-effects comparison against 753 matched non-VVP villages in the same districts confirms the summer-matched increase exceeds what the surrounding region experienced on its own (H4), a buffer-radius sweep confirms it is not an artifact of the specific 500m measurement radius used throughout this study, and a three-point 2021/2023/2025 extension shows the change is concentrated in a 2023-to-2025 recovery rather than sustained growth since programme sanction. Where budget scale can be directly compared against measured change, a tenfold difference in investment did not correspond to a proportional difference in outcome. The resulting implication is direct: a scheme of VVP-I's scale and strategic framing should not continue without the independent impact assessment its own parliamentary record confirms has never been conducted — and any future assessment should be held to the same compositing-window, control-group, and multi-year robustness standard applied here, rather than reporting whichever single-window, single-year, uncontrolled result is most convenient.

## References

Buzan, B., Wæver, O., & de Wilde, J. (1998). *Security: A New Framework for Analysis*. Lynne Rienner Publishers.

Zha, Y., Gao, J., & Ni, S. (2003). Use of normalized difference built-up index in automatically mapping urban areas from TM imagery. *International Journal of Remote Sensing*, 24(3), 583–594.

Elvidge, C. D., Baugh, K., Zhizhin, M., Hsu, F. C., & Ghosh, T. (2017). VIIRS night-time lights. *International Journal of Remote Sensing*, 38(21), 5860–5879.

Wilcoxon, F. (1945). Individual comparisons by ranking methods. *Biometrics Bulletin*, 1(6), 80–83.

Spearman, C. (1904). The proof and measurement of association between two things. *American Journal of Psychology*, 15(1), 72–101.

Angrist, J. D., & Pischke, J.-S. (2009). *Mostly Harmless Econometrics: An Empiricist's Companion*. Princeton University Press. [Difference-in-Differences specification, Section 3.7]

Ministry of Home Affairs. (2023, August 9). *Rajya Sabha Unstarred Question No. 2321: Vibrant Villages Programme*.

Ministry of Home Affairs. (2023). *Lok Sabha Question No. 2104: Vibrant Villages Programme*.

Ministry of Home Affairs. (2025). *Rajya Sabha Question No. 401: Vibrant Villages Programme*.

Ministry of Home Affairs. (2025). *Lok Sabha Question No. 4360: Vibrant Villages Programme*.

Ministry of Home Affairs. (2026, February 3). *Lok Sabha Unstarred Question No. 508: Vibrant Villages Programme*. Reply by Shri Nityanand Rai, Minister of State, to a question by Shri Baijayant Panda.

Natural Earth. (2024). *1:10m Cultural Vectors — Admin 0 Boundary Lines*. naturalearthdata.com

OpenStreetMap contributors. (2024). *Overpass API*. overpass-api.de [Non-VVP control-group village identification, Section 3.7]
