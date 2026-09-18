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
Each village — treated and, identically, the 721-village non-VVP control group — is
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
**Wilcoxon signed-rank test** (paired, non-parametric) for before/after change in NDBI
and night-lights, since normality cannot be assumed at this sample size, and for
per-village multi-year trend slopes tested against zero. **Spearman correlation**
(rank-based, robust to non-linear monotonic relationships) for state-level budget vs.
change (RQ2) and distance-to-border vs. change (H3) — both explicitly exploratory given
small state and moderate village counts respectively. **Difference-in-Differences (OLS)**
with district fixed effects and cluster-robust standard errors (14 district clusters,
plus a parallel HC3 no-fixed-effects specification) for the treated-vs-control comparison
(H4), and a **village-fixed-effects panel regression** as a second specification for the
multi-year trend.
""")

st.markdown("---")

st.markdown("### Known Limitations")

with st.expander("**Ladakh (UT) — Excluded from Analysis**"):
    st.markdown("""
    No publicly indexed government source with village-wise VVP-I data was found for
    Ladakh's 35 sanctioned villages, despite a deliberate search across state portals,
    parliamentary annexures, and secondary sources. Ladakh is fully excluded from this
    analysis rather than approximated. This is documented as an open gap, not silently
    omitted.
    """)

with st.expander("**Himachal Pradesh — Illustrative Only, Not Core Sample**"):
    st.markdown("""
    Of 75 priority villages under the VVP-I Action Plan (₹658.31 crore), only 51
    inhabited villages could be identified by name (32 in Kinnaur, 19 in Lahaul and
    Spiti), and only 7 of those could be reliably geocoded. Himachal Pradesh is treated
    as an illustrative case study, not part of the core statistical sample used for
    hypothesis testing.
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
    sample's actual nearest segments: 220 of 251 villages (88%) are indeed nearest to the
    China boundary, but 19 (Arunachal Pradesh, mostly Tawang and West Kameng) are nearest
    to Bhutan, 8 (Sikkim's North district and Uttarakhand's Pithoragarh) are nearest to
    Nepal, and 4 (Arunachal's Anjaw district) are nearest to Myanmar. For those 31 villages,
    the H3 "border proximity" variable is measuring distance to a different country's
    frontier than the LAC specifically — a reasonable variable for a general
    border-securitization hypothesis (VVP-I villages are, after all, still border villages
    in that broader sense), but not literally "distance to the LAC" for that minority of
    the sample. H3 is already treated as exploratory in this study for other reasons; this
    is an additional reason to read it that way rather than as a clean LAC-proximity test.
    """)

with st.expander("**Composite Window Trade-Off — Snow vs. Monsoon Cloud**"):
    st.markdown("""
    Full-year composites risk snow-cover contamination in high-altitude Himalayan
    terrain. Summer-matched (Jun–Sep) composites avoid snow but are vulnerable to monsoon
    cloud cover — at one point, this eliminated all valid summer observations for Sikkim.
    That gap turned out to be an archive-timing artifact rather than a permanent one: the
    Sentinel-2 archive had not yet backfilled scenes for those dates when the original
    extraction ran. A complete re-extraction recovered valid data for all 31 Sikkim
    villages, and on that complete data, both compositing windows now agree that built-up
    change is not significant (Development Log Entries 21–22; see Statistical Validation).
    Where a result's direction or significance still changes between the two windows for
    other tests, that instability continues to be reported as a finding in itself.
    """)

with st.expander("**Control-Group Baseline Imbalance — Resolved, Then Reopened by a Later Fix**"):
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
    the control list happened not to show. The full-year night-lights DiD result itself
    stays null on the corrected list (p = 0.45334, see H4 above) — but that null can no
    longer be read as sitting on a well-matched baseline for this one outcome/window
    combination, the way it briefly could between Entries 25 and 37 (see Research Paper
    §6.7 for the full account). A genuine parallel-pre-trends placebo test *has* since been
    run (Development Log Entry 30) — see the "Parallel Pre-Trends Placebo Test" expander
    below — by pulling a second, earlier pre-treatment year (2019) for both groups, closing
    the gap this section used to describe as unclosable with the existing single-pre-period
    extraction.
    """)

with st.expander("**Multi-Year Trend Is Not Monotonic (and Nets Out to a Null, Like the Two-Point Comparison)**"):
    st.markdown("""
    Extending the core sample to a third time point (2023) shows the 2021-vs-2025 summer
    NDBI comparison — itself not significant on the complete data — is not a steady trend
    either: mean NDBI declines from 2021 to 2023, then rises significantly from 2023 to
    2025, netting out to no significant three-point linear trend overall. This is
    consistent with, not a contradiction of, the two-point comparison's own null result.
    This study's satellite-only evidence cannot distinguish between possible explanations
    for the decline-then-recovery shape (a late-starting rollout, a weather-driven dip
    earlier in the window, or some combination) — see Statistical Validation.
    """)

with st.expander("**Buffer-Radius Comparison — An Archive-Timing Confound, Present in Both Directions**"):
    st.markdown("""
    Sentinel-2's archive keeps backfilling scenes for past dates, so any two extractions
    of the same fixed date range, run on different days, can disagree on scene counts and
    composite values even with identical query parameters — a mechanism this project has
    now seen affect both the 500m extraction (Development Log Entries 21–22, where a
    stale extraction was missing an entire state's villages) and, separately, the 250m/1km
    comparison here (where the two smaller/larger radii were run in August, before the
    fresh, complete 500m re-extraction). The buffer-radius conclusion is unaffected either
    way — all three radii are null on the summer NDBI test, whether compared as-extracted
    or restricted to villages valid at every radius (now the full core sample at every
    radius). A same-day re-pull of all three radii together has since been done (see
    Research Paper §4.8): all three now stand at n=251, pulled the same day, closing the
    archive-timing gap this section originally flagged.
    """)

with st.expander("**H3 Border-Proximity — Stress-Tested, and Surviving**"):
    st.markdown("""
    Two H3 border-proximity correlations survive the paper-wise Holm-Bonferroni
    correction: summer NDBI (ρ = +0.291) and full-year night-lights (ρ = -0.252).
    Both have now been put through the same leave-one-district-out and
    randomization-inference checks that this study's own now-null results (the
    summer NDBI-change test, the full-year lights DiD) were checked with before
    failing — `src/analysis/h3_border_proximity_robustness.py`. Both survive:
    14 of 14 district-dropped reruns stay significant with the same sign, and
    2,000-permutation randomization inference gives p<0.001 for each. The
    full-year lights result had previously been described as robust only
    because it stayed significant across several data re-extractions — a
    weaker claim than actually being checked this way, which it now has been.

    One more check has since been added, and it's a more conservative one than
    either of the above: these 251 villages are not spatially independent
    observations, so an ordinary p-value can overstate significance if nearby
    villages' values are correlated with each other for reasons that have
    nothing to do with border distance. `src/analysis/spatial_moran_and_h3_correction.py`
    first confirms both outcomes ARE spatially autocorrelated (Moran's I = 0.346,
    p = 0.001 for summer NDBI change; I = 0.076, p = 0.003 for full-year lights
    change — reproducing this study's own already-published values as an internal
    check), then calibrates a spatial autoregressive model to match that same
    autocorrelation and re-derives significance from 2,000 spatially-structured
    synthetic fields rather than treating villages as independent. Both H3
    findings survive this stricter test too: spatially-corrected p = 0.0295 for
    summer NDBI (naive p = 0.0000026) and p = 0.0035 for full-year lights (naive
    p = 0.0000547) — weaker than the naive p-values, as expected once spatial
    clustering is accounted for, but still comfortably below 0.05.

    The two remaining checks from the original plan are done now too
    (Development Log Entry 27). On linearity: summer NDBI's correlation with
    distance is close to a straight line across all five distance quintiles
    (quadratic term not significant, F=0.89, p=0.347); full-year lights'
    quintile pattern isn't monotonic (rising, falling twice, then jumping back
    up), though a formal quadratic test still doesn't flag it as curved
    (F=0.69, p=0.406) — the simplest read is that this one looks more like a
    handful of districts sitting at particular distances than a smooth
    proximity effect. On the three-point 2021/2023/2025 cross-check: both
    correlations reproduce closely over the full period (summer NDBI
    rho=+0.293 vs. the two-point extraction's +0.291; full-year lights
    rho=-0.252, exactly matching), but neither is stable across sub-periods —
    summer NDBI's relationship flips sign between 2021-2023 and 2023-2025, and
    full-year lights weakens substantially in the second half. Neither of
    these newer findings overturns either H3 result, but "stress-tested and
    surviving" needs the more precise description above rather than a blanket
    "stable and linear" claim.
    """)

with st.expander("**Parallel Pre-Trends Placebo Test — Now Run, Mostly Clean**"):
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

    Three of the four resulting checks are clean: full-year NDBI (placebo
    coefficient +0.00398, p = 0.73497), full-year lights (-0.00647,
    p = 0.75898), and summer lights (+0.00632, p = 0.52021) all show no
    significant pre-treatment divergence between treated and control
    villages — direct evidence *for* this study's DiD design, not merely an
    unexamined assumption behind it. The fourth is a genuine, flagged
    exception: summer NDBI's placebo coefficient is +0.01173, p = 0.07421 —
    not significant at the conventional threshold under the
    district-fixed-effects specification, but close to it, and the
    unadjusted raw comparison for the same combination is sharply
    significant (p = 0.00003). This is reported as a borderline result, not
    rounded up to a clean pass. It's also worth noting this borderline
    pre-period effect runs in the *opposite* direction from the real,
    already-null summer NDBI DiD (-0.00275) — so it does not look like a
    pre-existing trend that mechanically continues into and explains away the
    main result.

    These are the district-verification-corrected, 721-village figures
    (Development Log Entry 41): re-run against the corrected control list,
    closing the vintage gap this section previously flagged. The immediately
    preceding 732-village version had full-year NDBI p=0.864, full-year
    lights p=0.755, summer lights p=0.968, and summer NDBI p=0.064 (raw
    p=0.00001) — the same borderline pattern, no reversal.
    """)

with st.expander("**14 District Clusters — An Exact Wild Cluster Bootstrap, Not Just Asymptotics**"):
    st.markdown("""
    The district fixed-effects DiD's cluster-robust standard errors rely on
    having enough clusters (usually 30-40+ recommended) for their own
    asymptotic theory to be trustworthy — this study has only 14. Rather than
    take that on faith, `src/analysis/wild_cluster_bootstrap.py` re-derives
    significance for all four outcome/window DiD estimates using an exact
    wild cluster bootstrap (Cameron, Gelbach & Miller 2008, restricted
    variant): full enumeration of all 2^14 = 16,384 possible Rademacher
    (+1/-1) sign-flip combinations across the 14 district clusters, refitting
    the model under each one to build an exact bootstrap null distribution for
    the test statistic, rather than an approximation. All four remain
    non-significant under this stricter test — full-year NDBI p = 0.354,
    full-year lights p = 0.505, summer NDBI p = 0.585, summer lights p = 0.680
    — meaning the small cluster count is not itself manufacturing a false
    null; the primary result's non-significance holds up under a test
    specifically designed to be robust to too few clusters.

    (This script's own manual OLS and cluster-robust standard-error
    implementation was validated by reproducing `did_model.py`'s already-
    published coefficient and standard error to roughly 10 significant figures
    before being trusted for the bootstrap itself.)
    """)

with st.expander("**Triangulation Against Independent Proxies — An Open Tension, Not a Confirmation**"):
    st.markdown("""
    The primary design uses NDBI and night-lights. As a further check, the
    same control-group DiD was run on two independent proxies of different
    kinds — Sentinel-1 SAR backscatter (VV and VH, a genuinely different
    sensor, radar rather than optical, immune to the cloud-masking concerns
    that affect optical imagery) and Dynamic World, a machine-learned
    per-pixel built-up probability that is algorithm-independent of NDBI but
    not sensor-independent, since it is itself derived from the same
    Sentinel-2 imagery — via
    `src/analysis/triangulation_analysis.py`. This was meant to be an ordinary
    robustness check. For SAR, that's what it was: null in both windows, both
    polarizations, agreeing with NDBI. For Dynamic World, it wasn't: its
    control-group DiD is significant in **both** windows (full-year coefficient
    +0.0026, p = 0.0159; summer +0.0059, p = 0.0006).

    That disagreement is hard to dismiss as one stray significant test among
    many, for two reasons. First, `src/analysis/building_footprint_validation.py`
    checked all three proxies against an independent, non-satellite ground
    truth — actual building counts from Google's Open Buildings dataset — and
    Dynamic World tracks real building counts far more closely (Spearman
    ρ = 0.808) than NDBI (ρ = 0.399) or night-lights (ρ = 0.478) do. Second, at
    three villages this project separately confirmed underwent real
    construction (Walong — a border-terminal building and a hostel, Kaho — a
    basketball court and solar streetlighting, Musai — solar streetlighting),
    Dynamic World and night-lights both correctly
    registered a before-to-after increase at all three, while NDBI moved in
    the *wrong* direction at all three.

    A village-level cross-check (`src/analysis/dw_sar_ndbi_village_level_check.py`)
    found the three proxies agreeing on the direction of change in only about a
    third to two-thirds of individual villages, depending on the proxy pair
    and window — close to chance. This is reported as this study's single most
    important open question, not resolved in either direction: it could mean
    the primary 500m-buffer NDBI measure is not sensitive enough to detect a
    real, modest VVP-I effect that Dynamic World is picking up, or it could
    mean Dynamic World's significant DiD is itself a different kind of false
    positive. Night-lights detecting the three ground-truth cases correctly
    while its own aggregate control-group DiD stays null shows these two things
    ("detects the case-study villages" and "produces a significant aggregate
    result") don't automatically travel together — a reason for caution before
    reading too much into either proxy's result on its own.

    One more check closes out what could be tested without a further live
    re-extraction (Development Log Entry 43): a Dynamic World analogue of the
    NDBI/lights pre-treatment placebo test above — a genuine second
    pre-treatment year (2019), both groups, both windows, comparing the
    2019-to-2021 change in DW "built" probability, a period VVP-I could not
    possibly have affected since it wasn't sanctioned until February 2023.
    Both windows come back clean (full-year p = 0.93406, summer p = 0.17869)
    — no pre-existing divergence between treated and control villages in
    either window. This doesn't resolve the disagreement above: whether
    Dynamic World's significant control-group DiD reflects a real, small
    effect the other two proxies are missing, or a different kind of false
    positive, is still an open question. But it does rule out one specific
    candidate explanation: it isn't a continuation of a pre-existing trend
    that was already there before VVP-I existed.
    """)

with st.expander("**Statistical Power — What This Design Could (and Couldn't) Detect**"):
    st.markdown("""
    A null result says a test wasn't significant — on its own, it doesn't say
    whether the design could have detected a real effect if one existed.
    `src/analysis/power_analysis.py` computes the Minimum Detectable Effect
    (MDE) for the primary H1 (treated-only) and H4 (control-group DiD) tests
    at 80% power, α=0.05, using t-quantiles at this study's own degrees of
    freedom rather than a large-sample z approximation. H1's MDE, as Cohen's
    d, is 0.157 across every outcome/window — comfortably under Cohen's own
    "small effect" threshold of 0.2 — meaning this design was sensitive
    enough to catch a small-to-moderate real effect had one existed; H1's
    null is substantive, not a power artifact. H4's cluster-based design is
    less sensitive, as expected, but every observed H4 coefficient still
    sits at only 15-35% of its own detection threshold — a clear gap, not a
    near-miss.
    """)

st.markdown("---")

st.warning("""
**Budget correlation (RQ2) is exploratory only** — with just three states with sufficient
valid data (Arunachal Pradesh, Uttarakhand, and — as of the complete summer-window
extraction — Sikkim), and a correlation whose direction itself flips between compositing
windows at this sample size, this should not be read as a confirmatory or causal result.
""")

st.error("""
**H3 border-proximity correlation should be read alongside the LAC geometry caveat above**
— any observed relationship reflects distance to a disputed, de facto line, not a settled
legal boundary.
""")

st.markdown("---")
st.markdown(
    "<p class='caption-text' style='text-align:center;'>BORDER OPTICS — A Satellite-Based Verification Framework</p>",
    unsafe_allow_html=True,
)