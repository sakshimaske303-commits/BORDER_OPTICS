# BORDER OPTICS — Development Log

This is my working log for BORDER OPTICS, a satellite-verification study I built to independently test whether India's Vibrant Villages Programme has produced measurable, on-the-ground development in the border villages it targets. I kept this log the way I keep every project's log — as an honest, chronological record of the decisions, dead ends, and fixes that went into the analysis, not a cleaned-up summary written after the fact.

What follows is organized as a set of entries, each covering one phase of the work: framing the research questions, building the village-level dataset, geocoding it, pulling satellite imagery, running the statistical tests, and the review passes that came after. Every number, p-value, and citation below reflects what I actually found when I ran the analysis, including the results that didn't go the way I expected.

*November 2026: entries that only recorded housekeeping (dashboard and figure layout, document syncing, file paths, review rounds that changed no result) were removed, so that this log shows only changes and additions to the research. The remaining entries keep their original numbers, so references to them elsewhere in the project still work. The full earlier log is in the repository's git history.*

## Index

1. [Entry 1](#entry-1)
2. [Entry 2](#entry-2)
3. [Entry 3](#entry-3)
4. [Entry 4](#entry-4)
5. [Entry 5](#entry-5)
6. [Entry 6](#entry-6)
7. [Entry 9](#entry-9)
8. [Entry 10](#entry-10)
9. [Entry 12](#entry-12)
10. [Entry 13](#entry-13)
11. [Entry 14](#entry-14)
12. [Entry 15](#entry-15)
13. [Entry 18](#entry-18)
14. [Entry 20](#entry-20)
15. [Entry 21](#entry-21)
16. [Entry 22](#entry-22)
17. [Entry 23](#entry-23)
18. [Entry 24](#entry-24)
19. [Entry 25](#entry-25)
20. [Entry 26](#entry-26)
21. [Entry 27](#entry-27)
22. [Entry 28](#entry-28)
23. [Entry 29](#entry-29)
24. [Entry 30](#entry-30)
25. [Entry 31](#entry-31)
26. [Entry 32](#entry-32)
27. [Entry 33](#entry-33)
28. [Entry 34](#entry-34)
29. [Entry 35](#entry-35)
30. [Entry 36](#entry-36)
31. [Entry 37](#entry-37)
32. [Entry 39](#entry-39)
33. [Entry 42](#entry-42)
34. [Entry 43](#entry-43)
35. [Entry 44](#entry-44)
36. [Entry 46](#entry-46)
37. [Entry 47](#entry-47)
38. [Entry 48](#entry-48)
39. [Entry 49](#entry-49)
40. [Entry 50](#entry-50)

## Entry 1

BORDER OPTICS is my independent satellite-verification study of India's Vibrant Villages Programme (VVP), the Government of India's border-area development scheme launched in 2022–23. VVP-I sanctioned roughly ₹4,800 crore (later detailed as 2,558 works worth ₹3,431 crore) across 2,967 border villages in 46 blocks, 19 districts, and 5 states/UTs — Arunachal Pradesh, Himachal Pradesh, Uttarakhand, Sikkim, and Ladakh — with 662 of those villages designated "priority" villages for Phase 1 development.

I started this project because VVP sits at an intersection I find hard to treat as three separate academic silos: political science, geospatial science, and economics. Politically, VVP reads as a textbook case of securitization theory (Buzan and Waever) — border infrastructure framed as civilian welfare development while functioning simultaneously as a geopolitical signal along a contested frontier. Economically, it's a large, multi-year public investment whose actual delivery has never been independently measured. Geospatially, it's a rare case where a government development claim can be tested directly against satellite evidence — built-up area change, road construction, night-time lights — rather than taken on faith.

What actually pushed me to start was a single sentence on the parliamentary record: a reply stating explicitly that "no impact assessment has been carried out" for VVP. A scheme this large, this strategically framed, and this expensive has no independent, public, evidence-based accounting of whether the development it promised has actually happened on the ground, and that gap is what I set out to close.

My aim was to independently verify, using multi-temporal satellite imagery and open government data, whether VVP-I's "priority" villages show measurable physical development — built-up area expansion, road network growth, night-time light intensity change — between programme sanction and the present, and whether that development, where present, correlates with each state's sanctioned budget and project count, or diverges from it in ways that raise questions about implementation, prioritization, or securitization logic overriding genuine developmental need.

I framed four questions I wanted the data to answer, and three hypotheses coming out of the securitization framing. First, whether VVP-I priority villages show statistically detectable built-up area growth between a pre-programme baseline and the present, using Sentinel-2/Landsat imagery. Second, whether the magnitude of physical change correlates with each state's sanctioned VVP budget and project count, or whether there are states where large budgets haven't translated into detectable ground change. Third, whether night-time light (VIIRS) trends corroborate or contradict the built-up-area findings. Fourth, whether there's a spatial or political pattern to where development is concentrated — for example, villages closer to the Line of Actual Control developing faster than those further back, consistent with a securitization-driven rather than needs-driven allocation logic. My working hypotheses were that priority villages would show a statistically significant increase in built-up area after programme sanction compared to a matched pre-programme baseline; that the size of this change would not be uniformly proportional to sanctioned budget, with some high-budget states showing comparatively muted physical change and vice versa; and that villages nearer the international border/LAC would show disproportionately faster change than villages further back within the same state.

Before any of that could be tested, I needed a complete, verified, village-level dataset of all 662 VVP-I priority villages across the five states/UTs — village/habitation name, district, block, and where available, LGD code, Census 2011 households/population, and coordinates — since satellite verification requires knowing exactly where to look before any imagery analysis can begin. By the point this entry was written, Arunachal Pradesh (455/455 villages) was fully compiled and verified against the official state government source, including LGD codes and Census figures. Sikkim (46/46 villages) was fully compiled and verified against a Rajya Sabha parliamentary annexure. Uttarakhand (51/51 village names) was compiled and cross-verified against official block-wise totals, though the block assignment for 19 of Pithoragarh's villages remained genuinely unresolved pending a primary source pairing name to block. Himachal Pradesh (75 villages) and Ladakh (35 villages) remained incomplete — a documented, ongoing data-availability limitation rather than an unattempted one, with specific leads (an unindexed page in a Himachal government PDF, an RTI-only path for Ladakh) identified and being pursued.

This entry captures the project's intent before the entries that follow document the actual acquisition process, sourcing decisions, and verification steps I used to get there.

## Entry 2

With the project's framing established in Entry 1, the next task was building the
foundation every downstream analysis depends on: a verified, village-level list of
all 662 VVP-I priority villages across Arunachal Pradesh, Sikkim, Uttarakhand,
Himachal Pradesh, and Ladakh. This turned into the most time-consuming phase of the
project so far, and it did not resolve cleanly for all five.

**Arunachal Pradesh — fully resolved (455/455).**
Sourced the complete list from the Arunachal Pradesh state government's official
identified-villages document. It included district, block, habitation name, LGD
code, and Census 2011 households/population for every entry. Verified it by
counting rows and cross-tabulating by district — the totals matched the officially
reported "455 villages across 11 districts" figure exactly, so this dataset is
complete and fully sourced from a primary government document.

**Sikkim — fully resolved (46/46).**
Found the actual village-wise annexure inside a Rajya Sabha Unstarred Question
reply (Question No. 2321, dated 09 August 2023) from the Ministry of Home Affairs —
this is a primary parliamentary document, not a secondary source. It lists district,
block, and village name for all 46 Sikkim villages. Verified the count by tabulating
district and block totals (East: 4, North: 42), which is internally consistent.
LGD codes, Census figures, and coordinates are not in this source, so those fields
remain blank for Sikkim and will need to be geocoded separately by name and district.

**Uttarakhand — mostly resolved (51/51 names, block assignment partial).**
The Uttarakhand Rural Development Department's VVP page gave the official
block-wise and district-wise village counts (Pithoragarh 27 — split Munsyari 8,
Dharchula 17, Kanalichhina 2; Chamoli 14, all under Joshimath block; Uttarkashi 10,
all under Bhatwari block) but did not publish the actual village names. The names
themselves came from a secondary tourism/information source (euttaranchal.com),
which listed exactly 51 villages split 14/27/10 across the three districts — an
exact numeric match to the official government counts, which gives real confidence
in the list despite it not being a primary government citation itself.
Cross-checked the block assignment against known regional geography: Chamoli's 14
and Uttarkashi's 10 map cleanly onto Joshimath and Bhatwari respectively since the
block total equals the full district total. For Pithoragarh, identified 8 of the
27 villages (Bilju, Burphu, Martoli, Milam, Pachhu Gunth, Panchhu, Rilkot, Tola) as
the Munsyari block set, since these are the well-documented Johar Valley
settlements. The remaining 19 Pithoragarh villages could not be confidently split
between Dharchula (17) and Kanalichhina (2) from any source found — no document
pairs individual village name to block for this subset, so those rows are marked
"unresolved" rather than guessed. This does not block the satellite analysis itself
(which only needs village name + district to geocode), only the administrative
block label for those 19 rows.

**Himachal Pradesh — genuine, documented gap (7 of 51 inhabited villages named).**
This state does not have a public village-wise annexure. What I was able to confirm:
Himachal identified 703 total border villages, of which 75 were selected as VVP-I
priority villages, and of those 75 only 51 are actually inhabited (32 in Kinnaur, 19
in Lahaul-Spiti) — the other 24 have no population. An Action Plan for these 51
villages, worth ₹658.31 crore, was submitted to the Ministry of Home Affairs on 11
September 2023. Checked Rajya Sabha Question No. 401 (2025) and Lok Sabha Question
No. 2104 (2023) — both confirm the count of 75 but neither includes an annexure of
names. News coverage across several Tribune articles named individual villages in
passing while covering unrelated project launches — Chhitkul, Pooh, Nako, Leo, and
Chango in Kinnaur, and Gue and Lalung in Spiti — which is how 7 of the 51 names got
confirmed. Beyond that, the actual Action Plan submitted to MHA (which almost
certainly contains the full village list) was never publicly indexed anywhere I
could find it.

**Ladakh — genuine, documented gap (0 of 35 named).**
Confirmed 35 revenue villages are split across Durbuk and Nyoma sub-divisions from
a DC Leh review-meeting notice and matching PIB releases, but no source gives the
actual names. Lok Sabha Question No. 4360 (2025) specifically asked for the list of
selected villages; the publicly available reply text does not include the
annexure. Checked whether a village-tourism directory (rural.tourism.gov.in) or a
general village database (viewvillage.in, which lists 6 total revenue villages in
Durbuk block: Chushul, Durbok, Kargyam, Man Pangong, Shachokol, Tagste) could
substitute — neither confirms which villages are actually VVP-I selected versus
just administratively present in the block, so neither was usable as a substitute
for an actual scheme-eligibility list.

**Decision on how to close this gap.**
Considered filing RTI applications with the DC Kinnaur/ADC Spiti office (Himachal)
and DC Leh office (Ladakh), since both cases involve a specific, named, dated
government Action Plan document that demonstrably exists but was never published
online. Decided against filing for now — the 30-day RTI turnaround isn't worth
holding up the rest of the project, and this isn't information being deliberately
withheld from the public record so much as never digitized/indexed.

**Final scope decision for the analysis.**
Rather than let this incomplete state block the project, decided to explicitly
scope the village-level satellite analysis (built-up area change, VIIRS night-light
trend, border-proximity pattern) to the three states/UTs with complete official
village identification: Arunachal Pradesh, Sikkim, and Uttarakhand — 552 villages,
a full statistical sample. Himachal Pradesh's 7 confirmed villages will be carried
as a small, clearly-labeled illustrative case study, not part of the core
statistical sample. Ladakh will be excluded from village-level analysis entirely
and discussed only at the state aggregate level. The budget-versus-development
correlation question (RQ2) still runs across all five states/UTs, since sanctioned
budget and project counts are known at the state level for all five regardless of
village-name completeness.

This scope restriction — and the reasoning behind it — will be stated explicitly
in the Data and Methodology section of the Research Paper, not left implicit, so
the coverage gap is transparent to any reader rather than something they'd have to
infer from missing figures later on.

## Entry 3

With 552 villages confirmed by name across Arunachal Pradesh, Sikkim, and
Uttarakhand (plus 7 named Himachal Pradesh villages carried as an illustrative
case study), the next task was converting each into a precise coordinate that
satellite imagery pipelines could actually query against.

**First pass — OpenStreetMap (Nominatim).** Built a script that queries each
village by name, block, district, and state, falling back to a simplified
query (dropping the block name) when the full query returned nothing.
Iterated through several bugs before this was reliable: an initial version
using the `geopy` library kept failing with connection timeouts that
persisted even after increasing the configured timeout value — an internal
quirk in how geopy resolves its timeout parameter rather than a genuine
network problem. Rewrote the geocoding calls to hit Nominatim's HTTP API
directly via `requests`, with an explicit per-call timeout, retry-with-backoff
logic, and incremental checkpoint saving every 10 rows so an interrupted run
never loses more than a few rows of progress. Also excluded "Forest Block"
entries from geocoding attempts entirely — these are forest survey
compartments included in the Sikkim VVP list under village jurisdiction, not
actual inhabited settlements.

**Second pass — Bhuvan (ISRO) Village Geocoding API.** Registered for API
access and used Bhuvan's Census-linked village geocoding endpoint as a
fallback for everything Nominatim missed. This API returns richer data than
OSM (village code, household count, population alongside coordinates), but
testing revealed it does not filter by state or district — a common village
name can silently return a same-named village in a completely different
state. A direct test confirmed this: querying "Kharman" (an Anjaw district,
Arunachal Pradesh village) returned a same-named village in Jhajjar district,
Haryana, instead. Added a validation step that only accepts a Bhuvan result
if its returned district name matches the village's expected district — any
mismatch is discarded as a name collision rather than treated as a genuine
match. A second, separate bug surfaced during this phase: a pandas column
that starts out entirely empty gets inferred as a float64 column, which then
rejects the (string-typed) village codes Bhuvan returns — fixed by explicitly
casting those columns to object dtype before writing to them. Also had to fix
a resume-logic bug where re-running the Nominatim script after the Bhuvan
pass briefly overwrote already-Bhuvan-matched rows, since the Nominatim
script's "already done" check didn't recognize Bhuvan's status labels —
temporarily dropped Sikkim and Uttarakhand's matched counts before being
caught and restored.

**Results: 258 of 559 attempted villages geocoded** — Arunachal Pradesh
186/455, Sikkim 31/46, Uttarakhand 34/51, Himachal Pradesh 7/7. Sikkim and
Uttarakhand improved meaningfully from the Bhuvan fallback (Sikkim 14→31,
Uttarakhand 26→34); Arunachal Pradesh did not gain a single additional match
from Bhuvan.

**A substantive finding, not just a data gap.** Looking at what the
unmatched Arunachal entries actually are is informative in its own right.
Many are not civilian revenue villages at all — they are Border Roads Task
Force camps, army staging huts, labour camps, and administrative headquarters
designations ("Walong BRTF Camp," "Misai Labour Camp," "Staging Hut Krosam,"
"Chaglagam H.Q."). These appear in the official VVP "priority village" list
because the programme targets any inhabited point along the border, however
small or transient, but they have no footprint in any civilian geospatial
database — not OpenStreetMap, not the Census-linked Bhuvan directory —
because they were never classified as villages in the first place. This is
worth carrying into the Discussion section as a real observation about what
"village-level development" along a securitized frontier actually consists
of on the ground, rather than treating it only as a limitation to apologize
for.

**Scope decision.** The core satellite analysis (built-up area change,
VIIRS night-light trend, border-proximity pattern) will run on the 251
villages with confirmed coordinates across Arunachal Pradesh, Sikkim, and
Uttarakhand, preserving the three-state comparative structure. Himachal
Pradesh's 7 confirmed villages are carried as a small, separately-labeled
illustrative case study. The remaining villages stay in the administrative
dataset for context but are excluded from point-based satellite sampling,
with the reason — genuine absence from every available public geolocation
source — stated explicitly.

## Entry 4

With 258 villages geocoded (251 in the core three-state sample, 7 in the Himachal
Pradesh illustrative case study), the next task was pulling actual satellite
evidence for each point — the whole reason the geocoding phase existed in the
first place.

**Merging into a single master table.** Wrote a script to combine the four
per-state geocoded CSVs into one table, keeping only villages with a confirmed
match (discarding the "NO MATCH" and "EXCLUDED — forest block" rows), and adding
an `is_core_sample` flag so Himachal Pradesh could be carried separately from the
three-state statistical sample without needing a different pipeline. This produced
`border_optics_master_villages.csv` — 258 rows, ready for upload.

**Uploading to Earth Engine.** Uploaded the master CSV as a Table asset through the
Code Editor's Assets panel, same workflow used for Stolen Strata. The asset ID
that Earth Engine assigns on ingest is not the same as the internal task ID shown
mid-upload — pasted the wrong one into the script the first time (the ingest task's
short internal hash instead of the full `projects/earthengine-legacy/assets/...`
path), which produced a "Collection asset not found" error until corrected by
copying the ID directly from the Assets panel rather than from the task log.

**Building the extraction script.** Wrote a script to, for each village point:
buffer it by 500m (small enough to stay village-specific, large enough to average
out single-pixel noise), pull a cloud-masked Sentinel-2 composite for a "before"
and an "after" window, compute NDBI (Normalized Difference Built-up Index, using
the SWIR1 and NIR bands) as the built-up proxy, and pull a VIIRS night-lights mean
for the same two windows as an independent proxy. Hit one structural bug getting
this to run: passing a buffered Feature directly into `reduceRegion`'s `geometry`
argument fails, because Earth Engine's buffer operation on a Feature returns
another Feature, not a Geometry, and `reduceRegion` requires a Geometry
specifically — fixed by explicitly calling `.geometry()` on the buffered feature
before passing it through.

**First result set — full calendar year (2021 vs 2025).** With the pipeline
working, ran it using full-year composites (Jan-Dec) for the "before" (2021, pre
VVP-I sanction) and "after" (2025, most recent complete year) windows. Result:
no evidence of a significant increase in built-up area (Wilcoxon signed-rank test
on paired NDBI values, p = 1.000 for the alternative that "after" exceeds
"before") — if anything, the mean NDBI change across the 251-village core sample
was slightly negative. VIIRS night-lights showed a borderline result (p = 0.050).

Before treating this as a finding, one thing needed checking first: a full
calendar-year composite in high-altitude Himalayan terrain will include months
of snow cover, and if the ratio of snow-covered to snow-free images differs
between the 2021 and 2025 composites — which is plausible, since it depends on
which specific days happened to be cloud-free in each year — that alone could
shift the NDBI value regardless of any real change on the ground. Stolen Strata's
own methodology used season-matched (Jun-Sep) composites for exactly this reason,
so the same discipline needed to apply here before this result could be trusted.

## Entry 5

**Switching to season-matched composites.** Changed both windows to June-September
only (summer, largely snow-free across the sample's elevation range) to remove the
snow-cover confound identified in Entry 4. This immediately broke the script in a
new way: several villages had zero cloud-free Sentinel-2 images available in that
narrower four-month window, producing an empty composite image with no bands, which
crashed the NDBI computation (`normalizedDifference` on an image with no bands).
Fixed by checking each village's image count for both windows before compositing,
and writing a null value (rather than crashing) for any village with zero usable
images in a given window — also kept the image counts themselves as output columns,
since they're a direct signal of how trustworthy each village's composite actually
is.

**Sikkim's data disappeared entirely.** Once the summer-only version ran clean,
it became clear why the full-year version had looked usable in the first place:
in the June-September window specifically, all 31 of Sikkim's geocoded villages
returned zero cloud-free images for at least one of the two periods, wiping out
Sikkim's NDBI data completely. This makes physical sense — June-September is
peak monsoon in the Eastern Himalaya, so Sikkim in particular gets almost no clear
satellite days in exactly the window chosen to avoid snow. The full-year composite
had been masking this by allowing the algorithm to reach for whatever clear days
existed at any point across twelve months; narrowing to summer-only fixed the snow
problem but broke Sikkim on cloud cover instead. This is a real, geography-driven
trade-off between the two seasonal choices, not a bug to code around.

**The result flipped.** With the summer-only composite (now n=154/251 villages
with valid data after the Sikkim dropout and a smaller number of Arunachal/
Uttarakhand gaps), the same Wilcoxon test on NDBI now showed a highly significant
increase (p < 0.000001) — the opposite conclusion from the full-year version. VIIRS
night-lights, tested the same way on the same summer window, showed the opposite
pattern again: p = 0.9999, essentially zero evidence of a positive change, actually
trending slightly negative at the median.

**What this means.** Two composite choices, both individually defensible, produced
opposite conclusions from the same NDBI-based approach — which means the underlying
signal is not robust to a methodological choice that should, in principle, be a
minor detail. VIIRS night-lights, the more temporally stable of the two proxies
because it isn't affected by vegetation/snow phenology the way a spectral index is,
gave a consistent answer across both windows: no significant evidence of increased
night-time activity following VVP-I sanction, in either version of the test. Taken
together, the more trustworthy signal is the one that didn't change when the
methodology changed — and that signal shows no confirmed increase. Rather than
picking whichever NDBI result is more convenient, the plan is to report both
composite results side by side in the Research Paper as an explicit robustness
check, with the instability itself treated as a finding: a single-date spectral
index comparison is not sufficient to make a confident claim about built-up change
in this terrain, and the more stable proxy available (night-lights) does not
support a measurable development signal either way. This lines up directly with
the project's founding premise — the parliamentary record stating no independent
impact assessment has ever been carried out for VVP.

**A second, independent observation from RQ2.** Restricting to villages with valid
summer-window NDBI data left only two states with enough coverage to compare:
Arunachal Pradesh (120 villages, mean NDBI change +0.0284) and Uttarakhand (34
villages, mean NDBI change +0.0293) — Sikkim dropped out entirely. These two
states' sanctioned VVP-I budgets differ by roughly a factor of ten (₹2,749.74
crore and 2,082 projects for Arunachal Pradesh, versus ₹270.58 crore and 200
projects for Uttarakhand), yet their average measured built-up change is nearly
identical. Two data points cannot support a statistical claim, but descriptively
this is consistent with H2 — budget scale is not translating proportionally into
a correspondingly larger physical development signal.

**Next step.** With both the full-year and summer-matched results now on hand,
the remaining satellite work is: deciding on the final reporting format for this
robustness check in the Research Paper's Results section, and picking up RQ4
(border-proximity pattern), which still needs a Line of Actual Control / border
geometry layer that hasn't been sourced yet.

## Entry 6

With the built-up and night-light change values in hand for both composite
windows, the last untested hypothesis was H3 — that villages nearer the
international border/LAC would show disproportionately more change than
villages further back within the same state, consistent with securitization
theory's prediction that border proximity, not developmental need, drives
where VVP resources actually land.

**Sourcing a border line.** Used Natural Earth's Admin 0 Boundary Lines
dataset (land boundaries, 1:10m scale) as the border geometry — a standard,
citable, publicly available cartographic source. This needs an explicit
caveat for the Research Paper: India's international boundary with China,
commonly referred to in this context as the LAC, is disputed and has no
single internationally agreed alignment. Natural Earth's rendering is a
cartographic simplification, not a legal or official claim, and any
distance-to-border figure computed from it should be read as approximate
and relative (useful for comparing villages against each other) rather than
as an authoritative statement of where the boundary actually sits on the
ground. The download link on the Natural Earth site had changed since it
was last referenced — the boundary-lines-only URL 404s now; the current
page is `10m-admin-0-boundary-lines` (previously indexed with a
"-land" suffix that no longer resolves).

**Computing distance per village.** Loaded the 258 geocoded village points
and the boundary shapefile into GeoPandas, filtered the boundary file down
to the 27 segments involving India (matched on the `ADM0_LEFT`/`ADM0_RIGHT`
attribute fields, since Natural Earth's boundary-line schema identifies
each segment by the two countries it separates rather than by a single
country code), reprojected both layers to a metric CRS appropriate for the
Himalayan region (UTM 44N), and computed the straight-line distance from
each village to the nearest point on the combined India border geometry.
Distances ranged from 0.1 km to 69.4 km, with a mean of 27.3 km — a
plausible spread for a sample explicitly selected as "priority" border
villages.

**Testing H3 against both composite windows.** Ran a Spearman correlation
between distance-to-border and each village's NDBI change and night-light
change, separately for the full-year and summer-matched datasets, following
the same robustness-check logic established in Entry 5 rather than trusting
a single result.

Results:
- NDBI change vs. distance: not significant in either window (full-year
  rho = 0.043, p = 0.497; summer-matched rho = 0.037, p = 0.650). This is a
  stable non-finding — both composite choices agree that built-up change,
  as measured here, shows no relationship with border proximity.
- Night-light change vs. distance: significant in the full-year composite
  (rho = -0.259, p < 0.0001 — negative rho meaning villages closer to the
  border show more light increase, consistent with H3), but not significant
  in the summer-matched composite (rho = -0.076, p = 0.233).

**Interpretation.** The NDBI result is consistent and trustworthy precisely
because it doesn't change with the compositing choice — there is no
confirmed relationship between border proximity and built-up area change in
this dataset. The night-light result is more complicated: it shows a
strong, clean signal in one version of the analysis and no signal at all in
the other, which is the same instability pattern already documented for
RQ1 in Entry 5. Given that pattern, this result cannot be reported as
"H3 confirmed" — the honest characterization is that there is a suggestive,
non-robust signal in one methodological version, not a finding that
survives the same robustness check the rest of the project's satellite
results are being held to. This reinforces rather than contradicts Entry
5's broader conclusion: single-date/single-window spectral and radiance
comparisons in this terrain are not stable enough, on their own, to support
confident directional claims, and every result in this project needs to be
reported with that caveat attached rather than cherry-picking whichever
version looks cleanest.

**Status after this entry.** All four research questions have now been run
against the satellite pipeline at least once, with RQ1 and H3 both showing
the same non-robust, composite-window-sensitive pattern, and RQ2's
budget-independence observation (Entry 5) still standing as the most
consistent descriptive finding so far. What remains before the Research
Paper stage is: deciding on final reporting language for this
robustness-check framing, and building the plots/maps that will actually
visualize all of this once the analysis phase is fully closed out.

## Entry 9

**Status.** A check of the repository before first submission found that two parts of the analysis pipeline had never been added to it.

**Missing satellite-extraction script.** The single script that actually
pulls Sentinel-2 NDBI and VIIRS night-lights values from Google Earth
Engine — described in detail in Entry 4 (buffer-then-`.geometry()` fix,
QA60 cloud masking, per-village null-safe extraction) — was never checked
into `src/acquisition/`, even though every downstream script depends on its
output. Reconstructed it as `extract_satellite_data.py`, matching the
documented logic exactly, runnable against either compositing window via a
`--window` flag, so the pipeline is reproducible from source rather than
only from its cached CSV outputs.

**Missing full-year counterpart to the core analysis script.**
`analyze_results.py` only ever covered the summer-matched window; the
full-year analyzed output (`border_optics_village_results_analyzed.csv`,
used throughout the Research Paper and dashboard) had no corresponding
script in the repository that could regenerate it. Added
`analyze_results_fullyear.py`, mirroring the same logic against the
full-year extraction output.

## Entry 10

**Status.** An outside review of the finished first version led to the following changes to the research itself.

**An uncited pivotal claim, now cited precisely.** Every parliamentary
fact in the paper carried an exact Question number and date except the
single most load-bearing one — "no impact assessment has ever been carried
out for VVP" — which had been stated generically without a citation.
Searched specifically for the source and found it: Lok Sabha Unstarred
Question No. 508 (3 February 2026), asked by Shri Baijayant Panda and
answered by Shri Nityanand Rai (Minister of State, Home Affairs), whose
reply states verbatim: "No impact assessment has been carried out."
Replaced the generic phrasing with this exact citation throughout
Research_Paper.md, README.md, and Project_Report.md, and added the
corresponding References entry.

**Multiple-testing check.** This project runs four distinct statistical
tests under two compositing windows each (eight tests total) without a
multiple-comparisons correction, since each test answers a different
research question rather than the same hypothesis tested repeatedly. As a
conservative sanity check anyway, applied a Holm-Bonferroni correction
across all eight simultaneously — both results already reported as
significant survive even the strictest step of the correction, and nothing
already reported as non-significant becomes significant. Documented this
directly in Research_Paper.md's robustness section rather than leaving it
as an unaddressed question a reviewer would have to raise themselves.

**Selection-bias check, tested rather than asserted.** Geocoding coverage
is uneven (258/559 attempted villages, 46%), which raises an obvious
question: are villages that fail to geocode systematically different from
ones that succeed? Arunachal Pradesh's raw village list carries Census 2011
population and household counts for every village regardless of geocoding
outcome, so this was testable directly rather than left as a caveat. A
Mann-Whitney U test found no significant population or household
difference between geocoded and non-geocoded Arunachal Pradesh villages
(p = 0.310 and p = 0.540) — evidence against a size-driven selection bias
in the analyzed sample, for the one state where it could actually be
checked. Sikkim and Uttarakhand's raw lists don't carry these fields, so
the check is explicitly scoped to Arunachal Pradesh rather than implied to
cover the whole sample.

**Ground-truth positive control — attempted, not found, documented
honestly.** Reviewers asked whether NDBI/VIIRS are even sensitive enough
at 500m to detect the scale of development VVP-I typically funds. The
direct way to answer that is a positive control: a specific, dated,
independently-confirmed completed VVP-I project that also happens to fall
within the 258-village geocoded sample. Searched for one rather than
assuming it didn't exist — found VVP's original 2023 launch village
(Kibithoo, Arunachal Pradesh) referenced in a Ministry press release, but
it is not itself among the 258 geocoded villages, so it could not serve as
a real positive control without fabricating a match. Recorded as an
explicit open item in the new Future Work section rather than forcing a
weak match or quietly dropping the question.

**New Future Work section added to Research_Paper.md** (Section 7,
Conclusion renumbered to Section 8), consolidating every extension
identified during this review that requires new data acquisition rather
than a documentation fix: SAR-based change detection (Sentinel-1, immune
to the cloud/snow confounds this study already documents), building-
footprint or sub-500m structural analysis, a genuine Difference-in-
Differences design against non-VVP control villages, a multi-year
phenology-normalized trend instead of two single-year composites, buffer-
size sensitivity testing (250m/500m/1km, following the same robustness
discipline already applied to the compositing window), the ground-truth
positive-control check described above, and RTI follow-through for
Himachal Pradesh and Ladakh's still-missing village annexures.

## Entry 12

**Status.** In progress — scripts written and ready to run, satellite extraction not yet executed.

**Why now.** Section 7 of the research paper names seven concrete extensions, none yet implemented. I picked three to move on together this round, rather than one at a time, since they share the same acquisition machinery: a genuine non-VVP control group (§7.3), a third time point for a real trend line instead of a two-point difference (§7.4), and a buffer-radius sensitivity check (§7.5). I also went back and re-checked whether the two coverage gaps (§6.1, §7.7 — Ladakh fully excluded, Himachal Pradesh at 7 of 51 villages) could move without filing an RTI. They can't: I found one government source (an All India Radio piece) confirming Ladakh's 35 identified villages by count but not by name, and the current Lok Sabha Q&A record (Question 508, February 2026) still reports only state-level aggregates for both regions — no village-wise breakdown. A couple of Himachal news pieces name individual VVP villages in Lahaul-Spiti (Gue, Lalung), but both were already in the dataset from the original acquisition pass. Nothing new to add this round; RTI remains the only path to close these two gaps, and it stays on the open list rather than getting a partial, lower-confidence workaround in its place.

**Control-group design.** The single biggest thing missing from this study, by its own account, is a control group — every result so far is each village's own before/after, with nothing to say whether a matched non-VVP village saw the same regional change over the same period. `select_control_villages.py` builds one: for each district already in the core sample (Arunachal Pradesh, Sikkim, Uttarakhand), it queries OpenStreetMap's Overpass API for named villages/hamlets in that district, drops anything matching a treated village's name, and keeps candidates within 1.5x the treated sample's own maximum border-distance for that district — border-region villages of a comparable character, not distant lowland towns pulled in just to pad the count. I matched on district rather than a tight distance band on purpose: pinning control villages to the exact same distance-to-border range as the treated sample would shrink the candidate pool down to almost nothing, and the villages that *did* survive that filter would mostly be the ones sitting right next to a treated village — which are the most likely to have been left out of VVP-I for a specific reason, not by chance. District-level matching keeps "same regional trend" defensible while giving the DiD design a real sample to work with.

**Multi-year extraction.** `extract_multiyear_satellite_data.py` adds 2023 as a third snapshot for the existing treated villages, run under both compositing windows for consistency with the rest of this study's own robustness discipline. This isn't another before/after pair — it pulls a single NDBI/lights value per village per year, so three points can support an actual trend line instead of one two-point difference that a single anomalous year at either end could be driving on its own.

**Buffer-sensitivity extraction.** `extract_buffer_sensitivity_data.py` re-runs the same before/after extraction at 250m and 1km, scoped to the summer window only — the window carrying the significant NDBI result, and so the one actually worth stress-testing here. Re-running the full-year window's null result at two more buffer sizes wouldn't add much; the summer result is the one a buffer-choice critique would target.

**What's ready to run.** All four scripts are written, checked into `src/acquisition/`, and pass a syntax check, but none have been executed — `select_control_villages.py` needs network access to the public Overpass API (my analysis environment can't reach it directly, the same constraint that always applied to Nominatim), and the three extraction scripts need a live Google Earth Engine session, same as the original `extract_satellite_data.py`. I don't touch API credentials myself; these get run locally, the same way the original acquisition pipeline was.

**What's still open.** Everything in this entry is preparation, not results — the actual control-group DiD estimate, the multi-year trend, and the buffer-sensitivity comparison all depend on data that doesn't exist yet. Himachal Pradesh and Ladakh's coverage gaps remain genuinely blocked on an RTI that hasn't been filed. SAR-based change detection (§7.1), building-footprint analysis (§7.2), and ground-truth positive-control validation (§7.6) remain untouched this round — bigger, separate undertakings each.

## Entry 13

**Status.** Complete. All three extractions described in Entry 12 finished, all three analyses written and run, the research paper and every other document rewritten to fold the results in as part of the study's design rather than reported as a bolt-on addition.

**Acquisition, finally run.** `select_control_villages.py`'s Overpass calls hit the shared public instance's rate limiting hard on the first attempt (429s and 504s under load, worse on the larger district bounding-box queries) — added retry/backoff (5 attempts, 20/40/80/160s escalating waits, honoring `Retry-After` on 429s) and per-district checkpointing so a stuck district doesn't cost the whole run. Reran end to end: 753 control villages across all 14 districts. Separately, `earthengine-api` has moved to requiring an explicit Cloud project on `Initialize()` since I last touched this pipeline — a bare browser re-auth no longer implies one, so all four `extract_*.py` scripts needed an `EE_PROJECT` environment variable wired through `python-dotenv`, matching the existing `BHUVAN_TOKEN` convention. Documented in `.env.example`. With that fixed, ran all four extraction passes: control-group full-year and summer (753/753 valid each), multi-year full-year and summer (258/258 valid at all three years), and buffer-sensitivity at 250m and 1km (258/258 valid each, summer window).

**Control-group DiD (§7.3 → now §3.7/4.6 of the research paper).** Reshaped treated (251-village core sample) and control (753 villages, same 14 districts) into a before/after panel and ran a district-fixed-effects DiD with SEs clustered by district. Summer-matched: did coefficient +0.0377, cluster-robust p = 0.0021 (HC3 no-FE comparison spec: +0.0287, p = 0.0116). Full-year: +0.0082, p = 0.215 — not significant. This is the same window-sensitivity split the core H1 test already shows, now confirmed after controlling for whatever regional trend the surrounding non-VVP villages experienced on their own. Ran a baseline-balance check in place of a true pre-trends placebo test, since the control group only has the same single before/after pair as the treated sample, not a multi-year pre-period: treated villages start from a significantly lower mean 2021 NDBI than control villages in both windows (p < 0.00001 summer) — expected, since VVP-I priority villages were themselves selected partly for remoteness, but worth being upfront that this is a level-balance check, not a confirmed shared pre-trend.

**Multi-year trend (§7.4 → now §3.8/4.7).** Fit a per-village linear slope across 2021/2023/2025 for the core sample, tested against zero with a one-sided Wilcoxon on the slopes, and cross-checked with a village-fixed-effects panel regression. Neither shows a significant overall trend in either window (summer Wilcoxon p = 0.442). Splitting into the two sub-periods explains why: a 2021→2023 decline (summer mean change -0.023, clearly not a significant increase) followed by a 2023→2025 increase that is itself highly significant (p < 0.000001). So the headline 2021-vs-2025 result this study has reported all along is real but concentrated in the second half of the window, not a steady trend since sanction — a genuinely useful thing to know and not something the two-point comparison alone could have shown.

**Buffer sensitivity (§7.5 → now §3.9/4.8) — caught a real confound before reporting it as a finding.** First pass looked bad: comparing NDBI significance "as extracted" at each radius, 500m was significant (n=154, p < 0.000001) but 250m and 1km were not (n=251 each, p = 0.126 and p = 0.899). Before writing that up as "the result doesn't survive a buffer-radius check," checked *why* the valid-village counts differed so much between radii — 500m has 97 nulls (66 Arunachal Pradesh, 31 Sikkim) that 250m and 1km don't have at all. That's not something a buffer-radius change should do on its own: Sentinel-2 tile footprints are tens of kilometres across, so whether a scene intersects a village's buffer shouldn't flip between 250m and 1km around the same point. The real explanation is more mundane — the 250m/1km extractions ran today, weeks after the original 500m extraction, against the identical fixed 2021/2025 date ranges but a Sentinel-2 archive that's kept backfilling scenes for a period this close to the present. Restricted all three buffers to the 154 villages valid at every radius, which holds sample composition fixed: on that matched subsample, NDBI is significant at all three radii (250m p = 0.000009, 500m p < 0.000001, 1km p = 0.001471). Documented the archive-timing issue directly in the script and in the paper's limitations (§6.9) rather than either hiding it or letting the raw "doesn't replicate" numbers stand uncorrected — the matched-subsample check is the actual answer to the question this test was asking.

**What's still open.** A true parallel-pre-trends placebo test for the control group (needs pre-2021 extraction for both groups — new Future Work item 7.5). SAR-based change detection, building-footprint analysis, and ground-truth positive-control validation remain untouched. Himachal Pradesh and Ladakh's coverage gaps are still blocked on an RTI that hasn't been filed.

## Entry 14

**Status.** Complete — a second acquisition-code review pass, this time specifically on the three scripts added in Entry 12/13 (`select_control_villages.py`, `extract_satellite_data.py`, `extract_buffer_sensitivity_data.py`) plus the Entry 13 figures. Entry 11's Deep Verify covered the original statistical pipeline; this pass covers the newer acquisition code that Deep Verify predates.

**Control-village resume logic was silently inert.** `select_control_villages.py`'s resume support skipped any (state, district) pair already present in the output file, full stop — it never actually checked whether that district's rows had been through a real boundary check or not. Practically, that meant a partial or interrupted run's bbox-only rows would get treated as "done" forever, since the district's name was already in the file. Fixed the resume condition to only skip a district once every one of its saved rows is confirmed polygon-verified; anything else gets its old rows dropped and rebuilt from scratch on the next run.

**Bbox overlap can double-count a village across districts — added dedup, then found a bug in the dedup itself.** Because each district's Overpass search box has a generous margin (0.6° so as not to miss legitimate border-area candidates), two adjacent districts' boxes overlap, and the same physical OSM point can turn up as a candidate for both. Added a cross-run coordinate set so a point claimed by one district can't be pulled in again under a different district's label. First version of this had an ordering bug, though: it marked a coordinate as claimed as soon as it passed the distance/polygon checks, before the per-district cap (3x the treated count) had a chance to cut it — so a candidate that lost out on the cap in District A's larger candidate pool could still permanently block a legitimate match in District B, even though it was never actually saved anywhere. Moved the claim to after the cap is applied, so only coordinates that actually make it into the saved file get reserved.

**Extraction resume logic was checking the wrong columns, twice over.** Both `extract_satellite_data.py` and `extract_buffer_sensitivity_data.py` treated a row as "already extracted" once its four value columns (`ndbi_before`/`ndbi_after`/`lights_before`/`lights_after`) were filled, without checking the four image-count columns alongside them. A row checkpointed mid-write with valid values but a still-null image count would never get revisited on a later run. Extended the completeness check to all eight outcome columns in both scripts.

**What this doesn't fix.** None of the above regenerates `border_optics_control_villages.csv` itself — the 753-row file already committed predates every fix in this entry, including the polygon-membership check and the coordinate dedup, and (checked directly) does contain the kind of same-village-different-district duplicate the old bbox-only matching could produce. Regenerating it needs the resume file deleted and the script rerun with live Overpass/Nominatim access, followed by re-running the control-village satellite extraction and `did_model.py` so the reported DiD numbers are computed from the corrected control set rather than the old one. That's acquisition + a live GEE session, same as always — flagged here rather than done silently, and not yet actioned.

## Entry 15

**Status.** Complete. The regeneration Entry 14 flagged as "not yet actioned" was attempted, failed silently on the first attempt for a reason worth documenting in full, was fixed, and the corrected rerun's numbers are now independently verified and folded into every document.

**The regeneration's first attempt did nothing, and the DiD script couldn't tell.** `select_control_villages.py` was rerun with the Entry 14 dedup fix and correctly produced a new 735-village list (753 minus 18 cross-district duplicates). `extract_control_satellite_data.py` was then rerun against it — but its resume logic checked whether a row for a given `village_id` already had filled-in NDBI/lights values, and `village_id` is nothing more than a sequential 1..N index reassigned fresh on every regeneration of the village list. The old 753-row checkpoint file still had values for `village_id` 1 through 753 sitting on disk, so every one of the new list's 735 rows found a "complete" match at the same index and the script skipped straight to done without a single new Earth Engine call. The resulting `did_model.py` numbers were, byte-for-byte, the old bugged numbers — which is exactly how this got caught: they were independently reproducible from the old, still-committed 753-row control-results file, run locally against that stale data, before trusting anything pasted from a terminal.

**Fix.** Rewrote the resume check to match on coordinate (rounded lat/lon) instead of `village_id`: it now compares the current village list's coordinate set against the checkpoint file's coordinate set, and only resumes if they match. A 735-village list against a 753-row checkpoint doesn't match, so the corrected script correctly detects this and starts fresh. Verified locally against both the same-list-reordered case (should resume) and the regenerated-list case (should restart) before pushing — the same class of "test it before believing it fixed anything" discipline this project's development log has tried to hold itself to throughout, applied here specifically because the first version of this exact fix had already been trusted once without that check.

**Independent verification of the actual rerun, not just the pasted terminal output.** After the corrected extraction was rerun and pushed, pulled the result and checked it directly rather than taking the pasted DiD numbers on faith: `border_optics_control_villages.csv` is 735 rows with zero duplicate coordinates (confirmed programmatically); `border_optics_control_results.csv` and `border_optics_control_results_summer.csv` are both 735 rows with image-count columns that vary row to row (73/86/12/12, 146/170/12/12, and so on) rather than sitting at a suspicious constant, which is what a genuine set of fresh Earth Engine calls looks like and what a silently-skipped extraction would not produce. Reran `did_model.py` locally against this pulled data myself for both windows and it reproduced the pasted numbers exactly, to the fifth decimal place, for every coefficient, SE, CI, and p-value in both outcomes and both windows — this is what "verified" means here, not "the numbers looked plausible."

**Two real results changed, not just their precision.** The summer-window NDBI gap against the control group holds, and holds slightly more tightly: did coefficient +0.0322 (was +0.0377), cluster-robust p = 0.00033 (was p = 0.0021). The full-year NDBI gap remains non-significant: +0.0088, p = 0.275 (was +0.0082, p = 0.215) — same conclusion, a little noisier now that the control group's valid full-year sample is 190 villages rather than 753. Night-lights is the one that actually changes conclusion: under the old, bugged control list, no DiD effect was reported in either window. Under the corrected list, a significant positive gap now shows up in both — summer +0.1413, p = 0.0044, agreeing under both the fixed-effects and no-fixed-effects specifications; full-year +0.1653, p = 0.0364 under fixed effects but p = 0.1033 without them, a specification disagreement rather than a clean result. Checked why before writing it up as "night-lights now shows an effect": Section 4.3's treated-only Wilcoxon test on the same summer window is still a clean null (p = 0.9999) — treated villages' own night-lights didn't rise. What happened is that the *control* villages' night-lights fell over the same period in most districts while treated villages held roughly flat, so the treated-minus-control gap comes out positive without any absolute increase on the treated side. Documented this distinction explicitly everywhere the new lights-DiD number appears, rather than letting a positive coefficient read as "VVP-I villages lit up" when the more accurate description is "VVP-I villages didn't decline the way the surrounding region did."

**Baseline imbalance is worse than previously reported, not better.** The old write-up only checked and disclosed a baseline (2021) imbalance for NDBI. Checking all four outcome/window combinations against the corrected control group: NDBI summer is still imbalanced but the gap between treated and control means shrank considerably (treated −0.2461 vs. control −0.2442, versus the old run's treated −0.246 vs. control −0.185); NDBI full-year is the only one of the four that is not significantly imbalanced (p = 0.125); night-lights summer is mildly imbalanced (p = 0.0165); and night-lights full-year is the most imbalanced of all four (p < 0.00001) — which is also the one combination where the two DiD specifications disagree, a pattern consistent with (though not proof of) that baseline gap being handled differently by each. Added this full four-way breakdown to Section 4.6 and 6.7 of the paper, the README, and the Executive Summary, where previously only the NDBI figure was disclosed.

**What this doesn't change.** The core NDBI headline — that the summer-window built-up-area gap survives a control-group comparison, a buffer-radius sweep, and Holm-Bonferroni correction, while the full-year gap doesn't — is unchanged in direction and, if anything, slightly more precise now. What's genuinely new is the night-lights control-group finding, and it's reported with the same specification and baseline-imbalance caveats applied to every other borderline result in this study, not as a second confirmed headline.

## Entry 18

**Status.** Complete — a third external review round repeated the same by-now-familiar stale claims (753 vs 735, DiD-vs-paper mismatch) verbatim, all still false against `origin/main` as of this entry's starting commit. But it also raised two claims genuinely worth checking on their own merits rather than dismissing alongside the stale ones: (1) `compute_border_distance.py` projects the entire study area — which spans roughly 77°E to 97°E — into a single UTM zone (44N, centered on 81°E), and (2) the "border/LAC distance" variable is computed as distance to the *nearest* India-related Natural Earth boundary segment, which is not necessarily the China segment. Both turned out to be real, and both were checked quantitatively rather than taken on faith, in either direction.

**UTM 44N: real bias, quantified, doesn't change any conclusion.** Wrote a direct comparison — the old single-zone UTM44N planar distance vs. a proper WGS84-ellipsoid geodesic distance — for representative points in Uttarakhand (near the zone's own central meridian), Sikkim (~7.5° east of it), and Arunachal Pradesh (~11-15° east of it). Confirmed the old method systematically *overstated* distance the further east a village sits: negligible in Uttarakhand, but up to ~3% in Arunachal Pradesh's easternmost villages (mean bias -1.5% for the state, worst single village off by just over 2km). Rewrote `compute_border_distance.py` to find the nearest boundary point in unprojected lon/lat space (adequate for identifying *which* point is nearest at these scales) and then compute the actual distance geodesically via `pyproj.Geod` — this has no zone dependency at all, so it is correct everywhere in the study area rather than only near one meridian. Regenerated `border_optics_master_villages_with_distance.csv` and reran every downstream script that reads it: `test_h3_border_proximity.py` (H3's four Spearman tests), `holm_correction.py` (two of its eight tests are H3 border-proximity tests), and the two figures that display H3 numbers as text (`03_h3_border_distance_vs_lights.png`, `07_robustness_summary.png`). Every H3 ρ/p value moved by a small amount (e.g. full-year NDBI-proximity: ρ 0.043→0.049, p 0.497→0.443; full-year lights-proximity Holm-adjusted p: 2.24×10⁻⁴→3.83×10⁻⁴) but **not one test's significant/non-significant status changed** — updated the exact numbers everywhere they're cited (paper §4.5, §4.9, the RQ1 opening paragraph, and the Section 4.9 line-up) and added a note at §4.5 explaining the correction and confirming no conclusion moved.

**Not touched: control-village selection's own copy of this same distance logic.** `select_control_villages.py` independently computes distance-to-border for the same reason (as a soft candidate-selection filter, `METRIC_CRS = "EPSG:32644"` — same UTM44N choice) and reads treated-village distances from the same file this entry regenerated. Making that fully consistent would mean re-running `select_control_villages.py` (needs live Overpass API access) and every downstream control-satellite-extraction and DiD script (needs a live Google Earth Engine session) — neither of which I have access to in this environment. Flagging this rather than leaving it silently inconsistent: the currently-committed 735-village control list and every DiD number derived from it still reflect the old UTM44N-based distance filter. Given the filter is a generous 1.5x-treated-max soft cap and the actual bias is 1-3% at the country's edge, this is very unlikely to have excluded or included villages it shouldn't have, but a fully rigorous fix would need that live rerun, flagged here as the follow-up rather than done silently or claimed as done.

**"Border/LAC distance" is not always distance to the LAC — checked exactly how often, rather than asserting a number.** Computed, per core-sample village, which country's Natural Earth boundary segment is actually nearest: 220 of 251 (88%) are nearest to the China segment, but 19 (Arunachal Pradesh, mostly Tawang and West Kameng) are nearest to Bhutan, 8 (North Sikkim, and Uttarakhand's Pithoragarh) are nearest to Nepal, and 4 (Arunachal's Anjaw) are nearest to Myanmar. The code's own filter (`ADM0_LEFT`/`ADM0_RIGHT` == "India") was always correctly finding the nearest *India* boundary of any kind, not specifically the LAC/China segment — this was working as written, just not disclosed as precisely as it should have been. Added the exact breakdown to the paper's §6.2 and the dashboard's Methodology & Limitations page, framing it honestly: for the 12% of the sample nearest a non-China border, H3 is a reasonable general border-securitization-proximity measure (these are still border villages in the broader sense VVP-I itself uses) but not literally an LAC-proximity test for those specific villages. H3 was already disclosed as exploratory elsewhere (Executive Summary, Methodology page) for other reasons (small sample geometry, no covariate control); this is an additional, more specific reason not to lean on it as a clean confirmatory result. Also corrected `pages/1_Study_Design.py`'s claim that UTM-reprojection was done "for accuracy" — the fixed version now correctly describes the geodesic method and why a single-zone reprojection wasn't accurate for this study's east-west extent.

**What this doesn't change.** No hypothesis flips from significant to non-significant or back. H3 remains what it always was: a mostly-null, exploratory test, now on slightly more accurate (and more honestly described) distances. The two headline conclusions from Entry 15 onward are unaffected.

## Entry 20

**Status.** Complete — this entry does two things: (1) adds four extended robustness checks to the summer-window control-group DiD result (H4), all built from data already extracted, no new GEE/Overpass acquisition; (2) closes out the framing/precision critiques that Entry 19 flagged but deliberately deferred ("matched control group" overstating the design, "three independent stress tests" overstating independence between checks that share the same underlying satellite observations).

**Why now.** Entry 19's own "bottom line" left two categories of open item: things that were genuine precision critiques but not bugs, and the standing fact that the control-group DiD's cluster-robust p-values rest on only 14 district clusters — small enough that the asymptotic theory behind cluster-robust standard errors is itself worth stress-testing, not just assumed. Both are addressed here rather than left for a fifth review round to raise again.

**1. Leave-one-district-out.** The summer-window DiD (both NDBI and night-lights) was rerun 14 times, dropping one of the 14 districts each time. Both outcomes stay significant (p < 0.05) in all 14/14 reruns — NDBI's coefficient ranges from +0.0240 to +0.0359 (against +0.0322 with every district included), night-lights' from +0.1117 to +0.1731 (against +0.1413). No single district is carrying either result.

**2. Randomization inference.** Treatment was reshuffled 2,000 times within each district (preserving each district's actual treated/control counts, seed=42), building a permutation null for the DiD coefficient that doesn't lean on cluster-robust asymptotic theory at all. NDBI's observed +0.0322 sits far outside its null (mean +0.0005, SD 0.0048; p = 0.0005); night-lights' observed +0.1413 likewise (mean +0.0033, SD 0.0323; p = 0.0005). This and the leave-one-out check both test the same thing from different angles — whether the reported cluster-robust p-values can be trusted given only 14 clusters — not the separate, still-open baseline-imbalance question from Entry 15/§6.7.

**3. Log1p-transformed VIIRS.** VIIRS radiance is right-skewed, so the night-lights DiD (and the treated-only Wilcoxon borderline case from §4.3) were re-run on log1p-transformed values, as a check against a handful of high-radiance villages driving the result. Nothing flips: the summer DiD result survives and strengthens on the log scale (raw p = 0.0044 → log1p p = 0.0003), the full-year DiD holds at about the same significance either way (p = 0.0364 vs. p = 0.0374), and the §4.3 full-year treated-only borderline case (p = 0.050) stays non-significant on the log scale too (p = 0.068).

**4. Summer-window missingness, quantified.** The 154 core-sample villages with valid summer-window data are not a random 154 out of 251 — checked this directly rather than leaving it at "monsoon cloud cover thinned the sample." The 154 summer-valid and 97 summer-invalid villages differ significantly in state composition (chi-square = 71.42, p ≈ 3.1×10⁻¹⁶ — mostly mechanical, since Sikkim's entire 31-village contingent drops out on its own) and, separately, in their own 2021 full-year baseline NDBI (Mann-Whitney U, p = 0.00063: summer-valid villages start from a mean of -0.2047, summer-invalid from -0.1527). This doesn't establish which direction, if any, that biases the reported summer-window change, but it upgrades the previous qualitative "cloud cover" framing into a quantified, previously-underspecified selection fact, and it means the summer-window result should be read as describing that specific subsample rather than the full core sample by default.

**What this doesn't change.** No hypothesis flips from significant to non-significant or back, and no headline coefficient changes — every number added this round is a new check *of* an existing result, not a replacement for one. The control-group DiD for H4 is, after this entry, the most heavily stress-tested single result in the study: it holds under the original cluster-robust and HC3 specifications, under leave-one-district-out, under randomization inference, and (for night-lights) under a log-scale transform — while the separate, still-open baseline-imbalance caveat from Entry 15/§6.7 remains exactly that: open, and correctly kept open rather than papered over by these new checks answering a different question.

## Entry 21

**Status.** Open finding, not fixed — a fresh, code-level, data-level check (prompted by an external review that raised the right *kind* of question — whether the 3-point trend and the 2021-vs-2025 headline could really be computed on the same footing — even though its own claims about the paper's current wording turned out to be wrong on inspection) turned up something real and more serious than anything that review actually named: the summer window's "Sikkim has zero valid data" claim, load-bearing across §4.2, §4.6, and the new §6.4 missingness paragraph from Entry 20, looks like it may itself be a stale archive-timing artifact, not a permanent fact about the data.

**What was checked.** `extract_satellite_data.py` (the two-point 2021/2025 extraction, behind the §4.2/§4.6 headline numbers) and `extract_multiyear_satellite_data.py` (the 2021/2023/2025 extraction added for §4.7) run the *identical* query for the summer window at 2021 and 2025: same collection (`COPERNICUS/S2_SR_HARMONIZED`), same QA60 cloud/cirrus mask, same 500m buffer, same June 1 – Oct 1 date range. Compared row-by-row on `village_id`, direct from the committed CSVs:

- `border_optics_village_results_summer_analyzed.csv` (two-point): all 31 Sikkim villages have `before_image_count = 0` and `after_image_count = 0` — zero Sentinel-2 scenes found, NDBI null, which is why Sikkim drops out of the 154-village summer sample.
- `border_optics_multiyear_summer.csv` (three-point, extracted later): the *same* 31 Sikkim villages, for the *same* 2021 and 2025 date ranges, show `ndbi_n_2021 = 24` and `ndbi_n_2025 = 31` — 24 and 31 scenes found, real NDBI values computed, nothing null.

This is the identical mechanism already disclosed in §6.9's buffer-radius work — the Sentinel-2 archive backfilling additional scenes for past dates between two extraction runs — just showing up here between the two-point and three-point summer extractions instead of between buffer radii, and not yet disclosed for this pair. It is not a code bug in either script (the query logic is identical in both); it is a real difference in what Earth Engine's archive returned at two different points in time. Full-year shows no such discrepancy — both extractions agree at 251/251 valid for both windows — so this is specific to the summer window's already-known cloud/monsoon-driven data sparsity, which apparently made the *original* summer extraction's timing sensitive to exactly which scenes had been backfilled into the archive by the day it ran.

**Why this matters more than a wording nitpick.** The 154-village summer sample is not a side detail — it is the basis for the §4.2 headline NDBI result, the §4.6 control-group DiD's summer-window n, the Holm correction's summer NDBI p-value, the buffer-sensitivity matched-subsample (also 154 villages), and Entry 20's own new missingness-mechanism paragraph in §6.4, which quantified a difference between summer-valid and summer-invalid villages that may partly describe a which-day-the-query-ran artifact rather than a stable selection mechanism. None of this is confirmed to be wrong — the 154-village result could very well survive a fresh extraction with Sikkim included, or the archive could have since re-stabilized differently — but it has not been re-verified since this discrepancy was found, and the honest thing is to say that plainly rather than let the "154, Sikkim excluded" framing stand as settled.

**Not fixed in this entry, and deliberately not fixed by editing prose alone.** This needs a live re-run of `extract_satellite_data.py --window summer` against a live Google Earth Engine session — unavailable in my analysis environment (no `ee.Authenticate()` credentials here) — and if that changes Sikkim's summer availability, every summer-window downstream number (§4.2, §4.6, Holm, §4.8's matched subsample, and Entry 20's four new checks, all of which are summer-window results) would need re-running against the new sample, not just re-described. Flagging this exactly the way Entry 18 flagged the unresolved UTM-in-control-selection issue: real, checked, not silently claimed as fixed, and left for a run I can't perform in this environment.

**Recommended next step, not yet taken.** Re-run `python src/acquisition/extract_satellite_data.py --window summer` from a machine with an authenticated Earth Engine session. The script only re-queries rows missing any of its eight outcome/count columns (existing valid rows are left untouched), so this is safe to run and will not silently overwrite anything already valid — it will only fill in currently-null rows, Sikkim's 31 included, with whatever the archive returns today. If Sikkim villages come back with valid summer NDBI/lights, treat the resulting n as the new "as-extracted" summer sample and re-run, in order: `did_model.py --window summer`, `holm_correction.py`, `buffer_sensitivity.py`, and `extended_robustness_checks.py`, then rewrite every summer-window number those touch across the paper, Executive Summary, README, and dashboard rather than patching the current ones in place — and add an Entry 22 documenting exactly what changed and why, the same way Entries 15 and 18 documented their own re-extractions.

**Also checked while verifying this, and genuinely not real:** the external review's specific claims that "matched control group," "matched non-VVP control group," and "three independent stress tests"/"three independent methods in three more stress tests" are still present in the current abstract, §4.6, §4.9, the Discussion, the Conclusion, or `README.md` — grepped all of them directly against the current committed files; none of those phrases exist anymore, all correctly reflecting Entry 20's fixes. Two of the review's minor points are real but were never claimed as fixed by Entry 20 and remain open, low-priority wording items: the Executive Summary's "two independent compositing windows" (the two windows are alternative specifications over overlapping underlying satellite collections, not independent datasets) and the Limitations section's "natural experiment" phrasing (already immediately hedged in the same sentence as "not as a fully clean natural experiment," but "district-restricted observational DiD" would be tighter). Left both as-is pending a decision on whether they're worth a fifth wording pass, since they're cosmetic next to the archive-timing question above.

## Entry 22

**Status.** Entry 21's open question is now answered, and the answer overturns the study's central "surviving signal" narrative. A fresh, same-day, complete re-extraction of both the treated and control summer-window satellite data was run end-to-end, and every downstream summer-window test was recomputed against it. Sikkim's summer data is no longer missing. But once it's included — and once treated and control data are pulled on the same day so neither carries stale archive state relative to the other — every result that Entries 15-20 had built up as "the one signal that survives everything" (§4.2's headline NDBI change, §4.6's control-group DiD, the buffer-radius sweep, leave-one-district-out, randomization inference) goes from significant to non-significant. One new significant result shows up in its place (H3 NDBI border-proximity, previously a stable null), and it has not been stress-tested at all yet. This entry documents exactly what was rerun, two real script bugs found and fixed along the way, and every number that moved.

**Two script bugs found and fixed while re-running the extractions.** Both were latent — present before this entry, never triggered until a full re-extraction from a stale checkpoint was actually attempted.

1. `extract_satellite_data.py`'s resume logic read the checkpoint file directly and assumed it always carried `latitude`/`longitude` columns. The committed `border_optics_village_results_summer.csv` predates this script's current per-row-loop design (it carries `system:index`/`.geo`, leftovers from an earlier `Export.table`-based version) and never had lat/lon columns at all — only `border_optics_master_villages.csv` does. Resuming from it crashed with `KeyError: 'longitude'` the instant it reached any row still needing (re-)extraction. Fixed by merging coordinates back in from the master village list on `village_id` when the checkpoint lacks them, with a warning printed for any row that still can't be matched. Verified locally (258/258 rows recovered coordinates, zero missing) before it was run for real.
2. A second, different bug in `extract_control_satellite_data.py`'s coordinate-based resume-merge crashed with `KeyError: (27.903587, 96.940911)` (village Shirong, Anjaw) partway through a restart at row 610/735. Root cause: the aggregate "does this checkpoint match the current village list" check rounded coordinates with pandas' vectorized `Series.round(6)`, but each row's own per-row lookup key used Python's built-in scalar `round()` — the two rounding paths can disagree at the 6th decimal for some floating-point values even when the underlying number is the same, so a real, non-corrupted row failed an exact-match `.at[]` lookup and crashed the whole run. Fixed by using `Series.round(6)` consistently on both sides and replacing the fragile `.at[]` index lookup with a `dict.get()` that degrades gracefully (re-extracts the row) instead of crashing if a key is ever genuinely missing. Verified locally against the actual partial checkpoint (0 missing keys, 610/735 correctly recovered) before shipping.

**Why the treated-side fix produced a full re-extraction, not a partial one.** `extract_satellite_data.py`'s "already done" check tests for the per-metric column names (`ndbi_before_image_count`, etc.), which the old checkpoint never had — it only carried the older, generic `before_image_count`/`after_image_count`. Once the lat/lon fix let the resume proceed at all, every row failed the "already done" check and got re-extracted from scratch, not just Sikkim's. This was not a bug fixed separately — it was the mechanism that ended up (correctly, per the "whatever it takes, accuracy first" standing direction for this project) forcing a full, same-day-consistent re-pull of the entire 258-village treated summer sample, rather than only patching in Sikkim's 31 villages on top of an otherwise 4-year-old extraction date. The control-group extraction was restarted from scratch on the same basis, deliberately (old file renamed to `border_optics_control_results_summer.OLD_PRE_ENTRY22.csv` rather than resumed), so that treated and control summer data would not carry two different archive-snapshot dates into the same DiD comparison.

**Result: 258/258 treated (251 core + 7 Himachal-illustrative), 735/735 control, same day.** Both extractions are now fully populated with no missing rows on either side.

**Every summer-window headline number, before and after this entry's fresh extraction:**

| Test | Before (stale/partial data) | After (fresh, same-day, complete) |
|---|---|---|
| H1 NDBI, treated-only Wilcoxon | n=154, p < 0.000001 (highly significant) | n=251, p = 0.435831 (not significant) |
| H1 lights, treated-only Wilcoxon | n=251, p = 0.9999 (not significant) | n=251, p = 0.999994 (not significant, unchanged) |
| H4 NDBI, control-group DiD | coef = +0.0322, p = 0.00033 (significant) | coef = -0.0038, p = 0.44701 (not significant — sign flips) |
| H4 lights, control-group DiD | coef = +0.1413, p = 0.0044 (significant) | coef = +0.0374, p = 0.36553 (not significant) |
| H3 NDBI border-proximity (Spearman) | ρ = 0.038, p = 0.641 (null) | ρ = 0.291, p = 2.6×10⁻⁶ (significant — new) |
| H3 lights border-proximity (Spearman) | ρ = -0.071, p = 0.266 (null) | ρ = -0.071, p = 0.2658 (null, unchanged) |
| Buffer sweep (250/500/1000m), NDBI Wilcoxon | all three p < 0.002 (significant) | p = 0.126 / 0.436 / 0.899 (none significant) |
| Leave-one-district-out (both outcomes) | significant in 14/14 reruns | significant in 0/14 reruns |
| Randomization inference, NDBI / lights | p = 0.0005 / 0.0005 | p = 0.115 / 0.094 |
| Log1p-VIIRS DiD | raw p = 0.0044 → log1p p = 0.0003 (strengthens) | raw p = 0.366 → log1p p = 0.426 (stays null) |
| Baseline (2021) balance, NDBI / lights | p = 0.00073 / 0.0165 (imbalanced) | p = 0.478 / 0.354 (balanced) |

The last row is the one place this entry's data is *more* defensible than before, not less: the summer-window treated-vs-control baseline imbalance flagged in §6.7 as an open caveat is resolved by the fuller sample — 2021 levels are now statistically indistinguishable between treated and control villages in the summer window, which is a better starting point for a DiD design's parallel-trends assumption than the old partial sample had.

**Descriptive detail on the new H1 result, since "non-significant" alone under-describes it.** By state: Arunachal Pradesh mean ndbi_change ≈ +0.0023, Sikkim ≈ -0.0347 (now includable, and negative — this is what pulls the pooled Wilcoxon to non-significance), Uttarakhand ≈ +0.0125. RQ2 (state-level budget vs. mean NDBI change) is now computable across all 3 core states for the first time in the summer window (previously 2, since Sikkim had no data to average): Spearman rho = 0.500, p = 0.667 — still not a powered test at n=3, but a genuine coverage improvement over the old 2-state version.

**Not done in this entry.** The 250m/1km buffer-radius summer files (`border_optics_buffer250_summer.csv`, `border_optics_buffer1000_summer.csv`) are dated August 21 — before this entry's fresh 500m re-extraction — so the buffer-sensitivity table above compares three different archive-snapshot dates, the same kind of vintage mismatch Entry 21 flagged and this entry was supposed to close out for the main 2021/2025 comparison. It wasn't re-extracted here: each buffer radius takes as long as the main run (over an hour, per direct experience getting the control group done in this entry), there's no dedicated, committed script for it in `src/acquisition/` (whatever produced these two files wasn't kept), and the buffer conclusion is already null at 500m on its own, so a same-day 250m/1km re-pull was not run before flagging this rather than presenting it as fully consistent. The `§6.4` summer-missingness-mechanism paragraph and its underlying `extended_robustness_checks.py` check are now moot, not just outdated — there are zero summer-invalid core-sample villages left (251/251), so the chi-square/Mann-Whitney comparison it was built on no longer has a second group to compare against (reran it directly: it now errors out with a `SmallSampleWarning` and returns `NaN`, confirming this rather than leaving it asserted). None of `BO_Research_Paper.md`, `BO_Executive_Summary.md`, `README.md`, or the dashboard pages have been rewritten yet — every summer-window number in all four currently describes the old, partial/stale-vintage sample, and every one of them is now wrong in the same direction (overstating what survives). That rewrite needs a decision on how to reframe the paper's central claim, not just a numbers swap, so it's being surfaced directly rather than rewritten unilaterally in this entry.

**What this changes.** Nearly everything the paper currently calls its "surviving" or "significant" result. The honest summary, pending the rewrite: once the summer-window extraction is complete and same-day-consistent with the control group, none of the four core hypothesis tests (H1 built-up change, H4 control-group DiD for either outcome) shows a significant effect in the summer window any more than the full-year window already didn't — and the one new significant result (H3 NDBI border-proximity) is freshly discovered, not yet robustness-checked, and cuts against the paper's own prior framing of H3 as "a truly stable null." This is a different, and arguably cleaner, finding than the one the paper currently makes: not "an ambiguous, window-sensitive signal that survives stress-testing," but "no satellite-detectable effect survives once the data is complete and consistent, checked two ways, across two proxies, against a control group, and at three buffer radii" — which is still a real, defensible, and reportable answer to the question the Ministry of Home Affairs said had never been asked.

## Entry 23

**Status.** A full methodology audit, prompted by two independent external reviews of the post-Entry-22 push, was run against the current code rather than taken on the reviews' word — per this project's own standing rule that every claim gets checked against the actual repository before being acted on. Most of what both reviews flagged as numerical claims checked out exactly against this project's own regenerated files (the DiD coefficients, buffer-sensitivity p-values, leave-one-out counts, and the H3 correlation were all verified independently and matched to the figure shown). Two code-level claims were verified directly by reading the source, and one new, previously undocumented issue was found independently while doing so, described below. This entry documents findings only — the two code fixes it identifies are deliberately deferred to a future entry, per an explicit decision to do the free/documentation-only hardening first and the higher-cost re-extraction work separately.

**Confirmed: `select_control_villages.py` still computes distance in UTM 44N, inconsistent with the geodesic method `compute_border_distance.py` now uses.** `select_control_villages.py` line 40 sets `METRIC_CRS = "EPSG:32644"` with a comment claiming this is "the same CRS `compute_border_distance.py` uses" — that comment is now false; `compute_border_distance.py` was changed to a geodesic WGS84 calculation via `pyproj.Geod` for exactly the reason documented in its own module docstring (a single UTM zone distorts distance for a study area spanning roughly 20 degrees of longitude, from Ladakh to Arunachal Pradesh). Checked the actual scope of this inconsistency rather than assuming it invalidates everything downstream: `test_h3_border_proximity.py` and `holm_correction.py` (the H3 border-proximity tests) read `distance_to_border_km` from `border_optics_master_villages_with_distance.csv`, which is the treated-village file already computed geodesically — H1 and H3 are unaffected by this bug. The UTM distance is used only inside `select_control_villages.py`, for the soft eligibility filter (`d > max_dist * 1.5`) that caps how far from the border a candidate control village may be, and for the `distance_to_border_km` column stored on the 735 control-village rows themselves. This narrows the practical blast radius to the composition of the control pool used in the H4 (DiD) comparison — it does not touch H1, H3, the buffer-radius sweep, or the multi-year trend. Still a genuine correctness bug worth fixing (a soft filter computed with a systematically distorted distance measure could admit or exclude the wrong villages, especially for Arunachal Pradesh, far from UTM 44N's central meridian), just not the study-wide problem it could have been. **Deferred**, since fixing it requires regenerating the 735-village control list, re-running the control satellite extraction (over an hour per the timing noted in Entry 22), and re-running every H4 downstream output — a bigger job than this entry's documentation-only scope.

**Major new finding: 20 control villages sit at the exact same coordinates as 21 treated villages — the same physical settlement, entered twice under two different name spellings.** Started from a narrower check (do any control-village names match an official-but-ungeocoded VVP priority-village name?) and found 3 matches this way — see below — but then ran the more fundamental check directly: does any control village's coordinate (rounded to 6 decimals, sub-meter precision) exactly match a treated village's coordinate? It does, 20 times over, implicating 21 distinct treated villages (19 in Arunachal Pradesh, 2 in Uttarakhand — one coordinate has two treated villages, "Gumsing" and "Taying," matching a single merged control entry "Gumsing Taying"). Every one of these pairs is unmistakably the same OSM node under a different name string: transliteration variants (`Sibia`/`Sebia`, `Nisuk`/`Nissuk`, `Maliney`/`Malinye`, `Emuli`/`Emoli`, `Ngaming`/`Naming`, `Gamsali`/`Gamshali`), punctuation the exclusion filter's `normalize_name` doesn't strip (`Lengdi/Liang` vs. `Lengdi Liang` — the "/" survives NFKD-ASCII-folding since it's already ASCII, so these two strings never compare equal), a dropped/added qualifier (`Kongra(Metung)`/`Kongra`, `Hapuk (I)`/`Hapuk`, `Pado I`/`Pado`, `Angrim Valley`/`Angrim Valley Village`), and — the case no ASCII name-matching approach could ever have caught — OSM's alternate-language name tag surfacing in a different script entirely for the identical point: `Chate`/`赛探`, `Chulla`/`胡巴`, `Tarba`/`达尔巴` (Chinese), `Gunji`/`गूंजी` (Devanagari). `select_control_villages.py`'s exclusion logic is name-based only (`normalize_name(name) in treated_names`); it was never going to catch a same-point, different-script or different-transliteration collision, because there is no shared normalized string to match on. This is a bigger and more direct problem than the raw-list gap below — it means 20 of the 735 "non-VVP" control villages are, physically, VVP-I treated villages, not merely villages that happen to share a name with one.

**Narrower, related finding: 3 of the 735 control villages also share a name (not just a coordinate) with an official VVP-I priority village that was never geocoded, and so was never excluded from the control pool by the name filter either.** `select_control_villages.py` excludes candidate control villages by checking their normalized name against `treated_names`, built from `border_optics_master_villages_with_distance.csv` — but that file contains only the 251 core-sample villages that were *successfully geocoded*, not the full official priority-village universe. The raw per-state village lists in `data/raw/` (`arunachal_pradesh_vvp_villages.csv`, `sikkim_vvp_villages.csv`, `uttarakhand_vvp_villages.csv`) record 454, 46, and 51 official priority-village names respectively — 552 total against the 3 core states, versus 251 successfully geocoded, leaving 301 officially-named priority villages that were never checked against the Overpass control-candidate results at all. Checked the current 735-village control list against this fuller name set directly: 3 matches, all in Arunachal Pradesh — **Gai (Anjaw district), Tayeng (Kurung Kumey district), and Pamdung (Tawang district)** — each a village named in the official VVP-I list that could not be geocoded (so is absent from the treated sample) but that OSM/Overpass has under place=village or place=hamlet, and that consequently entered the "non-VVP" control group under its own real, VVP-listed name. These 3 are separate from, and do not overlap with, the 20 coordinate-exact duplicates above (different villages, different failure mode — one is a matching-logic gap, this one is a data-coverage gap).

**Combined scope: 21 treated villages have a physical or nominal duplicate in the 735-village control list (2.9% of the control group), all traceable to the exclusion filter's reliance on exact ASCII name matching.** This is very unlikely to be single-handedly reversing the reported DiD nulls (the effect sizes involved are small relative to 251/735-village group means), but it is a genuine, now-quantified defect in what "non-VVP control group" means as currently constructed, and a sharper fix than either the name-list-coverage fix alone or the UTM-distance fix above would deliver on its own. **Deferred** alongside the UTM fix, for the same reason: fixing it requires regenerating the control list (this time with BOTH a coordinate-proximity exclusion — e.g., drop any candidate within ~50m of any treated village, name matching aside — and the fuller official-name-list exclusion), re-running the control satellite extraction, and re-running every H4 downstream output. `tests/test_data_integrity.py`'s `test_no_treated_control_coordinate_overlap` now documents this exact count (20) as a known ceiling so a future run that makes it worse fails loudly, and one that fixes it can tighten the ceiling to 0.

**Checked and cleared: differential image-count between before/after periods is not driving the reported NDBI/lights change.** One review raised, as a general concern, whether an image-count asymmetry between periods (more or fewer usable Sentinel-2/VIIRS scenes in one period than the other, independent of any real ground change) could itself produce an apparent "change" via a compositing-sample-size artifact. Tested directly rather than left as an open worry: Spearman correlation between `(ndbi_after_image_count - ndbi_before_image_count)` and `ndbi_change` across the 251-village summer core sample gives ρ = 0.038, p = 0.551 — no detectable relationship. (The equivalent lights check could not be computed on this pass — the lights image-count difference column was constant across the sample tested, which needs a second look rather than being read as a null result; flagged here rather than silently dropped.)

**Not done in this entry, and why.** The UTM-to-geodesic fix and the control-name-exclusion fix above are both real but deferred, per the explicit choice (made this entry) to separate zero-cost documentation hardening from the higher-cost re-extraction work rather than mix them. A genuine pre-treatment panel (Section 7.5), SCL/Cloud Score+ cloud masking as a sensitivity check, a Sentinel-1 SAR cross-check, building-footprint validation, and spatial-autocorrelation testing on the new H3 result were all raised by the external reviews and are judged genuinely valuable but out of scope for a solo-researcher project on the current timeline — logged here as known, deliberately not-pursued extensions rather than silently dropped, consistent with how Section 7 already treats similarly-scoped future work.

## Entry 24

**Status.** Both fixes Entry 23 identified and deferred — the UTM-vs-geodesic distance mismatch and the control-list contamination — are now fixed in `select_control_villages.py`. This entry covers the code change only; the corrected 735-village control list has not yet been regenerated, because doing so needs live Overpass/Nominatim access, which this working environment's network policy blocks (confirmed directly: both hosts return a proxy `connect_rejected`). The actual rerun, the control satellite re-extraction that must follow it, and every H4/DiD downstream output are still open — see "Not done" below.

**Fix 1: distance metric.** `select_control_villages.py` no longer reprojects into `EPSG:32644` (UTM 44N) for its border-distance filter. `load_border_union()` now returns the India boundary union in unprojected EPSG:4326 (used only to find *which* point is nearest), and `distance_to_border_km()` computes the actual reported distance geodesically via `pyproj.Geod(ellps="WGS84").inv(...)` — the identical method `compute_border_distance.py` already uses for the treated-village distances this filter's `max_dist * 1.5` threshold is compared against. Both scripts now agree on what "distance to border" means.

**Fix 2: contamination.** Two new exclusion checks were added to the candidate loop, both scoped to catch what Entry 23 found by working backward from a passing test rather than being caught during generation in the first place:

- A geodesic coordinate-proximity check (`nearest_treated_distance_m`, threshold 50m) against every treated village's coordinates — not just the current district's — run alongside the existing cross-district OSM-point dedup. A candidate within 50m of any treated village is treated as the same physical settlement recorded twice, regardless of what name OSM has attached to it. This is what actually would have caught the 20 exact-coordinate collisions (Sibia/Sebia, Gunji/गूंजी, and the rest of the list in Entry 23) — a name-based filter structurally cannot, no matter how good the normalization.
- A full official-priority-village name check (`load_official_priority_village_names()`, reading the three raw `data/raw/*_vvp_villages.csv` files directly) alongside the existing check against the 251 successfully-geocoded treated names. This is what would have caught the 3 name-only matches (Gai, Tayeng, Pamdung) — villages that are officially VVP-I listed but never geocoded, so their names never appeared in the old `treated_names` set at all.

**Verification done in this environment (Overpass/Nominatim unreachable, so not a live rerun).** Since the actual candidate-generation step needs network access I don't have here, I instead verified the new exclusion logic by re-applying it to the *existing* 735-village control list — i.e., treating the already-fetched OSM candidates as input and checking how many the new rules would now catch. (`pyproj` also isn't installable here — same network restriction — so this verification used a plain-Python Haversine distance as a stand-in for the coordinate check; the committed script itself uses `pyproj.Geod`, which will run correctly on a machine with normal network/package access.) Result: the official-name check correctly finds exactly 3 matches, matching Entry 23's number precisely once the check is scoped the same way (against official names not already geocoded into the treated list — mathematically equivalent to the OR-condition structure the new code uses). The coordinate-proximity check at 50m finds 21 of the existing 735 control rows within range of a treated village — the same 20 exact-coordinate matches Entry 23 already documented, plus one additional case: control village "Jorging" (Upper Siang) sits 40.3m from treated village "Tenggo" (Upper Siang), a pair with no obvious name relationship to each other. This is a lower-confidence case than the other 20 — those are all unmistakably the same OSM node under a name variant or alt-script tag; Jorging/Tenggo could be the same reasoning, or could be two genuinely distinct hamlets 40m apart, which does happen in these village clusters. Flagged here rather than silently folded into the headline "20/21" count used elsewhere (`BO_Research_Paper.md` §6.10, `ANALYSIS_FREEZE.md`); it should be looked at manually (e.g., checking OSM's raw tags for both points) once the real rerun happens, rather than assumed either way.

**Resume-logic hazard, called out explicitly in the script's docstring.** `select_control_villages.py` checkpoints per district and skips districts already marked `district_verified` on resume — but every existing row in the current `border_optics_control_villages.csv` was verified under the OLD exclusion rules, not these new ones. Running the fixed script as-is would treat all 14 districts as already done and never re-check any of them. The script's module docstring now says explicitly: delete or rename the existing output file before rerunning, so every district is rebuilt fresh.

**Exact commands for the actual rerun (network/package access I don't have from my analysis environment — must run on my own machine):**
```
mv data/processed/border_optics_control_villages.csv data/processed/border_optics_control_villages_PRE_ENTRY24_FIX.csv
python3 src/acquisition/select_control_villages.py
python3 src/acquisition/extract_control_satellite_data.py
```
followed by re-running whatever downstream script(s) consume `border_optics_control_villages.csv` / `border_optics_control_results*.csv` (H4 DiD, buffer sensitivity, leave-one-out, randomization inference, and the figures/dashboard/PDFs that embed those numbers) — the same downstream set Entry 22 re-ran after its own data correction.

**Not done in this entry.** The control list has not been regenerated (blocked by this environment's network policy, per above) — `border_optics_control_villages.csv` on disk is still the old, contaminated 735-row file, and every number in `BO_Research_Paper.md`, `ANALYSIS_FREEZE.md`, and the dashboard that depends on the control group (H4 DiD, buffer sensitivity, LOO, RI) still reflects that old file. This is a code fix awaiting a data fix, not a completed correction — do not read this entry as "the contamination is resolved." `tests/test_data_integrity.py`'s ceiling constants (`KNOWN_OVERLAP_CEILING = 20`, `KNOWN_CONTAMINATION_CEILING = 3`) are also left unchanged for the same reason: they describe the *current on-disk data*, which hasn't changed yet.

## Entry 25

**Status.** The Entry 24 code fix was actually run for real, on a machine with live Overpass/Nominatim/Earth Engine access, exactly per the "exact commands for the actual rerun" left at the end of that entry. The control list is regenerated, both contamination counts are independently confirmed at zero (not just under a documented ceiling), both satellite-extraction windows were re-pulled against the new list, both DiD models and the extended robustness suite were re-run against the new data, and — this is the headline of this entry — the one result the entire paper has been treating as its "surviving significant finding" since Entry 22 does not survive this fix. It was a symptom of the same contamination Entry 23 found and Entry 24 patched, not a real effect.

**What was actually run, and where.** I still can't reach Overpass, Nominatim, or Earth Engine from my analysis environment (same network policy Entry 24 hit), so I ran the full pipeline on my own machine: `mv` the old control list aside, `select_control_villages.py` (regenerate), `extract_control_satellite_data.py --window full_year`, `extract_control_satellite_data.py --window summer`, `did_model.py --window full_year`, `did_model.py --window summer`, `extended_robustness_checks.py` — the exact sequence Entry 24 specified, run to completion with no shortcuts. The resulting files were pulled back into my analysis environment from my laptop and independently re-verified here (test suite plus a direct recount) rather than taken on trust from the terminal output alone.

**Contamination: genuinely zero, not just under-ceiling.** The new control list has 732 villages (down from 735 — 3 net fewer, not simply "20 removed" or "3 removed," because the 50m coordinate-proximity filter and the fuller official-name filter both operate on the *candidate* pool before final selection, not as a post-hoc subtraction from the old list — some previously-excluded-by-name candidates are now also excluded by coordinate, and the district-level candidate pools differ from before). Re-ran both of Entry 23's original checks directly against the new 732-village list, independently of `tests/test_data_integrity.py`'s ceiling assertions:

- Exact-coordinate overlap with any of the 251 treated villages: **0** (was 20, implicating 21 treated villages).
- Name match against the full official VVP-I priority-village universe (552 names across the three core states), not just the 251 geocoded ones: **0** (was 3 — Gai, Tayeng, Pamdung).

Both `KNOWN_OVERLAP_CEILING` and `KNOWN_CONTAMINATION_CEILING` in `tests/test_data_integrity.py` are tightened from 20→0 and 3→0 accordingly, `EXPECTED_CONTROL` updated from 735→732, and the full suite now passes 12/12 against the real regenerated data (previously 11/12, the one failure being the stale 735 constant against the new 732-village list — itself confirmation the new count is real, not a copy-paste artifact). The lower-confidence 40.3m Jorging/Tenggo near-miss Entry 24 flagged separately (not folded into the headline 20/21 count, since it had no name relationship unlike the other 20) is resolved by construction: the 50m coordinate-proximity threshold used in the actual fix catches it along with everything else, so it does not need separate manual adjudication any more.

**Both satellite-extraction windows re-pulled clean: 732/732 valid, both windows.** `extract_control_satellite_data.py`'s resume-hazard warning (added in Entry 24, see that entry's "Resume-logic hazard" note) worked as intended — the coordinate-set mismatch between the new 732-village list and any stale checkpoint was detected automatically, and both windows extracted fresh rather than silently resuming a mismatched cache. Full-year: 732/732 control villages have valid before/after NDBI and lights data (previously the full-year DiD ran on only 190 of 735 control villages with valid data — this fix also incidentally closed a missingness gap that had nothing to do with contamination, since the new pull is complete on both metrics for every village). Summer: 732/732 valid, same as before the fix (summer control data was already complete under the old list; only its content changed, not its completeness).

**The reversal: full-year night-lights DiD, this paper's only surviving significant control-group result since Entry 22, is now null under every check that used to find it significant.**

| Check | Before (contaminated 735-list) | After (clean 732-list, Entry 25) |
|---|---|---|
| Primary DiD (district FE, cluster-robust SE) | coef = +0.1653, 95% CI [+0.0105, +0.3202], p = 0.0364 | coef = +0.05046, 95% CI [-0.0468, +0.1478], p = 0.30946 |
| Comparison DiD (no FE, HC3) | p = 0.1033 | p = 0.57800 |
| Leave-one-district-out | significant in 10 of 14 reruns (coef range +0.1161 to +0.2166) | significant in 0 of 14 reruns (coef range +0.01703 to +0.08081) |
| Randomization inference (2,000 permutations) | p = 0.0155 (perm mean/SD not previously recorded in the summary JSON) | p = 0.12994 (observed +0.05046 vs. permutation mean -0.00292, SD 0.03335) |
| Log1p-transformed DiD | raw p = 0.0364 → log1p p = 0.0374 (both significant, mutually consistent) | raw p = 0.30946 → log1p p = 0.50048 (both null) |
| 2021 baseline balance (treated vs. control) | treated 0.4282 vs. control 0.4082, p < 0.00001 (worst imbalance in the study) | treated 0.42821 vs. control 0.41006, p = 0.08976 (not significant) |

Every one of these was, in every earlier version of this paper, the specific piece of evidence cited for treating this result as "real but fragile" rather than a null — the 10/14 LOO count, the RI p-value, the log1p consistency check, all cited by name in §4.6, §4.9, §6.7, and §6.10 of `BO_Research_Paper.md`. All four now point the same way as every other test in this study: null. The full-year NDBI DiD, which was already null before this fix (+0.0088, p = 0.275, on an incomplete 190-village control subsample), is also now cleanly re-estimated on the complete 732-village set: +0.00667, p = 0.30996 (HC3 p = 0.61425) — same conclusion, tighter footing. Both summer-window DiDs (NDBI and lights) were already null before this fix and remain null after it, with numbers essentially unchanged (summer NDBI: -0.0038→-0.00357, p 0.447→0.47290; summer lights: +0.0374→+0.03244, p 0.366→0.45017) — consistent with the fact that only 732 of 735 control villages changed at all, and the summer window's own contamination-driven bias was apparently too small to move a result that was already comfortably null.

**Why this is the correct outcome, not a disappointing one.** The full-year lights DiD's old significance was built, in part, on 20 control villages that were physically the same settlements as 21 treated villages, and 3 more that were officially-listed-but-ungeocoded treated villages under their own real names — a contaminated comparison where some of the "control" group's night-lights trajectory was actually the treated group's own trajectory, counted twice on opposite sides of the same regression. A DiD result that depends on a village serving as its own counterfactual is not a fragile-but-real effect; it is exactly the artifact this study's own Entry 23 warned it might be, now confirmed by removing the artifact and watching the result disappear along with it. This is the same shape of finding as Entry 22's Sikkim discovery — a result that looked like it survived every check, until the actual data problem behind it was fixed rather than worked around — and it is treated with the same honesty: reported in full, not minimized, per this project's standing rule that the methodology has to be right regardless of which way the result goes.

**What this means for the paper's headline claim.** With this fix, there is no longer any control-group DiD result — for either outcome, in either window — that clears significance under any specification. Combined with the already-null H1 treated-only result (both windows, Section 4.2) and the already-null buffer-radius sweep (Section 4.8), the paper's honest headline becomes unconditional rather than qualified: no satellite-detectable effect of VVP-I on built-up area or night-lights survives being checked two ways (compositing window), across two proxies (NDBI, night-lights), against a control group, and at three buffer radii — full stop, with no remaining "one fragile exception" to carve out. This is, if anything, a cleaner and more defensible result to publish than the one it replaces: a uniform null across every test this study built, rather than a null with one asterisk that itself turned out to be a data artifact.

## Entry 26

**Status.** Entry 23's "genuinely valuable but out of scope" future-work item — a Sentinel-1 SAR cross-check, listed in `BO_Research_Paper.md` §7.1 — was actually pursued, alongside a second, previously-unplanned independent check (Google Dynamic World's "built" probability band, algorithm-independent of NDBI though not sensor-independent — see that extraction script's own docstring caveat). Both were run for treated and control, both windows (full_year, summer), against the current 258-treated/732-control sample this study has used since Entry 25's fix. One incomplete-extraction problem was found and fixed along the way, the same "checkpoint exists but the run behind it never finished" class of issue this project has hit before. Final numbers below are from `src/analysis/triangulation_analysis.py`, run with `statsmodels` on my own machine — not my analysis environment's manual-OLS stand-in, which I used only to catch the bug below before I attempted a real run.

**What was extracted.** `src/acquisition/extract_dynamicworld_built.py` (GOOGLE/DYNAMICWORLD/V1 "built" band) and `src/acquisition/extract_sar_backscatter.py` (COPERNICUS/S1_GRD VV/VH, descending orbit) — both at the same 500m buffer and before/after windows as the primary NDBI extraction, both run treated+control × full_year+summer (eight extraction runs total). I have no Earth Engine access in my analysis environment, the same standing limitation every prior entry's satellite work has hit, so I did all eight runs on my own machine and copied the results back into the repository.

**Bug found: `border_optics_control_sar_summer.csv` was a stalled checkpoint, not a completed extraction, and nothing in the pipeline would have caught this on its own.** Before the fix, this file had valid VV/VH values for only 50 of 732 control villages — and, tellingly, `sar_before_image_count`/`sar_after_image_count` were also null (not zero) for the other 682, meaning the extraction loop never reached those rows, as opposed to reaching them and finding zero usable Sentinel-1 scenes. `extract_sar_backscatter.py`'s resume logic itself is not buggy the way Entry 22's scripts were — it correctly checks all six outcome columns before treating a row as done, and correctly resumes from the checkpoint rather than the master list — but a checkpoint file existing at all does not mean the run behind it finished, and nothing short of actually counting valid rows against the expected total surfaces that. It was caught by running `triangulation_analysis.py`'s own H1/H4 logic (replicated by hand in a test harness, since `statsmodels` is unavailable in this environment) against the on-disk files before treating any result as final, per this project's standing rule of checking every claim against the actual data rather than taking a file's existence on trust. The other three SAR/Dynamic World files (treated SAR, both windows; control SAR full_year) were already complete (732/732 or 258/258, all outcome and image-count columns populated) — this was specific to one file, not a systemic problem.

**Fix.** Re-ran `python src/acquisition/extract_sar_backscatter.py --group control --window summer`. Its resume logic picked up exactly where the stalled checkpoint left off (skipped the 50 already-done rows, processed the remaining 682) and finished at 732/732.

**Final results, all three independent checks, both windows:**

| Source | Window | H1 (treated-only, paired) | H4 (control-group DiD) |
|---|---|---|---|
| Dynamic World "built" | Full-year | n=249, mean change +0.00673, Wilcoxon p<0.000001 | n=1940 (249 treated/721 control), coef +0.00310, SE 0.00123, 95% CI [+0.00069, +0.00551], p=0.01168 |
| Dynamic World "built" | Summer | n=169, mean change +0.00711, Wilcoxon p<0.000001 | n=1428 (169 treated/545 control), coef +0.00736, SE 0.00229, 95% CI [+0.00286, +0.01185], p=0.00133 |
| SAR VV (dB) | Full-year | n=251, mean change -0.09879, Wilcoxon p=1.00000 (not greater) | n=1966 (251/732), coef -0.00837, SE 0.03162, 95% CI [-0.07035, +0.05361], p=0.79116 |
| SAR VV (dB) | Summer | n=251, mean change -0.17734, Wilcoxon p=1.00000 (not greater) | n=1966 (251/732), coef +0.01151, SE 0.03175, 95% CI [-0.05071, +0.07373], p=0.71701 |
| SAR VH (dB) | Full-year | n=251, mean change -0.09873, Wilcoxon p=1.00000 (not greater) | n=1966 (251/732), coef -0.00849, SE 0.02951, 95% CI [-0.06633, +0.04936], p=0.77370 |
| SAR VH (dB) | Summer | n=251, mean change -0.15353, Wilcoxon p=1.00000 (not greater) | n=1966 (251/732), coef -0.00238, SE 0.04018, 95% CI [-0.08114, +0.07637], p=0.95267 |

`outputs/triangulation_results.json` holds the full machine-readable output. There is no statsmodels-verified "before-the-fix" number for the SAR-summer control DiD — the fix was applied as soon as the incompleteness was found, before a real `statsmodels` run was attempted on the partial file. My analysis environment's manual-OLS approximation on that 50-village partial data had shown VV coef +0.11964, p=0.01441 and VH coef +0.14335, p=0.0001, both spuriously significant on a tiny, non-random (first-50-processed, not sampled) subset of the control group; both are gone once the extraction actually finished (p=0.717 and p=0.953 above).

**What this means for the paper.** SAR — the one check here that is genuinely sensor-independent (a different satellite constellation, radar rather than optical, immune to the cloud cover this study has hit real bugs over twice before, Entries 21-22 and the buffer-radius same-day gap) — is null on both bands, both windows, every specification. This is the strongest new evidence for this study's existing headline claim (Entry 25's "no satellite-detectable effect... full stop"): a completely independent sensor was pointed at the same villages and found nothing either. Dynamic World — algorithm-independent but not sensor-independent, same Sentinel-2 source imagery as NDBI per that script's own docstring — disagrees: a small, statistically significant increase in "built" probability in treated villages relative to control, in both windows, at an effect size of roughly +0.003 to +0.007 on a 0-1 probability scale. This is real and robust in the narrow sense that it reproduces to several significant figures between my analysis environment's manual OLS and the actual `statsmodels` run, and both windows agree in sign and rough magnitude — it is not a repeat of Entries 22/25's contamination-driven artifacts, and it was not affected by this entry's SAR-checkpoint bug (Dynamic World's own image-count columns were fully populated throughout; its nulls are genuine no-cloud-free-scene cases). It does not overturn the primary NDBI-based estimand — NDBI, not Dynamic World, is the primary estimand per `ANALYSIS_FREEZE.md` — and the two checks that are actually sensor-independent (SAR VV, SAR VH) both support the null. But it is a genuine, honest complication for a triangulation section that hoped for three-out-of-three agreement, and needs to be reported as such, not folded silently into "the null is confirmed."

**Not done in this entry.** `BO_Executive_Summary.md`, `README.md`, and the dashboard pages make no mention of either check. The root/`static/` PDF copies of `BO_Research_Paper.pdf`/`BO_Development_Log.pdf` have not been rebuilt against this entry's text changes (`build_docs_pdfs.sh`, same two-step pattern as every prior entry that touched paper text).

## Entry 27

**Status.** I worked through four of the open items I'd flagged after Entry 26 — the unexplained Dynamic World divergence, both remaining §7.6 H3 stress-test items (linearity, multi-year cross-check), and the previously-identified-but-untested spatial-autocorrelation threat (§6.10) — this entry, all against data already on disk, no new Earth Engine extraction needed. Two genuinely new findings came out of it, one of them a direct structural echo of this study's own Entry 21-22 history. The remaining open items from that list (pre-treatment panel, buffer-radius same-day re-extraction, ground-truth candidates, building-footprint check, RTI drafting) need either live Earth Engine access or real-world action and are tracked separately, not covered here.

**Dynamic World investigation, finding 1: the effect is broad-based, not outlier-driven, and not a baseline-imbalance artifact.** Dropping the 5 highest- and 5 lowest-|built_change| treated villages moves the full-year mean from +0.00673 to +0.00621, and the summer mean from +0.00711 to +0.00655 — a handful of leverage points are not carrying this result. Treated-vs-control baseline (`built_before`) balance is clean in both windows (Mann-Whitney p=0.996 full-year, p=0.155 summer), so this is not last entry's contamination/imbalance story replaying under a new proxy.

**Dynamic World investigation, finding 2: a genuine and unexplained asymmetry — the increase is concentrated in treated villages that already had a higher baseline "built" probability, and control villages show the opposite pattern.** Spearman(built_before, built_change) for treated villages is +0.272 (p=0.00001, full-year) and +0.124 (p=0.109, summer, not significant on its own) — villages that started more built-up increased more. Control villages show no such relationship in full-year (rho=+0.020, p=0.585) and a significant *negative* one in summer (rho=-0.229, p<0.00001) — control villages that started more built-up tended to decrease, the more ordinary regression-to-mean/ceiling pattern expected on a bounded 0-1 probability scale. Treated villages do not show that ceiling effect; if anything they show the reverse. Two explanations are both plausible and neither is tested here: a real "existing settlements densify preferentially" pattern specific to VVP-I investment, or a measurement-sensitivity artifact where already-more-built-up villages simply produce a less noisy "built" probability estimate in which a small real or spurious change is easier for Dynamic World's classifier to register. Left open, flagged in the paper rather than adjudicated.

**Dynamic World investigation, finding 3 — a structural echo of Entries 21-22: all 31 Sikkim treated villages are null in the summer window, none in the full-year window.** Checked directly: 0 of 31 Sikkim core-sample villages have valid summer `built_change`; the same 31 are all valid (though weak: mean change +0.00098, far below Arunachal Pradesh's +0.0075 and Uttarakhand's +0.0078) in the full-year window. This is the exact shape of the bug Entry 21-22 found and fixed for NDBI — a whole state's summer data going to zero — except this time it's Dynamic World's own Sentinel-2 L1C pull, not the SR-Harmonized NDBI pipeline Entry 22 fixed, and it has not been checked whether this is a genuine monsoon-cloud blackout (plausible, and consistent with why this study runs a summer-matched window check at all, §2.4) or another archive-backfill snapshot artifact like the one Entry 22 found and resolved by simply re-extracting later. Not re-extracted or resolved in this entry — flagged rather than assumed either way. Practically, this means the summer Dynamic World DiD (+0.00736, p=0.00133) is estimated on a treated sample missing an entire state that, in the full-year window, shows the weakest signal of the three — so the summer result may be inflated by Sikkim's absence in a structurally similar way to the pre-Entry-22 NDBI summer result, though unlike that case this has not been confirmed either way by an actual re-extraction. The full-year Dynamic World DiD, which does include Sikkim and is still significant (p=0.01168) despite Sikkim's weak individual contribution, is the more trustworthy of the two windows for this reason.

**Dynamic World investigation, finding 4: a weak, real, but modest image-count correlation, in opposite directions for treated and control.** Spearman(image-count difference between periods, built_change) for treated villages: rho=+0.126 (p=0.047, full-year), rho=+0.172 (p=0.025, summer) — villages that gained more usable scenes between periods show slightly more "built" increase. For control villages the same check gives the opposite sign: rho=-0.076 (p=0.042, full-year), rho=-0.117 (p=0.006, summer). Both are real (significant) but small, and opposite-signed between groups, so this does not look like a single, consistent imaging-density artifact driving the treated-control gap the way Entry 23 tested for and ruled out in NDBI (that check came back null, ρ=0.038, p=0.551; this one does not come back null, but it is much weaker and sign-inconsistent, so it is reported as a genuine partial confound worth naming, not a full explanation).

**H3 §7.6 item 1 (linearity), finding: the summer NDBI-proximity correlation is clean and close to linear across the full distance range; the full-year lights-proximity correlation is not, on inspection of its binned means, even though a formal linear-vs-quadratic F-test does not flag it.** Summer NDBI-change in five equal-sized distance quintiles rises monotonically: -0.0182, -0.0074, +0.0009, +0.0071, +0.0135 (nearest to farthest) — genuinely progressive, not concentrated at either end (quadratic term F=0.89, p=0.347, not significant). Full-year lights-change in the same five bins: +0.0815, +0.1557, +0.0090, +0.0073, +0.1765 — not monotonic at all; it rises, falls twice, then jumps back up in the farthest bin. The quadratic F-test on this one is also not significant (F=0.69, p=0.406), so a simple curved-relationship story doesn't fit either, but the honest read of the binned means is that this correlation's shape looks more like a small number of districts happening to sit at particular distances than a smooth proximity gradient. This is a real caveat for the full-year lights-proximity result specifically, distinct from and in addition to its already-reported leave-one-out/randomization-inference robustness (§7.6, established before this entry).

**H3 §7.6 item 2 (multi-year cross-check), finding: both H3 results replicate against the independent 3-point extraction in overall direction and magnitude, but neither is stable across both sub-periods — one reverses sign.** Distance vs. the full 2021-2025 multi-year-extraction change reproduces the headline numbers closely (summer NDBI rho=+0.293 vs. the two-point extraction's +0.291; full-year lights rho=-0.252 vs. -0.252 exactly) — a genuine independent-data consistency check, not a tautology, since the multi-year extraction (Section 3.8) is its own separate pull. Split into the two sub-periods, summer NDBI's relationship reverses: distance vs. 2021-2023 change is rho=+0.426 (p<0.00001, same direction, stronger), but distance vs. 2023-2025 change is rho=-0.222 (p=0.0004, opposite sign, significant). Full-year lights is more consistent but still uneven: 2021-2023 rho=-0.239 (p=0.0001, same direction), 2023-2025 rho=-0.078 (p=0.218, same direction but no longer significant). Read together with Section 4.7's own finding that the aggregate two-point NDBI comparison hides a decline-then-recovery pattern within it, this says the border-proximity relationship is not a steady, one-directional gradient holding constant across the study period either — for NDBI it is actually opposite-signed in the two halves, netting out to the reported positive correlation over the full period; for lights it is concentrated in the earlier half. Neither finding invalidates the headline H3 correlations (both are real, Holm-significant results on the actual 2021-2025 comparison this study specifies), but both are now known to be less temporally stable than a report of "ρ=0.291, p=0.0000026" alone would suggest.

**Spatial autocorrelation, finding: confirmed present and significant, not merely a theoretical concern — and it survives even after removing the effect §7.6 is testing in the first place.** §6.10's Threats-to-Validity table listed this as "identified, not yet tested." It is now tested. `libpysal`/`esda` are not installed in my analysis environment, so Moran's I was computed by hand (k=8 nearest-neighbor weights by haversine distance, permutation-based p-value, 999 shuffles — the same "implement it from scratch when the package isn't available" approach this project used for OLS in Development Log Entries 20/22 and again in Entry 26's manual test harness). Summer NDBI-change: Moran's I = 0.346 against a null mean of -0.002 (SD 0.029), permutation p = 0.001. Full-year lights-change: I = 0.076 against a null mean of -0.004 (SD 0.020), p = 0.004. Both are real, positive, significant spatial clustering — nearby villages' outcomes move together more than chance would predict. Crucially, this is not simply restating the H3 distance relationship itself: recomputing Moran's I on the *residuals* of summer NDBI-change after removing the linear distance-to-border trend still gives I = 0.272, p = 0.001 — nearby villages resemble each other for reasons beyond their shared distance-to-border. This means the 251 core-sample villages are not the statistically independent observations every test in this study (H1's Wilcoxon, H3's Spearman and its own randomization-inference check, H4's cluster-robust SE which already clusters by district but not by finer-grained proximity) implicitly treats them as, and the true effective sample size is smaller than 251 — which, in the standard direction this kind of clustering biases things, means every p-value in this study is probably somewhat more optimistic than it should be, H3's most of all since it is the test most directly about spatial structure. A properly spatially-corrected test (an effective-sample-size adjustment or a spatial permutation null, per Dutilleul (1993) or a spatial-lag/error model) is the natural next step and was not run in this entry — this entry establishes that the correction is needed and quantifies the clustering, not what a corrected p-value would be.

**What this means for the paper.** None of these four findings changes the primary NDBI estimand's own conclusion (Sections 4.2, 4.6, §7 SAR check) — all four are about secondary or exploratory results (Dynamic World, H3, and the general independence assumption underlying every test's stated p-value). All four make this study's own reporting more honest, not less favorable to it: naming a real, unexplained asymmetry and a Sikkim-summer echo in Dynamic World rather than treating "the disagreement is real" (Entry 26) as the end of the inquiry; naming that one of the two surviving H3 results doesn't look like a clean gradient on inspection, and that neither is stable within the study period despite both replicating against an independent extraction; and naming, with an actual number, that this study's stated p-values are probably a bit too confident because villages cluster in space. This is the same standing approach Entries 21, 22, 23, and 25 each took toward a result that looked fine until checked harder — apply it here too, even though none of these four checks flips a headline conclusion the way those did.

**Not done in this entry.** The remaining items from the same request — a genuine pre-treatment panel (§7.5), a same-day buffer-radius re-extraction (§6.9), ground-truth positive-control candidates (§7.3), a building-footprint cross-check (§7.2), and RTI draft text for Himachal Pradesh/Ladakh (§7.4) — are tracked as separate, ongoing work; the first two need live Earth Engine access I don't have in my analysis environment and I'm preparing them as ready-to-run scripts for my own machine, the next needs web research (in progress separately), and the last needs me to actually file it, not something automatable. A spatially-corrected p-value for H3, identified as the natural next step above, is also not computed in this entry.

## Entry 28

**Status.** `src/acquisition/extract_pretreatment_baseline.py` (new) and `src/analysis/pretreatment_placebo_test.py` (new) are written and ready for me to run on my own machine for Section 7.5's pre-treatment panel; `src/acquisition/extract_buffer_sensitivity_data.py`'s docstring now documents the exact resume hazard and same-day rerun sequence Section 6.9 needs, rather than requiring a new script (the 250m/1km extraction logic already existed and was already correct — the gap was purely that it and the 500m primary run were never pulled on the same day, and a bare re-run of either would silently skip everything as already-done instead of pulling fresh data). Neither has been run for real yet — both need live Earth Engine access I don't have in my analysis environment. Separately, and completed for real in this entry: a ground-truth positive-control search (Section 7.3) that the paper had twice previously reported as unsuccessful.

**Ground-truth positive control: found, and the result is this study's most important secondary finding to date.** News coverage of an official two-day tour of Anjaw district, Arunachal Pradesh, by the state's Deputy Chief Minister (Arunachal Times, `arunachalobserver.org`, 31 October – 1 November 2023) documents 15 specific, named, dated projects inaugurated across several Anjaw villages. Checked each village name against this study's 258-village geocoded sample directly: three matches — **Walong** (civil terminal building at Walong's advanced landing ground; 30-bed girls' hostel at Walong Govt. Secondary School), **Kaho** (basketball court, solar street lights, school library, explicitly reported as VVP-funded), and **Musai** (solar street lights and other "model village" facilities, also explicitly VVP-attributed). Two other villages named in the same coverage — Kibithoo and Tinai — are not in the geocoded sample and were not usable.

Pulled each of these three villages' individual values from the extractions already on disk (no new extraction needed) across all four proxies, full-year window, 2021-before vs. 2025-after:

| Village | NDBI change | VIIRS lights change | Dynamic World "built" change | SAR VV / VH change (dB) |
|---|---|---|---|---|
| Walong | -0.038 | +0.909 (0.892→1.801, ~doubling) | +0.016 | -0.08 / +0.13 |
| Kaho | -0.057 | +0.420 (0.514→0.934, +82%) | +0.044 | +0.11 / +0.19 |
| Musai | -0.064 | +0.011 (0.317→0.328) | +0.006 | -0.04 / +0.07 |

VIIRS night-lights clearly registers the confirmed new infrastructure at Walong and Kaho, both well above this study's own pooled full-year lights mean change. NDBI moves in the *wrong direction* at all three villages, despite independently-confirmed new construction in the exact comparison window. Dynamic World shows a small positive change at all three, directionally consistent though far smaller than lights'. SAR shows no clear signal at any of the three, consistent with SAR's own pooled null (Section 4.10).

**Why this matters, and its limits.** This is a 3-village case study drawn from one official visit to one district, not a random sample of VVP-I's investment portfolio — it cannot establish that VIIRS is "the correct" proxy for this programme in general, or that NDBI is simply wrong. But it is real, sourced evidence — not a plausible-sounding conjecture, which is what Section 7.2's "NDBI's 500m buffer might be too coarse for VVP-I's actual investment scale" argument was before this entry — for a specific, useful explanation of part of this study's own pooled null: the confirmed projects here (solar streetlights, a hostel, a basketball court, a terminal building) are small, point-scale additions that shift a radiance sensor's reading directly but are a rounding error inside a 500m-radius reflectance average dominated by terrain, vegetation, and existing built surface. It also gives a first empirical reason to weight this study's own night-lights results (Section 4.3) somewhat more heavily than its NDBI results specifically for detecting *this kind* of small infrastructure investment, though not enough evidence on its own to reweight the study's headline conclusion, which is stated in terms of NDBI as the primary estimand (Section 3.12) regardless.

**Not done in this entry.** The pre-treatment and buffer-radius scripts above still need me to actually run them on my own machine before Section 7.5/6.9 can report real numbers. A building-footprint cross-check (§7.2) and RTI draft text for Himachal Pradesh/Ladakh (§7.4) are tracked separately and not done here.

## Entry 29

**Status.** The last two open items from the same punch list are now done as far as they can be from my analysis environment: a building-footprint extraction script and its validation companion for Section 7.2, and a full draft RTI application for Section 7.4. Both are deliverables prepared here for action elsewhere, not results — neither has been run or filed yet.

**Building-footprint check (§7.2): `extract_building_footprints.py` and `building_footprint_validation.py` added, with a scope correction recorded up front rather than discovered later.** Section 7.2 as originally written implied a before/after building-footprint comparison, symmetric with this study's other before/after extractions. Checked directly before writing the extraction script: Google's Open Buildings dataset (used here) and Microsoft's Global ML Building Footprints are both single-vintage products, not multi-temporal time series — there is no "2021 Open Buildings" to difference against a "2025 Open Buildings" the way ndbi_before/ndbi_after are differenced elsewhere. This is recorded in the new script's own docstring, the same way `extract_dynamicworld_built.py` recorded and explained ruling out GHSL for a comparable reason (Development Log entries around the original Dynamic World extraction). What the new pair of scripts actually does instead: extract a single current-vintage building count/area per village buffer (`extract_building_footprints.py`, treated and control), then cross-sectionally validate this study's own NDBI/lights/Dynamic World "after" values against it (`building_footprint_validation.py`) and specifically check whether Walong, Kaho, and Musai (Entry 28's ground-truth case study villages) show a building-footprint count consistent with the confirmed new construction. Neither script has been run — both need live Earth Engine access I don't have in my analysis environment.

**RTI draft (§7.4): full application text drafted and delivered, `docs/RTI_draft_HP_Ladakh_village_lists.md`.** Combined application to the Ministry of Home Affairs' CPIO (Border Management Division) requesting the village-wise lists behind the 75 Himachal Pradesh and 35 Ladakh villages the Ministry has already confirmed in count via Lok Sabha/Rajya Sabha replies (cited by exact question number and date in the draft) without publishing the names — the same two gaps Section 6.1 documents. Includes filing mechanics (RTI Online Portal vs. postal, fee, CPIO address, Section 7(1) 30-day timeline, first-appeal path if it stalls), a note on when to split it into two separate applications instead of one combined submission, and a short follow-up procedure for geocoding whatever village names come back through this study's existing `geocode_villages.py`/`geocode_villages_bhuvan.py` pipeline once (if) a response arrives. Filing this is a real-world action only I can take myself — nothing here does that for me.

**What this means for the paper.** Neither item changes anything reportable yet — a written-but-unrun script and a written-but-unfiled RTI application are preparatory work, not findings. Sections 7.2 and 7.4 are left as future work in `BO_Research_Paper.md`, correctly, since nothing has actually been extracted or received. This closes out every item I wanted to work through after Entry 26 that could be done without live Earth Engine access, a live RTI filing, or a wait for the Ministry's response: Entries 26-29 between them cover the Dynamic World investigation, both remaining §7.6 H3 checks, spatial autocorrelation, the ground-truth case study, and now these last two. The three genuinely unstarted next actions are all mine to take: run the pre-treatment and buffer-radius extractions (§7.5, §6.9) and the building-footprint extraction (§7.2) on a machine with Earth Engine access, and file the RTI (§7.4) — each logged here as a specific, named, ready-to-execute next step rather than a vague "future work" line.

**Not done in this entry.** Running any of the four now-ready scripts (`extract_pretreatment_baseline.py`, `extract_buffer_sensitivity_data.py`'s same-day sequence, `extract_building_footprints.py`, and their analysis companions) and filing the RTI application are all still outstanding, and all require action outside my analysis environment.

## Entry 30

**Status.** I actually ran `extract_pretreatment_baseline.py` and `extract_building_footprints.py` (both written in Entry 29) for real on my own machine — all 6 combinations (4 pre-treatment, 2 footprint) completed cleanly on the first pass, no failures, via the `run_all_new_extractions.py` one-command runner (also Entry 29). `pretreatment_placebo_test.py` and `building_footprint_validation.py` were then run against the results. Both produce real findings, one of them significant enough to change how a section of the paper is written.

**Pre-treatment placebo test (§7.5): 3 of 4 combinations clean, 1 flagged.** Full-year NDBI (placebo DiD coef +0.00196, p=0.864), full-year lights (-0.00665, p=0.755), and summer lights (+0.00047, p=0.968) all show no significant 2019-to-2021 divergence between treated and control villages — a period during which VVP-I could not have had an effect. This is genuine, direct evidence for this study's own parallel-trends assumption in three of four combinations, not merely an assumption asserted and left untested. Summer NDBI is the exception, and it does not get rounded up to a clean pass here just because the script's own auto-verdict function (a bare p>0.05 check) printed "PASSES": the district-fixed-effects placebo DiD coefficient is +0.01287 with p=0.06429 — borderline, not clearing the conventional threshold but close to it — while the raw, unadjusted Mann-Whitney comparison of the same two groups' distributions is sharply significant, p=0.00001. Read together: district composition absorbs most, but evidently not all, of a real pre-existing difference in how treated and control villages' summer NDBI moved between 2019 and 2021. Checked whether this pre-period effect could explain away the real, already-null summer NDBI DiD (Section 4.6, coefficient -0.00357): it cannot in any simple sense, since the pre-period effect (+0.01287, treated trending up) runs in the *opposite* direction from the real result, not the same one — a naive "the pre-trend explains the main result" story does not fit the actual signs.

**Building-footprint validation (§7.2): a real, previously-unavailable calibration result for the Section 4.10 Dynamic World disagreement.** Cross-sectional correlation between an independent, non-satellite-index building-footprint count (Google Open Buildings, confidence ≥ 0.75) and each proxy's 2025-era level: NDBI rho=0.399 (p<0.00001), night-lights rho=0.478 (p<0.00001), Dynamic World "built" probability rho=0.808 (p<0.00001) — Dynamic World's correlation with actual, independently-detected building footprints is roughly double NDBI's. This is a level correlation, not a change-detection test, so it does not resolve Section 4.10's disagreement about which proxy correctly detects *change* — but it is real evidence, not a plausible-sounding excuse, that Dynamic World's classifier tracks ground-truth built structure in this terrain noticeably better than NDBI's fixed two-band formula does, which is directly relevant context for how much weight Section 4.10's Dynamic World finding deserves relative to NDBI's own null. The three Section 7.3 case-study villages' building counts (Walong 524, Kaho 78, Musai 108, against a sample median of 34) confirm they are all real, moderate-to-large settlements, not negligible hamlets where a small addition would move a percentage-based index dramatically — consistent with, and a further concrete reason for, why NDBI's 500m area-average missed the confirmed new construction at all three (Section 7.3).

**What this means for the paper.** Two sections move from "future work" to "done, with a real result": §7.5 is now mostly reassuring for this study's DiD design, with one specific, honestly-flagged exception rather than either a blanket "resolved" or leaving the concern as abstract and untested. §7.2 produces a genuinely new piece of evidence bearing on Section 4.10's still-open Dynamic World-vs-NDBI disagreement — not resolving it, but giving a concrete, sourced reason to weight Dynamic World's reading of these villages more seriously than "it disagrees with the primary estimand, so it's probably noise" would suggest. Neither finding changes the primary NDBI estimand itself (Section 3.12) or this study's headline null.

**Not done in this entry.** The same-day buffer-radius re-extraction (§6.9) has still not been run — it is independent of everything in this entry and remains the one open item from the original punch list that needs my own machine time. `BO_Executive_Summary.md`, `README.md`, and the dashboard pages still do not reflect any of Entries 26-30's findings — the documentation sweep flagged as outstanding since Entry 26 remains outstanding.

## Entry 31

**Status.** I ran the last open item from the original punch list — the same-day buffer-radius re-extraction flagged in §6.9 — for real on my own machine. All three radii (500m primary via `extract_satellite_data.py --window summer`, then 250m and 1000m via `extract_buffer_sensitivity_data.py`) were re-extracted back-to-back on the same day, after first renaming aside the three stale, non-same-day checkpoint files so none of the three scripts could silently skip-as-already-done against old data. All three completed cleanly: 258/258 (500m primary extraction) and 258/258 at each buffer radius, no failures. `analyze_results.py` was then re-run to regenerate the 500m "analyzed" file from today's fresh extraction (the pre-existing `buffer_sensitivity.py` reads that file, not the raw one, for its 500m leg), and `buffer_sensitivity.py` itself was run to produce the real three-radius comparison.

**Result: still a clean null at all three radii, and the archive-timing fix barely moved the numbers.** NDBI Wilcoxon (core sample, n=251 at every radius, matched — no coverage gap between radii this time): 250m mean change +0.00175, p=0.121369; 500m mean change -0.00090, p=0.435831; 1000m mean change -0.00293, p=0.897611. Night-lights: 250m p=0.999976, 500m p=0.999994, 1000m p=1.000000 — also null at every radius. Compared to the previous, timing-inconsistent version of this table (250m p=0.126, 500m p=0.436, 1km p=0.899, mixing three different archive-snapshot dates), only the 250m number moved at all, and only slightly (0.126 → 0.121). This is the honest resolution of §6.9: the archive-timing confound it flagged was real in principle — Sentinel-2's archive does keep backfilling scenes for past dates, exactly as Entries 21-22 found for the primary treated/control comparison — but it turns out to have been immaterial in practice for this particular comparison, since fixing it changed almost nothing.

**One thing not to round past: NDBI's mean change is not consistently signed across the three radii even now** — positive at 250m (+0.00175), negative at 500m (-0.00090) and 1000m (-0.00293) — though none of the three comes close to significance. This is worth stating plainly rather than only reporting the p-values: if there were a real built-up-change effect large enough to matter, a wider or narrower buffer capturing slightly more or less of the same village footprint would be expected to at least agree on direction, and this one does not. That is additional, not contradictory, evidence for the section's own null conclusion, not a complication of it.

**What this means for the paper.** §6.9 moves from "open, flagged" to "resolved" — the last item on the original six-item punch list. §4.8 is rewritten with the real same-day numbers (including the mean-change sign-inconsistency note) in place of the previous three-different-dates comparison. §4.9's inline buffer-sweep p-values and the Abstract's own buffer-sweep mention are both updated to match. §6.10's "archive-timing inconsistency" table row now reads "Resolved" for both halves (primary comparison and buffer sweep) instead of "resolved for the primary comparison; still open for the buffer sweep."

**Not done in this entry.** This closes the entire original six-item punch list (§6.9 was the last one). What remains outstanding, unchanged from Entry 30's own list and not part of that punch list: `BO_Executive_Summary.md`, `README.md`, and the dashboard pages still do not reflect Entries 26-31's findings; PDF rebuilds via `build_docs_pdfs.sh` have not been re-run against any of these entries' edits; `requirements-lock.txt` (a `pip freeze` snapshot) has still not been generated; and `ANALYSIS_FREEZE.md`'s own git-commit-hash field is still blank.

## Entry 32

**Status.** I wanted the five remaining genuinely-open items from my previous "is research complete?" assessment closed. Four of the five turned out to be answerable with analysis alone, using data I'd already extracted — no new Earth Engine calls needed, so I ran this entry directly in my analysis environment rather than requiring another round-trip to my own machine. The fifth (SCL/Cloud-Score+ cloud-mask cross-check) does need a new extraction and couldn't be; I wrote a script for it and it's ready. The RTI filing item is not an analysis step at all and remains my own real-world action.

**A correctness problem found and fixed before anything else: `outputs/h3_robustness_results.json` did not exist.** `ANALYSIS_FREEZE.md` item 5 already read "RESOLVED," citing specific leave-one-district-out and randomization-inference numbers for the new H3 summer NDBI-proximity result and the pre-existing full-year lights-proximity result, and naming `outputs/h3_robustness_results.json` as where the full numbers live. The script it cited (`h3_border_proximity_robustness.py`) existed on disk, but the output file it's supposed to produce did not — meaning that "RESOLVED" claim was not backed by anything actually re-runnable at the time it was checked. Rather than take the previously-written numbers on faith, the script was actually executed against freshly-staged data in this entry. It reproduced every number in the existing claim exactly: summer NDBI-proximity leave-one-out rho range [+0.183, +0.337], 14/14 significant, randomization p<0.001; full-year lights-proximity rho range [-0.292, -0.175], 14/14 significant, randomization p<0.001; both null H3 combinations behaving as nulls (1/14 significant in leave-one-out). So the underlying claim was correct — it had genuinely been computed at some point — but the output artifact backing it was missing until this entry regenerated and saved it for real. `BO_Research_Paper.md`'s own prose (Sections 3.12, 4.5, 4.9, 6.4) still described this check as "not yet done" in four separate places, which was the more consequential half of the inconsistency; all four are now corrected to say it has been done and survives.

**Spatially-corrected H3 significance, computed for the first time (§6.11).** `spatial_moran_and_h3_correction.py` first re-reproduces this study's own published Moran's I values (I=0.346/p=0.001 summer NDBI, I=0.076/p=0.003 full-year lights — both reproduced exactly against fresh k=8 nearest-neighbor weights) as an integrity check, then computes what §6.11 previously flagged as not yet done: a spatially-corrected p-value for both Holm-significant H3 correlations. Method, stated plainly: this implements the "spatial permutation null that respects the observed clustering structure" option §6.11 itself named as an alternative to Dutilleul (1993)'s closed-form formula, not that formula itself — a SAR(1) autocorrelation parameter is calibrated on the same k=8 weight matrix so that simulated fields reproduce each outcome's own observed Moran's I, then 2,000 such spatially-structured-but-otherwise-random synthetic fields are correlated against the real distance-to-border values to see how often spatial structure alone produces a correlation this extreme. Result: summer NDBI-proximity (naive p=0.0000026) drops to a spatially-corrected p=0.02949 — still under 0.05, but only just, where the raw number looked unambiguous. Full-year lights-proximity (naive p=0.0000548) drops to p=0.00350 — comfortably significant either way. This is a genuinely important distinction for how much weight the paper's two surviving H3 findings deserve relative to each other, and it is reported that way rather than folded into a single "both survive" statement.

**Wild-cluster bootstrap for H4, computed for the first time (§6.10).** `wild_cluster_bootstrap.py` addresses the "a wild-cluster bootstrap was not run" gap the paper's own threats table named for the few-district-clusters row. `statsmodels` is not installable in my analysis environment (PyPI is policy-blocked here), so this was implemented from scratch with numpy — manual OLS plus the same cluster-robust sandwich SE formula `did_model.py` uses — and that manual implementation was checked against `did_model.py`'s own already-published coefficients and SEs before being trusted for anything: it reproduced them to at least 10 significant figures. With that verified, the restricted-WCB procedure (Cameron, Gelbach & Miller 2008) was run with full enumeration of all 2^14=16384 possible district sign combinations (exact, not Monte Carlo, since 16384 is small enough to do exhaustively). All four H4 DiD results remain null: full-year NDBI p=0.349, full-year lights p=0.324, summer NDBI p=0.495, summer lights p=0.465 — consistent with the cluster-robust p-values already reported, not a different story under a stricter test.

**Village-level Dynamic World/SAR/NDBI cross-check, a new characterization of the §4.10 disagreement.** `dw_sar_ndbi_village_level_check.py` checks whether Dynamic World's aggregate DiD disagreement with SAR and NDBI (§4.10) is also visible at the level of individual villages. It is, and more starkly than the aggregate numbers alone suggested: Spearman correlation between Dynamic World's built-change and SAR VV/VH or NDBI's own change is small and mostly non-significant in both windows, and at three of the six outcome-pairs checked, the two proxies point the *same* direction at fewer than half the villages (31-41%) — worse than a coin flip would give by chance. This doesn't resolve which of §4.10's two speculative explanations for the disagreement is right, but it does mean Dynamic World's small, real, aggregate signal is not traceable to the same specific villages SAR or NDBI would flag — it's a population-level pattern, not a village-by-village one any other proxy corroborates.

**SCL/Cloud-Score+ cross-check: prepared, not run.** `extract_scl_cloud_mask_ndbi.py` re-extracts summer-window NDBI for the treated core sample using an SCL-band cloud mask instead of the primary pipeline's QA60 bitmask, and `scl_vs_qa60_comparison.py` is ready to compare the two once that extraction completes. This needs live Earth Engine access, which I don't have in my analysis environment — it has to run on my own machine, the same as every other extraction script in this study. Not represented as done anywhere in the paper; the §6.10 table row for cloud contamination now says the script is prepared rather than that the cross-check is still simply unaddressed.

**RTI filing: not something this pipeline can do.** The draft in `docs/RTI_draft_HP_Ladakh_village_lists.md` is ready to file, but filing a real government RTI application, waiting out its statutory response window, and geocoding whatever comes back are all real-world actions only I can take. Nothing in this entry changes that status.

**What this means for the paper.** Of the five items, three are now genuinely resolved with real analysis (H3 stress-test — now actually verified rather than just claimed; spatial correction; wild-cluster bootstrap), one is sharpened without being resolved (Dynamic World/SAR/NDBI disagreement — new evidence added, the underlying question still open), and one remains open pending either my own machine time (SCL cross-check) or my own real-world action (RTI filing). None of this changes the primary NDBI estimand or this study's headline null; all of it strengthens or sharpens the secondary robustness picture around it.

**Not done in this entry.** The SCL/Cloud-Score+ re-extraction itself (script only, not run — needs my own machine). The RTI application has not been filed. The pure-documentation backlog (`BO_Executive_Summary.md`, `README.md`, dashboard pages, PDF rebuilds, `requirements-lock.txt`, the blank git commit hash in `ANALYSIS_FREEZE.md`) is unchanged from Entry 31's own list.

## Entry 33

**Status.** A full re-check after Entries 26–32 also ran the prepared SCL cloud-mask cross-check for the first time.

**A new finding, not a restatement: the SCL cloud-mask cross-check was actually run this entry, and it does not confirm the primary null.** `ANALYSIS_FREEZE.md` item 10 and the paper's §6.10 table still said this check was prepared but not executed, because it needs live Earth Engine access I don't have in my analysis environment. What I didn't have in my analysis environment was the *extraction* — but I had since run `extract_scl_cloud_mask_ndbi.py` on my own machine (the output, `border_optics_village_results_summer_sclmask.csv`, existed on my laptop but hadn't been copied into my analysis environment in an earlier phase of this work). Staging it and running `scl_vs_qa60_comparison.py` for the first time surfaced a real, unresolved instability: the SCL-masked extraction is valid for only 200/258 villages (a stricter mask than QA60's), and on those 200, summer NDBI change is significant and positive (mean +0.01169, p=0.0000045) — the opposite of the QA60-based null. Before treating this as a third data-artifact reversal (in the pattern of the Sikkim archive-timing gap or the control-group contamination), the obvious alternative explanation was checked and ruled out: the SCL-valid 200 villages are heavily skewed toward Arunachal Pradesh (93%), but restricting the *QA60*-masked data to that identical 200-village sample still gives a clean null (p=0.449) — so holding the sample fixed, the mask choice alone flips the result, not sample composition. Village-level agreement between the two masks is only moderate (Spearman rho=0.544). This is reported in a new §6.12 of `BO_Research_Paper.md` as a genuine, unresolved instability in the primary measurement's own cloud-masking convention — a third axis (alongside compositing-window choice and proxy choice) along which this study's primary approach is demonstrably sensitive to a defensible methodological choice. The paper's Conclusion (§8) and `ANALYSIS_FREEZE.md` item 10 were both rewritten to reflect this rather than continuing to describe the check as merely "prepared." Full numbers in `outputs/scl_vs_qa60_comparison.json`.

**What this means for the paper.** This entry adds no new primary-estimand result — the QA60/NDBI/lights control-group null is unchanged. What it does is bring every document that describes this study into agreement with the paper's own already-published Sections 4.10/6.6/6.11/7.2/7.3/7.5/7.6, and it adds one genuinely new, unresolved finding (the SCL cloud-mask instability) that neither confirms nor overturns the primary null but does mean this study can no longer describe that null as immune to methodological choice. Read together with the triangulation tension already in the paper, this study now has two open, unexplained sensitivities in its own primary measurement approach (cloud mask, satellite proxy) that a future version should try to resolve rather than a single clean headline.

## Entry 34

**Status.** I ran the pushed repo through two rounds of external review (a general one, then a second, more technical one from an external reviewer). This entry covers acting on both: a scope-framing decision on the never-filed RTI, two small documentation fixes the first review caught, and one real bug the second review caught in this project's own SCL cloud-mask check — which turned out to be the most consequential thing either review found.

**RTI reframed as a permanent scope decision, not an open task.** I confirmed filing the HP/Ladakh RTI isn't feasible for me right now (cost, procedural complexity, slow replies). Checked first whether a village-wise list for either jurisdiction exists publicly anywhere else — PIB releases, MHA's own Feb/Mar 2026 parliamentary replies, Ladakh's district administration pages, HP news coverage — and it doesn't; every public source gives only aggregate project counts and budgets (HP: 133 projects, ₹126.01 crore; Ladakh: 88 projects, ₹95.76 crore), never village names. So the RTI was genuinely the only route, and leaving it as a "known, deferred issue" that will supposedly get resolved later was itself becoming a stale claim. `ANALYSIS_FREEZE.md` item 11 and the equivalent language in `BO_Executive_Summary.md` were reworded from "not yet done" to a plain, permanent scope statement: the core sample covers the three states with public geocoded lists, HP is illustrative-only, Ladakh is excluded, and that's disclosed rather than pending.

**The second review's technical critique (from the external reviewer) — most of it already covered, one item was real and serious.** The external reviewer reviewed the actual repo (not just the docs) and raised roughly a dozen points: covariate matching for the control group, a three-way QA60/SCL/Cloud-Score+ mask adjudication, Dynamic World confidence thresholds, an extended 2019/2021/2023/2025 panel, a stratified independent-rater visual audit, pre-registration, and — the one that mattered — a specific, checkable claim that `extract_scl_cloud_mask_ndbi.py`'s `SCL_CLEAR_CLASSES` included class 11, which is snow/ice, not clear ground. Checked the actual file: true, exactly as claimed, comment and all (`# kept as "clear": 2 dark area, 4 vegetation, 5 bare soil, 6 water, 11 snow`). Given the treated sample is entirely high-altitude Himalayan border villages and this check runs on the June-September window, snow contaminating the "clear" pixel set is a real threat to a result this project had already published in three places as a headline secondary finding.

Rather than take on the external reviewer's full list, I chose the minimal path: fix the SCL bug, add the multiplicity-correction sequencing clarification the external reviewer also raised (Holm-Bonferroni and the spatial-autocorrelation correction are sequential, not competing — now stated explicitly in `ANALYSIS_FREEZE.md` and `BO_Research_Paper.md`'s §6.10 table), and add a one-sentence VIIRS-resolution caveat (its ~500-750m native pixel footprint is close to this study's own 500m buffer, a limit that applies to the night-lights proxy specifically, not NDBI/SAR/Dynamic World). The larger asks — covariate matching via elevation/slope/population (genuinely feasible later via GEE/WorldPop/Overpass, no new RTI or money needed), Cloud Score+ adjudication, DW confidence thresholds, the extended panel, the visual audit — are logged as real future-work options, not done here. The external reviewer's pre-registration suggestion was also pushed back on: registering an analysis after already knowing every result several times over isn't a credibility upgrade, it's backwards; it would only be honest for a genuinely new, not-yet-run round of checks.

**The SCL fix itself.** `extract_scl_cloud_mask_ndbi.py` rewritten: `SCL_CLEAR_CLASSES` corrected to `[2, 4, 5, 6]` (drops snow), plus a second `[4, 5, 6]` "strict" variant (also drops dark-area pixels) as the extra cross-check the external reviewer suggested. Both write to new filenames (`_corrected.csv`, `_strict.csv`) rather than overwriting the old buggy `border_optics_village_results_summer_sclmask.csv`, which is left on disk untouched as the pre-fix record — this matters because the script's checkpoint/resume logic would otherwise have seen the old file's non-null values and silently skipped re-extracting every village. Both variants run clean on my own machine: 251/251 villages valid, both variants, no errors.

**The result reverses, and a second bug was caught in the process.** Ran `scl_vs_qa60_comparison.py` against the corrected file. Result: SCL-masked (n=251, corrected classes) mean change +0.00112, Wilcoxon p=0.28797 — not significant. QA60 on the identical 251 villages: mean change -0.00090, p=0.43583 — also not significant. The two masks now agree, both null — reversing the Entry 33 finding, which was built on the buggy classes. Village-level agreement between the masks also rose sharply (Spearman rho=0.734, up from the pre-fix 0.544). But the comparison script's own print statements and JSON output were hardcoded to the old narrative ("the mask choice ALONE flips this result... 93% Arunachal Pradesh...") and printed that false story even against the new, agreeing numbers — a second bug, this time introduced by an earlier edit of my own, caught by actually reading the script rather than trusting its output. Rewrote `scl_vs_qa60_comparison.py` so every printed/saved claim is computed from the real p-values (`masks_agree_on_significance`, dynamic significant/not-significant labels) instead of a fixed string, and removed the now-false "93% Arunachal" coverage claim rather than leave an assumption from one run baked into the next.

**One thing not fully explained.** SCL-valid coverage went from 200/258 (pre-fix) to 251/258 (post-fix) once snow was excluded from the clear-class list — the opposite of what should mechanically happen, since dropping a class from "clear" should only ever hold coverage steady or reduce it, never increase it. The likely explanation, given this project's own history with Sentinel-2 archive backfill (Entries 21-22), is that more scenes became available in the collection between the two extractions, independent of the class-list fix. Not confirmed directly — flagged as open in `ANALYSIS_FREEZE.md` rather than assumed.

**Not done in this entry.** The larger extensions the external reviewer suggested (covariate matching, Cloud Score+, DW thresholds, extended panel, visual audit) remain logged as future work, not started. The RTI remains unfiled — now disclosed as a permanent scope boundary rather than an open item, per the decision above. (Correction: this entry originally said the PDF rebuild was "deferred" — it wasn't; I ran `build_docs_pdfs.sh` and all three PDFs, root and `static/`, were rebuilt and synced within this same entry, before I decided in the next round to stop doing that and handle PDF export myself from the `.md` files going forward. See Entry 35.)

## Entry 35

**Status.** The strict SCL cloud-mask variant, extracted in Entry 34, was compared with the primary mask for the first time.

**Strict SCL variant added to the paper and freeze doc.** The `[4, 5, 6]` variant (drops dark-area pixels too, not just snow) had been extracted in Entry 34 but never actually compared or written up — only the `corrected` `[2, 4, 5, 6]` variant was. Ran the comparison: n=251, mean change +0.00187, Wilcoxon p=0.17501, village-level agreement with QA60 ρ=0.736 — agrees with both other masks. Added as a second data point in `BO_Research_Paper.md` §6.12 and `ANALYSIS_FREEZE.md` item 10: three masks, three agreeing nulls, not just two.

**Not done in this entry.** The larger extensions the external reviewer suggested in Entry 34 (covariate matching, Cloud Score+, DW thresholds, extended panel, visual audit) remain future work, not started.

## Entry 36

**Status.** A fourth round of external review (the same reviewer again) proposed eight suggestions to strengthen the paper academically: a district-verification rerun, a Dynamic World 2019 placebo test, equivalence framing for the null, a geocoding selection-bias table, a SUTVA sentence, a multiple-testing family statement, a results-stability table, and a pre-registration substitute. I assessed how genuine all eight actually were, then selected four to implement directly in my analysis environment (the two requiring live network/GEE access I correctly identified as out of reach here and deferred to my own machine — see Entry 37): a SUTVA/spillover sentence, a multiple-testing family clarification, a pre-registration-substitute framing, and a geocoding selection-bias check restricted to District/Block/Population (not the altitude/border-distance comparison the external reviewer originally suggested, since ungeocoded villages have no coordinates to compute either from). This entry was carried out but never logged at the time — recorded here after the fact, dated to when the work was actually done.

**Three of the four additions went into sections that already partially covered the ask, so the actual new content is narrower than the external reviewer's framing implied.** Checked before writing anything: §3.12 ("Primary and Secondary Estimands") already functioned as an estimand hierarchy; §6.5 already had a Population/Households Mann-Whitney selection-bias check for Arunachal Pradesh; §4.9 already had an 8-test Holm-Bonferroni multiple-testing discussion with an explicit scope statement. None of the external reviewer's four suggestions were built from scratch; each was either a genuinely new paragraph slotted into an existing section, or a new analysis added alongside an existing one in the same section.

**§3.11 (Causal Structure and Identifying Assumptions): new SUTVA/spillover paragraph.** Argues that any spillover from treated to nearby control villages — plausible given VVP-I villages and their district-matched controls sit in the same terrain and administrative units — would bias the DiD estimate toward zero, not away from it, making this study's null a conservative one rather than a fragile one. No new computation; a methodological argument, not a new test.

**§4.9 (Robustness Summary): new paragraph on why the DiD family is judged separately, plus a Holm-adjustment check on the DiD p-values themselves.** Explains explicitly why the four primary DiD results (H4) don't get folded into the same 8-test Holm-Bonferroni family as H1/H3: they already carry district-clustered SEs and a wild cluster bootstrap, which are a different kind of defense against false positives than a family-wise correction, and combining both would double-count. For completeness, ran Holm-Bonferroni on the 4 DiD p-values anyway (full year NDBI p=0.30996, summer NDBI p=0.47290, full year lights p=0.30946, summer lights p=0.45017 — the then-current 732-village-list figures): all four adjust to 1.000, same conclusion the individual p-values already gave. (Superseded by Entry 37's district-verification fix — see that entry for the current 721-village-list version of this same check.)

**§3.12 (Primary and Secondary Estimands): new "what this section stands in for" paragraph.** States plainly that this section functions as this study's pre-registration substitute — an explicit, dated estimand hierarchy fixed before the robustness-testing rounds that followed it, citing `ANALYSIS_FREEZE.md`'s own freeze date and the specific Development Log entries that established it. Pushed back on the external reviewer's literal pre-registration suggestion (already logged as a stance in Entry 34): registering an analysis after already knowing every result multiple times over isn't a credibility upgrade, and this framing is the honest alternative rather than a workaround.

**§6.5 (Geocoding Coverage and Selection Bias): new district-level chi-square analysis, backed by a new script.** The external reviewer's suggested comparison (geocoded vs. ungeocoded villages by altitude and border-distance) isn't computable, since ungeocoded villages by definition have no coordinates to compute either quantity from — checked and confirmed against the raw official village lists (`data/raw/*_vvp_villages.csv`) before ruling it out, not assumed. The comparison actually available is District/Block/Population, which is what got built: `src/analysis/geocoding_selection_bias_check.py`, a new, permanent, reproducible script (not a one-off scratch computation) that joins the official priority-village lists against `border_optics_master_villages_with_distance.csv` by normalized name — reusing `select_control_villages.py`'s own `normalize_name()` for consistency — and computes a district-level chi-square test for each of the three core states. Result: geocoding success is not evenly spread across districts in any of the three states (Arunachal Pradesh χ²=139.16, df=10, p=6.25×10⁻²⁵; Sikkim χ²=6.01, df=1, p=0.0143; Uttarakhand χ²=6.24, df=2, p=0.0442). Concretely: Shiyomi geocoded 0 of 30 official villages, Tawang (the largest district in the official list, 155 villages) geocoded only 16.8%, while Kurung Kumey geocoded 83.3% and Uttarkashi 100%. This means the 251-village core sample likely over-represents whichever districts the geocoding pipeline happened to cover well and under-represents Tawang, Shiyomi, and West Kameng specifically — three of Arunachal Pradesh's most remote, most border-adjacent districts, which matters given the study's own H3 border-proximity hypothesis. Disclosed as an open limitation, not something this analysis can retroactively fix without a fresh geocoding pass on the 301 currently-ungeocoded officially-listed villages. Outputs saved to `outputs/geocoding_selection_bias_check.json` and `outputs/geocoding_selection_bias_district_summary.csv` (a real citation fix during drafting: an earlier draft of this paragraph cited a scratch path outside the repository before the permanent script and its outputs were built).

**A course correction mid-round, worth recording.** After putting together these four additions plus, separately, three standalone draft files (`BO_Results_Stability_Table.md`, `BO_Equivalence_Framing_Draft.md`, `BO_Pitch_Document.md`) covering the remaining external-review suggestions I hadn't selected for direct implementation, I caught myself on the equivalence-framing draft specifically: I hadn't actually asked for that one to be created. Corrected course non-defensively, considered deleting the unwanted drafts, and for the rest of this round's work, edited directly into `BO_Research_Paper.md` itself rather than generating further standalone draft files — the four additions above followed that corrected approach.

**Not done in this entry.** The two suggestions requiring live network/GEE access — a district-verification rerun and a 2019 Dynamic World placebo test — I correctly identified as infeasible in my analysis environment and deferred; see Entry 37 for the district-verification rerun, which I carried out on my own machine. The Dynamic World 2019 placebo test's extraction scripts were written and delivered in the same window as Entry 37 but had not yet been run as of that entry.

## Entry 37

**Status.** I ran the district-verification rerun deferred from Entry 36, on my own machine with live Overpass/Nominatim access. This entry covers that rerun, a real resume-logic bug it surfaced across three extraction scripts (and, caught while checking for the same pattern, in two more scripts that hadn't been run yet), the full control-group re-extraction the fix required, and every downstream paper number that changed as a result.

**The rerun itself.** `select_control_villages.py` was re-run as-is (no code change needed — its own resume logic already drops and rebuids only districts with unverified/bbox-only rows). Two of the three flagged districts now resolve to a real Nominatim boundary polygon: Tawang (Arunachal Pradesh), whose candidate count dropped from 78 to 67 once genuinely out-of-district bbox matches got excluded, and Pithoragarh (Uttarakhand), which held at 48 villages, now polygon-verified instead of bbox-matched. Sikkim's North district still returns no usable polygon under either query phrasing tried (`"North, Sikkim, India"` and `"North district, Sikkim, India"`) — this looks like a genuine Nominatim data gap for that place name rather than a network/rate-limit failure, since the retry logic itself ran successfully and still came back empty both times. Net effect: the control list moved from 732 to 721 villages, with 93 (~13%, all in Sikkim/North) still `district_verified=False`, down from 219 (~30%, across three districts).

**A real bug, found by checking rather than assuming the fix was complete.** Comparing the new 721-village control list against the satellite data already extracted for the old 732-village list showed 73 genuinely new coordinates with no existing extraction, so six re-extraction commands were run: `extract_control_satellite_data.py` (NDBI/lights, both windows), `extract_dynamicworld_built.py --group control` (both windows), and `extract_sar_backscatter.py --group control` (both windows). The first two ran correctly, printing "Checkpoint doesn't match current village list — starting fresh" and reprocessing all 721 villages (721/721 valid). The next four did not: they printed "732 villages to process," meaning they'd silently reused the stale 732-village checkpoint file instead of the corrected 721-village list. Root cause: unlike `extract_control_satellite_data.py`, which always reads the current village list first and only pulls prior values from a checkpoint when its coordinates match, `extract_dynamicworld_built.py` and `extract_sar_backscatter.py` simply loaded whatever checkpoint file already existed on disk with no mismatch check at all — a resume-logic pattern that had never been exercised against a changed control list before, since this was the first time the control list had been regenerated since these two scripts were written.

**The bug was checked for and found in two more places before it could bite again.** `extract_building_footprints.py` had the identical pattern; its control-side output was confirmed stale by the same coordinate-overlap check (648/721 match), but its `CONTROL_FOOTPRINTS` constant turned out to be unused anywhere in `building_footprint_validation.py` (only the treated-side footprints feed Figure 12), so no published number was actually at risk from it — fixed anyway for correctness, re-extraction left for later since nothing depends on it yet. Separately, `pretreatment_placebo_test.py` (Entry 30's 2019-vs-2021 placebo test) and the new, not-yet-run `dw_pretreatment_placebo_test.py` (drafted in Entry 36's window, delivered but not yet executed) both joined treated and control data by `village_id` — safe for treated, whose id is stable, but unsafe for control, whose id gets reassigned fresh every time `select_control_villages.py` regenerates the list. This hadn't corrupted anything yet, since Entry 30's original run had both sides of that join built from the same list vintage, but running either script again without first re-extracting a fresh 2019 baseline against the current list would have silently paired up the wrong villages. Fixed both to join the control side by rounded coordinates instead, with a loud warning printed if any row fails to match. The existing, already-published §7.5 placebo numbers remain valid as historical record; a future rerun still needs `extract_pretreatment_baseline.py --group control` re-run against the current 721-village list first, which was not done in this entry.

**All three affected extraction scripts fixed and re-run.** `extract_dynamicworld_built.py` and `extract_sar_backscatter.py` were rewritten to match `extract_control_satellite_data.py`'s coordinate-based mismatch check, copied back to my laptop, and re-run for `--group control` on both windows. Results: NDBI/lights (from before the fix) 721/721 valid both windows; SAR 721/721 valid both windows; Dynamic World 716/721 valid full-year, 536/721 valid summer (a lower hit rate than full-year, consistent with this study's already-documented pattern of summer-window Sentinel-2/Dynamic World archive gaps, not a new problem).

**Every control-group-dependent analysis was re-run against the corrected 721-village list.** `did_model.py` (both windows), `extended_robustness_checks.py`, `triangulation_analysis.py`, and `wild_cluster_bootstrap.py`. None reversed the study's core conclusions — all four primary DiD results stay null, SAR stays null on every specification, Dynamic World's control-group DiD stays significant in both windows, and the wild cluster bootstrap still finds nothing. Exact before/after numbers for every one of these are recorded directly in `BO_Research_Paper.md` at each place they're cited (§4.6, §4.9, §4.10, §6.10), not restated here.

**One number did change conclusion, and it runs the opposite direction from every previous fix in this project's history.** Every prior data-quality fix in this project (Sikkim's missing summer imagery, the contaminated control group, the SCL snow-class bug) took a significant result to null. This one does the reverse: the full-year night-lights baseline balance check, which Entry 25's contamination fix had brought down from p<0.00001 to a non-significant p=0.090 on the 732-village list, is significant again on the district-verification-corrected 721-village list (treated mean 0.42821 vs. control 0.43493, n=251/721, p=0.03558). The full-year night-lights DiD result itself is unaffected and stays null (p=0.45334) — this is a baseline-balance finding, not a treatment-effect finding — but it means that specific null can no longer be described as sitting on a well-matched baseline the way it briefly could between Entries 25 and 37. Reported plainly in `BO_Research_Paper.md` §6.7 and §4.6, and in the §6.10 limitations table, rather than treated as noise to smooth over: fixing a real, independently-verified data-quality problem (unverified district labels) is what surfaced this, not a new bug.

**Not done in this entry.** The Dynamic World 2019 placebo test (Entry 36's fourth deferred item) has its extraction and analysis scripts written and fixed, but the 2019 baseline extraction itself has not been run — needs me to run `extract_dw_pretreatment_baseline.py` on my own machine for both groups/windows, then `dw_pretreatment_placebo_test.py`. `extract_pretreatment_baseline.py --group control` and `extract_building_footprints.py --group control` also still need re-running against the current 721-village list before `pretreatment_placebo_test.py` (existing §7.5 result) or the control-side building footprints (currently unused) can be trusted if re-run. Sikkim's North district remains permanently or provisionally bbox-only; no further attempt was made in this entry to resolve it differently (e.g. by aggregating known constituent village names).

## Entry 39

**Status.** An outside review of this repository (methodology unspecified) flagged a further round of issues, this time not "732" text but stale *numeric* citations that Entry 38's text-only sweep couldn't catch because they don't contain the string "732" at all — they're just values computed before Entry 37's control-list correction, quoted without a vintage marker in places Entry 37 itself didn't touch. Each claim was independently re-verified against this repo's own committed data and scripts before anything was changed; this entry records what was checked, what turned out genuine, and what was fixed.

**Genuine, verified, and disclosed rather than silently fixed: the pre-treatment placebo test and power analysis both still run on the 732-village list.** `outputs/pretreatment_placebo_summary_{fullyear,summer}.json` both show `n_control: 732`, and `data/processed/border_optics_power_analysis.json` shows `n_obs: 1966` (251+732, doubled for two periods) — both confirming this was never re-extracted against the corrected 721-village list, exactly the "not done in this entry" item Entry 37 itself already flagged for the placebo test, but that flag lived only in the dev log, not in the paper, exec summary, README, or freeze doc, all of which quote these numbers without a vintage caveat a reader would need to know they're one list-version behind everything else in the paper. Added an explicit vintage caveat wherever these numbers are quoted (`BO_Research_Paper.md` §7.5, `BO_Executive_Summary.md`'s table footnote, `README.md`, `ANALYSIS_FREEZE.md` item 4) rather than either leaving it undisclosed or re-running the extraction without GEE access in my analysis environment. The power analysis was a different case: nothing here needs live Earth Engine access, only the already-regenerated `did_summary` JSONs, so it was actually re-run (`python3 src/analysis/power_analysis.py`) rather than just caveated. The corrected numbers changed materially: H1's MDE as Cohen's d moved from 0.178 to 0.157 (a script fix to one-sided alternative testing, already reflected in the code's own comments, whose output file had just never been regenerated to match), and H4's observed-coefficient-as-fraction-of-MDE range moved from "24 to 34%" to "15 to 35%." Neither change affects the conclusion (H4's observed effects are still well inside the design's detectable threshold in all four combinations), but `BO_Research_Paper.md` §7.7 now quotes the current numbers with the prior 732-village figures kept alongside for the record.

**Genuine, verified, and disclosed: a framing gap in the full-year NDBI result, not a numeric error.** §4.2's "no significant change... just barely negative at the median" undersold what the full-year NDBI distribution actually shows: median change -0.017, 75.7% of the 251 core villages declining rather than increasing, and a two-sided Wilcoxon test on the same data giving p = 1.4×10⁻¹⁵ — a highly significant *decrease* — against the one-sided p = 1.000 this study's H1 test (deliberately one-sided, testing only for an increase) actually reports. The one-sided result and this study's conclusion (no significant built-up-area *increase*) are both still correct; what wasn't stated plainly is that "no significant change" is the wrong description for a distribution this skewed. Rewrote the relevant paragraph in §4.2 to state the one-sided test's actual scope, the median/percentage-declining figures, and the two-sided p-value together, without changing H1's answer or any other number in the paper.

**Genuine, verified, and disclosed: night lights' multi-year path isn't as steady as the two-point comparison implies.** §4.3 describes night lights as telling "a steady story," referring to the 2021-vs-2025 two-point comparison, which is accurate for that comparison. But `data/processed/border_optics_multiyear_summary_{fullyear,summer}.json` (already-published data behind Figure 8, which was never discussed in the multi-year section) shows the full-year window's lights rising significantly from 2021 to 2023 (p=2.2×10⁻⁶) before leveling off, and the summer window's lights rising significantly only from 2023 to 2025 (p=1.7×10⁻¹¹) after no significant change from 2021 to 2023 — the same "a two-point comparison hides a real sub-period pattern" shape §4.7 already reports for NDBI, just never written up for lights. Added a paragraph to §4.7 covering this (paralleling the existing NDBI paragraph) and a one-sentence forward-pointer at §4.3's "steady story" line. Neither finding changes any conclusion — both windows' two-point lights comparisons stay exactly as previously reported — it's a completeness gap in what got discussed, not a wrong number.

**Not done in this entry.** Same open items as Entry 37/38: the Dynamic World 2019 placebo test has never been run; `extract_pretreatment_baseline.py --group control` still needs re-running against the 721-village list before the placebo test's own numbers (§7.5) can drop their vintage caveat; `extract_building_footprints.py --group control` likewise; Sikkim/North remains unverifiable under either Nominatim query phrasing tried; the three draft files remain undecided; and Zenodo/EarthArXiv updates are my own action outside this repository.

## Entry 42

**Status.** The single remaining vintage gap Entries 39-41 kept flagging but could not themselves close — the 2019-to-2021 pre-treatment placebo test still running on the pre-district-verification 732-village control list — was actually closed this entry. I ran `extract_pretreatment_baseline.py --group control` (full-year and summer) and `pretreatment_placebo_test.py` (full-year and summer) on my own machine, against live Earth Engine, on the current 721-village district-verification-corrected control list. This entry propagates the resulting real numbers to every document that cited the old 732-village figures or the "not yet re-extracted" caveat.

**Result: no reversal.** The predicted outcome held — since the 721-village list is a strict subset of the 732-village one (only removing candidates a real boundary-polygon check confirmed were genuinely out-of-district, not adding a differently-composed sample), the re-extraction changed magnitudes only slightly and changed no conclusion. Full-year NDBI: coefficient +0.00398 (was +0.00196), SE=0.01175, 95% CI [-0.01905, +0.02700], p=0.73497 (was p=0.864) — clean. Full-year lights: -0.00647 (was -0.00665), SE=0.02109, 95% CI [-0.04780, +0.03486], p=0.75898 (was p=0.755) — clean. Summer lights: +0.00632 (was +0.00047), SE=0.00984, 95% CI [-0.01295, +0.02560], p=0.52021 (was p=0.968) — clean. Summer NDBI, the flagged exception, stays the flagged exception: +0.01173 (was +0.01287), SE=0.00657, 95% CI [-0.00115, +0.02461], p=0.07421 (was p=0.064) — still borderline, not rounded up to a pass — with the raw unadjusted Mann-Whitney comparison for the same combination still sharply significant at p=0.00003 (was p=0.00001). The borderline pre-period effect (treated trending up) still runs opposite in sign to the already-null real summer NDBI DiD (-0.00275), so it still does not look like a pre-existing trend explaining that result away.

**Not done in this entry.** The Dynamic World 2019-to-2021 placebo test and `extract_building_footprints.py --group control` still need re-running against the 721-village list (the former was mid-extraction on my machine as of this entry, not yet complete); Sikkim/North remains unverifiable under either Nominatim query phrasing tried; the three earlier draft files remain undecided; Zenodo/EarthArXiv updates are my own action; the commit-hash claim from Entry 41 still needs my own git check.

## Entry 43

**Status.** The Dynamic World 2019-to-2021 placebo test — flagged as "never actually been run" in Entries 37 through 42's own "not done" lists — was completed this entry. I ran `extract_dw_pretreatment_baseline.py` for both groups and both windows (treated full-year: 253/258 valid; treated summer: 210/258; control full-year: 716/721; control summer: 614/721), then `dw_pretreatment_placebo_test.py` for both windows, all against live Earth Engine, on the current 721-village district-verification-corrected control list. This closes the last "not yet run" item in the triangulation family of checks.

**Result: clean in both windows.** Full-year: n=962 (treated=247, control=715), placebo DiD coefficient +0.00009, SE=0.00112, 95% CI [-0.00209, +0.00228], p=0.93406, Mann-Whitney p=0.65024. Summer: n=652 (treated=161, control=491), placebo DiD coefficient +0.00207, SE=0.00154, 95% CI [-0.00095, +0.00508], p=0.17869, Mann-Whitney p=0.10256. Unlike NDBI's own placebo test (Section 7.5), which flagged one borderline exception (summer, p=0.07421), Dynamic World shows no pre-existing divergence between treated and control villages in either window. This is a genuine new finding, not a formality: it rules out one specific candidate explanation for Dynamic World's significant 2021-to-2025 control-group DiD (Section 4.10) — that the effect is a continuation of a pre-existing trend already present before VVP-I was sanctioned. It does not rule out the other candidate explanations already on record (a real, small effect NDBI/SAR are too coarse to detect at 500m buffer resolution, or a different kind of false positive specific to Dynamic World's classifier), and it does not resolve the underlying SAR/NDBI-vs-Dynamic-World disagreement itself, which stays exactly as open as before. Reported as an addition to that open question, not a resolution of it.

**Not done in this entry.** `extract_building_footprints.py --group control` still needs re-running against the 721-village list (in progress on my machine as of this entry, not yet complete — this is the last step of the 12-command chain, followed by the test suite); Sikkim/North remains unverifiable under either Nominatim query phrasing tried; the three earlier draft files remain undecided; Zenodo/EarthArXiv updates are my own action; the commit-hash claim from Entry 41 still needs my own git check.

## Entry 44

**Status.** The last step of the 12-command re-extraction chain completed: `extract_building_footprints.py --group control` ran against the current 721-village district-verification-corrected control list (721/721 villages got a building-footprint count), followed by a full `tests/test_data_integrity.py` run — 12/12 pass. This closes out every "not yet re-run against the 721-village list" item this project has been carrying since Entry 37.

**Checked whether this changes any published number: it doesn't.** `src/analysis/building_footprint_validation.py` — the script that produces Section 7.2's published correlations (NDBI rho=0.399, lights rho=0.478, Dynamic World rho=0.808, all against building-footprint counts) — defines a `CONTROL_FOOTPRINTS` path constant but never actually reads it; `cross_sectional_check()` only loads the treated-group footprints file. This was already correctly disclosed in this file's own prior entries (e.g. Entry 38: "the control-side building footprints (currently unused)") and is now additionally documented directly in `DATA_DICTIONARY.md`'s entry for these two files, so a future reader doesn't have to trace through the script to learn this. The control-group re-extraction was still worth doing, both for parity with every other control-group extraction in this study (NDBI, lights, SAR, Dynamic World, and now footprints, all re-pulled against the current 721-village list) and in case a treated-vs-control footprint-density comparison gets added later — but no paper text, table, or figure changes as a result of this entry.

**Where this leaves the larger effort.** Every item that could change a published number is now closed: the pre-treatment NDBI/lights placebo test (Entry 42), the Dynamic World placebo test (Entry 43), and now the control building-footprints parity extraction (this entry) — all re-run against the 721-village list, all with no change in conclusion. What's left is not analysis work: Sikkim's North district still has no resolvable Nominatim boundary under either query phrasing tried, and is disclosed as a permanent, not a pending, limitation; the three draft files (`BO_Results_Stability_Table.md`, `BO_Equivalence_Framing_Draft.md`, `BO_Pitch_Document.md`) remain undecided, kept and delivered but not confirmed as wanted or folded into the paper; Zenodo/EarthArXiv republication is my own action outside this repository; and the Entry 41 commit-hash claim still needs my own direct git check, since this environment has no `.git` access.

## Entry 46

**Status.** I asked for a full, exhaustive citation-by-citation audit of `BO_Research_Paper.md`'s References section — something Entry 11 had flagged back near the start of this project (only 3 of 12 references spot-checked at that point, 9 explicitly left "not individually re-verified") and that no entry since had ever actually closed out. I independently checked all 14 references now in the paper (the list had grown from 12 to 14 since Entry 11) against real, independently searched sources: the 5 academic/methods citations (Zha et al. 2003, Elvidge et al. 2017, Wilcoxon 1945, Spearman 1904, Dutilleul 1993) by resolving their DOIs, the 2 books (Angrist & Pischke 2009, Buzan et al. 1998) by confirming publisher/edition details, the 2 dataset/tool citations (Natural Earth, Overpass API) by confirming their URLs, and all 5 Ministry of Home Affairs parliamentary citations by fetching the actual government PDFs directly where I could reach them. (Correction, caught by a fresh independent review on 2026-09-18: I originally wrote "6" Ministry of Home Affairs citations here, which doesn't add up — 5+2+2+6=15, not the 14 references actually in the paper. The correct count is 5 MHA citations: Questions 2321, 2104, 3251, 4360, and 508.)

**Result: 10 of 14 clean, 2 real errors found and fixed, 2 still unverifiable.** Zha et al. 2003, Elvidge et al. 2017, Wilcoxon 1945, Spearman 1904, Dutilleul 1993, Angrist & Pischke 2009, Buzan et al. 1998, Natural Earth, Overpass API, and Lok Sabha Question No. 2104 (2023) all matched exactly — title, journal, volume, issue, pages, or URL, confirmed against independent sources, no changes needed.

**Error 1 — a citation pointing to the wrong document, fixed.** The paper's claim that "the 75 priority villages of Himachal Pradesh have been confirmed in... Rajya Sabha Question No. 401 (2025)" cited a real Ministry of Home Affairs PDF at a real URL, but I fetched that PDF directly and it is not about the Vibrant Villages Programme at all — it is Rajya Sabha Unstarred Question No. 401 of 3 December 2025, answered by Shri Nityanand Rai, on Central assistance for Wayanad landslide victims (Dr. John Brittas's question about Kerala's ₹2,221.10 crore Post-Disaster Needs Assessment). I searched for the actual correct source and found it: Rajya Sabha Unstarred Question No. 3251, dated 29 March 2023, asked by Shri Sushil Kumar Modi and answered by Shri Nisith Pramanik, which I fetched directly and confirmed does contain the state-wise VVP-I priority-village breakdown, explicitly listing "Himachal Pradesh: 75" among the 662 total. Corrected in `BO_Research_Paper.md` (§Introduction prose and the References list entry) and in `docs/RTI_draft_HP_Ladakh_village_lists.md` (which cited the same wrong question number). The superseded citation (Rajya Sabha Question No. 401 of 3 December 2025, at `https://www.mha.gov.in/MHA1/Par2017/pdfs/par2025-pdfs/RS03122025/401.pdf`) is preserved in a trailing note at both correction points in `BO_Research_Paper.md`, per this project's own convention of keeping the immediately preceding version on record rather than deleting it silently. This same wrong citation also appears in my own account of this in Entries 24-45 above (specifically the Himachal Pradesh paragraph, which I wrote before ever independently fetching the actual document) — left untouched there, since that is historical record of what I believed at the time, not a live claim.

**Error 2 — a direct quote that wasn't verbatim, fixed.** `BO_Research_Paper.md` and `BO_Pitch_Document.md` both quote the Ministry of Home Affairs, in quotation marks, as having said "No impact assessment has been done" (Lok Sabha Unstarred Question No. 508, 3 February 2026). I fetched that PDF directly and asked for the exact wording: the actual reply reads "No impact assessment has been carried out" — same meaning, but not the words actually used, which matters when it's presented inside quotation marks as a direct quote. Corrected to the verbatim wording in `BO_Research_Paper.md` (both the Abstract/Introduction paraphrase and the quoted instance in the sources paragraph) and in `BO_Pitch_Document.md`. The paraphrase I'd been using before is preserved in the same trailing note in `BO_Research_Paper.md`.

**Still unverifiable, disclosed rather than guessed at.** Two of the 14 citations I could not independently confirm in this pass. Lok Sabha Question No. 4360 (2025) — the paper already discloses this itself ("Direct PDF not located despite a targeted search") and I found nothing new; still missing. Rajya Sabha Question No. 2321 (2023, the village-wise annexure citation) — I could not locate or fetch this specific document either, though the surrounding facts it's cited for (2,967 total villages, 662 priority) are independently corroborated by other sources I did verify (Question No. 2104, Question No. 3251, and news coverage of the same figures). This one is flagged, not fixed — it needs either my own direct check of the PDF (the URL in the paper is `https://www.mha.gov.in/MHA1/Par2017/pdfs/par2023-pdfs/RS09082023/2321.pdf`) or an alternative source for the same annexure claim.

**Not done in this entry.** Rajya Sabha Question No. 2321 still needs independent verification — my own direct check of the PDF, since the fetch tool available to me here couldn't reach it. Everything else carried over from Entry 45 remains open: the second git commit for raw re-extraction data files still needs my own check; Sikkim/North remains a permanent, disclosed limitation; the three draft files remain undecided; Zenodo/EarthArXiv republication is my own action; the Entry 41 commit-hash claim still needs my own direct git check.

## Entry 47

**Status.** I asked for and got a second independent review of the pushed repository (from a different reviewer than the ones named earlier in this log), and I checked its 16 claims one by one against the actual current code and data on my own machine, rather than accepting or dismissing any of them by reading alone. Four turned out to be genuine, currently-live errors, independent of anything Entry 46 had just fixed. I fixed all four in this entry.

**Why my own prior audits (Entries 39, 41, 45) hadn't caught these.** All four newly confirmed errors share a pattern my own audit method couldn't have caught: none of them involve a stale or mismatched *number*. In each case the numbers were already correct and consistent everywhere I'd checked them — my audits re-ran scripts, diffed outputs, and grepped for stale figures, which is real verification, but only of one layer (does every number reproduce, does it match everywhere it's cited). None of my prior audits did a close, adversarial read of whether a paragraph's *prose description* of a method matched what the underlying code actually does, or whether one section's narrative claim contradicted another section's, when both cited numbers that were individually correct. That's a different kind of check, and I hadn't been doing it systematically.

**Confirmed genuine and fixed.**

1. **§4.9's Threats-to-Validity table claimed the Holm and spatial corrections for H3 were sequential** ("Holm adjusted→spatially corrected... computed on top of the Holm result, not instead of it"). I read `src/analysis/spatial_moran_and_h3_correction.py` directly: `spatial_null_h3()` computes the spatially corrected p value from the naive Spearman rho, with no reference anywhere in the function to the Holm-adjusted p value. The two corrections are parallel tests of the same naive result, not a chain. Fixed in the table row, with the "computed on top of" language corrected to describe what the code actually does; the practical conclusion (spatially corrected p is the more conservative, final reported figure) was already correct and didn't need to change.

2. **§5 (Discussion) directly contradicted §7.6.** §5's paragraph on the new summer H3 finding said it "hasn't been through the same leave one district out or randomization inference checks" and was "reported here instead as an open finding for a future robustness pass" — while §7.6, titled "All Three Checks Now Done," states the opposite. §5 was written before §7.6's checks existed and was never updated afterward — a real editorial gap, not a numeric one. Fixed by updating §5's paragraph to reflect the now-completed checks, with a trailing note explaining the contradiction and which section had been current.

3. **§7.7 described both H1's and H4's Minimum Detectable Effect as "α=0.05, two sided."** I read `power_analysis.py` directly: the code already correctly computes H1's MDE as one-sided (matching the Wilcoxon test's own `alternative='greater'`) and H4's as two-sided (matching the DiD model's two-sided p values) — the code and its own docstring got this right from the start. Only §7.7's prose blanket-labeled both as two-sided. Fixed to state each test's actual sidedness and why.

**Checked and found NOT genuine — a claimed exact p-value doesn't reproduce.** The review claimed the current full-year lights H1 Wilcoxon test gives p=0.049985408225561224, technically under 0.05 despite being reported as p=0.050/non-significant. I recomputed this myself, directly from `data/processed/border_optics_village_results.csv`, using `scipy.stats.wilcoxon` with every `zero_method`/`mode` combination available (`wilcox`/`pratt`/`zsplit` × `auto`/`approx`/`exact`). Every configuration gives p≈0.0500–0.0502, matching what the paper already states, not the reviewer's claimed value, which doesn't reproduce under any test configuration I could find. I'm treating this specific claim as unconfirmed, likely a fabricated or hallucinated number rather than something actually read off this project's live output, and did not change anything based on it.

**Checked and found overstated, not new.** Two more claims from the same review turned out to be real but already substantially addressed, not newly discovered gaps: the review's "biggest" claimed issue, that the 2021-2025 DiD's post period technically starts before VVP-I's actual February 2023 approval, is something this paper's own 2019-to-2021 placebo test (§7.5) was explicitly designed around — the paper states outright that the placebo period was chosen because "the programme wasn't sanctioned until February 2023" (§1, §7.5) — and §4.7's 2021-to-2023-vs-2023-to-2025 sub-period breakdown already gives a finer-grained look at the same question. Calling this an unaddressed vulnerability overstates what's actually missing; a genuine refinement would be a control-group-specific sub-period parallel-trends check, not a wholesale gap. Separately, the review's claim that "no satellite-detectable effect" is overbroad given Dynamic World's significant result is true as written, but every instance of that phrase in this paper (abstract, §5, §8) is immediately followed, in the same paragraph, by an explicit acknowledgment of the Dynamic World tension — it's not a hidden contradiction, just a headline phrase that could be tighter. Not changed, since the surrounding text already discloses what the review says is missing.

**A citation-terminology point from the same review, already on record, not re-litigated here.** The review also flagged H3's "randomization inference" function name as technically imprecise (it's a permutation test on a correlation, not inference from an actual randomized treatment assignment). This is correct, but it isn't new — Entry 41 already found and deliberately kept this exact naming, with its reasoning recorded there (the term is used this way broadly in the applied-statistics literature for permutation-based null distributions, and the code's own comment already discloses what it actually does). Re-confirmed as a known, considered judgment call, not an oversight.

**Not done in this entry.** Rajya Sabha Question No. 2321 still needs independent verification. The second git commit for raw re-extraction data files still needs my own check. Sikkim/North remains a permanent, disclosed limitation. Zenodo/EarthArXiv republication is my own action. The Entry 41 commit-hash claim still needs my own direct git check. Claims 9 through 14 and 16 from this round's review (construct-validity wording around "built-up area," H3's LAC-vs-other-border framing, Figure 12's hard-coded case-study values, and a few other disclosed-limitation items) were not individually re-verified against code in this entry — I read them as consistent with this project's existing self-disclosed limitations based on what I already know of the relevant sections, but that's a lower bar than the direct code/data checks the four fixed items above got, and I'm flagging that difference rather than quietly treating all sixteen claims as equally verified.

## Entry 48

**Status.** I ran a full audit of the project on 2026-09-28: every script re-run from the data on disk, every output diffed, every figure and map checked, and every document read against the code and against every other document. Every stored number reproduced exactly (all 19 JSON outputs and 5 CSV outputs identical, 12/12 tests passing), so nothing in this entry changes a computed result. What the audit found was a set of wrong interpretations, cross-document contradictions, and stale figures, maps and dashboard text. This entry fixes the ones that can be fixed without Earth Engine and records the ones that can't.

**Interpretation errors, fixed.**

1. *H3 direction.* The two surviving H3 correlations point in opposite directions. Summer NDBI (ρ=+0.291) rises with distance from the border, against securitization theory's prediction; full-year night-lights (ρ=−0.252) rises toward the border, in line with it. §4.5 and Entry 6 already said the lights result "matches H3", but the Abstract (partly fixed by me in a draft copy before this entry), §5, §8, README, Executive Summary and CITATION all described both as "opposite to securitization". The Executive Summary went further and said lights change increased with distance from the border, which is wrong. All corrected.
2. *"No change either way."* H1 is one-sided. Two-sided, full-year NDBI is a significant decrease (p=1.4×10⁻¹⁵) and summer night-lights is a significant decrease (p=1.2×10⁻⁵). §4.2 already said this for NDBI; README, §4.3, §4.9, §6.4, §6.8 and dashboard pages 2, 5, 6 and 8 still said "null in both windows" or "no change either way". Corrected to "no significant increase", with the two-sided results stated.
3. *§4.7's explanation of the full-year trend.* It said the one-sided Wilcoxon (p=1.000) and the panel regression (p=0.000001) disagree because the panel weights the 2023-2025 recovery more. They don't disagree: the panel coefficient is −0.0046 per year, a significant decline, and a one-sided "greater" test returning p=1.000 says the same. Rewritten. §3.8 also said the slope test checked "different from zero" (the code is one-sided) and that the panel ran "on those same slopes" (it runs on the three-point values). Both corrected.
4. *Entry 47's "hallucinated" p-value was real.* Entry 47 dismissed a reviewer's p=0.049985408225561224 for full-year night-lights as fabricated because the two-point test gives 0.0501. The number is in `border_optics_multiyear_summary_fullyear.json`: it is the one-sided Wilcoxon on per-village full-year lights *slopes*. The dismissal was wrong. That result, borderline significant upward, is now reported in §4.7.
5. *§3.12's pre-specification claim.* It said Entry 5 records the dual-window design being locked in before either window's result was known. Entry 4 shows the full-year result was computed first, and the summer window was added after. §3.12 now says so. The estimand hierarchy was written down at Entry 23, after the main results were known, and §3.12 now says that too.
6. *`ANALYSIS_FREEZE.md` commit hash.* The recorded hash `ebab143...` is a 22 August 2026 commit that predates Entry 22 and every control-group fix. The accompanying note said `a1bfe9e...` "didn't match my repository", but that commit exists (14 September, "doc fix"). The freeze now records `feb0195...` (the 18 September HEAD, which holds every data file these numbers use). The freeze's multiple-testing paragraph still called the Holm and spatial corrections "sequential", and its power section still said "two-sided" for H1. Entry 47 fixed both of these in the paper but not in the freeze; both are fixed now.

**One new check, added because the audit raised it.** The contamination fix drops controls within 50m of a treated village, but extraction uses a 500m buffer. 82 of the 721 controls sit within 1km of a treated village, so their buffers overlap a treated buffer (5 are within 200m). New script `src/analysis/buffer_overlap_sensitivity.py` re-runs the primary DiD without them: all four results stay null (full-year NDBI +0.00683, p=0.322; full-year lights +0.03185, p=0.511; summer NDBI −0.00222, p=0.631; summer lights +0.01117, p=0.783). Output in `outputs/buffer_overlap_sensitivity_results.json`. Reported in §4.6 and §6.10.

**Disclosed, not fixed (need Earth Engine or a decision).**

- `select_control_villages.py` keeps the candidates closest to the border first when applying the 3× cap (it sorts by distance), so the control group is partly selected on border proximity. Now disclosed in §3.7 and §6.10 and commented in the script; a random draw would need a fresh Overpass run and control re-extraction.
- Treated and control extractions are not same-day any more: summer treated 16 September, summer control 17 September (Entry 37); full-year treated from the original July 2026 pull, full-year control from September. §6.10's archive-timing row said "Resolved"; it now says partly resolved. Closing it needs a same-day full-year re-pull of both groups.
- According to the Earth Engine catalog, Sentinel-2's QA60 band was not populated from early 2022 to early 2024. If so, the 2023 multi-year composites were built with little or no cloud masking. I haven't re-checked this against the catalog for this entry. Flagged in §3.4, §6.8 and §6.10; checking it needs a look at QA60 values on 2023 scenes, and fixing it would need a 2023 re-extraction with a different cloud mask (e.g. SCL or Cloud Score+).
- The drafts `BO_Pitch_Document.md` and `BO_Equivalence_Framing_Draft.md` (and `BO_Deep_Audit_Report.md`, Entry 38) are not in the project folder; git shows the first two were deleted on 17 September, before Entries 39-46 describe editing them. Those entries are left as written. The commit message for Entry 36's round mentions a CI test workflow, but there is no `.github/` folder.
- Entry 41 has two "Not done in this entry" paragraphs; the second is a leftover from Entry 37's list. Left as is (historical record).
- Rajya Sabha Q. 2321 still couldn't be located online. Lok Sabha Q. 508 (3 February 2026) is corroborated by news coverage of the reply the next day.

## Entry 49

**Status.** Version 2.0. On 19 October 2026 the whole project went through an independent forensic review: the reviewer went through the repository read-only, reproduced the analysis independently, and listed every problem found. I then made every fix that could be made without Earth Engine or live web APIs. Fixes that need Earth Engine, manual geocode review or new source data are prepared but not run (`docs/NEXT_STEPS_EARTH_ENGINE.md`). The review itself is in `docs/FORENSIC_REVIEW_2026-10-19.md`.

**What was verified first.** Every headline number was reproduced independently. Eleven analysis scripts were re-run unchanged, and their outputs are identical to the committed ones. The DiD, HC3, balance, leave-one-out, placebo, Dynamic World and multi-year results were re-implemented in NumPy (statsmodels could not be installed) and match to at least 5 decimals; the new `src/analysis/did_numpy.py` reproduces `did_model.py` to machine precision. All dashboard pages execute. The problem was not arithmetic but measurement, design and interpretation.

**Findings that change the interpretation.**

1. *The NDBI null is uninformative.* Buildings cover a median 0.33% of a 500 m buffer (Open Buildings), and buffer-mean NDBI rises only 0.53–0.84 per unit of building cover (cross-sectional, district FE). Doubling a typical village's buildings would move NDBI by ~0.002, 13–14% of the DiD's MDE; the NDBI CIs span changes of 4–7× a typical village's whole building stock; TOST against a doubling fails. The Cohen's-d power argument (§7.7 of v1.7) was misleading and is removed. New: `measurement_sensitivity.py`.
2. *Dynamic World is the stronger evidence, not a nuisance.* Its DiD passes t(13) and the exact wild cluster bootstrap (p = 0.041 full year, 0.008 summer; never bootstrapped before). Summer: 12/12 leave-one-out. Full year: not significant without Sikkim (p = 0.074) or when Dibang Valley or North is dropped. Equivalent to ~840 m² (full year) and ~2,080 m² (summer) of building-equivalent surface per village. New: `dynamic_world_robustness.py`.
3. *H3 was a between-district pattern.* Within districts (stratified Spearman, within-district permutation), summer NDBI proximity vanishes (ρ = +0.03, p = 0.78) and night lights reverse (ρ = +0.24, p = 0.021 full year; +0.42, p < 0.001 summer). Same with distance to the China boundary only. The v1.7 "stress-tested and surviving" description is withdrawn. New: `border_geometry.py`, `compute_lac_distance.py` (reproduces all 979 committed distances to < 1 mm), `h3_within_district.py`.
4. *The case villages were mis-attributed.* The Arunachal Times (1 Nov 2023) and ANI (31 Oct 2023) reports describe Kaho's and Musai's works as model-village works and do not describe Walong's as VVP; only Kibithoo's are described as "under the Vibrant Villages Programme", and Kibithoo failed geocoding ("Kibithoo H.Q."). The v1.7 claim that Kaho and Musai were "explicitly" VVP-funded is corrected, and the URLs are now in the references. Figure 12 now shows each village's change as a percentile of all villages instead of colouring it by sign.

**Data-quality findings (bounded, not yet fixed).** `sample_qa_sensitivity.py` re-runs H1 and the DiD under each variant below; no conclusion changes under any of them, alone or combined.
- 7 duplicated treated locations (14 rows).
- 35 treated and 61 control buffers with no building (e.g. Lachung appears ~10 km from the town).
- Joshimath (a town) in the treated list; it alone flips the sign of mean summer night-light change.
- 10 controls that are official priority villages written with a qualifier ("Sawa" vs "Sawa H.Q.").
- The full-year treated values come from an unpreserved Code Editor export and differ from the Python pipeline by more than 0.01 at 187/251 villages (2021); swapping them in gives a full-year NDBI DiD of +0.0029, p = 0.64.

**Code changes.**
- `select_control_villages.py`: qualifier-stripping name match (`core_name`), `--selection random --seed --out` (default unchanged); not yet run.
- `extended_robustness_checks.py`: writes a `window` column.
- New, not yet run: `extract_settlement_masked.py` (footprint-zone NDBI/DW, DW built area in m², Cloud Score+ and snow masking, cf_cvg-filtered VIIRS, 2019/2021/2025/2026), `settlement_masked_did.py` (tested on synthetic data with a known effect), `check_s2_archive_ingestion.py`.
- Tests: 3 new (treated duplicate ceiling 7, qualifier-contamination ceiling 10, distance reproduction); 15/15 pass.

**Documents.**
- `BO_Research_Paper.md` rewritten as v2.0 around one research question, with the DiD primary (a post-hoc change from v1.7's treated-only primary estimand, stated in §4.1 and §9) and the revision history moved to §9.
- `BO_Executive_Summary.md`, `README.md`, `CITATION.cff` (v2.0.0, data references) rewritten; `LICENSE` gains a third-party data note (OSM-derived files are ODbL).
- `DATA_DICTIONARY.md` extended; dashboard home, Study Design, Statistical Validation and Methodology & Limitations pages updated.
- The v1.7 paper, summary and README are kept in `archive/root/`.

**Not done (needs Earth Engine, manual work or a decision).**
- Same-day full-year re-extraction.
- Footprint-zone extraction and the 2026 window.
- Archive-ingestion check.
- Random-draw control regeneration.
- Geocode review against imagery (including Kibithoo and Joshimath).
- VVP block membership of controls.
- Works-completion data.
- Source of the 7 Himachal Pradesh names (and the 75 vs 51 count).
- Whether to license code under MIT instead of CC BY 4.0.
- Regenerating the folium maps.
- Deleting the stale `BO_Research_Paper-1.md` (identical in purpose to the archived v1.7 paper).

## Entry 50

**Status.** Check of the paper after version 2.0 (31 October 2026). No extracted data and no existing result changed. Three statements in the paper were corrected and one analysis was added.

**What was verified.** The 15 data-integrity tests pass. Every analysis script that runs without statsmodels or Earth Engine was re-run, and all saved outputs reproduce (the exact bootstrap p-values differ only in the fourth decimal, from floating-point ties). The main DiD estimates for NDBI, night lights, radar and Dynamic World were recomputed with independent code and match Table 2. About 60 numbers in the paper were checked against the result files.

**Fixed in the paper.**
- §5.1 said "the three most extreme values start from 2021 NDBI below −0.6". Only two villages do (Mana and Jadung), and they are the largest full-year *increases*. Sentence and Figure 2 caption corrected.
- Table 3: the summer NDBI change from doubling a village's buildings is 0.00175, now given as +0.0017 everywhere (it was +0.0018 in the paper and +0.0017 on the dashboard).
- Table 5: the buffer-radius and SCL rows are one-sided tests for an increase; now labelled, so they no longer appear to contradict the two-sided p = 0.87 in §5.1.
- New: Holm correction across the six triangulation DiDs (`src/analysis/triangulation_holm.py`, `outputs/triangulation_holm_results.json`). Summer Dynamic World stays significant (adjusted p = 0.027); full-year does not (0.157). Added to §4.5, §5.2 and the abstract.
