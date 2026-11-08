import streamlit as st
from utils.theme import inject_theme, PALETTE
from utils.data import load_data

st.set_page_config(page_title="Methodology & Limitations — BORDER OPTICS", page_icon="📖", layout="wide")
inject_theme()

villages, full_year, summer = load_data()

st.markdown("<h1>📖 METHODOLOGY & LIMITATIONS</h1>", unsafe_allow_html=True)
st.markdown(
    "<h3 style='text-align: center; font-weight: 700;'>Full Transparency and Reproducibility</h3>",
    unsafe_allow_html=True,
)
st.markdown("---")

st.markdown("### Data Sources")

col1, col2 = st.columns(2)
with col1:
    st.markdown("""
    - **Village Lists** — State VVP-I portals, Rajya Sabha / Lok Sabha Q&A annexures
    - **Geocoding** — OpenStreetMap Nominatim, ISRO Bhuvan Village Geocoding API
    - **Non-VVP Control Villages** — OpenStreetMap Overpass API, district-matched
    - **Built-Up Index** — Sentinel-2 SR Harmonized (NDBI), Google Earth Engine
    """)
with col2:
    st.markdown("""
    - **Night-Lights** — VIIRS DNB monthly composites, Google Earth Engine
    - **Triangulation proxies** — Sentinel-1 SAR backscatter, Dynamic World built-up probability (Google Earth Engine)
    - **Ground-truth validation** — Google Open Buildings v3 footprint counts, Google Earth Engine
    - **Border/LAC Geometry** — Natural Earth 10m Admin-0 Boundary Lines
    - **Budget Figures** — Independently compiled from parliamentary records
    """)

st.markdown("---")

st.markdown("### Processing Pipeline")

st.markdown("""
Each village — treated and, identically, the 628-village non-VVP control group — is
buffered (500m primary, with 250m and 1km run as a robustness check) and used as the
region for `reduceRegion` over cloud-masked Sentinel-2 composites (QA60 bitmask) and
VIIRS monthly composites, for both a full-year window and a season-matched (Jun–Sep)
window at 2021 and 2025, plus a third time point (2023) for the core treated sample.
Villages with an empty composite in any period are marked null rather than defaulted to
zero, and image-count columns are retained for quality auditing. Village coordinates and
distance-to-border are computed separately via GeoPandas (nearest-point distance to the
nearest India border/LAC segment, computed geodesically on the WGS84 ellipsoid via
`pyproj.Geod` rather than a single UTM-zone reprojection, since the study area spans
roughly 20 degrees of longitude — see Development Log Entry 18) and merged in by
village ID.
""")

st.markdown("---")

st.markdown("### Statistical Methods")

st.markdown("""
**Primary: difference-in-differences (OLS)** of priority vs. comparison villages, 2021→2025,
with district-by-period fixed effects, so each village is compared only with villages in its
own district, and district-clustered standard errors. With only 13 clusters, p-values use t
with 12 degrees of freedom and an exact wild cluster bootstrap (all 8,192 sign flips); a
no-fixed-effects HC3 specification is reported for comparison. Pre-specified
outcomes: NDBI and night lights; radar and Dynamic World are triangulation outcomes.
**Detectability (SQ1):** the cross-sectional response of each index to Open Buildings
footprint cover converts estimates into building-equivalent area, with an equivalence test
against a doubling of a typical village's buildings. **Descriptive:** two-sided Wilcoxon
signed-rank tests for priority villages' own change, and **Spearman correlation** for border
distance (SQ2, pooled and within districts, with a within-district permutation test).
""")

st.markdown("---")

st.markdown("### Known Limitations")

with st.expander("**Ladakh (UT) — Excluded from Analysis**"):
    st.markdown("""
    No publicly indexed government source with village-wise VVP-I data was found for
    Ladakh's 35 sanctioned villages, despite a deliberate search across state portals,
    parliamentary annexures, and secondary sources. Ladakh is fully excluded from this
    analysis rather than approximated. Getting the names would need an RTI application, which
    was drafted but deliberately not filed, so this is a disclosed, permanent scope boundary,
    not a pending task.
    """)

with st.expander("**Himachal Pradesh — Illustrative Only, Not Core Sample**"):
    st.markdown("""
    Himachal Pradesh has 75 VVP-I priority villages, of which 51 are inhabited (32 in
    Kinnaur, 19 in Lahaul and Spiti); its Action Plan (₹658.31 crore) covers those 51. No
    public list names them, so only 7 could be identified by name from news coverage, and
    all 7 were geocoded. Himachal Pradesh is treated as an illustrative case study, not part
    of the core statistical sample used for hypothesis testing.
    """)

with st.expander("**Sikkim — Outside the Core Sample From Version 2.1**"):
    st.markdown("""
    No district boundary polygon could be retrieved for Sikkim's North district, so the
    control-selection script fell back to a box of about 65 km around the district's
    priority villages, and it took the candidates closest to the border first. By their own
    coordinates, 84 of the 93 Sikkim comparison villages lie outside North Sikkim; many are
    in Nepal, Bhutan or West Bengal. Version 2.0 used them. A second review of the code and
    data found this, and from version 2.1 a comparison village is used only if its district
    was checked against a polygon. That leaves Sikkim with no valid comparison villages, so
    its 31 priority villages are outside the core sample too. The core sample is now 220
    priority and 628 comparison villages in 13 districts. With this change (and the
    within-district model), the full-year Dynamic World estimate is no longer significant;
    the other results stand. Rebuilding Sikkim's comparison villages inside a verified
    boundary is listed as a next step.
    """)

with st.expander("**Uttarakhand — Residual Block Ambiguity**"):
    st.markdown("""
    Block-level assignment for 19 villages in Pithoragarh district carries residual
    ambiguity between Dharchula and Kanalichhina blocks, since no official village-wise
    annexure disambiguating them was found. Block confidence is tracked per-village in
    the underlying dataset.
    """)

with st.expander("**Border/LAC Geometry — A Cartographic Proxy, Not a Legal Claim**"):
    st.markdown("""
    Distance to border is computed against Natural Earth's 10m Admin-0 boundary lines.
    Along the Line of Actual Control this is a cartographic convenience for measurement
    purposes only — it is not a legal, diplomatic, or political claim. The LAC is disputed
    and is not a settled international boundary.

    A second, more specific point worth being explicit about: "distance to border/LAC" is
    computed as distance to the *nearest* India-related boundary segment in Natural Earth's
    data, not specifically the China boundary. Checking this directly against the core
    sample's actual nearest segments: 190 of 220 villages (86%) are indeed nearest to the
    China boundary, but 19 (Arunachal Pradesh, mostly Tawang and West Kameng) are nearest
    to Bhutan, 7 (Uttarakhand's Pithoragarh) are nearest to Nepal, and 4 (Arunachal's
    Anjaw district) are nearest to Myanmar. For those 30 villages,
    the border-distance variable is measuring distance to a different country's
    frontier than the LAC specifically — a reasonable variable for a general
    border-securitization hypothesis (VVP-I villages are, after all, still border villages
    in that broader sense), but not literally "distance to the LAC" for that minority of
    the sample. Repeating the analysis with distance to the China boundary only gives the
    same result (`compute_lac_distance.py`, `h3_within_district.py`).
    """)

with st.expander("**Composite Window Trade-Off — Snow vs. Monsoon Cloud**"):
    st.markdown("""
    Full-year composites risk snow-cover contamination in high-altitude Himalayan
    terrain. Summer-matched (Jun–Sep) composites avoid snow but are vulnerable to monsoon
    cloud cover — at one point, this eliminated all valid summer observations for Sikkim.
    That gap turned out to be an archive-timing artifact rather than a permanent one: the
    Sentinel-2 archive had not yet backfilled scenes for those dates when the original
    extraction ran. A complete re-extraction recovered valid data for all 31 Sikkim
    villages (Development Log Entries 21–22). (Sikkim is outside the core sample from
    version 2.1 for a different reason; see above.) In the 220-village core sample the two
    windows disagree: run two-sided, the full-year window shows a significant NDBI
    *decrease* (p = 2.5×10⁻¹³), while the summer window shows a small *increase*
    (p = 0.037). Comparison villages changed in the same way, so neither is a programme
    difference.
    Where a result's direction or significance still changes between the two windows for
    other tests, that instability continues to be reported as a finding in itself.
    """)

with st.expander("**Control-Group Baseline Imbalance — Night Lights Differ at Baseline**"):
    st.markdown("""
    On the complete data (Development Log Entry 22), only one of the four outcome/window
    combinations still showed treated villages starting from a significantly different mean
    2021 baseline than the control group: night-lights, full-year — which was
    also, at the time, the one control-group DiD result still significant under any
    specification, and the one combination where the two DiD specifications disagreed on
    significance. That imbalance looked resolved for a while: once the control group's own
    contamination was found (Development Log Entry 23 — 20 exact-coordinate duplicates of
    treated villages plus 3 official-name matches, together implicating 23 control-group
    rows) and actually fixed against live data (Entry 25), the full-year night-lights
    baseline was no longer significantly imbalanced on that 732-village control list
    (p = 0.090), and neither was any other combination.

    That picture changed again with the Development Log Entry 37 district-verification fix
    (the control list going from 732 to 721 villages, Tawang and Pithoragarh now
    boundary-verified rather than bbox-matched) — and not in the direction of "more
    resolved." The full-year night-lights baseline is imbalanced again on the corrected
    721-village list: treated mean 0.42821 vs. control 0.43493, n = 251/721,
    **p = 0.03558**. The other three combinations stay balanced (full-year NDBI p = 0.181,
    summer NDBI p = 0.461, summer night-lights p = 0.088). This is disclosed rather than
    smoothed over: fixing a real, independently-verified data-quality problem (unverified
    district labels) surfaced a baseline imbalance that a previous, less-correct version of
    the control list happened not to show. In version 2.1 (220 priority vs. 628 comparison
    villages, Sikkim removed) night lights differ at baseline in both windows (full year
    p = 0.019, summer p = 0.008), while NDBI is balanced (p = 0.79, 0.86). Both night-light
    DiDs stay null (full year p = 0.33, summer p = 0.44, t with 12 df) — but that null can no
    longer be read as sitting on a well-matched baseline for this one outcome/window
    combination, the way it briefly could between Entries 25 and 37 (see Research Paper
    §6, Table 5). A genuine parallel-pre-trends placebo test *has* since been
    run (Development Log Entry 30) — see the "Parallel Pre-Trends Placebo Test" expander
    below — by pulling a second, earlier pre-treatment year (2019) for both groups, closing
    the gap this section used to describe as unclosable with the existing single-pre-period
    extraction.
    """)

with st.expander("**2023 Mid-Point — Shown, Not Interpreted**"):
    st.markdown("""
    Extending the core sample to a third time point (2023) shows that summer NDBI is not a
    steady trend: mean NDBI declines from 2021 to 2023 and recovers by 2025, netting out to
    a small rise. Sentinel-2's QA60 cloud band is not populated for most of
    2022–2024 in the harmonized collection, so the 2023 composites may be effectively unmasked.
    The dip and recovery are therefore not interpreted, and the 2023 point plays no part in the
    programme estimate.
    """)

with st.expander("**Buffer-Radius Comparison — Same-Day Extraction**"):
    st.markdown("""
    The 250 m and 1 km extractions were first pulled on a different day from the 500 m
    run. Because two extractions of the same date range made on different days (or with
    different code) have disagreed in this project, all three radii were re-extracted back
    to back on the same day. On the summer NDBI test for an increase in priority villages
    (n = 220 at every radius) the small rise shows at 250 m and 500 m (p = 0.001, 0.019) and
    not at 1 km (p = 0.22); comparison villages rose by a similar amount (DiD null). The earlier explanation for such disagreements, Sentinel-2
    "archive backfill", has not been verified; a check is prepared
    (`src/acquisition/check_s2_archive_ingestion.py`).
    """)

with st.expander("**SQ2 Border Distance — Pooled Correlations Do Not Hold Within Districts**"):
    st.markdown("""
    Pooled across all 220 villages, summer NDBI change rises with distance from the boundary
    (ρ = +0.23) and full-year night-light change falls with it (ρ = −0.25). Earlier versions
    treated both as robust because they survived leave-one-district-out, randomization
    inference and a spatial-autocorrelation correction. None of those checks separates
    variation **within** districts from differences **between** districts.

    `src/analysis/h3_within_district.py` does: villages are ranked inside their own district
    and distance is permuted only within districts. Within districts the summer NDBI
    association disappears (ρ = +0.01, p = 0.93) and the night-light association reverses:
    villages *farther* from the boundary gained more light (ρ = +0.26, p = 0.015 full year;
    +0.45, p < 0.001 summer). Using distance to the China boundary only
    (`compute_lac_distance.py`; 30 villages are nearest to Bhutan, Nepal or Myanmar) gives
    the same pattern. The pooled correlations reflect which districts lie closer to the
    boundary, not a proximity gradient, so there is no consistent evidence that change
    concentrates near the border.
    """)

with st.expander("**Parallel Pre-Trends Placebo Test — Clean Coefficients, One Warning**"):
    st.markdown("""
    The baseline-imbalance section above used to note that a genuine
    parallel-pre-trends placebo test could not be run, because the control
    group's satellite extraction only ever had one pre-treatment point (2021)
    to work with — a level-balance check, not a trend check. That gap is now
    closed (Development Log Entry 30): a second, earlier pre-treatment year
    (2019) was extracted for both treated and control villages, both windows,
    via `src/acquisition/extract_pretreatment_baseline.py`, and a placebo DiD
    comparing the 2019-to-2021 change was run via
    `src/analysis/pretreatment_placebo_test.py` — a period during which VVP-I
    could not possibly have had an effect, since the programme wasn't
    sanctioned until February 2023.

    In version 2.1 (220 priority vs. 628 comparison villages, district fixed
    effects on the 2019-to-2021 change, t with 12 df) all four placebo
    coefficients are null: full-year NDBI (+0.0069, p = 0.62), full-year
    lights (−0.0083, p = 0.74), summer NDBI (+0.0070, p = 0.17) and summer
    lights (−0.0030, p = 0.66). Dynamic World is null too (p = 0.41 full
    year, 0.21 summer). One warning remains: for summer NDBI the raw
    2019-to-2021 changes of the two groups still differ (Mann–Whitney
    p = 0.006), so parallel trends for summer NDBI are uncertain. This is
    reported as a warning, not rounded up to a clean pass.

    Version 2.0 (721 comparison villages, Sikkim included) gave the same
    pattern: summer NDBI placebo p = 0.074 with a raw p = 0.00003, the
    other three null.
    """)

with st.expander("**13 District Clusters — An Exact Wild Cluster Bootstrap, Not Just Asymptotics**"):
    st.markdown("""
    The DiD's cluster-robust standard errors rely on having enough clusters
    (usually 30-40+ recommended) for their own asymptotic theory to be
    trustworthy — this study has only 13. Rather than
    take that on faith, `src/analysis/wild_cluster_bootstrap.py` re-derives
    significance for all four outcome/window DiD estimates using an exact
    wild cluster bootstrap (Cameron, Gelbach & Miller 2008, restricted
    variant): full enumeration of all 2^13 = 8,192 possible Rademacher
    (+1/-1) sign-flip combinations across the 13 district clusters, refitting
    the model under each one to build an exact bootstrap null distribution for
    the test statistic, rather than an approximation. All four remain
    non-significant under this stricter test — full-year NDBI p = 0.422,
    full-year lights p = 0.325, summer NDBI p = 0.917, summer lights p = 0.480
    — meaning the small cluster count is not itself manufacturing a false
    null; the primary result's non-significance holds up under a test
    specifically designed to be robust to too few clusters.

    (This script's own manual OLS and cluster-robust standard-error
    implementation was validated by reproducing `did_model.py`'s already-
    published coefficient and standard error to roughly 10 significant figures
    before being trusted for the bootstrap itself.)
    """)

with st.expander("**Triangulation — Radar Null, Dynamic World Positive**"):
    st.markdown("""
    The same DiD was run on Sentinel-1 radar (VV and VH) and on Dynamic World's built-up
    probability. Radar is null in both windows. Dynamic World shows a small positive
    difference in the summer window: +0.0050 (p = 0.006, t with 12 df; wild cluster
    bootstrap p = 0.017; Holm-adjusted across the six triangulation tests p = 0.038)
    (`src/analysis/dynamic_world_robustness.py`). It is significant in all 12
    leave-one-district-out reruns. The full-year estimate is smaller and not significant
    (+0.0024, p = 0.067; bootstrap p = 0.072). In version 2.0 it was significant
    (p = 0.031), but only because of the misplaced Sikkim comparison villages. A 2019–2021
    placebo is null in both windows (p = 0.41, 0.21), so the summer result is not an earlier
    trend continuing.

    Converted with each measure's own response to buildings
    (`src/analysis/measurement_sensitivity.py`), the summer Dynamic World difference
    corresponds to roughly 1,900 m² of built-up surface per village (an approximate
    conversion). NDBI could not have registered a
    change that size, which is why the measures disagree; at village level they point the
    same way in only 31–63% of villages. Whether the Dynamic World difference is early
    programme construction, related works (roads, the state's model-village schemes), or a
    classifier artefact is not yet established. Footprint-zone outcomes and a 2026 follow-up
    are prepared to test it.

    **Case villages, corrected in v2.0.** News reports of the 31 October 2023 visit to Anjaw
    (Arunachal Times; ANI) list new facilities at Walong (terminal building, girls' hostel),
    Kaho and Musai (basketball courts, solar streetlights, school buildings). Kaho's and
    Musai's works are described as state Golden Jubilee model-village works, later merged
    into VVP; Walong's are not described as VVP. The only works described as VVP-funded are at
    Kibithoo, which is not in the sample because its geocoding failed. Measured as a
    percentile of all 220 core villages' change, night lights at Kaho and Walong were in the
    top 5% and Dynamic World at the 97th and 81st percentiles, while Musai was near the median
    on both, and NDBI fell further than at most villages at all three. Three villages in one
    district are illustrative, not validation.
    """)

with st.expander("**Control-Group Construction — Selection Rule and Buffer Overlap**"):
    st.markdown("""
    Two details of how the control group was built, disclosed here because they bear on
    the DiD. First, after the distance and exclusion filters, `select_control_villages.py`
    keeps up to 3× the treated count per district by taking the candidates **closest to
    the border** first (it sorts by distance to border), not a random draw. The control
    group is therefore selected partly on border proximity.

    Second, the contamination fix excludes control candidates within 50 m of a treated
    village, but every extraction uses a 500 m buffer. So a control village less than
    1 km from a treated village shares pixels with it: 82 of the 628 controls are in that
    position (5 of them within 200 m). Shared pixels would push the DiD toward zero.
    `src/analysis/buffer_overlap_sensitivity.py` re-runs the primary DiD without those 82
    villages: all four results stay null (full-year NDBI p = 0.36, full-year lights
    p = 0.33, summer NDBI p = 0.92, summer lights p = 0.51, t with 12 df), so the overlap
    does not explain the null.
    """)

with st.expander("**Extraction Timing, Pipeline and Cloud Masking — Open Items**"):
    st.markdown("""
    The full-year treated values come from an early Earth Engine Code Editor export that is
    not preserved in the repository, made about seven weeks before the control extraction.
    The repository's own Python pipeline gives village values that differ by more than 0.01
    NDBI at 164 of 220 villages in 2021 and 190 in 2025 — more than the change a doubling of
    buildings would produce. Substituting them changes no conclusion (full-year NDBI DiD
    +0.0052, p = 0.40; `src/analysis/sample_qa_sensitivity.py`), but the full-year NDBI values
    cannot be exactly reproduced until the same-day re-extraction is run. A same-day
    full-year re-extraction is the first step in `docs/NEXT_STEPS_EARTH_ENGINE.md`.

    Sentinel-2's QA60 cloud band is not populated for most of 2022 to early 2024 in the
    harmonized collection, so the 2023 multi-year composites may be effectively unmasked and
    the 2023 dip should not be interpreted. The prepared footprint-zone extraction uses Cloud
    Score+ instead, which is consistent across all years.
    """)

with st.expander("**Sample Quality — What Was Found and How Much It Matters**"):
    st.markdown("""
    A v2.0 audit found: 7 pairs of treated villages sharing identical coordinates; 29 of 220
    core treated buffers (and 60 control buffers) with no mapped building, suggesting the point may
    not sit on the settlement (e.g. Lachung); Joshimath, a block-headquarters town, in the
    treated list; and 10 control villages that are official priority villages written with a
    qualifier ("Sawa" vs "Sawa H.Q."). Re-running every test without each of these, and
    without all of them together, leaves every NDBI and night-light DiD null and the summer
    Dynamic World DiD significant (`sample_qa_sensitivity.py`, `dynamic_world_robustness.py`).
    Joshimath alone accounts for most of the mean summer night-light change (+0.032 with it,
    +0.005 without), which is why medians are reported. Geocodes still need checking against high-resolution imagery.
    """)

with st.expander("**What the Design Could Detect — In Physical Units**"):
    st.markdown("""
    Earlier versions argued that a Cohen's-d minimum detectable effect of 0.157 made the
    null "substantive". That was misleading: Cohen's d says nothing about whether plausible
    construction moves a buffer-average index at all. Buildings cover a median 0.32% of a
    500 m buffer, and across all 848 villages buffer-mean NDBI rises by only about 0.5–0.8 per
    unit of building cover. Doubling a typical village's buildings would therefore move NDBI
    by about 0.002, which is 12–17% of the DiD's minimum detectable effect, and the NDBI
    confidence intervals span changes from a loss of about four times to a gain of up to nine
    times a typical village's building stock. An equivalence test against a doubling fails for both windows. The NDBI
    null is uninformative about construction, not evidence that none happened
    (`src/analysis/measurement_sensitivity.py`).
    """)

st.markdown("---")

st.error("""
**Border-distance correlations should be read alongside the LAC geometry caveat above**
— any observed relationship reflects distance to a disputed, de facto line, not a settled
legal boundary.
""")

st.markdown("---")
st.markdown(
    "<p class='caption-text' style='text-align:center;'>BORDER OPTICS — Evaluating a Place-Based Border Programme from Space: Evidence and Indicator Limits from India's Vibrant Villages Programme</p>",
    unsafe_allow_html=True,
)