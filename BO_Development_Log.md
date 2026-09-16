# BORDER OPTICS — Development Log

This is my working log for BORDER OPTICS, a satellite-verification study I built to independently test whether India's Vibrant Villages Programme has produced measurable, on-the-ground development in the border villages it targets. I kept this log the way I keep every project's log — as an honest, chronological record of the decisions, dead ends, and fixes that went into the analysis, not a cleaned-up summary written after the fact.

What follows is organized as a set of entries, each covering one phase of the work: framing the research questions, building the village-level dataset, geocoding it, pulling satellite imagery, running the statistical tests, building the dashboard, and the review passes that came after. Every number, p-value, and citation below reflects what I actually found when I ran the analysis, including the results that didn't go the way I expected.

## Index

1. [Entry 1](#entry-1)
2. [Entry 2](#entry-2)
3. [Entry 3](#entry-3)
4. [Entry 4](#entry-4)
5. [Entry 5](#entry-5)
6. [Entry 6](#entry-6)
7. [Entry 7](#entry-7)
8. [Entry 8](#entry-8)
9. [Entry 9](#entry-9)
10. [Entry 10](#entry-10)
11. [Entry 11](#entry-11)
12. [Entry 12](#entry-12)
13. [Entry 13](#entry-13)

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

## Entry 7

With all four research questions tested (Entries 5-6), the next task was
turning the numeric results into visuals — three static charts and two
interactive maps.

**Static charts.** Built three figures in Python/Matplotlib: (1) the NDBI
change distribution for both composite windows side by side, visually
confirming the sign-flip documented in Entry 5; (2) state-level mean NDBI
change plotted against sanctioned VVP-I budget, visually confirming the
budget-independence pattern (Arunachal Pradesh's much larger budget bar
paired with a negative change bar, against Uttarakhand's small budget bar
paired with the largest positive change); (3) the H3 border-distance
scatter plots for both windows, showing the same flat/non-robust pattern
identified statistically in Entry 6.

**Interactive maps.** Built Folium-based interactive maps of all 251 core
villages, color-coded by NDBI change (blue = decrease, red = increase),
with click-through popups showing each village's NDBI change, night-light
change, and distance to border. Hit two design bugs building this: first,
Folium's colorbar legend isn't tied to a layer's visibility toggle — it's
a standalone map element — so a single combined map with both composite
windows as togglable layers always showed both legends stacked on top of
each other regardless of which layer was actually checked. Fixed by
generating two separate map files (one per composite window) instead of
forcing both into one togglable map, which also keeps each map visually
cleaner on its own. Second, the initial zoom level defaulted to a
centroid-based view that, given how geographically spread the three-state
sample is, opened zoomed out to roughly all of South Asia rather than the
actual village cluster — fixed with `fit_bounds()` so each map opens
already framed on its own data.

**Status.** Analysis and visualization phase is now functionally complete:
village data acquisition, geocoding, satellite extraction (both composite
windows), all four RQ/hypothesis tests, and both static and interactive
visual outputs. What remains is deciding the next build priority — a full
dashboard (as with the prior project) versus moving straight into Research
Paper drafting now that the plots and maps exist to draw on.

## Entry 8

With the analysis and visualization phase closed out, the final build
priority was a multi-page Streamlit dashboard, mirroring the structure used
for the prior project rather than a static write-up alone — the raw
figures, interactive maps, and live-recalculating statistical tests all
benefit from an explorable interface more than a fixed document does.

**Dashboard structure.** Built `app.py` as the entry point (Home page) with
a `pages/` directory holding seven sub-pages — Study Design, Built-Up
Change, Night-Lights, Statistical Validation, Explore Trends, Interactive
Maps, and Methodology & Limitations — plus a shared `utils/theme.py`
(watermelon-and-mint dark theme, consistent styling across every page) and
`utils/data.py` (a single cached `load_data()` used by every page, merging
the master village table with both compositing-window result files so
`latitude`/`longitude`/`distance_to_border_km` are available wherever
needed without re-reading the merge logic per page).

**Live recomputation over static numbers.** Several pages compute their
statistics live from the underlying CSVs on every load (Wilcoxon tests on
Statistical Validation, Spearman correlations on H3, state-level aggregates
on Explore Trends) rather than hardcoding the numbers already reported in
the Research Paper — this keeps the dashboard honest against the
underlying data if it's ever regenerated, at the cost of needing the raw
`data/processed/` CSVs to ship with the repository rather than only the
derived figures.

**Full Project Documentation section.** Added a section to the Home page
with three download buttons for the Research Paper, Project Report, and
Development Log as PDFs, matching the pattern used for the prior project's
dashboard.

**Research Paper.** Drafted the formal academic write-up from the completed
analysis — literature review grounding the securitization-theory framing,
full methodology section documenting every acquisition, geocoding, and
compositing-window decision made in Entries 1–7, results section reporting
both compositing windows side by side rather than a single preferred
version, and a limitations section carrying forward every documented data
gap (Ladakh exclusion, Himachal illustrative-only status, Pithoragarh block
ambiguity, LAC cartographic caveat) rather than treating them as resolved.

## Entry 9

Before treating the project as submission-ready, went back through every
file — all three documents, `requirements.txt`, `app.py`, every dashboard
page, and every script in `src/` — looking specifically for the kind of
issue that survives a first pass: stale numbers that drifted from the data,
scripts referenced in the documentation but missing from the repository,
and anything that would silently fail for a reader trying to reproduce the
pipeline end to end.

**Village-count discrepancy.** The Project Report's Study Area section
stated "262 geocoded villages," while the Research Paper, README, and the
underlying `border_optics_master_villages.csv` all agree on 258. Traced
this to a stale figure left over from an earlier point in the geocoding
pipeline (Entry 3 records the geocoding pass evolving in stages) that never
got updated in the Report after the final Bhuvan-fallback numbers landed.
Corrected to 258 throughout.

**Figure numbering out of sequence.** The Research Paper's Results section
referenced figures in the order Figure 1, 4, 6, 5, 2, 3 — each individual
reference was internally correct (pointing at the right image), but the
numbering itself wasn't sequential with reading order, since figures were
numbered by the order their source PNGs were generated (Entries 5 and 7)
rather than the order they appear in the paper. Renumbered to a clean 1–6
sequence matching reading order; no image files needed to change, only the
figure labels and captions referencing them.

**A live secret committed to source, not just to `.env`.** Unlike the
Sentinel Hub credentials pattern from the prior project (kept in a
`.env` file that `.gitignore` failed to exclude), this project's exposed
credential was worse in one respect: the Bhuvan API token was hardcoded
directly inside `geocode_villages_bhuvan.py` itself, committed to source
control with no `.gitignore` entry that could have caught it. Moved it to
an environment variable (`BHUVAN_TOKEN`, loaded via `python-dotenv`),
added a `.env.example` template, and added `.env` plus common
service-account-key filename patterns to `.gitignore`. Since this token
was live in a public repository, it should be treated as compromised and
regenerated from the Bhuvan API portal rather than reused — the old value
needs to be scrubbed from git history separately, since removing it from
the current file alone leaves it recoverable from any prior commit.

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

**`requirements.txt` incompleteness.** The file listed five packages
(`streamlit`, `pandas`, `numpy`, `scipy`, `plotly`) against a pipeline that
actually imports `geopandas`, `shapely`, `matplotlib`, `requests`,
`folium`, `branca`, and (once the satellite-extraction script above was
restored) `earthengine-api` and `python-dotenv`. A clean install from this
file alone would have failed the moment any acquisition or analysis script
ran. Expanded it to match actual usage.

**Full Project Documentation download buttons were dead.** The three
download buttons on the dashboard's Home page pointed at
`Research_Paper.pdf`, `Project_Report.pdf`, and `Development_Log.pdf` —
none of which had ever been generated; only the three source `.md` files
existed. Every visit to the Home page was silently showing "file not found"
warnings in place of working downloads. Built all three PDFs from the
source Markdown (via `pandoc`/`wkhtmltopdf`, embedding the actual result
figures) and added `build_docs_pdfs.sh` so they can be regenerated
whenever the underlying `.md` files change, rather than going stale again.

**Stale output path in a superseded fix script.** `fix_lights_map.py` (an
earlier patch script addressing the night-lights map's colorbar/marker
color issue, later folded properly into `make_interactive_map.py`) still
saved its output to `outputs/maps/`, a path that was never correct relative
to the rest of the pipeline's `outputs/interactive_maps/maps/` convention.
Corrected the path for consistency, though `make_interactive_map.py` is the
version actually used to regenerate the live maps.

## Entry 10

Circulated the finished project for outside review before treating it as
submission-ready. The most useful catch was a bug in the compiled
`BORDER_OPTICS_Maps_and_Plots.pdf` itself: the script that builds it had
labelled each image by its *source PNG filename number* (`01_...`
through `07_...`) rather than by the figure's actual position in
Research_Paper.md's renumbered sequence (Entry 9 renumbered the paper's
figures to a clean 1–7, but the PDF-compilation script was written
separately and never cross-checked against that renumbering). The result
was that the compiled PDF's "Figure 3" and "Figure 6" pages showed the
wrong charts relative to their labels — a real, confirmed mismatch, not a
stylistic nitpick. Fixed by remapping every entry against the paper's
actual captions and adding a comment in the script explaining why the
filename number and the figure number are not the same thing.

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

**Reproducibility package.** Added `DATA_DICTIONARY.md`, documenting every
column in the processed CSVs (including the two GEE-export artifact
columns, `system:index` and `.geo`, that are harmless but otherwise
unexplained) and the exact date ranges used for each compositing window,
alongside the already-existing `requirements.txt` and pipeline scripts.

## Entry 11

**Status.** Complete, bringing this project's Deep Verify from an earlier partial pass (Mann-Whitney selection-bias test + 1 pivotal citation) up to a full pass. No discrepancies found — everything matched exactly.

**Method.** Every statistical claim in `Research_Paper.md` was independently re-derived by re-running this project's own scripts directly against its own processed data: `src/analysis/analyze_results_fullyear.py` and `src/analysis/analyze_results.py` (both compositing windows' Wilcoxon and RQ2 budget-correlation tests), `src/analysis/compute_border_distance.py` (re-run from scratch against the raw Natural Earth boundary shapefile and the master village list, not read from the already-saved output) and `src/analysis/test_h3_border_proximity.py` (both windows' Spearman tests), plus a hand-reimplementation of the §6.5 Mann-Whitney selection-bias test and the §4.6 Holm-Bonferroni correction across all 8 tests, neither of which has a standalone script in this repo.

**What was independently reproduced and confirmed exact:**
- **H1 (§4.2/4.3), full-year window:** NDBI Wilcoxon p=1.000000 (paper: 1.000); night-lights Wilcoxon p=0.050075 (paper: 0.050, "borderline"). Both re-derived directly from `border_optics_village_results.csv`, re-computing `ndbi_change`/`lights_change` from the raw before/after columns rather than trusting the pre-existing `_analyzed.csv`.
- **H1, summer-matched window:** NDBI Wilcoxon on n=154 valid villages, p=9.29×10⁻¹⁵ (paper: "p < 0.000001," and this exact figure separately matches the Holm-Bonferroni table's cited "p = 9.3 × 10⁻¹⁵"); night-lights Wilcoxon p=0.999994 (paper: 0.9999).
- **§4.4 Budget independence (RQ2):** Arunachal Pradesh 120 villages, mean NDBI change 0.028350 → rounds to +0.0284 (paper: +0.0284); Uttarakhand 34 villages, mean NDBI change 0.029270 → +0.0293 (paper: +0.0293). Budget/project figures (₹2,749.74cr/2,082 projects vs ₹270.58cr/200 projects) match the hardcoded values in both analysis scripts exactly.
- **§3.6/4.5 Border-distance and H3:** re-ran `compute_border_distance.py` from scratch (raw Natural Earth `ne_10m_admin_0_boundary_lines_land` shapefile + `border_optics_master_villages.csv`, UTM 44N reprojection, nearest-point distance) rather than trusting the saved `_with_distance.csv`: distances range from 0.101 km to 69.356 km, mean 27.325 km (paper: 0.1–69.4 km, mean 27.3 km) — exact match. H3 Spearman tests, re-run against this freshly-computed distance file: full-year NDBI ρ=0.043/p=0.4968 (paper: 0.497), summer NDBI ρ=0.037/p=0.6501 (paper: 0.650), full-year lights ρ=−0.259/p=3.21×10⁻⁵ (paper: p<0.0001, and this exact figure separately matches the Holm-Bonferroni table's cited "p = 3.2 × 10⁻⁵"), summer lights ρ=−0.076/p=0.2325 (paper: 0.233). All four exact matches, including the specific full-year/summer reversal pattern the paper reports for night-lights and the specific stable-null pattern for NDBI.
- **§4.6 Holm-Bonferroni correction:** hand-reimplemented (`statsmodels.stats.multitest.multipletests`, method='holm') across all 8 tests (4 metrics × 2 windows). Confirms exactly what the paper claims: the two nominally-significant results (H1 NDBI summer, H3 lights full-year) both survive the correction; all 6 already-non-significant results remain non-significant. No discrepancy.
- **§6.5 Mann-Whitney selection-bias test:** re-derived directly from `arunachal_pradesh_geocoded.csv`'s raw `geocode_status` column (186 matched / 269 unmatched, splitting on whether the status string contains "matched"): Population matched mean=135.0 vs unmatched mean=145.7, p=0.3095 (paper: p=0.310); Households matched mean=25.8 vs unmatched mean=28.8, p=0.5398 (paper: p=0.540). Exact match, including the specific 186/269 split cited in §4.1/§6.5.

**What could not be independently re-derived.** The underlying raw satellite extraction (`src/acquisition/extract_satellite_data.py`, which populates `ndbi_before`/`ndbi_after`/`lights_before`/`lights_after` per village via Google Earth Engine) requires a live GEE account and cannot be re-run in this environment. Read the script in full for logic review instead: cloud masking via the QA60 bitmask (bits 10/11), NDBI as a standard normalized difference of B11/B8, VIIRS monthly composite mean, 500m point buffers, and explicit null-vs-zero handling for periods with no cloud-free imagery — no issues found. This mirrors how DOUBLE_JEOPARDY's terrain-raster-dependent statistics were treated in that project's own Deep Verify pass: code-reviewed rather than independently re-run, and explicitly flagged as such rather than silently assumed verified.

**Citations.** This pass adds 2 more spot-checks to the 1 (Lok Sabha Q508) already verified in an earlier round: Zha, Gao & Ni (2003), *Use of normalized difference built-up index in automatically mapping urban areas from TM imagery*, International Journal of Remote Sensing 24(3), 583–594 — confirmed real, exact match (Taylor & Francis). Elvidge, Baugh, Zhizhin, Hsu & Ghosh (2017), *VIIRS night-time lights*, International Journal of Remote Sensing 38(21) — confirmed real, exact match (DOI 10.1080/01431161.2017.1342050). A specific attempt to independently locate Lok Sabha Question No. 4360 (2025, cited for Ladakh's 35 sanctioned villages) via web search did not turn up that exact question by number — VVP-I's broader facts (Ladakh's inclusion, the programme's overall scope) are independently corroborated by PIB and the official VVP portal, but this specific parliamentary citation is flagged as not independently confirmed this round, rather than treated as verified by association. 3 of 12 references now spot-checked total (2 academic + 1 parliamentary from the earlier round); the remaining 9 (mostly parliamentary Q&A citations, plus Buzan et al. 1998, Wilcoxon 1945, Spearman 1904, and Natural Earth) were not individually re-verified.

**Outcome.** No fixes required to `Research_Paper.md`, `Project_Report.md`, or the dashboard this round — every independently re-derivable statistic matched exactly, including several exact-to-the-significant-figure matches (9.3×10⁻¹⁵, 3.2×10⁻⁵) that would have been very unlikely to reproduce by coincidence if the underlying pipeline had drifted from what the paper reports. BORDER_OPTICS moves from a partial to a full Deep Verify — the last of the four retroactive-plan projects (GPIE, DOUBLE_JEOPARDY, ECOCIDE, BORDER_OPTICS) now complete.

## Entry 12

**Status.** In progress — scripts written and ready to run, satellite extraction not yet executed.

**Why now.** Section 7 of the research paper names seven concrete extensions, none yet implemented. I picked three to move on together this round, rather than one at a time, since they share the same acquisition machinery: a genuine non-VVP control group (§7.3), a third time point for a real trend line instead of a two-point difference (§7.4), and a buffer-radius sensitivity check (§7.5). I also went back and re-checked whether the two coverage gaps (§6.1, §7.7 — Ladakh fully excluded, Himachal Pradesh at 7 of 51 villages) could move without filing an RTI. They can't: I found one government source (an All India Radio piece) confirming Ladakh's 35 identified villages by count but not by name, and the current Lok Sabha Q&A record (Question 508, February 2026) still reports only state-level aggregates for both regions — no village-wise breakdown. A couple of Himachal news pieces name individual VVP villages in Lahaul-Spiti (Gue, Lalung), but both were already in the dataset from the original acquisition pass. Nothing new to add this round; RTI remains the only path to close these two gaps, and it stays on the open list rather than getting a partial, lower-confidence workaround in its place.

**Control-group design.** The single biggest thing missing from this study, by its own account, is a control group — every result so far is each village's own before/after, with nothing to say whether a matched non-VVP village saw the same regional change over the same period. `select_control_villages.py` builds one: for each district already in the core sample (Arunachal Pradesh, Sikkim, Uttarakhand), it queries OpenStreetMap's Overpass API for named villages/hamlets in that district, drops anything matching a treated village's name, and keeps candidates within 1.5x the treated sample's own maximum border-distance for that district — border-region villages of a comparable character, not distant lowland towns pulled in just to pad the count. I matched on district rather than a tight distance band on purpose: pinning control villages to the exact same distance-to-border range as the treated sample would shrink the candidate pool down to almost nothing, and the villages that *did* survive that filter would mostly be the ones sitting right next to a treated village — which are the most likely to have been left out of VVP-I for a specific reason, not by chance. District-level matching keeps "same regional trend" defensible while giving the DiD design a real sample to work with.

**Multi-year extraction.** `extract_multiyear_satellite_data.py` adds 2023 as a third snapshot for the existing treated villages, run under both compositing windows for consistency with the rest of this study's own robustness discipline. This isn't another before/after pair — it pulls a single NDBI/lights value per village per year, so three points can support an actual trend line instead of one two-point difference that a single anomalous year at either end could be driving on its own.

**Buffer-sensitivity extraction.** `extract_buffer_sensitivity_data.py` re-runs the same before/after extraction at 250m and 1km, scoped to the summer window only — the window carrying the significant NDBI result, and so the one actually worth stress-testing here. Re-running the full-year window's null result at two more buffer sizes wouldn't add much; the summer result is the one a buffer-choice critique would target.

**What's ready to run.** All four scripts are written, checked into `src/acquisition/`, and pass a syntax check, but none have been executed — `select_control_villages.py` needs network access to the public Overpass API (this environment's sandbox can't reach it directly, the same constraint that always applied to Nominatim), and the three extraction scripts need a live Google Earth Engine session, same as the original `extract_satellite_data.py`. I don't touch API credentials myself; these get run locally, the same way the original acquisition pipeline was.

**What's still open.** Everything in this entry is preparation, not results — the actual control-group DiD estimate, the multi-year trend, and the buffer-sensitivity comparison all depend on data that doesn't exist yet. Himachal Pradesh and Ladakh's coverage gaps remain genuinely blocked on an RTI that hasn't been filed. SAR-based change detection (§7.1), building-footprint analysis (§7.2), and ground-truth positive-control validation (§7.6) remain untouched this round — bigger, separate undertakings each.

## Entry 13

**Status.** Complete. All three extractions described in Entry 12 finished, all three analyses written and run, the research paper and every other document rewritten to fold the results in as part of the study's design rather than reported as a bolt-on addition.

**Acquisition, finally run.** `select_control_villages.py`'s Overpass calls hit the shared public instance's rate limiting hard on the first attempt (429s and 504s under load, worse on the larger district bounding-box queries) — added retry/backoff (5 attempts, 20/40/80/160s escalating waits, honoring `Retry-After` on 429s) and per-district checkpointing so a stuck district doesn't cost the whole run. Reran end to end: 753 control villages across all 14 districts. Separately, `earthengine-api` has moved to requiring an explicit Cloud project on `Initialize()` since I last touched this pipeline — a bare browser re-auth no longer implies one, so all four `extract_*.py` scripts needed an `EE_PROJECT` environment variable wired through `python-dotenv`, matching the existing `BHUVAN_TOKEN` convention. Documented in `.env.example`. With that fixed, ran all four extraction passes: control-group full-year and summer (753/753 valid each), multi-year full-year and summer (258/258 valid at all three years), and buffer-sensitivity at 250m and 1km (258/258 valid each, summer window).

**Control-group DiD (§7.3 → now §3.7/4.6 of the research paper).** Reshaped treated (251-village core sample) and control (753 villages, same 14 districts) into a before/after panel and ran a district-fixed-effects DiD with SEs clustered by district. Summer-matched: did coefficient +0.0377, cluster-robust p = 0.0021 (HC3 no-FE comparison spec: +0.0287, p = 0.0116). Full-year: +0.0082, p = 0.215 — not significant. This is the same window-sensitivity split the core H1 test already shows, now confirmed after controlling for whatever regional trend the surrounding non-VVP villages experienced on their own. Ran a baseline-balance check in place of a true pre-trends placebo test, since the control group only has the same single before/after pair as the treated sample, not a multi-year pre-period: treated villages start from a significantly lower mean 2021 NDBI than control villages in both windows (p < 0.00001 summer) — expected, since VVP-I priority villages were themselves selected partly for remoteness, but worth being upfront that this is a level-balance check, not a confirmed shared pre-trend.

**Multi-year trend (§7.4 → now §3.8/4.7).** Fit a per-village linear slope across 2021/2023/2025 for the core sample, tested against zero with a one-sided Wilcoxon on the slopes, and cross-checked with a village-fixed-effects panel regression. Neither shows a significant overall trend in either window (summer Wilcoxon p = 0.442). Splitting into the two sub-periods explains why: a 2021→2023 decline (summer mean change -0.023, clearly not a significant increase) followed by a 2023→2025 increase that is itself highly significant (p < 0.000001). So the headline 2021-vs-2025 result this study has reported all along is real but concentrated in the second half of the window, not a steady trend since sanction — a genuinely useful thing to know and not something the two-point comparison alone could have shown.

**Buffer sensitivity (§7.5 → now §3.9/4.8) — caught a real confound before reporting it as a finding.** First pass looked bad: comparing NDBI significance "as extracted" at each radius, 500m was significant (n=154, p < 0.000001) but 250m and 1km were not (n=251 each, p = 0.126 and p = 0.899). Before writing that up as "the result doesn't survive a buffer-radius check," checked *why* the valid-village counts differed so much between radii — 500m has 97 nulls (66 Arunachal Pradesh, 31 Sikkim) that 250m and 1km don't have at all. That's not something a buffer-radius change should do on its own: Sentinel-2 tile footprints are tens of kilometres across, so whether a scene intersects a village's buffer shouldn't flip between 250m and 1km around the same point. The real explanation is more mundane — the 250m/1km extractions ran today, weeks after the original 500m extraction, against the identical fixed 2021/2025 date ranges but a Sentinel-2 archive that's kept backfilling scenes for a period this close to the present. Restricted all three buffers to the 154 villages valid at every radius, which holds sample composition fixed: on that matched subsample, NDBI is significant at all three radii (250m p = 0.000009, 500m p < 0.000001, 1km p = 0.001471). Documented the archive-timing issue directly in the script and in the paper's limitations (§6.9) rather than either hiding it or letting the raw "doesn't replicate" numbers stand uncorrected — the matched-subsample check is the actual answer to the question this test was asking.

**Figures.** Added three new figures (08 control-group DiD effect plot, 09 multi-year trend lines, 10 buffer-sensitivity comparison), matching the existing light-academic matplotlib style used for Figures 1/3/7.

**Documentation rewrite.** Folded all three results into `Research_Paper.md` as part of the original design rather than as an appendix: new RQ5/H4, new Methodology subsections 3.7-3.9, new Results subsections 4.6-4.8, an expanded Discussion, three new Limitations items (baseline imbalance, non-monotonic trend, archive-timing confound), and Future Work trimmed from seven items to four (SAR, building-footprint, ground-truth positive control, RTI follow-through survive; a fifth item — a genuine pre-treatment panel for the control group — replaces the three now-completed items). Mirrored the same changes into `Project_Report.md`, `README.md`, and `CITATION.cff` (bumped to v1.1.0).

**What's still open.** A true parallel-pre-trends placebo test for the control group (needs pre-2021 extraction for both groups — new Future Work item 7.5). SAR-based change detection, building-footprint analysis, and ground-truth positive-control validation remain untouched. Himachal Pradesh and Ladakh's coverage gaps are still blocked on an RTI that hasn't been filed.

## Entry 14

**Status.** Complete — a second acquisition-code review pass, this time specifically on the three scripts added in Entry 12/13 (`select_control_villages.py`, `extract_satellite_data.py`, `extract_buffer_sensitivity_data.py`) plus the Entry 13 figures. Entry 11's Deep Verify covered the original statistical pipeline; this pass covers the newer acquisition code that Deep Verify predates.

**Control-village resume logic was silently inert.** `select_control_villages.py`'s resume support skipped any (state, district) pair already present in the output file, full stop — it never actually checked whether that district's rows had been through a real boundary check or not. Practically, that meant a partial or interrupted run's bbox-only rows would get treated as "done" forever, since the district's name was already in the file. Fixed the resume condition to only skip a district once every one of its saved rows is confirmed polygon-verified; anything else gets its old rows dropped and rebuilt from scratch on the next run.

**Bbox overlap can double-count a village across districts — added dedup, then found a bug in the dedup itself.** Because each district's Overpass search box has a generous margin (0.6° so as not to miss legitimate border-area candidates), two adjacent districts' boxes overlap, and the same physical OSM point can turn up as a candidate for both. Added a cross-run coordinate set so a point claimed by one district can't be pulled in again under a different district's label. First version of this had an ordering bug, though: it marked a coordinate as claimed as soon as it passed the distance/polygon checks, before the per-district cap (3x the treated count) had a chance to cut it — so a candidate that lost out on the cap in District A's larger candidate pool could still permanently block a legitimate match in District B, even though it was never actually saved anywhere. Moved the claim to after the cap is applied, so only coordinates that actually make it into the saved file get reserved.

**Extraction resume logic was checking the wrong columns, twice over.** Both `extract_satellite_data.py` and `extract_buffer_sensitivity_data.py` treated a row as "already extracted" once its four value columns (`ndbi_before`/`ndbi_after`/`lights_before`/`lights_after`) were filled, without checking the four image-count columns alongside them. A row checkpointed mid-write with valid values but a still-null image count would never get revisited on a later run. Extended the completeness check to all eight outcome columns in both scripts.

**Holm-Bonferroni output file was never actually committed.** The paper's Holm-adjusted p-values (§4.9) cite `src/analysis/holm_correction.py`'s output, but the CSV it writes, `outputs/holm_correction_results.csv`, wasn't in the repo — the script existed, its numbers were right, the artifact just hadn't been saved. Ran it and committed the output.

**Figure 9's sample size was hardcoded.** The multi-year trend plot's per-panel title said "core sample (n=251)" as a literal string, while the plot itself computes each year's mean/SE from whatever rows have that year's value — currently always all 251, so the label happens to be accurate today, but nothing would catch it drifting out of sync if a future rerun did have a missing year somewhere. Changed the title to compute the actual count(s) from the same per-year data the plot already uses, so it can't silently go stale.

**Wording softened in two places.** The paper's §4.9 said the Holm correction "validates" the two headline findings "aren't a coincidence" — reworded to say what a Holm correction actually establishes (controls the multiple-testing false-positive rate) rather than implying it validates anything causally. The README's budget/outcome comparison said it gave "an intuitive picture of budget-independent implementation" from just two states (Arunachal Pradesh, Uttarakhand) — reworded to flag explicitly that two states is descriptive, not a formal test, matching the more careful framing the paper's own §4.4 already uses.

**What this doesn't fix.** None of the above regenerates `border_optics_control_villages.csv` itself — the 753-row file already committed predates every fix in this entry, including the polygon-membership check and the coordinate dedup, and (checked directly) does contain the kind of same-village-different-district duplicate the old bbox-only matching could produce. Regenerating it needs the resume file deleted and the script rerun with live Overpass/Nominatim access, followed by re-running the control-village satellite extraction and `did_model.py` so the reported DiD numbers are computed from the corrected control set rather than the old one. That's acquisition + a live GEE session, same as always — flagged here rather than done silently, and not yet actioned.

## Entry 15

**Status.** Complete. The regeneration Entry 14 flagged as "not yet actioned" was attempted, failed silently on the first attempt for a reason worth documenting in full, was fixed, and the corrected rerun's numbers are now independently verified and folded into every document.

**The regeneration's first attempt did nothing, and the DiD script couldn't tell.** `select_control_villages.py` was rerun with the Entry 14 dedup fix and correctly produced a new 735-village list (753 minus 18 cross-district duplicates). `extract_control_satellite_data.py` was then rerun against it — but its resume logic checked whether a row for a given `village_id` already had filled-in NDBI/lights values, and `village_id` is nothing more than a sequential 1..N index reassigned fresh on every regeneration of the village list. The old 753-row checkpoint file still had values for `village_id` 1 through 753 sitting on disk, so every one of the new list's 735 rows found a "complete" match at the same index and the script skipped straight to done without a single new Earth Engine call. The resulting `did_model.py` numbers were, byte-for-byte, the old bugged numbers — which is exactly how this got caught: they were independently reproducible from the old, still-committed 753-row control-results file, run locally against that stale data, before trusting anything pasted from a terminal.

**Fix.** Rewrote the resume check to match on coordinate (rounded lat/lon) instead of `village_id`: it now compares the current village list's coordinate set against the checkpoint file's coordinate set, and only resumes if they match. A 735-village list against a 753-row checkpoint doesn't match, so the corrected script correctly detects this and starts fresh. Verified locally against both the same-list-reordered case (should resume) and the regenerated-list case (should restart) before pushing — the same class of "test it before believing it fixed anything" discipline this project's development log has tried to hold itself to throughout, applied here specifically because the first version of this exact fix had already been trusted once without that check.

**Independent verification of the actual rerun, not just the pasted terminal output.** After the corrected extraction was rerun and pushed, pulled the result and checked it directly rather than taking the pasted DiD numbers on faith: `border_optics_control_villages.csv` is 735 rows with zero duplicate coordinates (confirmed programmatically); `border_optics_control_results.csv` and `border_optics_control_results_summer.csv` are both 735 rows with image-count columns that vary row to row (73/86/12/12, 146/170/12/12, and so on) rather than sitting at a suspicious constant, which is what a genuine set of fresh Earth Engine calls looks like and what a silently-skipped extraction would not produce. Reran `did_model.py` locally against this pulled data myself for both windows and it reproduced the pasted numbers exactly, to the fifth decimal place, for every coefficient, SE, CI, and p-value in both outcomes and both windows — this is what "verified" means here, not "the numbers looked plausible."

**Two real results changed, not just their precision.** The summer-window NDBI gap against the control group holds, and holds slightly more tightly: did coefficient +0.0322 (was +0.0377), cluster-robust p = 0.00033 (was p = 0.0021). The full-year NDBI gap remains non-significant: +0.0088, p = 0.275 (was +0.0082, p = 0.215) — same conclusion, a little noisier now that the control group's valid full-year sample is 190 villages rather than 753. Night-lights is the one that actually changes conclusion: under the old, bugged control list, no DiD effect was reported in either window. Under the corrected list, a significant positive gap now shows up in both — summer +0.1413, p = 0.0044, agreeing under both the fixed-effects and no-fixed-effects specifications; full-year +0.1653, p = 0.0364 under fixed effects but p = 0.1033 without them, a specification disagreement rather than a clean result. Checked why before writing it up as "night-lights now shows an effect": Section 4.3's treated-only Wilcoxon test on the same summer window is still a clean null (p = 0.9999) — treated villages' own night-lights didn't rise. What happened is that the *control* villages' night-lights fell over the same period in most districts while treated villages held roughly flat, so the treated-minus-control gap comes out positive without any absolute increase on the treated side. Documented this distinction explicitly everywhere the new lights-DiD number appears, rather than letting a positive coefficient read as "VVP-I villages lit up" when the more accurate description is "VVP-I villages didn't decline the way the surrounding region did."

**Baseline imbalance is worse than previously reported, not better.** The old write-up only checked and disclosed a baseline (2021) imbalance for NDBI. Checking all four outcome/window combinations against the corrected control group: NDBI summer is still imbalanced but the gap between treated and control means shrank considerably (treated −0.2461 vs. control −0.2442, versus the old run's treated −0.246 vs. control −0.185); NDBI full-year is the only one of the four that is not significantly imbalanced (p = 0.125); night-lights summer is mildly imbalanced (p = 0.0165); and night-lights full-year is the most imbalanced of all four (p < 0.00001) — which is also the one combination where the two DiD specifications disagree, a pattern consistent with (though not proof of) that baseline gap being handled differently by each. Added this full four-way breakdown to Section 4.6 and 6.7 of the paper, the README, and the Executive Summary, where previously only the NDBI figure was disclosed.

**Documents updated.** `BO_Research_Paper.md` (§3.1, Abstract, §4.6 rewritten with an explicit note on the bug and correction, §6.7, Discussion, Conclusion, §7.5), `README.md`, `BO_Executive_Summary.md` (checklist table gained a Night-Lights DiD row), `CITATION.cff` (735-village count, version bumped to 1.1.1), `DATA_DICTIONARY.md`, `app.py`, and dashboard pages `1_Study_Design.py`, `5_Statistical_Validation.py` (added a Night-Lights DiD card pair alongside the existing NDBI one, since it's no longer a null result not worth displaying), `7_Interactive_Maps.py`, and `8_Methodology_Limitations.py`. Figure 8 (`08_control_group_did_effect.png`) and its interactive counterpart both read live from the DiD summary JSONs rather than hardcoding coefficients, so regenerating them after `did_model.py`'s rerun was enough to pick up the corrected numbers with no script changes needed there. Figures 9 and 10 (multi-year trend, buffer sensitivity) don't depend on the control group at all and are unaffected by any of this.

**What this doesn't change.** The core NDBI headline — that the summer-window built-up-area gap survives a control-group comparison, a buffer-radius sweep, and Holm-Bonferroni correction, while the full-year gap doesn't — is unchanged in direction and, if anything, slightly more precise now. What's genuinely new is the night-lights control-group finding, and it's reported with the same specification and baseline-imbalance caveats applied to every other borderline result in this study, not as a second confirmed headline.

## Entry 16

**Status.** Complete — a small but real overreach caught during an external review pass over §4.9's Holm-Bonferroni writeup, checked directly against `outputs/holm_correction_results.csv` rather than taken on the paper's word.

**The claim checked out wrong.** §4.9 said that of the eight headline p-values, the two significant ones stayed significant after Holm correction (true, and cited correctly) and that "all the results remaining non-significant do not change (all Holm-adjusted to 1.000, since they were already at or near the ceiling before correction)." That second half isn't what the committed CSV shows. Five of the six remaining tests are indeed already at the ceiling (raw p ≥ 0.497) and Holm-adjust to exactly 1.000. The sixth, `H3_lights_change_full-year` — the full-year night-lights before/after Wilcoxon, raw p = 0.0501 — is nowhere near that ceiling and Holm-adjusts to p = 0.300, not 1.000. It's still non-significant either way, so the correction's actual conclusion (no borderline result becomes significant, and no significant result stops being one) is unaffected — the bug was a sloppy blanket description of the intermediate numbers, not a wrong headline claim.

**Also checked, and not a bug:** an external reviewer separately flagged `src/analysis/holm_correction.py` as "missing" from the repo. It isn't — it's present, checked in since Entry 12/13, and its committed output (`outputs/holm_correction_results.csv`, restored in Entry 14 after being caught un-committed) is exactly what §4.9 cites. That specific claim doesn't hold up; only the "all adjusted to 1.000" wording did.

**Fix.** Reworded §4.9 in `BO_Research_Paper.md` to state the actual per-test breakdown: five of six remaining non-significant tests Holm-adjust to 1.000, the sixth (full-year night-lights change) adjusts to p = 0.300, and explained why — a raw p just under 0.05 isn't "near the ceiling" the way a raw p over 0.49 is. Checked the Executive Summary and the dashboard's Statistical Validation page for the same "adjusted to 1.000" phrasing; neither repeats it, so no changes needed there. Rebuilt `BO_Executive_Summary.pdf`, `BO_Research_Paper.pdf`, and `BO_Development_Log.pdf` (root + `static/`) via `build_docs_pdfs.sh` to match.

**What this doesn't change.** No numbers in `outputs/holm_correction_results.csv` changed — only the prose describing them. The paper's substantive conclusions in §4.9 (both significant findings survive correction; no non-significant result becomes significant) were already correct and remain so.

## Entry 17

**Status.** Complete — a second external review pass (a 25-point list, most of it framed as "current, live-repo" problems) came in immediately after Entry 16 was pushed to `origin/main`. Checked every claim against the actual current `origin/main` tip rather than against what the review quoted, since a review generated even a few minutes earlier can be reading a stale GitHub cache from before a push lands.

**The four "critical/must-count" claims were already false at the moment they were raised.** The review's top four items — (1) committed summer NDBI DiD JSON (+0.0322, p=0.000334) contradicting the paper (+0.0377, p=0.0021), (2) committed summer night-lights DiD JSON (+0.1413, p=0.0044) contradicting a paper claim of "no effect, p=0.8485", (3) the control file's actual 753 rows contradicting a "735 villages" claim repeated across the dashboard, and (4) the Development Log ending at Entry 12's "in progress, not yet executed" — all describe the *pre-Entry-15* state of this repository. `git fetch origin main` and `git show origin/main:<path>` for each file named in the review confirms the paper, README, and every dashboard page currently in `origin/main` already report the corrected 735-village, +0.0322/p=0.00033 NDBI and +0.1413/p=0.0044 lights-DiD numbers consistently, the control CSV has exactly 735 data rows, and the Development Log runs through Entry 16. All four were fixed by the Entry 15 documentation sync and the Entry 15 commit itself, and were live on `origin/main` before this review's claims were made — most likely the review was run against a browser cache of the GitHub page from before that push, or before the push had happened at all.

**Also re-confirmed not a bug:** the review's Holm-correction section (its own #15) explicitly withdrew the "script missing" claim from an earlier review round and found the current Holm output internally consistent — matches what Entry 16 already established directly from `outputs/holm_correction_results.csv`.

**But two real, current staleness bugs were found underneath the noise, in files the review didn't actually name.** Chasing down the review's "753 vs 735" claim by grepping the whole repo for literal `753` (rather than trusting which files the review cited) turned up three real current instances the review missed entirely: `app.py`'s two homepage description strings ("...control group of 753 villages...", "...plus 753 matched control villages..."), `DATA_DICTIONARY.md`'s description of `border_optics_control_villages.csv` ("753 rows"), and a hardcoded map title in `src/visualization/make_control_multiyear_maps.py` ("753 matched control villages") that had baked itself into the committed `outputs/interactive_maps/maps/village_treated_vs_control_map.html`. All four dated from before the Entry 15 dedup fix and were never updated when the dashboard pages, README, paper, and Executive Summary were. Fixed all four; regenerated the affected map (the other two maps that script produces re-rendered with new random Folium element IDs but no content change, so those two were reverted to avoid a pointless diff).

**One genuine methodology-wording overclaim, also missed by the review's own explanation of it.** The review's #5 correctly senses something off about "controlling for the regional trend" language but attributes it loosely. Checked `did_model.py`'s actual formula (`outcome ~ treatment + post + did_term + C(district)`, OLS with cluster-robust SEs by district): `C(district)` is a set of district intercepts — it nets out each district's own time-invariant *baseline level*, nothing about a trend. The single shared `post` term is what nets out a trend, and only a *common* one, assumed shared by treated and control villages alike (the standard DiD parallel-trends assumption) — never a *district-specific* trend, since there is no district×post interaction anywhere in the formula. The paper's §3.1 (Methodology) had a sentence attributing "remove the district-specific trend" directly to the district-fixed-effects term, which conflates the two. Reworded that sentence, and a related README sentence that had the same "controlling for each region's own trend" phrasing sitting right next to "district-fixed-effects DiD," to correctly separate what the FE term does (baseline-level adjustment) from what the control-group comparison as a whole does (nets out a trend common to treated and control, not a district-specific one). Checked the same "regional trend" language everywhere else it appears (README's opening bullet, `pages/1_Study_Design.py`, `pages/5_Statistical_Validation.py`) — those instances describe a *shared* regional trend being netted out by the control-group comparison generally, not attributed specifically to district FE, so they were already accurate and left alone. Also fixed `did_model.py`'s own docstring, which still said "753-village matched control" in a comment above code that has used the 735-village list since Entry 15.

**The rest of the review (its items 6-14, 18-20) is fair commentary, not found to be a current factual error.** Points like "matched control group" overstating the design, "same villages" glossing over the 251-vs-154 valid-sample shrinkage in the summer window, NDBI being described loosely as literal "built-up area," "three independent stress tests" overstating independence between checks that share the same underlying satellite observations, and the Executive Summary's opening line reading more confident than the immediately-following paragraph's own disclosure of a non-monotonic trend — these are real framing/precision critiques worth keeping in mind for a future editing pass, but every one of them is already substantively caveated elsewhere in the same documents (the baseline-imbalance limitation, the Section 4.7 non-monotonic-trend writeup, the Section 6 exploratory-scope disclaimers). Not treated as bugs this round; flagged here in case a future pass wants to tighten the prose further.

**Documents updated.** `BO_Research_Paper.md` (§3.1 methodology sentence), `README.md` (§ NDBI/DiD summary paragraph), `app.py` (two description strings), `DATA_DICTIONARY.md` (control-file row count), `src/analysis/did_model.py` (docstring), `src/visualization/make_control_multiyear_maps.py` (map title string), `outputs/interactive_maps/maps/village_treated_vs_control_map.html` (regenerated). Rebuilt `BO_Executive_Summary.pdf`, `BO_Research_Paper.pdf`, and `BO_Development_Log.pdf` (root + `static/`).

**What this doesn't change.** No statistical results changed — every fix in this entry is a documentation/label correction to match numbers that were already right. The two headline conclusions (summer NDBI gap survives the control-group/buffer/Holm checks; the gain is concentrated in a 2023-2025 recovery rather than sustained growth) are unaffected.

## Entry 18

**Status.** Complete — a third external review round repeated the same by-now-familiar stale claims (753 vs 735, DiD-vs-paper mismatch) verbatim, all still false against `origin/main` as of this entry's starting commit. But it also raised two claims genuinely worth checking on their own merits rather than dismissing alongside the stale ones: (1) `compute_border_distance.py` projects the entire study area — which spans roughly 77°E to 97°E — into a single UTM zone (44N, centered on 81°E), and (2) the "border/LAC distance" variable is computed as distance to the *nearest* India-related Natural Earth boundary segment, which is not necessarily the China segment. Both turned out to be real, and both were checked quantitatively rather than taken on faith, in either direction.

**UTM 44N: real bias, quantified, doesn't change any conclusion.** Wrote a direct comparison — the old single-zone UTM44N planar distance vs. a proper WGS84-ellipsoid geodesic distance — for representative points in Uttarakhand (near the zone's own central meridian), Sikkim (~7.5° east of it), and Arunachal Pradesh (~11-15° east of it). Confirmed the old method systematically *overstated* distance the further east a village sits: negligible in Uttarakhand, but up to ~3% in Arunachal Pradesh's easternmost villages (mean bias -1.5% for the state, worst single village off by just over 2km). Rewrote `compute_border_distance.py` to find the nearest boundary point in unprojected lon/lat space (adequate for identifying *which* point is nearest at these scales) and then compute the actual distance geodesically via `pyproj.Geod` — this has no zone dependency at all, so it is correct everywhere in the study area rather than only near one meridian. Regenerated `border_optics_master_villages_with_distance.csv` and reran every downstream script that reads it: `test_h3_border_proximity.py` (H3's four Spearman tests), `holm_correction.py` (two of its eight tests are H3 border-proximity tests), and the two figures that display H3 numbers as text (`03_h3_border_distance_vs_lights.png`, `07_robustness_summary.png`). Every H3 ρ/p value moved by a small amount (e.g. full-year NDBI-proximity: ρ 0.043→0.049, p 0.497→0.443; full-year lights-proximity Holm-adjusted p: 2.24×10⁻⁴→3.83×10⁻⁴) but **not one test's significant/non-significant status changed** — updated the exact numbers everywhere they're cited (paper §4.5, §4.9, the RQ1 opening paragraph, and the Section 4.9 line-up) and added a note at §4.5 explaining the correction and confirming no conclusion moved.

**Not touched: control-village selection's own copy of this same distance logic.** `select_control_villages.py` independently computes distance-to-border for the same reason (as a soft candidate-selection filter, `METRIC_CRS = "EPSG:32644"` — same UTM44N choice) and reads treated-village distances from the same file this entry regenerated. Making that fully consistent would mean re-running `select_control_villages.py` (needs live Overpass API access) and every downstream control-satellite-extraction and DiD script (needs a live Google Earth Engine session) — neither of which this environment has. Flagging this rather than leaving it silently inconsistent: the currently-committed 735-village control list and every DiD number derived from it still reflect the old UTM44N-based distance filter. Given the filter is a generous 1.5x-treated-max soft cap and the actual bias is 1-3% at the country's edge, this is very unlikely to have excluded or included villages it shouldn't have, but a fully rigorous fix would need that live rerun, flagged here as the follow-up rather than done silently or claimed as done.

**"Border/LAC distance" is not always distance to the LAC — checked exactly how often, rather than asserting a number.** Computed, per core-sample village, which country's Natural Earth boundary segment is actually nearest: 220 of 251 (88%) are nearest to the China segment, but 19 (Arunachal Pradesh, mostly Tawang and West Kameng) are nearest to Bhutan, 8 (North Sikkim, and Uttarakhand's Pithoragarh) are nearest to Nepal, and 4 (Arunachal's Anjaw) are nearest to Myanmar. The code's own filter (`ADM0_LEFT`/`ADM0_RIGHT` == "India") was always correctly finding the nearest *India* boundary of any kind, not specifically the LAC/China segment — this was working as written, just not disclosed as precisely as it should have been. Added the exact breakdown to the paper's §6.2 and the dashboard's Methodology & Limitations page, framing it honestly: for the 12% of the sample nearest a non-China border, H3 is a reasonable general border-securitization-proximity measure (these are still border villages in the broader sense VVP-I itself uses) but not literally an LAC-proximity test for those specific villages. H3 was already disclosed as exploratory elsewhere (Executive Summary, Methodology page) for other reasons (small sample geometry, no covariate control); this is an additional, more specific reason not to lean on it as a clean confirmatory result. Also corrected `pages/1_Study_Design.py`'s claim that UTM-reprojection was done "for accuracy" — the fixed version now correctly describes the geodesic method and why a single-zone reprojection wasn't accurate for this study's east-west extent.

**Also reconfirmed, once again, not current bugs:** the third review's repeat of 753-vs-735 and the DiD-number-vs-paper mismatch. Both are false against `origin/main` at every point they've been raised so far — verified again this round via direct `git fetch` + `git show origin/main:<path>` before touching anything, per the now-established pattern from Entries 16-17.

**Documents updated.** `src/analysis/compute_border_distance.py` (rewritten), `data/processed/border_optics_master_villages_with_distance.csv` (regenerated), `outputs/holm_correction_results.csv` (regenerated), `outputs/figures/03_h3_border_distance_vs_lights.png` and `07_robustness_summary.png` (regenerated), `BO_Research_Paper.md` (§4.2 intro figure, §4.5, §4.9, §6.2), `pages/8_Methodology_Limitations.py` (expanded LAC-geometry caveat), `pages/1_Study_Design.py` (border-distance methodology line). Rebuilt `BO_Executive_Summary.pdf`, `BO_Research_Paper.pdf`, and `BO_Development_Log.pdf` (root + `static/`).

**What this doesn't change.** No hypothesis flips from significant to non-significant or back. H3 remains what it always was: a mostly-null, exploratory test, now on slightly more accurate (and more honestly described) distances. The two headline conclusions from Entry 15 onward are unaffected.

## Entry 19

**Status.** Complete — a final, from-scratch publish-readiness audit, done independently of any external review's claims: reran the core scripts directly against the currently-committed source data (not against any cached JSON or doc) to confirm every headline number is actually reproducible, then swept the whole repo for anything a targeted review round might have missed simply because nobody had looked there yet.

**Every headline number reproduces from scratch.** Ran `did_model.py --window full_year` and `--window summer` fresh: output matches the paper's cited +0.0088/p=0.275 (full-year NDBI), +0.1653/p=0.0364 (full-year lights), +0.0322/p=0.00033 (summer NDBI), +0.1413/p=0.0044 (summer lights) to 5 decimal places (the JSON files it regenerates differ from the committed ones only in the ~13th decimal place — floating-point noise, not a real difference; reverted rather than committed). Ran `test_h3_border_proximity.py` and `holm_correction.py` fresh: both match the paper's Entry-18-corrected numbers exactly. This is the first time in this whole review cycle that the numbers were verified by *recomputing* them end-to-end from the committed CSVs, rather than by comparing one document's stated numbers against another's.

**Found one real thing none of the three external review rounds caught: `CITATION.cff` was never actually updated.** It still said "753 villages" in its abstract, and its `version`/`date-released` fields (1.1.0, 2026-08-14) predate every fix from Entry 15 onward. Root cause: earlier pushes in this cycle (Entries 16-18) synced the paper, README, dashboard pages, and Executive Summary file-by-file to the user's local folder, but `CITATION.cff` was never on any of those lists — it fell through a gap between the original repo (where a version bump to 1.1.1 was made in a since-orphaned local session that was never pushed to `origin/main`) and this repo's actual git history, which shows `CITATION.cff` was never touched past a 1.1.0 commit predating the 735-village correction entirely. Fixed the abstract's village count (735, not 753) and its results summary (added the control-group DiD gap for both NDBI and night-lights, not just the raw before/after comparison, since the abstract's old text predated the whole control-group section of the paper), and bumped `version: 1.2.0`, `date-released: "2026-09-07"`.

**Also found `pyproj` missing from `requirements.txt`.** Entry 18's rewrite of `compute_border_distance.py` imports it directly; it was previously only present transitively via `geopandas`. Added it explicitly so a fresh environment install doesn't depend on that being true of whatever `geopandas` version gets resolved.

**Other checks in this pass, all clean:** every `.py` file in `src/`, `pages/`, `utils/`, and `app.py` compiles without syntax errors; no `TODO`/`FIXME`/`XXX` markers left in tracked source; a full repo-wide grep for the old stale numbers (753, 0.0377, 0.8485, 0.7229) turns up nothing outside `BO_Development_Log.md`'s own historical entries, which correctly describe them in the past tense; `LICENSE` is present; the three doc PDFs were rebuilt and diffed against the committed ones via `pdftotext` — text content is byte-identical (the previous PDF rebuild's git diff was purely `wkhtmltopdf`'s non-deterministic embedded generation timestamp, not a content change), so the committed PDFs were left as-is rather than re-committed for no reason.

**Documents updated.** `CITATION.cff` (abstract, version, date), `requirements.txt` (added `pyproj`).

**Bottom line for this cycle.** Across four review rounds (Entries 16-19), one real statistical-writeup bug was found and fixed (Entry 16, the Holm §4.9 "all adjusted to 1.000" overstatement), one real staleness cluster was found and fixed (Entry 17, four leftover "753" references), one real methodological gap was found, quantified, and fixed (Entry 18, the UTM-zone distance bias and the undisclosed non-China border composition), and one real metadata gap was found and fixed in this entry (`CITATION.cff` never having been updated). None of the four changed any headline conclusion. Every other claim raised across three external review rounds was independently verified against the live repository and found to already be resolved, or in one case never true to begin with. As of this entry, every number in the paper, README, Executive Summary, Data Dictionary, and dashboard has been either directly cross-checked against a freshly-recomputed source, or checked for internal consistency against every other document that cites it.

## Entry 20

**Status.** Complete — this entry does two things: (1) adds four extended robustness checks to the summer-window control-group DiD result (H4), all built from data already extracted, no new GEE/Overpass acquisition; (2) closes out the framing/precision critiques that Entry 19 flagged but deliberately deferred ("matched control group" overstating the design, "three independent stress tests" overstating independence between checks that share the same underlying satellite observations).

**Why now.** Entry 19's own "bottom line" left two categories of open item: things that were genuine precision critiques but not bugs, and the standing fact that the control-group DiD's cluster-robust p-values rest on only 14 district clusters — small enough that the asymptotic theory behind cluster-robust standard errors is itself worth stress-testing, not just assumed. Both are addressed here rather than left for a fifth review round to raise again.

**`statsmodels` unavailable in this environment.** `pip install statsmodels` fails outright here (no matching distribution, despite `pypi.org` being in the environment's allowlist) — so the four checks below use a from-scratch NumPy implementation of OLS plus cluster-robust and HC3 sandwich covariance, written and checked before being trusted: it reproduces all four of `did_model.py`'s own committed headline coefficients/SEs/p-values (both windows, both outcomes) to 5+ significant figures against the already-committed JSON. The one non-obvious thing this caught: `statsmodels`'s default `cov_type='cluster'` significance test is a normal/z-test, not a t-test — matching that exactly (rather than a t-test with `G-1` or `n-k` degrees of freedom, which gives a close-but-wrong p-value) was necessary to hit an exact match. New script: `src/analysis/extended_robustness_checks.py`.

**1. Leave-one-district-out.** The summer-window DiD (both NDBI and night-lights) was rerun 14 times, dropping one of the 14 districts each time. Both outcomes stay significant (p < 0.05) in all 14/14 reruns — NDBI's coefficient ranges from +0.0240 to +0.0359 (against +0.0322 with every district included), night-lights' from +0.1117 to +0.1731 (against +0.1413). No single district is carrying either result.

**2. Randomization inference.** Treatment was reshuffled 2,000 times within each district (preserving each district's actual treated/control counts, seed=42), building a permutation null for the DiD coefficient that doesn't lean on cluster-robust asymptotic theory at all. NDBI's observed +0.0322 sits far outside its null (mean +0.0005, SD 0.0048; p = 0.0005); night-lights' observed +0.1413 likewise (mean +0.0033, SD 0.0323; p = 0.0005). This and the leave-one-out check both test the same thing from different angles — whether the reported cluster-robust p-values can be trusted given only 14 clusters — not the separate, still-open baseline-imbalance question from Entry 15/§6.7.

**3. Log1p-transformed VIIRS.** VIIRS radiance is right-skewed, so the night-lights DiD (and the treated-only Wilcoxon borderline case from §4.3) were re-run on log1p-transformed values, as a check against a handful of high-radiance villages driving the result. Nothing flips: the summer DiD result survives and strengthens on the log scale (raw p = 0.0044 → log1p p = 0.0003), the full-year DiD holds at about the same significance either way (p = 0.0364 vs. p = 0.0374), and the §4.3 full-year treated-only borderline case (p = 0.050) stays non-significant on the log scale too (p = 0.068).

**4. Summer-window missingness, quantified.** The 154 core-sample villages with valid summer-window data are not a random 154 out of 251 — checked this directly rather than leaving it at "monsoon cloud cover thinned the sample." The 154 summer-valid and 97 summer-invalid villages differ significantly in state composition (chi-square = 71.42, p ≈ 3.1×10⁻¹⁶ — mostly mechanical, since Sikkim's entire 31-village contingent drops out on its own) and, separately, in their own 2021 full-year baseline NDBI (Mann-Whitney U, p = 0.00063: summer-valid villages start from a mean of -0.2047, summer-invalid from -0.1527). This doesn't establish which direction, if any, that biases the reported summer-window change, but it upgrades the previous qualitative "cloud cover" framing into a quantified, previously-underspecified selection fact, and it means the summer-window result should be read as describing that specific subsample rather than the full core sample by default.

**Wording precision fixes, closing out Entry 19's deferred list.** "Matched control group" → "district-restricted control group" everywhere it described the 735-village non-VVP comparison group (the group is restricted to the same 14 districts, not individually matched to treated villages on covariates — "matched" overstated the design). "Three independent stress tests" → reworded to "complementary robustness checks" in the two places that used that exact framing, since the three checks share the same underlying satellite pipeline rather than being independent in the statistical sense — and since this entry adds two more checks (leave-one-out, randomization inference) that strengthen the *same* control-group check rather than adding a fourth and fifth independent method, the count itself needed rewording, not just relabeling. "One measurement option shows a real, significant rise in built-up area" (Executive Summary) → "...rise in NDBI — consistent with, but not direct proof of, built-up area growth," since NDBI is a proxy, not a direct built-up-area measurement.

**Documents updated.** New: `src/analysis/extended_robustness_checks.py`, `outputs/robustness_extended_results.json`, `outputs/leave_one_district_out_results.csv`. Edited: `BO_Research_Paper.md` (§4.2, §4.3, §4.6 — two new paragraphs, §4.9, §5, §6.4 — new paragraph, §6.7, Abstract, §3.1, Conclusion), `BO_Executive_Summary.md` (Project Overview, Method, Finding, Robustness Checklist, Honest Limitation), `README.md` (opening description, Key Findings), `app.py`, `utils/data.py`, `pages/1_Study_Design.py`, `pages/5_Statistical_Validation.py`, `DATA_DICTIONARY.md`, `src/analysis/did_model.py` (docstring + argparse description), `src/visualization/make_control_multiyear_maps.py` (map title string — regenerating the map itself needs `folium`, unavailable in this environment via pip, so the already-committed `outputs/interactive_maps/maps/village_treated_vs_control_map.html` was patched directly with the identical text change rather than left inconsistent with its own source script). Rebuilt `BO_Research_Paper.pdf`, `BO_Executive_Summary.pdf`, `BO_Development_Log.pdf` (root + `static/`) via `build_docs_pdfs.sh` — `BORDER_OPTICS_Maps_and_Plots.pdf` did not need rebuilding, since none of this entry's figure/map source scripts were re-run except the one HTML-map title patched directly above.

**What this doesn't change.** No hypothesis flips from significant to non-significant or back, and no headline coefficient changes — every number added this round is a new check *of* an existing result, not a replacement for one. The control-group DiD for H4 is, after this entry, the most heavily stress-tested single result in the study: it holds under the original cluster-robust and HC3 specifications, under leave-one-district-out, under randomization inference, and (for night-lights) under a log-scale transform — while the separate, still-open baseline-imbalance caveat from Entry 15/§6.7 remains exactly that: open, and correctly kept open rather than papered over by these new checks answering a different question.

## Entry 21

**Status.** Open finding, not fixed — a fresh, code-level, data-level check (prompted by an external review that raised the right *kind* of question — whether the 3-point trend and the 2021-vs-2025 headline could really be computed on the same footing — even though its own claims about the paper's current wording turned out to be wrong on inspection) turned up something real and more serious than anything that review actually named: the summer window's "Sikkim has zero valid data" claim, load-bearing across §4.2, §4.6, and the new §6.4 missingness paragraph from Entry 20, looks like it may itself be a stale archive-timing artifact, not a permanent fact about the data.

**What was checked.** `extract_satellite_data.py` (the two-point 2021/2025 extraction, behind the §4.2/§4.6 headline numbers) and `extract_multiyear_satellite_data.py` (the 2021/2023/2025 extraction added for §4.7) run the *identical* query for the summer window at 2021 and 2025: same collection (`COPERNICUS/S2_SR_HARMONIZED`), same QA60 cloud/cirrus mask, same 500m buffer, same June 1 – Oct 1 date range. Compared row-by-row on `village_id`, direct from the committed CSVs:

- `border_optics_village_results_summer_analyzed.csv` (two-point): all 31 Sikkim villages have `before_image_count = 0` and `after_image_count = 0` — zero Sentinel-2 scenes found, NDBI null, which is why Sikkim drops out of the 154-village summer sample.
- `border_optics_multiyear_summer.csv` (three-point, extracted later): the *same* 31 Sikkim villages, for the *same* 2021 and 2025 date ranges, show `ndbi_n_2021 = 24` and `ndbi_n_2025 = 31` — 24 and 31 scenes found, real NDBI values computed, nothing null.

This is the identical mechanism already disclosed in §6.9's buffer-radius work — the Sentinel-2 archive backfilling additional scenes for past dates between two extraction runs — just showing up here between the two-point and three-point summer extractions instead of between buffer radii, and not yet disclosed for this pair. It is not a code bug in either script (the query logic is identical in both); it is a real difference in what Earth Engine's archive returned at two different points in time. Full-year shows no such discrepancy — both extractions agree at 251/251 valid for both windows — so this is specific to the summer window's already-known cloud/monsoon-driven data sparsity, which apparently made the *original* summer extraction's timing sensitive to exactly which scenes had been backfilled into the archive by the day it ran.

**Why this matters more than a wording nitpick.** The 154-village summer sample is not a side detail — it is the basis for the §4.2 headline NDBI result, the §4.6 control-group DiD's summer-window n, the Holm correction's summer NDBI p-value, the buffer-sensitivity matched-subsample (also 154 villages), and Entry 20's own new missingness-mechanism paragraph in §6.4, which quantified a difference between summer-valid and summer-invalid villages that may partly describe a which-day-the-query-ran artifact rather than a stable selection mechanism. None of this is confirmed to be wrong — the 154-village result could very well survive a fresh extraction with Sikkim included, or the archive could have since re-stabilized differently — but it has not been re-verified since this discrepancy was found, and the honest thing is to say that plainly rather than let the "154, Sikkim excluded" framing stand as settled.

**Not fixed in this entry, and deliberately not fixed by editing prose alone.** This needs a live re-run of `extract_satellite_data.py --window summer` against a live Google Earth Engine session — unavailable in this sandboxed environment (no `ee.Authenticate()` credentials here) — and if that changes Sikkim's summer availability, every summer-window downstream number (§4.2, §4.6, Holm, §4.8's matched subsample, and Entry 20's four new checks, all of which are summer-window results) would need re-running against the new sample, not just re-described. Flagging this exactly the way Entry 18 flagged the unresolved UTM-in-control-selection issue: real, checked, not silently claimed as fixed, and left for a run this environment cannot perform.

**Recommended next step, not yet taken.** Re-run `python src/acquisition/extract_satellite_data.py --window summer` from a machine with an authenticated Earth Engine session. The script only re-queries rows missing any of its eight outcome/count columns (existing valid rows are left untouched), so this is safe to run and will not silently overwrite anything already valid — it will only fill in currently-null rows, Sikkim's 31 included, with whatever the archive returns today. If Sikkim villages come back with valid summer NDBI/lights, treat the resulting n as the new "as-extracted" summer sample and re-run, in order: `did_model.py --window summer`, `holm_correction.py`, `buffer_sensitivity.py`, and `extended_robustness_checks.py`, then rewrite every summer-window number those touch across the paper, Executive Summary, README, and dashboard rather than patching the current ones in place — and add an Entry 22 documenting exactly what changed and why, the same way Entries 15 and 18 documented their own re-extractions.

**Also checked while verifying this, and genuinely not real:** the external review's specific claims that "matched control group," "matched non-VVP control group," and "three independent stress tests"/"three independent methods in three more stress tests" are still present in the current abstract, §4.6, §4.9, the Discussion, the Conclusion, or `README.md` — grepped all of them directly against the current committed files; none of those phrases exist anymore, all correctly reflecting Entry 20's fixes. Two of the review's minor points are real but were never claimed as fixed by Entry 20 and remain open, low-priority wording items: the Executive Summary's "two independent compositing windows" (the two windows are alternative specifications over overlapping underlying satellite collections, not independent datasets) and the Limitations section's "natural experiment" phrasing (already immediately hedged in the same sentence as "not as a fully clean natural experiment," but "district-restricted observational DiD" would be tighter). Left both as-is pending a decision on whether they're worth a fifth wording pass, since they're cosmetic next to the archive-timing question above.

## Entry 22

**Status.** Entry 21's open question is now answered, and the answer overturns the study's central "surviving signal" narrative. A fresh, same-day, complete re-extraction of both the treated and control summer-window satellite data was run end-to-end, and every downstream summer-window test was recomputed against it. Sikkim's summer data is no longer missing. But once it's included — and once treated and control data are pulled on the same day so neither carries stale archive state relative to the other — every result that Entries 15-20 had built up as "the one signal that survives everything" (§4.2's headline NDBI change, §4.6's control-group DiD, the buffer-radius sweep, leave-one-district-out, randomization inference) goes from significant to non-significant. One new significant result shows up in its place (H3 NDBI border-proximity, previously a stable null), and it has not been stress-tested at all yet. This entry documents exactly what was rerun, two real script bugs found and fixed along the way, and every number that moved.

**Two script bugs found and fixed while re-running the extractions.** Both were latent — present before this entry, never triggered until a full re-extraction from a stale checkpoint was actually attempted.

1. `extract_satellite_data.py`'s resume logic read the checkpoint file directly and assumed it always carried `latitude`/`longitude` columns. The committed `border_optics_village_results_summer.csv` predates this script's current per-row-loop design (it carries `system:index`/`.geo`, leftovers from an earlier `Export.table`-based version) and never had lat/lon columns at all — only `border_optics_master_villages.csv` does. Resuming from it crashed with `KeyError: 'longitude'` the instant it reached any row still needing (re-)extraction. Fixed by merging coordinates back in from the master village list on `village_id` when the checkpoint lacks them, with a warning printed for any row that still can't be matched. Verified locally (258/258 rows recovered coordinates, zero missing) before it was run for real.
2. A second, different bug in `extract_control_satellite_data.py`'s coordinate-based resume-merge crashed with `KeyError: (27.903587, 96.940911)` (village Shirong, Anjaw) partway through a restart at row 610/735. Root cause: the aggregate "does this checkpoint match the current village list" check rounded coordinates with pandas' vectorized `Series.round(6)`, but each row's own per-row lookup key used Python's built-in scalar `round()` — the two rounding paths can disagree at the 6th decimal for some floating-point values even when the underlying number is the same, so a real, non-corrupted row failed an exact-match `.at[]` lookup and crashed the whole run. Fixed by using `Series.round(6)` consistently on both sides and replacing the fragile `.at[]` index lookup with a `dict.get()` that degrades gracefully (re-extracts the row) instead of crashing if a key is ever genuinely missing. Verified locally against the actual partial checkpoint (0 missing keys, 610/735 correctly recovered) before shipping.

**Why the treated-side fix produced a full re-extraction, not a partial one.** `extract_satellite_data.py`'s "already done" check tests for the per-metric column names (`ndbi_before_image_count`, etc.), which the old checkpoint never had — it only carried the older, generic `before_image_count`/`after_image_count`. Once the lat/lon fix let the resume proceed at all, every row failed the "already done" check and got re-extracted from scratch, not just Sikkim's. This was not a bug fixed separately — it was the mechanism that ended up (correctly, per the "whatever it takes, accuracy first" standing direction for this project) forcing a full, same-day-consistent re-pull of the entire 258-village treated summer sample, rather than only patching in Sikkim's 31 villages on top of an otherwise 4-year-old extraction date. The control-group extraction was restarted from scratch on the same basis, deliberately (old file renamed to `border_optics_control_results_summer.OLD_PRE_ENTRY22.csv` rather than resumed), so that treated and control summer data would not carry two different archive-snapshot dates into the same DiD comparison.

**Result: 258/258 treated (251 core + 7 Himachal-illustrative), 735/735 control, same day.** Both extractions are now fully populated with no missing rows on either side.

**`statsmodels` still unavailable in this sandbox.** Confirmed again (`pip install`, `apt-get install python3-statsmodels`, and a direct `pypi.org`/`files.pythonhosted.org`/`archive.ubuntu.com` fetch all return 403 from this environment) — same standing limitation Entry 20 hit. Reused Entry 20's approach: a from-scratch NumPy OLS with cluster-robust and HC3 sandwich covariance, re-validated line-for-line against the (unaffected-by-this-entry) full-year `did_model.py` output before trusting it on the fresh summer numbers — coefficients, SEs, and both cluster-robust and HC3 p-values reproduced to 9-10 significant figures, including the same non-obvious detail Entry 20 already flagged (statsmodels' default here is a normal/z-test, not a t-test).

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

**Documents updated in this entry.** `src/acquisition/extract_satellite_data.py` and `extract_control_satellite_data.py` (both bug fixes above). Regenerated with fresh data: `data/processed/border_optics_village_results_summer.csv` (258/258), `data/processed/border_optics_village_results_summer_analyzed.csv`, `data/processed/border_optics_control_results_summer.csv` (735/735, old version kept alongside as `..._OLD_PRE_ENTRY22.csv`), `data/processed/border_optics_did_panel_summer.csv`, `data/processed/border_optics_did_summary_summer.json`, `data/processed/border_optics_did_by_district_summer.csv`, `data/processed/border_optics_buffer_sensitivity_summary.json`, `outputs/holm_correction_results.csv`, `outputs/robustness_extended_results.json`, `outputs/leave_one_district_out_results.csv`. Not yet updated: `BO_Research_Paper.md`, `BO_Executive_Summary.md`, `README.md`, dashboard pages/data, static figures, PDFs — all still describe the pre-Entry-22 numbers and need a full rewrite, not a patch, once the reframing is decided.

**What this changes.** Nearly everything the paper currently calls its "surviving" or "significant" result. The honest summary, pending the rewrite: once the summer-window extraction is complete and same-day-consistent with the control group, none of the four core hypothesis tests (H1 built-up change, H4 control-group DiD for either outcome) shows a significant effect in the summer window any more than the full-year window already didn't — and the one new significant result (H3 NDBI border-proximity) is freshly discovered, not yet robustness-checked, and cuts against the paper's own prior framing of H3 as "a truly stable null." This is a different, and arguably cleaner, finding than the one the paper currently makes: not "an ambiguous, window-sensitive signal that survives stress-testing," but "no satellite-detectable effect survives once the data is complete and consistent, checked two ways, across two proxies, against a control group, and at three buffer radii" — which is still a real, defensible, and reportable answer to the question the Ministry of Home Affairs said had never been asked.

## Entry 23

**Status.** A full methodology audit, prompted by two independent external reviews of the post-Entry-22 push, was run against the current code rather than taken on the reviews' word — per this project's own standing rule that every claim gets checked against the actual repository before being acted on. Most of what both reviews flagged as numerical claims checked out exactly against this project's own regenerated files (the DiD coefficients, buffer-sensitivity p-values, leave-one-out counts, and the H3 correlation were all verified independently and matched to the figure shown). Two code-level claims were verified directly by reading the source, and one new, previously undocumented issue was found independently while doing so, described below. This entry documents findings only — the two code fixes it identifies are deliberately deferred to a future entry, per an explicit decision to do the free/documentation-only hardening first and the higher-cost re-extraction work separately.

**Confirmed: `select_control_villages.py` still computes distance in UTM 44N, inconsistent with the geodesic method `compute_border_distance.py` now uses.** `select_control_villages.py` line 40 sets `METRIC_CRS = "EPSG:32644"` with a comment claiming this is "the same CRS `compute_border_distance.py` uses" — that comment is now false; `compute_border_distance.py` was changed to a geodesic WGS84 calculation via `pyproj.Geod` for exactly the reason documented in its own module docstring (a single UTM zone distorts distance for a study area spanning roughly 20 degrees of longitude, from Ladakh to Arunachal Pradesh). Checked the actual scope of this inconsistency rather than assuming it invalidates everything downstream: `test_h3_border_proximity.py` and `holm_correction.py` (the H3 border-proximity tests) read `distance_to_border_km` from `border_optics_master_villages_with_distance.csv`, which is the treated-village file already computed geodesically — H1 and H3 are unaffected by this bug. The UTM distance is used only inside `select_control_villages.py`, for the soft eligibility filter (`d > max_dist * 1.5`) that caps how far from the border a candidate control village may be, and for the `distance_to_border_km` column stored on the 735 control-village rows themselves. This narrows the practical blast radius to the composition of the control pool used in the H4 (DiD) comparison — it does not touch H1, H3, the buffer-radius sweep, or the multi-year trend. Still a genuine correctness bug worth fixing (a soft filter computed with a systematically distorted distance measure could admit or exclude the wrong villages, especially for Arunachal Pradesh, far from UTM 44N's central meridian), just not the study-wide problem it could have been. **Deferred**, since fixing it requires regenerating the 735-village control list, re-running the control satellite extraction (over an hour per the timing noted in Entry 22), and re-running every H4 downstream output — a bigger job than this entry's documentation-only scope.

**Major new finding: 20 control villages sit at the exact same coordinates as 21 treated villages — the same physical settlement, entered twice under two different name spellings.** Started from a narrower check (do any control-village names match an official-but-ungeocoded VVP priority-village name?) and found 3 matches this way — see below — but then ran the more fundamental check directly: does any control village's coordinate (rounded to 6 decimals, sub-meter precision) exactly match a treated village's coordinate? It does, 20 times over, implicating 21 distinct treated villages (19 in Arunachal Pradesh, 2 in Uttarakhand — one coordinate has two treated villages, "Gumsing" and "Taying," matching a single merged control entry "Gumsing Taying"). Every one of these pairs is unmistakably the same OSM node under a different name string: transliteration variants (`Sibia`/`Sebia`, `Nisuk`/`Nissuk`, `Maliney`/`Malinye`, `Emuli`/`Emoli`, `Ngaming`/`Naming`, `Gamsali`/`Gamshali`), punctuation the exclusion filter's `normalize_name` doesn't strip (`Lengdi/Liang` vs. `Lengdi Liang` — the "/" survives NFKD-ASCII-folding since it's already ASCII, so these two strings never compare equal), a dropped/added qualifier (`Kongra(Metung)`/`Kongra`, `Hapuk (I)`/`Hapuk`, `Pado I`/`Pado`, `Angrim Valley`/`Angrim Valley Village`), and — the case no ASCII name-matching approach could ever have caught — OSM's alternate-language name tag surfacing in a different script entirely for the identical point: `Chate`/`赛探`, `Chulla`/`胡巴`, `Tarba`/`达尔巴` (Chinese), `Gunji`/`गूंजी` (Devanagari). `select_control_villages.py`'s exclusion logic is name-based only (`normalize_name(name) in treated_names`); it was never going to catch a same-point, different-script or different-transliteration collision, because there is no shared normalized string to match on. This is a bigger and more direct problem than the raw-list gap below — it means 20 of the 735 "non-VVP" control villages are, physically, VVP-I treated villages, not merely villages that happen to share a name with one.

**Narrower, related finding: 3 of the 735 control villages also share a name (not just a coordinate) with an official VVP-I priority village that was never geocoded, and so was never excluded from the control pool by the name filter either.** `select_control_villages.py` excludes candidate control villages by checking their normalized name against `treated_names`, built from `border_optics_master_villages_with_distance.csv` — but that file contains only the 251 core-sample villages that were *successfully geocoded*, not the full official priority-village universe. The raw per-state village lists in `data/raw/` (`arunachal_pradesh_vvp_villages.csv`, `sikkim_vvp_villages.csv`, `uttarakhand_vvp_villages.csv`) record 454, 46, and 51 official priority-village names respectively — 552 total against the 3 core states, versus 251 successfully geocoded, leaving 301 officially-named priority villages that were never checked against the Overpass control-candidate results at all. Checked the current 735-village control list against this fuller name set directly: 3 matches, all in Arunachal Pradesh — **Gai (Anjaw district), Tayeng (Kurung Kumey district), and Pamdung (Tawang district)** — each a village named in the official VVP-I list that could not be geocoded (so is absent from the treated sample) but that OSM/Overpass has under place=village or place=hamlet, and that consequently entered the "non-VVP" control group under its own real, VVP-listed name. These 3 are separate from, and do not overlap with, the 20 coordinate-exact duplicates above (different villages, different failure mode — one is a matching-logic gap, this one is a data-coverage gap).

**Combined scope: 21 treated villages have a physical or nominal duplicate in the 735-village control list (2.9% of the control group), all traceable to the exclusion filter's reliance on exact ASCII name matching.** This is very unlikely to be single-handedly reversing the reported DiD nulls (the effect sizes involved are small relative to 251/735-village group means), but it is a genuine, now-quantified defect in what "non-VVP control group" means as currently constructed, and a sharper fix than either the name-list-coverage fix alone or the UTM-distance fix above would deliver on its own. **Deferred** alongside the UTM fix, for the same reason: fixing it requires regenerating the control list (this time with BOTH a coordinate-proximity exclusion — e.g., drop any candidate within ~50m of any treated village, name matching aside — and the fuller official-name-list exclusion), re-running the control satellite extraction, and re-running every H4 downstream output. `tests/test_data_integrity.py`'s `test_no_treated_control_coordinate_overlap` now documents this exact count (20) as a known ceiling so a future run that makes it worse fails loudly, and one that fixes it can tighten the ceiling to 0.

**Checked and cleared: differential image-count between before/after periods is not driving the reported NDBI/lights change.** One review raised, as a general concern, whether an image-count asymmetry between periods (more or fewer usable Sentinel-2/VIIRS scenes in one period than the other, independent of any real ground change) could itself produce an apparent "change" via a compositing-sample-size artifact. Tested directly rather than left as an open worry: Spearman correlation between `(ndbi_after_image_count - ndbi_before_image_count)` and `ndbi_change` across the 251-village summer core sample gives ρ = 0.038, p = 0.551 — no detectable relationship. (The equivalent lights check could not be computed on this pass — the lights image-count difference column was constant across the sample tested, which needs a second look rather than being read as a null result; flagged here rather than silently dropped.)

**Also checked and found not to be a real issue:** the "natural experiment" wording objection raised by both reviews. Grepped every occurrence in `BO_Research_Paper.md`; the phrase appears twice, both times explicitly negated ("not a fully clean natural experiment," "rather than as a fully clean natural experiment") rather than asserted — this is already the correct framing and needs no change. This same point was raised and resolved once before, in a review predating Entry 20, and remains resolved.

**Documentation hardening done in this entry (no code or data changes):** `BO_Research_Paper.md` gained a "Primary and Secondary Estimands" subsection (§3.12) declaring which result the paper's headline conclusion actually rests on and which are pre-specified robustness checks, independent research questions, or unstressed exploratory findings; a causal-diagram subsection (§3.11) making explicit what the district-fixed-effects DiD does and does not control for; an explicit non-random-assignment caveat on the randomization-inference check in §4.6; and a corrected "three States" (was stale at "two States") in §3.10's description of the RQ2 budget correlation. A consolidated Threats-to-Validity table was added as new §6.10, tabulating every threat this paper already discusses individually plus the two new findings above, each marked with its current status (tested-and-resolved, tested-and-open, or identified-not-yet-tested) so a reader does not have to reconstruct that picture from ten separate limitations paragraphs. A standalone `ANALYSIS_FREEZE.md` was added recording the exact data-extraction state, tool versions, and primary/secondary estimand declaration this version of the paper is built on. A `tests/test_data_integrity.py` suite was added, asserting the specific invariants this project has broken before without noticing (duplicate control coordinates, treated/control coordinate overlap, non-unique village IDs, the exact core-sample and control-group counts, valid NDBI/date ranges) — exactly the class of error Entries 20-22 each found only after a robustness check surfaced a downstream symptom.

**Not done in this entry, and why.** The UTM-to-geodesic fix and the control-name-exclusion fix above are both real but deferred, per the explicit choice (made this entry) to separate zero-cost documentation hardening from the higher-cost re-extraction work rather than mix them. A genuine pre-treatment panel (Section 7.5), SCL/Cloud Score+ cloud masking as a sensitivity check, a Sentinel-1 SAR cross-check, building-footprint validation, and spatial-autocorrelation testing on the new H3 result were all raised by the external reviews and are judged genuinely valuable but out of scope for a solo-researcher project on the current timeline — logged here as known, deliberately not-pursued extensions rather than silently dropped, consistent with how Section 7 already treats similarly-scoped future work.

## Entry 24

**Status.** Both fixes Entry 23 identified and deferred — the UTM-vs-geodesic distance mismatch and the control-list contamination — are now fixed in `select_control_villages.py`. This entry covers the code change only; the corrected 735-village control list has not yet been regenerated, because doing so needs live Overpass/Nominatim access, which this working environment's network policy blocks (confirmed directly: both hosts return a proxy `connect_rejected`). The actual rerun, the control satellite re-extraction that must follow it, and every H4/DiD downstream output are still open — see "Not done" below.

**Fix 1: distance metric.** `select_control_villages.py` no longer reprojects into `EPSG:32644` (UTM 44N) for its border-distance filter. `load_border_union()` now returns the India boundary union in unprojected EPSG:4326 (used only to find *which* point is nearest), and `distance_to_border_km()` computes the actual reported distance geodesically via `pyproj.Geod(ellps="WGS84").inv(...)` — the identical method `compute_border_distance.py` already uses for the treated-village distances this filter's `max_dist * 1.5` threshold is compared against. Both scripts now agree on what "distance to border" means.

**Fix 2: contamination.** Two new exclusion checks were added to the candidate loop, both scoped to catch what Entry 23 found by working backward from a passing test rather than being caught during generation in the first place:

- A geodesic coordinate-proximity check (`nearest_treated_distance_m`, threshold 50m) against every treated village's coordinates — not just the current district's — run alongside the existing cross-district OSM-point dedup. A candidate within 50m of any treated village is treated as the same physical settlement recorded twice, regardless of what name OSM has attached to it. This is what actually would have caught the 20 exact-coordinate collisions (Sibia/Sebia, Gunji/गूंजी, and the rest of the list in Entry 23) — a name-based filter structurally cannot, no matter how good the normalization.
- A full official-priority-village name check (`load_official_priority_village_names()`, reading the three raw `data/raw/*_vvp_villages.csv` files directly) alongside the existing check against the 251 successfully-geocoded treated names. This is what would have caught the 3 name-only matches (Gai, Tayeng, Pamdung) — villages that are officially VVP-I listed but never geocoded, so their names never appeared in the old `treated_names` set at all.

**Verification done in this environment (Overpass/Nominatim unreachable, so not a live rerun).** Since the actual candidate-generation step needs network access this environment doesn't have, the new exclusion logic was instead verified by re-applying it to the *existing* 735-village control list — i.e., treating the already-fetched OSM candidates as input and checking how many the new rules would now catch. (`pyproj` also isn't installable here — same network restriction — so this verification used a plain-Python Haversine distance as a stand-in for the coordinate check; the committed script itself uses `pyproj.Geod`, which will run correctly on a machine with normal network/package access.) Result: the official-name check correctly finds exactly 3 matches, matching Entry 23's number precisely once the check is scoped the same way (against official names not already geocoded into the treated list — mathematically equivalent to the OR-condition structure the new code uses). The coordinate-proximity check at 50m finds 21 of the existing 735 control rows within range of a treated village — the same 20 exact-coordinate matches Entry 23 already documented, plus one additional case: control village "Jorging" (Upper Siang) sits 40.3m from treated village "Tenggo" (Upper Siang), a pair with no obvious name relationship to each other. This is a lower-confidence case than the other 20 — those are all unmistakably the same OSM node under a name variant or alt-script tag; Jorging/Tenggo could be the same reasoning, or could be two genuinely distinct hamlets 40m apart, which does happen in these village clusters. Flagged here rather than silently folded into the headline "20/21" count used elsewhere (`BO_Research_Paper.md` §6.10, `ANALYSIS_FREEZE.md`); it should be looked at manually (e.g., checking OSM's raw tags for both points) once the real rerun happens, rather than assumed either way.

**Resume-logic hazard, called out explicitly in the script's docstring.** `select_control_villages.py` checkpoints per district and skips districts already marked `district_verified` on resume — but every existing row in the current `border_optics_control_villages.csv` was verified under the OLD exclusion rules, not these new ones. Running the fixed script as-is would treat all 14 districts as already done and never re-check any of them. The script's module docstring now says explicitly: delete or rename the existing output file before rerunning, so every district is rebuilt fresh.

**Exact commands for the actual rerun (network/package access this environment doesn't have — must run on Sakshi's machine):**
```
mv data/processed/border_optics_control_villages.csv data/processed/border_optics_control_villages_PRE_ENTRY24_FIX.csv
python3 src/acquisition/select_control_villages.py
python3 src/acquisition/extract_control_satellite_data.py
```
followed by re-running whatever downstream script(s) consume `border_optics_control_villages.csv` / `border_optics_control_results*.csv` (H4 DiD, buffer sensitivity, leave-one-out, randomization inference, and the figures/dashboard/PDFs that embed those numbers) — the same downstream set Entry 22 re-ran after its own data correction.

**Not done in this entry.** The control list has not been regenerated (blocked by this environment's network policy, per above) — `border_optics_control_villages.csv` on disk is still the old, contaminated 735-row file, and every number in `BO_Research_Paper.md`, `ANALYSIS_FREEZE.md`, and the dashboard that depends on the control group (H4 DiD, buffer sensitivity, LOO, RI) still reflects that old file. This is a code fix awaiting a data fix, not a completed correction — do not read this entry as "the contamination is resolved." `tests/test_data_integrity.py`'s ceiling constants (`KNOWN_OVERLAP_CEILING = 20`, `KNOWN_CONTAMINATION_CEILING = 3`) are also left unchanged for the same reason: they describe the *current on-disk data*, which hasn't changed yet.

## Entry 25

**Status.** The Entry 24 code fix was actually run for real, on a machine with live Overpass/Nominatim/Earth Engine access, exactly per the "exact commands for the actual rerun" left at the end of that entry. The control list is regenerated, both contamination counts are independently confirmed at zero (not just under a documented ceiling), both satellite-extraction windows were re-pulled against the new list, both DiD models and the extended robustness suite were re-run against the new data, and — this is the headline of this entry — the one result the entire paper has been treating as its "surviving significant finding" since Entry 22 does not survive this fix. It was a symptom of the same contamination Entry 23 found and Entry 24 patched, not a real effect.

**What was actually run, and where.** This sandboxed environment still cannot reach Overpass, Nominatim, or Earth Engine (same network policy Entry 24 hit), so the full pipeline was run on the researcher's own machine: `mv` the old control list aside, `select_control_villages.py` (regenerate), `extract_control_satellite_data.py --window full_year`, `extract_control_satellite_data.py --window summer`, `did_model.py --window full_year`, `did_model.py --window summer`, `extended_robustness_checks.py` — the exact sequence Entry 24 specified, run to completion with no shortcuts. The resulting files were pulled back into this environment via the device bridge and independently re-verified here (test suite plus a direct recount) rather than taken on trust from the terminal output alone.

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

**Documents updated in this entry.** `tests/test_data_integrity.py` (`EXPECTED_CONTROL` 735→732, both known-ceiling constants tightened to 0, docstrings rewritten from "known, currently-failing" to "resolved"). `BO_Research_Paper.md` (Abstract; §4.6 heading and all five paragraphs; §4.9; §5 Discussion; §6.7; §6.10 table, two rows; §8 Conclusion). `ANALYSIS_FREEZE.md` (sample-sizes table, known-deferred-issues items 1-2, control-distance-metric row). `BO_Executive_Summary.md` and `README.md` (every reference to the 735-village count and the old full-year lights DiD numbers). `outputs/figures/08_control_group_did_effect.png` regenerated directly in this environment from the fresh JSON summaries (this figure only needed `matplotlib`/`pandas`/the JSON files, all available here, unlike the `statsmodels`-dependent model-fitting step itself); `09_multiyear_trend.png` and `10_buffer_sensitivity.png` were regenerated incidentally by the same script but are unaffected by this fix (neither depends on the control group) and their numbers are unchanged. Dashboard pages (`app.py`, `pages/1_Study_Design.py`, `pages/5_Statistical_Validation.py`, `pages/7_Interactive_Maps.py`, `pages/8_Methodology_Limitations.py`) still reference the old 735-count and old DiD numbers as of this entry being written and need the same sweep — see "Not done" below.

**Not done in this entry.** The dashboard pages listed above have not yet been edited (identified via grep, not yet fixed at the time of writing this entry — being done as a follow-up pass immediately after this entry, not deferred indefinitely). `BORDER_OPTICS_Maps_and_Plots.pdf` and the root/`static/` copies of `BO_Research_Paper.pdf`/`BO_Executive_Summary.pdf`/`BO_Development_Log.pdf` have not been rebuilt against this entry's text changes — `build_docs_pdfs.sh` needs to be re-run once every source `.md` file is finalized, the same two-step pattern Entry 20 used (text first, PDF rebuild once text is stable). The interactive Folium map (`outputs/interactive_maps/maps/village_treated_vs_control_map.html`) still shows the old 735-village control layer — regenerating it needs `folium`, unavailable via pip in this sandboxed environment (same restriction Entry 20 hit), so it is flagged here rather than silently left stale and unmentioned.

## Entry 26

**Status.** Entry 23's "genuinely valuable but out of scope" future-work item — a Sentinel-1 SAR cross-check, listed in `BO_Research_Paper.md` §7.1 — was actually pursued, alongside a second, previously-unplanned independent check (Google Dynamic World's "built" probability band, algorithm-independent of NDBI though not sensor-independent — see that extraction script's own docstring caveat). Both were run for treated and control, both windows (full_year, summer), against the current 258-treated/732-control sample this study has used since Entry 25's fix. One incomplete-extraction problem was found and fixed along the way, the same "checkpoint exists but the run behind it never finished" class of issue this project has hit before. Final numbers below are from `src/analysis/triangulation_analysis.py`, run with `statsmodels` on the researcher's own machine — not the sandbox's manual-OLS stand-in, which was used only to catch the bug below before a real run was attempted.

**What was extracted.** `src/acquisition/extract_dynamicworld_built.py` (GOOGLE/DYNAMICWORLD/V1 "built" band) and `src/acquisition/extract_sar_backscatter.py` (COPERNICUS/S1_GRD VV/VH, descending orbit) — both at the same 500m buffer and before/after windows as the primary NDBI extraction, both run treated+control × full_year+summer (eight extraction runs total). This sandbox has no Earth Engine access, the same standing limitation every prior entry's satellite work has hit, so all eight runs were done on the researcher's own machine and pulled back in via the device bridge.

**Bug found: `border_optics_control_sar_summer.csv` was a stalled checkpoint, not a completed extraction, and nothing in the pipeline would have caught this on its own.** Before the fix, this file had valid VV/VH values for only 50 of 732 control villages — and, tellingly, `sar_before_image_count`/`sar_after_image_count` were also null (not zero) for the other 682, meaning the extraction loop never reached those rows, as opposed to reaching them and finding zero usable Sentinel-1 scenes. `extract_sar_backscatter.py`'s resume logic itself is not buggy the way Entry 22's scripts were — it correctly checks all six outcome columns before treating a row as done, and correctly resumes from the checkpoint rather than the master list — but a checkpoint file existing at all does not mean the run behind it finished, and nothing short of actually counting valid rows against the expected total surfaces that. It was caught by running `triangulation_analysis.py`'s own H1/H4 logic (replicated by hand in a sandbox test harness, since `statsmodels` is unavailable in this environment) against the on-disk files before treating any result as final, per this project's standing rule of checking every claim against the actual data rather than taking a file's existence on trust. The other three SAR/Dynamic World files (treated SAR, both windows; control SAR full_year) were already complete (732/732 or 258/258, all outcome and image-count columns populated) — this was specific to one file, not a systemic problem.

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

`outputs/triangulation_results.json` holds the full machine-readable output. There is no statsmodels-verified "before-the-fix" number for the SAR-summer control DiD — the fix was applied as soon as the incompleteness was found, before a real `statsmodels` run was attempted on the partial file. The sandbox's manual-OLS approximation on that 50-village partial data had shown VV coef +0.11964, p=0.01441 and VH coef +0.14335, p=0.0001, both spuriously significant on a tiny, non-random (first-50-processed, not sampled) subset of the control group; both are gone once the extraction actually finished (p=0.717 and p=0.953 above).

**What this means for the paper.** SAR — the one check here that is genuinely sensor-independent (a different satellite constellation, radar rather than optical, immune to the cloud cover this study has hit real bugs over twice before, Entries 21-22 and the buffer-radius same-day gap) — is null on both bands, both windows, every specification. This is the strongest new evidence for this study's existing headline claim (Entry 25's "no satellite-detectable effect... full stop"): a completely independent sensor was pointed at the same villages and found nothing either. Dynamic World — algorithm-independent but not sensor-independent, same Sentinel-2 source imagery as NDBI per that script's own docstring — disagrees: a small, statistically significant increase in "built" probability in treated villages relative to control, in both windows, at an effect size of roughly +0.003 to +0.007 on a 0-1 probability scale. This is real and robust in the narrow sense that it reproduces to several significant figures between the sandbox's manual OLS and the actual `statsmodels` run, and both windows agree in sign and rough magnitude — it is not a repeat of Entries 22/25's contamination-driven artifacts, and it was not affected by this entry's SAR-checkpoint bug (Dynamic World's own image-count columns were fully populated throughout; its nulls are genuine no-cloud-free-scene cases). It does not overturn the primary NDBI-based estimand — NDBI, not Dynamic World, is the primary estimand per `ANALYSIS_FREEZE.md` — and the two checks that are actually sensor-independent (SAR VV, SAR VH) both support the null. But it is a genuine, honest complication for a triangulation section that hoped for three-out-of-three agreement, and needs to be reported as such, not folded silently into "the null is confirmed."

**`BO_Research_Paper.md` updated, in a follow-up pass immediately after this entry (not deferred indefinitely, same pattern as Entry 25's dashboard-page follow-up).** A new §4.10 ("Independent Triangulation: SAR and Dynamic World Cross-Checks") reports all three checks in full — SAR's confirmation of the null on both bands and both windows, and Dynamic World's small-but-significant disagreement, stated as an honest caveat rather than folded into a "three-for-three" triangulation claim this study cannot actually make. §7.1 ("SAR-Based Change Detection") is rewritten from a future-work proposal to a completed-check pointer at §4.10. §6.10's Threats-to-Validity table gains a new row ("Single-sensor / single-algorithm dependency") marked partially resolved, on the same logic. This was a text-only addition — it does not touch the primary NDBI/lights estimand or its control-group DiD, so it did not need the paper-wide rewrite Entries 22 and 25 each required for an actual headline-number change.

**`ANALYSIS_FREEZE.md` also updated**, gaining a new item 6 in "Known, deferred issues" marked partially resolved (SAR confirms the primary estimand's null; Dynamic World's disagreement is reported, not resolved), cross-referencing this entry and `BO_Research_Paper.md` §4.10, per that file's own stated convention.

**Not done in this entry.** `BO_Executive_Summary.md`, `README.md`, and the dashboard pages make no mention of either check. The root/`static/` PDF copies of `BO_Research_Paper.pdf`/`BO_Development_Log.pdf` have not been rebuilt against this entry's text changes (`build_docs_pdfs.sh`, same two-step pattern as every prior entry that touched paper text).

## Entry 27

**Status.** Four of the open items Sakshi asked to be worked through after Entry 26 — the unexplained Dynamic World divergence, both remaining §7.6 H3 stress-test items (linearity, multi-year cross-check), and the previously-identified-but-untested spatial-autocorrelation threat (§6.10) — were run this entry, all against data already on disk, no new Earth Engine extraction needed. Two genuinely new findings came out of it, one of them a direct structural echo of this study's own Entry 21-22 history. The remaining open items from that list (pre-treatment panel, buffer-radius same-day re-extraction, ground-truth candidates, building-footprint check, RTI drafting) need either live Earth Engine access or real-world action and are tracked separately, not covered here.

**Dynamic World investigation, finding 1: the effect is broad-based, not outlier-driven, and not a baseline-imbalance artifact.** Dropping the 5 highest- and 5 lowest-|built_change| treated villages moves the full-year mean from +0.00673 to +0.00621, and the summer mean from +0.00711 to +0.00655 — a handful of leverage points are not carrying this result. Treated-vs-control baseline (`built_before`) balance is clean in both windows (Mann-Whitney p=0.996 full-year, p=0.155 summer), so this is not last entry's contamination/imbalance story replaying under a new proxy.

**Dynamic World investigation, finding 2: a genuine and unexplained asymmetry — the increase is concentrated in treated villages that already had a higher baseline "built" probability, and control villages show the opposite pattern.** Spearman(built_before, built_change) for treated villages is +0.272 (p=0.00001, full-year) and +0.124 (p=0.109, summer, not significant on its own) — villages that started more built-up increased more. Control villages show no such relationship in full-year (rho=+0.020, p=0.585) and a significant *negative* one in summer (rho=-0.229, p<0.00001) — control villages that started more built-up tended to decrease, the more ordinary regression-to-mean/ceiling pattern expected on a bounded 0-1 probability scale. Treated villages do not show that ceiling effect; if anything they show the reverse. Two explanations are both plausible and neither is tested here: a real "existing settlements densify preferentially" pattern specific to VVP-I investment, or a measurement-sensitivity artifact where already-more-built-up villages simply produce a less noisy "built" probability estimate in which a small real or spurious change is easier for Dynamic World's classifier to register. Left open, flagged in the paper rather than adjudicated.

**Dynamic World investigation, finding 3 — a structural echo of Entries 21-22: all 31 Sikkim treated villages are null in the summer window, none in the full-year window.** Checked directly: 0 of 31 Sikkim core-sample villages have valid summer `built_change`; the same 31 are all valid (though weak: mean change +0.00098, far below Arunachal Pradesh's +0.0075 and Uttarakhand's +0.0078) in the full-year window. This is the exact shape of the bug Entry 21-22 found and fixed for NDBI — a whole state's summer data going to zero — except this time it's Dynamic World's own Sentinel-2 L1C pull, not the SR-Harmonized NDBI pipeline Entry 22 fixed, and it has not been checked whether this is a genuine monsoon-cloud blackout (plausible, and consistent with why this study runs a summer-matched window check at all, §2.4) or another archive-backfill snapshot artifact like the one Entry 22 found and resolved by simply re-extracting later. Not re-extracted or resolved in this entry — flagged rather than assumed either way. Practically, this means the summer Dynamic World DiD (+0.00736, p=0.00133) is estimated on a treated sample missing an entire state that, in the full-year window, shows the weakest signal of the three — so the summer result may be inflated by Sikkim's absence in a structurally similar way to the pre-Entry-22 NDBI summer result, though unlike that case this has not been confirmed either way by an actual re-extraction. The full-year Dynamic World DiD, which does include Sikkim and is still significant (p=0.01168) despite Sikkim's weak individual contribution, is the more trustworthy of the two windows for this reason.

**Dynamic World investigation, finding 4: a weak, real, but modest image-count correlation, in opposite directions for treated and control.** Spearman(image-count difference between periods, built_change) for treated villages: rho=+0.126 (p=0.047, full-year), rho=+0.172 (p=0.025, summer) — villages that gained more usable scenes between periods show slightly more "built" increase. For control villages the same check gives the opposite sign: rho=-0.076 (p=0.042, full-year), rho=-0.117 (p=0.006, summer). Both are real (significant) but small, and opposite-signed between groups, so this does not look like a single, consistent imaging-density artifact driving the treated-control gap the way Entry 23 tested for and ruled out in NDBI (that check came back null, ρ=0.038, p=0.551; this one does not come back null, but it is much weaker and sign-inconsistent, so it is reported as a genuine partial confound worth naming, not a full explanation).

**H3 §7.6 item 1 (linearity), finding: the summer NDBI-proximity correlation is clean and close to linear across the full distance range; the full-year lights-proximity correlation is not, on inspection of its binned means, even though a formal linear-vs-quadratic F-test does not flag it.** Summer NDBI-change in five equal-sized distance quintiles rises monotonically: -0.0182, -0.0074, +0.0009, +0.0071, +0.0135 (nearest to farthest) — genuinely progressive, not concentrated at either end (quadratic term F=0.89, p=0.347, not significant). Full-year lights-change in the same five bins: +0.0815, +0.1557, +0.0090, +0.0073, +0.1765 — not monotonic at all; it rises, falls twice, then jumps back up in the farthest bin. The quadratic F-test on this one is also not significant (F=0.69, p=0.406), so a simple curved-relationship story doesn't fit either, but the honest read of the binned means is that this correlation's shape looks more like a small number of districts happening to sit at particular distances than a smooth proximity gradient. This is a real caveat for the full-year lights-proximity result specifically, distinct from and in addition to its already-reported leave-one-out/randomization-inference robustness (§7.6, established before this entry).

**H3 §7.6 item 2 (multi-year cross-check), finding: both H3 results replicate against the independent 3-point extraction in overall direction and magnitude, but neither is stable across both sub-periods — one reverses sign.** Distance vs. the full 2021-2025 multi-year-extraction change reproduces the headline numbers closely (summer NDBI rho=+0.293 vs. the two-point extraction's +0.291; full-year lights rho=-0.252 vs. -0.252 exactly) — a genuine independent-data consistency check, not a tautology, since the multi-year extraction (Section 3.8) is its own separate pull. Split into the two sub-periods, summer NDBI's relationship reverses: distance vs. 2021-2023 change is rho=+0.426 (p<0.00001, same direction, stronger), but distance vs. 2023-2025 change is rho=-0.222 (p=0.0004, opposite sign, significant). Full-year lights is more consistent but still uneven: 2021-2023 rho=-0.239 (p=0.0001, same direction), 2023-2025 rho=-0.078 (p=0.218, same direction but no longer significant). Read together with Section 4.7's own finding that the aggregate two-point NDBI comparison hides a decline-then-recovery pattern within it, this says the border-proximity relationship is not a steady, one-directional gradient holding constant across the study period either — for NDBI it is actually opposite-signed in the two halves, netting out to the reported positive correlation over the full period; for lights it is concentrated in the earlier half. Neither finding invalidates the headline H3 correlations (both are real, Holm-significant results on the actual 2021-2025 comparison this study specifies), but both are now known to be less temporally stable than a report of "ρ=0.291, p=0.0000026" alone would suggest.

**Spatial autocorrelation, finding: confirmed present and significant, not merely a theoretical concern — and it survives even after removing the effect §7.6 is testing in the first place.** §6.10's Threats-to-Validity table listed this as "identified, not yet tested." It is now tested. `libpysal`/`esda` are not installed in this sandbox, so Moran's I was computed by hand (k=8 nearest-neighbor weights by haversine distance, permutation-based p-value, 999 shuffles — the same "implement it from scratch when the package isn't available" approach this project used for OLS in Development Log Entries 20/22 and again in Entry 26's manual test harness). Summer NDBI-change: Moran's I = 0.346 against a null mean of -0.002 (SD 0.029), permutation p = 0.001. Full-year lights-change: I = 0.076 against a null mean of -0.004 (SD 0.020), p = 0.004. Both are real, positive, significant spatial clustering — nearby villages' outcomes move together more than chance would predict. Crucially, this is not simply restating the H3 distance relationship itself: recomputing Moran's I on the *residuals* of summer NDBI-change after removing the linear distance-to-border trend still gives I = 0.272, p = 0.001 — nearby villages resemble each other for reasons beyond their shared distance-to-border. This means the 251 core-sample villages are not the statistically independent observations every test in this study (H1's Wilcoxon, H3's Spearman and its own randomization-inference check, H4's cluster-robust SE which already clusters by district but not by finer-grained proximity) implicitly treats them as, and the true effective sample size is smaller than 251 — which, in the standard direction this kind of clustering biases things, means every p-value in this study is probably somewhat more optimistic than it should be, H3's most of all since it is the test most directly about spatial structure. A properly spatially-corrected test (an effective-sample-size adjustment or a spatial permutation null, per Dutilleul (1993) or a spatial-lag/error model) is the natural next step and was not run in this entry — this entry establishes that the correction is needed and quantifies the clustering, not what a corrected p-value would be.

**What this means for the paper.** None of these four findings changes the primary NDBI estimand's own conclusion (Sections 4.2, 4.6, §7 SAR check) — all four are about secondary or exploratory results (Dynamic World, H3, and the general independence assumption underlying every test's stated p-value). All four make this study's own reporting more honest, not less favorable to it: naming a real, unexplained asymmetry and a Sikkim-summer echo in Dynamic World rather than treating "the disagreement is real" (Entry 26) as the end of the inquiry; naming that one of the two surviving H3 results doesn't look like a clean gradient on inspection, and that neither is stable within the study period despite both replicating against an independent extraction; and naming, with an actual number, that this study's stated p-values are probably a bit too confident because villages cluster in space. This is the same standing approach Entries 21, 22, 23, and 25 each took toward a result that looked fine until checked harder — apply it here too, even though none of these four checks flips a headline conclusion the way those did.

**Documents updated in this entry.** `BO_Research_Paper.md`: §4.10 gains a new paragraph reporting Dynamic World's baseline-dependency asymmetry and the Sikkim-summer parallel; §7.6 is rewritten from "two of three checks done" to report the linearity and multi-year-cross-check findings, replacing "left as future work" with "done, with findings, both partial"; §6.10's spatial-autocorrelation row is updated from "identified, not yet tested" to "tested, confirmed present and significant, not yet corrected for"; a new §6.11 ("Spatial Autocorrelation: Confirmed, Not Yet Corrected For") is added. `ANALYSIS_FREEZE.md` is not updated in this entry — none of these four findings changes the primary estimand or the freeze's own declared scope, unlike Entry 26's SAR item.

**Not done in this entry.** The remaining items from the same request — a genuine pre-treatment panel (§7.5), a same-day buffer-radius re-extraction (§6.9), ground-truth positive-control candidates (§7.3), a building-footprint cross-check (§7.2), and RTI draft text for Himachal Pradesh/Ladakh (§7.4) — are tracked as separate, ongoing work; the first two need live Earth Engine access this sandbox does not have and are being prepared as ready-to-run scripts for Sakshi's own machine, the next needs web research (in progress separately), and the last needs Sakshi to actually file it, not something automatable. A spatially-corrected p-value for H3, identified as the natural next step above, is also not computed in this entry.

## Entry 28

**Status.** `src/acquisition/extract_pretreatment_baseline.py` (new) and `src/analysis/pretreatment_placebo_test.py` (new) are written and ready to run on Sakshi's machine for Section 7.5's pre-treatment panel; `src/acquisition/extract_buffer_sensitivity_data.py`'s docstring now documents the exact resume hazard and same-day rerun sequence Section 6.9 needs, rather than requiring a new script (the 250m/1km extraction logic already existed and was already correct — the gap was purely that it and the 500m primary run were never pulled on the same day, and a bare re-run of either would silently skip everything as already-done instead of pulling fresh data). Neither has been run for real yet — both need live Earth Engine access this sandbox does not have. Separately, and completed for real in this entry: a ground-truth positive-control search (Section 7.3) that the paper had twice previously reported as unsuccessful.

**Ground-truth positive control: found, and the result is this study's most important secondary finding to date.** News coverage of an official two-day tour of Anjaw district, Arunachal Pradesh, by the state's Deputy Chief Minister (Arunachal Times, `arunachalobserver.org`, 31 October – 1 November 2023) documents 15 specific, named, dated projects inaugurated across several Anjaw villages. Checked each village name against this study's 258-village geocoded sample directly: three matches — **Walong** (civil terminal building at Walong's advanced landing ground; 30-bed girls' hostel at Walong Govt. Secondary School), **Kaho** (basketball court, solar street lights, school library, explicitly reported as VVP-funded), and **Musai** (solar street lights and other "model village" facilities, also explicitly VVP-attributed). Two other villages named in the same coverage — Kibithoo and Tinai — are not in the geocoded sample and were not usable.

Pulled each of these three villages' individual values from the extractions already on disk (no new extraction needed) across all four proxies, full-year window, 2021-before vs. 2025-after:

| Village | NDBI change | VIIRS lights change | Dynamic World "built" change | SAR VV / VH change (dB) |
|---|---|---|---|---|
| Walong | -0.038 | +0.909 (0.892→1.801, ~doubling) | +0.016 | -0.08 / +0.13 |
| Kaho | -0.057 | +0.420 (0.514→0.934, +82%) | +0.044 | +0.11 / +0.19 |
| Musai | -0.064 | +0.011 (0.317→0.328) | +0.006 | -0.04 / +0.07 |

VIIRS night-lights clearly registers the confirmed new infrastructure at Walong and Kaho, both well above this study's own pooled full-year lights mean change. NDBI moves in the *wrong direction* at all three villages, despite independently-confirmed new construction in the exact comparison window. Dynamic World shows a small positive change at all three, directionally consistent though far smaller than lights'. SAR shows no clear signal at any of the three, consistent with SAR's own pooled null (Section 4.10).

**Why this matters, and its limits.** This is a 3-village case study drawn from one official visit to one district, not a random sample of VVP-I's investment portfolio — it cannot establish that VIIRS is "the correct" proxy for this programme in general, or that NDBI is simply wrong. But it is real, sourced evidence — not a plausible-sounding conjecture, which is what Section 7.2's "NDBI's 500m buffer might be too coarse for VVP-I's actual investment scale" argument was before this entry — for a specific, useful explanation of part of this study's own pooled null: the confirmed projects here (solar streetlights, a hostel, a basketball court, a terminal building) are small, point-scale additions that shift a radiance sensor's reading directly but are a rounding error inside a 500m-radius reflectance average dominated by terrain, vegetation, and existing built surface. It also gives a first empirical reason to weight this study's own night-lights results (Section 4.3) somewhat more heavily than its NDBI results specifically for detecting *this kind* of small infrastructure investment, though not enough evidence on its own to reweight the study's headline conclusion, which is stated in terms of NDBI as the primary estimand (Section 3.12) regardless.

**Documents updated in this entry.** `BO_Research_Paper.md`: §6.6 ("No Ground-Truth Validation") rewritten to report the finding and point to §7.3; §7.3 ("Ground-Truth Positive-Control Validation") rewritten from "not found" to the full sourced case study with the table above. `src/acquisition/extract_pretreatment_baseline.py` and `src/analysis/pretreatment_placebo_test.py` added (new files, not yet run). `src/acquisition/extract_buffer_sensitivity_data.py`'s docstring updated with the same-day rerun sequence. `ANALYSIS_FREEZE.md` is not updated — the ground-truth finding is a secondary case study, not a change to the primary estimand's own frozen scope.

**Not done in this entry.** The pre-treatment and buffer-radius scripts above still need to actually be run on Sakshi's machine before Section 7.5/6.9 can report real numbers. A building-footprint cross-check (§7.2) and RTI draft text for Himachal Pradesh/Ladakh (§7.4) are tracked separately and not done here.

## Entry 29

**Status.** The last two open items from the same punch list are now done as far as they can be from this sandbox: a building-footprint extraction script and its validation companion for Section 7.2, and a full draft RTI application for Section 7.4. Both are deliverables prepared here for action elsewhere, not results — neither has been run or filed yet.

**Building-footprint check (§7.2): `extract_building_footprints.py` and `building_footprint_validation.py` added, with a scope correction recorded up front rather than discovered later.** Section 7.2 as originally written implied a before/after building-footprint comparison, symmetric with this study's other before/after extractions. Checked directly before writing the extraction script: Google's Open Buildings dataset (used here) and Microsoft's Global ML Building Footprints are both single-vintage products, not multi-temporal time series — there is no "2021 Open Buildings" to difference against a "2025 Open Buildings" the way ndbi_before/ndbi_after are differenced elsewhere. This is recorded in the new script's own docstring, the same way `extract_dynamicworld_built.py` recorded and explained ruling out GHSL for a comparable reason (Development Log entries around the original Dynamic World extraction). What the new pair of scripts actually does instead: extract a single current-vintage building count/area per village buffer (`extract_building_footprints.py`, treated and control), then cross-sectionally validate this study's own NDBI/lights/Dynamic World "after" values against it (`building_footprint_validation.py`) and specifically check whether Walong, Kaho, and Musai (Entry 28's ground-truth case study villages) show a building-footprint count consistent with the confirmed new construction. Neither script has been run — both need live Earth Engine access this sandbox does not have.

**RTI draft (§7.4): full application text drafted and delivered, `docs/RTI_draft_HP_Ladakh_village_lists.md`.** Combined application to the Ministry of Home Affairs' CPIO (Border Management Division) requesting the village-wise lists behind the 75 Himachal Pradesh and 35 Ladakh villages the Ministry has already confirmed in count via Lok Sabha/Rajya Sabha replies (cited by exact question number and date in the draft) without publishing the names — the same two gaps Section 6.1 documents. Includes filing mechanics (RTI Online Portal vs. postal, fee, CPIO address, Section 7(1) 30-day timeline, first-appeal path if it stalls), a note on when to split it into two separate applications instead of one combined submission, and a short follow-up procedure for geocoding whatever village names come back through this study's existing `geocode_villages.py`/`geocode_villages_bhuvan.py` pipeline once (if) a response arrives. Filing this is a real-world action only Sakshi can take — nothing here does that for her.

**What this means for the paper.** Neither item changes anything reportable yet — a written-but-unrun script and a written-but-unfiled RTI application are preparatory work, not findings. Sections 7.2 and 7.4 are left as future work in `BO_Research_Paper.md`, correctly, since nothing has actually been extracted or received. This closes out every item Sakshi asked to be worked through after Entry 26 that could be done without live Earth Engine access, a live RTI filing, or a wait for the Ministry's response: Entries 26-29 between them cover the Dynamic World investigation, both remaining §7.6 H3 checks, spatial autocorrelation, the ground-truth case study, and now these last two. The three genuinely unstarted next actions are all on Sakshi's side: run the pre-treatment and buffer-radius extractions (§7.5, §6.9) and the building-footprint extraction (§7.2) on a machine with Earth Engine access, and file the RTI (§7.4) — each logged here as a specific, named, ready-to-execute next step rather than a vague "future work" line.

**Documents updated in this entry.** `src/acquisition/extract_building_footprints.py` and `src/analysis/building_footprint_validation.py` added (new files). `docs/RTI_draft_HP_Ladakh_village_lists.md` added (new file). `BO_Research_Paper.md` is not updated in this entry — nothing here has a result yet to report into it.

**Not done in this entry.** Running any of the four now-ready scripts (`extract_pretreatment_baseline.py`, `extract_buffer_sensitivity_data.py`'s same-day sequence, `extract_building_footprints.py`, and their analysis companions) and filing the RTI application are all still outstanding, and all require action outside this sandbox.

## Entry 30

**Status.** `extract_pretreatment_baseline.py` and `extract_building_footprints.py` (both written in Entry 29) were actually run for real on Sakshi's machine — all 6 combinations (4 pre-treatment, 2 footprint) completed cleanly on the first pass, no failures, via the `run_all_new_extractions.py` one-command runner (also Entry 29). `pretreatment_placebo_test.py` and `building_footprint_validation.py` were then run against the results. Both produce real findings, one of them significant enough to change how a section of the paper is written.

**Pre-treatment placebo test (§7.5): 3 of 4 combinations clean, 1 flagged.** Full-year NDBI (placebo DiD coef +0.00196, p=0.864), full-year lights (-0.00665, p=0.755), and summer lights (+0.00047, p=0.968) all show no significant 2019-to-2021 divergence between treated and control villages — a period during which VVP-I could not have had an effect. This is genuine, direct evidence for this study's own parallel-trends assumption in three of four combinations, not merely an assumption asserted and left untested. Summer NDBI is the exception, and it does not get rounded up to a clean pass here just because the script's own auto-verdict function (a bare p>0.05 check) printed "PASSES": the district-fixed-effects placebo DiD coefficient is +0.01287 with p=0.06429 — borderline, not clearing the conventional threshold but close to it — while the raw, unadjusted Mann-Whitney comparison of the same two groups' distributions is sharply significant, p=0.00001. Read together: district composition absorbs most, but evidently not all, of a real pre-existing difference in how treated and control villages' summer NDBI moved between 2019 and 2021. Checked whether this pre-period effect could explain away the real, already-null summer NDBI DiD (Section 4.6, coefficient -0.00357): it cannot in any simple sense, since the pre-period effect (+0.01287, treated trending up) runs in the *opposite* direction from the real result, not the same one — a naive "the pre-trend explains the main result" story does not fit the actual signs.

**Building-footprint validation (§7.2): a real, previously-unavailable calibration result for the Section 4.10 Dynamic World disagreement.** Cross-sectional correlation between an independent, non-satellite-index building-footprint count (Google Open Buildings, confidence ≥ 0.75) and each proxy's 2025-era level: NDBI rho=0.399 (p<0.00001), night-lights rho=0.478 (p<0.00001), Dynamic World "built" probability rho=0.808 (p<0.00001) — Dynamic World's correlation with actual, independently-detected building footprints is roughly double NDBI's. This is a level correlation, not a change-detection test, so it does not resolve Section 4.10's disagreement about which proxy correctly detects *change* — but it is real evidence, not a plausible-sounding excuse, that Dynamic World's classifier tracks ground-truth built structure in this terrain noticeably better than NDBI's fixed two-band formula does, which is directly relevant context for how much weight Section 4.10's Dynamic World finding deserves relative to NDBI's own null. The three Section 7.3 case-study villages' building counts (Walong 524, Kaho 78, Musai 108, against a sample median of 34) confirm they are all real, moderate-to-large settlements, not negligible hamlets where a small addition would move a percentage-based index dramatically — consistent with, and a further concrete reason for, why NDBI's 500m area-average missed the confirmed new construction at all three (Section 7.3).

**What this means for the paper.** Two sections move from "future work" to "done, with a real result": §7.5 is now mostly reassuring for this study's DiD design, with one specific, honestly-flagged exception rather than either a blanket "resolved" or leaving the concern as abstract and untested. §7.2 produces a genuinely new piece of evidence bearing on Section 4.10's still-open Dynamic World-vs-NDBI disagreement — not resolving it, but giving a concrete, sourced reason to weight Dynamic World's reading of these villages more seriously than "it disagrees with the primary estimand, so it's probably noise" would suggest. Neither finding changes the primary NDBI estimand itself (Section 3.12) or this study's headline null.

**Documents updated in this entry.** `BO_Research_Paper.md`: §7.5 rewritten from "doesn't exist" to the full placebo-test account, including the flagged summer NDBI exception; §7.2 rewritten from a proposal to the full building-footprint validation account; §6.10's "genuine parallel pre-trends" row updated from "Open" to "Mostly resolved," with the exception stated in the table itself rather than only in prose. `ANALYSIS_FREEZE.md` item 4 updated from open to mostly resolved, cross-referencing this entry.

**Not done in this entry.** The same-day buffer-radius re-extraction (§6.9) has still not been run — it is independent of everything in this entry and remains the one open item from the original punch list that needs Sakshi's own machine time. `BO_Executive_Summary.md`, `README.md`, and the dashboard pages still do not reflect any of Entries 26-30's findings — the documentation sweep flagged as outstanding since Entry 26 remains outstanding.

## Entry 31

**Status.** The last open item from the original punch list — the same-day buffer-radius re-extraction flagged in §6.9 — was run for real on Sakshi's machine. All three radii (500m primary via `extract_satellite_data.py --window summer`, then 250m and 1000m via `extract_buffer_sensitivity_data.py`) were re-extracted back-to-back on the same day, after first renaming aside the three stale, non-same-day checkpoint files so none of the three scripts could silently skip-as-already-done against old data. All three completed cleanly: 258/258 (500m primary extraction) and 258/258 at each buffer radius, no failures. `analyze_results.py` was then re-run to regenerate the 500m "analyzed" file from today's fresh extraction (the pre-existing `buffer_sensitivity.py` reads that file, not the raw one, for its 500m leg), and `buffer_sensitivity.py` itself was run to produce the real three-radius comparison.

**Result: still a clean null at all three radii, and the archive-timing fix barely moved the numbers.** NDBI Wilcoxon (core sample, n=251 at every radius, matched — no coverage gap between radii this time): 250m mean change +0.00175, p=0.121369; 500m mean change -0.00090, p=0.435831; 1000m mean change -0.00293, p=0.897611. Night-lights: 250m p=0.999976, 500m p=0.999994, 1000m p=1.000000 — also null at every radius. Compared to the previous, timing-inconsistent version of this table (250m p=0.126, 500m p=0.436, 1km p=0.899, mixing three different archive-snapshot dates), only the 250m number moved at all, and only slightly (0.126 → 0.121). This is the honest resolution of §6.9: the archive-timing confound it flagged was real in principle — Sentinel-2's archive does keep backfilling scenes for past dates, exactly as Entries 21-22 found for the primary treated/control comparison — but it turns out to have been immaterial in practice for this particular comparison, since fixing it changed almost nothing.

**One thing not to round past: NDBI's mean change is not consistently signed across the three radii even now** — positive at 250m (+0.00175), negative at 500m (-0.00090) and 1000m (-0.00293) — though none of the three comes close to significance. This is worth stating plainly rather than only reporting the p-values: if there were a real built-up-change effect large enough to matter, a wider or narrower buffer capturing slightly more or less of the same village footprint would be expected to at least agree on direction, and this one does not. That is additional, not contradictory, evidence for the section's own null conclusion, not a complication of it.

**What this means for the paper.** §6.9 moves from "open, flagged" to "resolved" — the last item on the original six-item punch list. §4.8 is rewritten with the real same-day numbers (including the mean-change sign-inconsistency note) in place of the previous three-different-dates comparison. §4.9's inline buffer-sweep p-values and the Abstract's own buffer-sweep mention are both updated to match. §6.10's "archive-timing inconsistency" table row now reads "Resolved" for both halves (primary comparison and buffer sweep) instead of "resolved for the primary comparison; still open for the buffer sweep."

**Documents updated in this entry.** `BO_Research_Paper.md`: §4.8 rewritten with real same-day buffer-radius numbers; §6.9 rewritten from open gap to resolved; §6.10 table row updated; §4.9 and the Abstract's inline buffer-sweep p-values updated to match. `ANALYSIS_FREEZE.md`: buffer-radii sensitivity row updated to note same-day extraction; item 3 in "Known, deferred issues" updated from open to resolved, with the real numbers and the sign-inconsistency note.

**Not done in this entry.** This closes the entire original six-item punch list (§6.9 was the last one). What remains outstanding, unchanged from Entry 30's own list and not part of that punch list: `BO_Executive_Summary.md`, `README.md`, and the dashboard pages still do not reflect Entries 26-31's findings; PDF rebuilds via `build_docs_pdfs.sh` have not been re-run against any of these entries' edits; `requirements-lock.txt` (a `pip freeze` snapshot) has still not been generated; and `ANALYSIS_FREEZE.md`'s own git-commit-hash field is still blank.

**One more fix while checking the paper end-to-end for this entry.** Section 6.10's summary table had two stale rows left over from before Entries 28 and 30 closed the sections they summarize: the "NDBI as a proxy for development" row still said "Identified, not yet tested," and the "no ground-truth validation" row still said "Open," even though §7.2's building-footprint correlation and §7.3's ground-truth case study (both completed in Entry 30 and Entry 28 respectively) had already answered both in the body text. Fixed both rows to match what the rest of the paper already said — this was a documentation-consistency gap, not a new analysis.

## Entry 32

**Status.** Sakshi asked for the five remaining genuinely-open items from the previous "is research complete?" assessment to be closed. Four of the five turned out to be answerable with analysis alone, using data this study had already extracted — no new Earth Engine calls needed, so this entry was run directly in the sandbox rather than requiring another round-trip to Sakshi's own machine. The fifth (SCL/Cloud-Score+ cloud-mask cross-check) does need a new extraction and could not be; a script for it is written and ready. The RTI filing item is not an analysis step at all and remains Sakshi's own real-world action.

**A correctness problem found and fixed before anything else: `outputs/h3_robustness_results.json` did not exist.** `ANALYSIS_FREEZE.md` item 5 already read "RESOLVED," citing specific leave-one-district-out and randomization-inference numbers for the new H3 summer NDBI-proximity result and the pre-existing full-year lights-proximity result, and naming `outputs/h3_robustness_results.json` as where the full numbers live. The script it cited (`h3_border_proximity_robustness.py`) existed on disk, but the output file it's supposed to produce did not — meaning that "RESOLVED" claim was not backed by anything actually re-runnable at the time it was checked. Rather than take the previously-written numbers on faith, the script was actually executed against freshly-staged data in this entry. It reproduced every number in the existing claim exactly: summer NDBI-proximity leave-one-out rho range [+0.183, +0.337], 14/14 significant, randomization p<0.001; full-year lights-proximity rho range [-0.292, -0.175], 14/14 significant, randomization p<0.001; both null H3 combinations behaving as nulls (1/14 significant in leave-one-out). So the underlying claim was correct — it had genuinely been computed at some point — but the output artifact backing it was missing until this entry regenerated and saved it for real. `BO_Research_Paper.md`'s own prose (Sections 3.12, 4.5, 4.9, 6.4) still described this check as "not yet done" in four separate places, which was the more consequential half of the inconsistency; all four are now corrected to say it has been done and survives.

**Spatially-corrected H3 significance, computed for the first time (§6.11).** `spatial_moran_and_h3_correction.py` first re-reproduces this study's own published Moran's I values (I=0.346/p=0.001 summer NDBI, I=0.076/p=0.003 full-year lights — both reproduced exactly against fresh k=8 nearest-neighbor weights) as an integrity check, then computes what §6.11 previously flagged as not yet done: a spatially-corrected p-value for both Holm-significant H3 correlations. Method, stated plainly: this implements the "spatial permutation null that respects the observed clustering structure" option §6.11 itself named as an alternative to Dutilleul (1993)'s closed-form formula, not that formula itself — a SAR(1) autocorrelation parameter is calibrated on the same k=8 weight matrix so that simulated fields reproduce each outcome's own observed Moran's I, then 2,000 such spatially-structured-but-otherwise-random synthetic fields are correlated against the real distance-to-border values to see how often spatial structure alone produces a correlation this extreme. Result: summer NDBI-proximity (naive p=0.0000026) drops to a spatially-corrected p=0.02949 — still under 0.05, but only just, where the raw number looked unambiguous. Full-year lights-proximity (naive p=0.0000548) drops to p=0.00350 — comfortably significant either way. This is a genuinely important distinction for how much weight the paper's two surviving H3 findings deserve relative to each other, and it is reported that way rather than folded into a single "both survive" statement.

**Wild-cluster bootstrap for H4, computed for the first time (§6.10).** `wild_cluster_bootstrap.py` addresses the "a wild-cluster bootstrap was not run" gap the paper's own threats table named for the few-district-clusters row. `statsmodels` is not installable in this sandbox (PyPI is policy-blocked here), so this was implemented from scratch with numpy — manual OLS plus the same cluster-robust sandwich SE formula `did_model.py` uses — and that manual implementation was checked against `did_model.py`'s own already-published coefficients and SEs before being trusted for anything: it reproduced them to at least 10 significant figures. With that verified, the restricted-WCB procedure (Cameron, Gelbach & Miller 2008) was run with full enumeration of all 2^14=16384 possible district sign combinations (exact, not Monte Carlo, since 16384 is small enough to do exhaustively). All four H4 DiD results remain null: full-year NDBI p=0.349, full-year lights p=0.324, summer NDBI p=0.495, summer lights p=0.465 — consistent with the cluster-robust p-values already reported, not a different story under a stricter test.

**Village-level Dynamic World/SAR/NDBI cross-check, a new characterization of the §4.10 disagreement.** `dw_sar_ndbi_village_level_check.py` checks whether Dynamic World's aggregate DiD disagreement with SAR and NDBI (§4.10) is also visible at the level of individual villages. It is, and more starkly than the aggregate numbers alone suggested: Spearman correlation between Dynamic World's built-change and SAR VV/VH or NDBI's own change is small and mostly non-significant in both windows, and at three of the six outcome-pairs checked, the two proxies point the *same* direction at fewer than half the villages (31-41%) — worse than a coin flip would give by chance. This doesn't resolve which of §4.10's two speculative explanations for the disagreement is right, but it does mean Dynamic World's small, real, aggregate signal is not traceable to the same specific villages SAR or NDBI would flag — it's a population-level pattern, not a village-by-village one any other proxy corroborates.

**SCL/Cloud-Score+ cross-check: prepared, not run.** `extract_scl_cloud_mask_ndbi.py` re-extracts summer-window NDBI for the treated core sample using an SCL-band cloud mask instead of the primary pipeline's QA60 bitmask, and `scl_vs_qa60_comparison.py` is ready to compare the two once that extraction completes. This needs live Earth Engine access, which this sandbox doesn't have — it has to run on Sakshi's own machine, the same as every other extraction script in this study. Not represented as done anywhere in the paper; the §6.10 table row for cloud contamination now says the script is prepared rather than that the cross-check is still simply unaddressed.

**RTI filing: not something this pipeline can do.** The draft in `docs/RTI_draft_HP_Ladakh_village_lists.md` is ready to file, but filing a real government RTI application, waiting out its statutory response window, and geocoding whatever comes back are all real-world actions only Sakshi can take. Nothing in this entry changes that status.

**What this means for the paper.** Of the five items, three are now genuinely resolved with real analysis (H3 stress-test — now actually verified rather than just claimed; spatial correction; wild-cluster bootstrap), one is sharpened without being resolved (Dynamic World/SAR/NDBI disagreement — new evidence added, the underlying question still open), and one remains open pending either Sakshi's own machine time (SCL cross-check) or her own real-world action (RTI filing). None of this changes the primary NDBI estimand or this study's headline null; all of it strengthens or sharpens the secondary robustness picture around it.

**Documents updated in this entry.** `BO_Research_Paper.md`: Sections 3.12, 4.5, 4.9, and 6.4 corrected to say the H3 stress-test has been run (it had been computed before this entry but the paper's own prose still said otherwise); §6.11 rewritten with the real spatially-corrected p-values; §6.10 table rows updated for both the district-cluster/wild-cluster-bootstrap line and the spatial-autocorrelation line, plus the cloud-contamination line noting the SCL script is prepared; §4.10 gains a new paragraph on the village-level Dynamic World/SAR/NDBI cross-check. `ANALYSIS_FREEZE.md`: item 5 annotated with the missing-output-file finding and its fix; four new items (7-10) added for the spatial correction, wild-cluster bootstrap, village-level cross-check, and the not-yet-run SCL script; item 11 added stating plainly that the RTI filing is not this pipeline's to resolve.

**Not done in this entry.** The SCL/Cloud-Score+ re-extraction itself (script only, not run — needs Sakshi's machine). The RTI application has not been filed. The pure-documentation backlog (`BO_Executive_Summary.md`, `README.md`, dashboard pages, PDF rebuilds, `requirements-lock.txt`, the blank git commit hash in `ANALYSIS_FREEZE.md`) is unchanged from Entry 31's own list.

## Entry 33

**Status.** Sakshi asked, separately from the RTI matter, whether the project's documentation was actually updated everywhere — every doc, every dashboard page, README, citations — to reflect Entries 26-32's findings, rather than being told a generic "yes." An honest audit found it was not: the dashboard's Methodology page had a factually wrong sentence (still claiming a placebo test "could not be run either way" after Entry 30 had run one), Figure 9/10 depicted pre-resweep numbers, and `BO_Executive_Summary.md`, `README.md`, `CITATION.cff`, and `DATA_DICTIONARY.md` were all still written as of Entry 25 with zero mention of anything from Entries 26-32. She then asked for all of it to be updated, one item at a time. This entry is that update.

**Two new figures added, one existing one redesigned.** Figure 9/`10_buffer_sensitivity.png` (`make_expanded_analysis_charts.py`) was redesigned from a now-misleading two-series comparison (an "as-extracted" vs. a "matched n=154 subsample" series that became identical once the same-day resweep gave all three radii n=251 — Entry 31) to a single-series bar chart, one bar per radius, annotated with p-value and mean-change, colored by sign. New `make_triangulation_and_footprint_charts.py` produces Figure 11 (`11_triangulation_did.png`, a 4-panel forest plot of the control-group DiD across NDBI/SAR VV/SAR VH/Dynamic World, both windows, red where significant) and Figure 12 (`12_footprint_validation.png`, Panel A: each proxy's Spearman correlation against real building-footprint counts; Panel B: the three §7.3 ground-truth villages' actual before→after change per proxy, green where the proxy detects the confirmed real construction as an increase, red where it doesn't). Panel B was originally built plotting the wrong quantity (absolute `_after` level instead of actual change) — caught by comparing the rendered chart against the paper's own already-published claim that "NDBI moved in the wrong direction at all three villages," which the wrong-quantity version did not show; fixed by computing and hardcoding the real change values from source CSVs before finalizing. Both new figures embedded in `BO_Research_Paper.md` at §4.10 and §7.2 respectively.

**`DATA_DICTIONARY.md` brought current.** New sections added for every data file Entries 26-32 introduced and that the dictionary had never documented: the treated/control Dynamic World and SAR CSVs, the pretreatment (2019 baseline) CSVs, the building-footprint CSVs, and nine `outputs/` JSON/CSV files (triangulation, building-footprint validation, H3 robustness, spatial correction, wild-cluster bootstrap, village-level DW/SAR/NDBI check, pretreatment placebo summaries, extended robustness checks, leave-one-out/Holm CSVs). Column definitions were taken from the actual extraction/analysis scripts' own `OUT_PATHS`/`OUTCOME_COLS` and verified against real file headers where the underlying CSVs were staged into the sandbox for this entry, not written from memory of what the scripts were supposed to produce.

**`BO_Executive_Summary.md` and `README.md` rewritten.** Both were still describing the post-Entry-25 state (the two-artifact-reversal story) with no mention of anything after it. Rewritten to state plainly: the primary NDBI/lights null now additionally survives an exact wild-cluster bootstrap and a genuine 2019-to-2021 placebo test; the H3 border-proximity correlation, once flagged as new and unchecked, now survives leave-one-out, randomization inference, and a spatial-autocorrelation correction and is a real secondary finding; and triangulating against SAR and Dynamic World did NOT simply confirm the null — Dynamic World shows a significant control-group effect in both windows, validates more strongly against real building-footprint ground truth than NDBI does, and correctly detected all three confirmed ground-truth construction cases where NDBI did not. Both documents report this triangulation tension as an open question, not resolved toward either "no effect" or "an effect exists." `README.md`'s architecture diagram, "What This Project Does" list, repository-structure tree, and data-sources table were all updated to mention the new pipelines and proxies.

**`CITATION.cff` updated.** Abstract rewritten to match the current state (previously ended by calling the H3 result "flagged as open pending the same robustness checks," which was no longer true); version bumped 1.3.0 → 1.4.0; `date-released` updated to 2026-09-16; keywords extended with SAR, Dynamic World, building-footprint validation, wild cluster bootstrap, and spatial autocorrelation.

**Dashboard (`pages/8_Methodology_Limitations.py`) fixed and extended.** The one confirmed factual error found in the earlier audit — line 149's claim that "a genuine parallel-pre-trends placebo test still could not be run either way" — is fixed to point at the new expander describing the test Entry 30 actually ran. Three new expanders added: the pre-trends placebo test itself (3 of 4 clean, summer NDBI borderline at p=0.064, reported as borderline); the wild-cluster bootstrap (all four DiD results remain null under exact 16,384-combination enumeration); and the triangulation/ground-truth tension (Dynamic World's significant DiD, its stronger footprint-validation correlation, and the ground-truth case study's NDBI-wrong-direction finding), framed explicitly as an open question rather than a resolved one. The existing H3 expander gained the spatial-autocorrelation-correction numbers it was missing. The Data Sources section now lists SAR, Dynamic World, and Open Buildings. Verified with `python3 -m py_compile` after editing.

**A new finding, not a restatement: the SCL cloud-mask cross-check was actually run this entry, and it does not confirm the primary null.** `ANALYSIS_FREEZE.md` item 10 and the paper's §6.10 table still said this check was prepared but not executed, because it needs live Earth Engine access this sandbox doesn't have. What this sandbox didn't have was the *extraction* — but Sakshi had since run `extract_scl_cloud_mask_ndbi.py` on her own machine (the output, `border_optics_village_results_summer_sclmask.csv`, existed on the device but had not been staged into this sandbox in an earlier phase of this session). Staging it and running `scl_vs_qa60_comparison.py` for the first time surfaced a real, unresolved instability: the SCL-masked extraction is valid for only 200/258 villages (a stricter mask than QA60's), and on those 200, summer NDBI change is significant and positive (mean +0.01169, p=0.0000045) — the opposite of the QA60-based null. Before treating this as a third data-artifact reversal (in the pattern of the Sikkim archive-timing gap or the control-group contamination), the obvious alternative explanation was checked and ruled out: the SCL-valid 200 villages are heavily skewed toward Arunachal Pradesh (93%), but restricting the *QA60*-masked data to that identical 200-village sample still gives a clean null (p=0.449) — so holding the sample fixed, the mask choice alone flips the result, not sample composition. Village-level agreement between the two masks is only moderate (Spearman rho=0.544). This is reported in a new §6.12 of `BO_Research_Paper.md` as a genuine, unresolved instability in the primary measurement's own cloud-masking convention — a third axis (alongside compositing-window choice and proxy choice) along which this study's primary approach is demonstrably sensitive to a defensible methodological choice. The paper's Conclusion (§8) and `ANALYSIS_FREEZE.md` item 10 were both rewritten to reflect this rather than continuing to describe the check as merely "prepared." Full numbers in `outputs/scl_vs_qa60_comparison.json`.

**What this means for the paper.** This entry adds no new primary-estimand result — the QA60/NDBI/lights control-group null is unchanged. What it does is bring every document that describes this study into agreement with the paper's own already-published Sections 4.10/6.6/6.11/7.2/7.3/7.5/7.6, and it adds one genuinely new, unresolved finding (the SCL cloud-mask instability) that neither confirms nor overturns the primary null but does mean this study can no longer describe that null as immune to methodological choice. Read together with the triangulation tension already in the paper, this study now has two open, unexplained sensitivities in its own primary measurement approach (cloud mask, satellite proxy) that a future version should try to resolve rather than a single clean headline.

**Documents updated in this entry.** `src/visualization/make_expanded_analysis_charts.py` (Figure 9 redesign); new `src/visualization/make_triangulation_and_footprint_charts.py` (Figures 11-12); five figure PNGs (08, 09, 10, 11, 12); `BO_Research_Paper.md` (new Figure 11/12 embeds at §4.10/§7.2, §6.10 table row, new §6.12, rewritten §8 Conclusion); `DATA_DICTIONARY.md` (new sections for every Entries 26-32 data file); `BO_Executive_Summary.md` (full rewrite); `README.md` (architecture, findings, repo structure, data sources); `CITATION.cff` (abstract, version, date); `pages/8_Methodology_Limitations.py` (false-claim fix, three new expanders, H3 expander extended, data sources extended); `ANALYSIS_FREEZE.md` (item 10 rewritten from "not resolved" to "resolved, not a clean confirmation"); new `src/analysis/scl_vs_qa60_comparison.py` logic (added the QA60-matched-subsample check that isolates mask choice from sample composition) and its output `outputs/scl_vs_qa60_comparison.json`.

**Not done in this entry.** PDF rebuilds via `build_docs_pdfs.sh` were deferred until every source `.md` file was finalized, then run once the SCL discovery and Abstract rewrite were both in — all three PDFs (root + `static/`) now reflect the current text, verified by confirming "SCL"/"Dynamic World" both appear in the rebuilt `BO_Research_Paper.pdf` and `BO_Executive_Summary.pdf` text extraction, not just assumed from a clean pandoc exit code. Distinguishing which of the two explanations (QA60 under-masking vs. SCL over-masking) behind the new cloud-mask instability is correct — would need a village-level visual audit or a third independent masking method, neither attempted here. The RTI application remains unfiled, which continues to be Sakshi's own action, not this pipeline's.

**Two closing items, done by Sakshi on her own machine and folded back in.** `requirements-lock.txt` (`pip freeze` output, 5818 bytes) now exists in the repository root, confirmed present on the device. `ANALYSIS_FREEZE.md`'s git-commit-hash field, blank since the file was first written, is now filled in: `a1bfe9ed140b18197480e6b923f62ee120ac93b6`. Both were the only two items in this whole "update everything" pass that genuinely could not be done from this sandbox — everything else in Entries 26-33 was either analysis this sandbox could run directly or documentation this sandbox could write and verify against the live repository.

## Entry 34

**Status.** Sakshi ran the pushed repo through two rounds of external AI review (a general one, then a second, more technical one from a tool called Anara). This entry covers acting on both: a scope-framing decision on the never-filed RTI, two small documentation fixes the first review caught, and one real bug the second review caught in this project's own SCL cloud-mask check — which turned out to be the most consequential thing either review found.

**RTI reframed as a permanent scope decision, not an open task.** Sakshi confirmed filing the HP/Ladakh RTI isn't feasible for her right now (cost, procedural complexity, slow replies). Checked first whether a village-wise list for either jurisdiction exists publicly anywhere else — PIB releases, MHA's own Feb/Mar 2026 parliamentary replies, Ladakh's district administration pages, HP news coverage — and it doesn't; every public source gives only aggregate project counts and budgets (HP: 133 projects, ₹126.01 crore; Ladakh: 88 projects, ₹95.76 crore), never village names. So the RTI was genuinely the only route, and leaving it as a "known, deferred issue" that will supposedly get resolved later was itself becoming a stale claim. `ANALYSIS_FREEZE.md` item 11 and the equivalent language in `BO_Executive_Summary.md` were reworded from "not yet done" to a plain, permanent scope statement: the core sample covers the three states with public geocoded lists, HP is illustrative-only, Ladakh is excluded, and that's disclosed rather than pending.

**Two small fixes from the first (general) review.** (1) `ANALYSIS_FREEZE.md`'s "Exploratory, unstressed finding" section had gone stale — it still described the summer H3 NDBI-proximity correlation as "not yet leave-one-out or randomization-inference checked," directly contradicting item 5 two paragraphs later, which says that exact check was done and passed in Entry 32. Fixed to point at item 5 instead of repeating the outdated claim. (2) `README.md` and `CITATION.cff` both called Dynamic World and SAR "two fully independent proxies" without qualification. The Freeze doc and the paper's own §4.10 already draw the real distinction correctly — SAR is sensor-independent (a different satellite constellation), Dynamic World is only algorithm-independent (same Sentinel-2 imagery as NDBI) — but README/CITATION had let that nuance slip. Both reworded to match.

**The second (Anara) review's technical critique — most of it already covered, one item was real and serious.** Anara reviewed the actual repo (not just the docs) and raised roughly a dozen points: covariate matching for the control group, a three-way QA60/SCL/Cloud-Score+ mask adjudication, Dynamic World confidence thresholds, an extended 2019/2021/2023/2025 panel, a stratified independent-rater visual audit, pre-registration, and — the one that mattered — a specific, checkable claim that `extract_scl_cloud_mask_ndbi.py`'s `SCL_CLEAR_CLASSES` included class 11, which is snow/ice, not clear ground. Checked the actual file: true, exactly as claimed, comment and all (`# kept as "clear": 2 dark area, 4 vegetation, 5 bare soil, 6 water, 11 snow`). Given the treated sample is entirely high-altitude Himalayan border villages and this check runs on the June-September window, snow contaminating the "clear" pixel set is a real threat to a result this project had already published in three places as a headline secondary finding.

Rather than take on the full Anara list, Sakshi chose the minimal path: fix the SCL bug, add the multiplicity-correction sequencing clarification Anara also raised (Holm-Bonferroni and the spatial-autocorrelation correction are sequential, not competing — now stated explicitly in `ANALYSIS_FREEZE.md` and `BO_Research_Paper.md`'s §6.10 table), and add a one-sentence VIIRS-resolution caveat (its ~500-750m native pixel footprint is close to this study's own 500m buffer, a limit that applies to the night-lights proxy specifically, not NDBI/SAR/Dynamic World). The larger asks — covariate matching via elevation/slope/population (genuinely feasible later via GEE/WorldPop/Overpass, no new RTI or money needed), Cloud Score+ adjudication, DW confidence thresholds, the extended panel, the visual audit — are logged as real future-work options, not done here. Anara's pre-registration suggestion was also pushed back on: registering an analysis after already knowing every result several times over isn't a credibility upgrade, it's backwards; it would only be honest for a genuinely new, not-yet-run round of checks.

**The SCL fix itself.** `extract_scl_cloud_mask_ndbi.py` rewritten: `SCL_CLEAR_CLASSES` corrected to `[2, 4, 5, 6]` (drops snow), plus a second `[4, 5, 6]` "strict" variant (also drops dark-area pixels) as the extra cross-check Anara suggested. Both write to new filenames (`_corrected.csv`, `_strict.csv`) rather than overwriting the old buggy `border_optics_village_results_summer_sclmask.csv`, which is left on disk untouched as the pre-fix record — this matters because the script's checkpoint/resume logic would otherwise have seen the old file's non-null values and silently skipped re-extracting every village. Both variants run clean on the researcher's own machine: 251/251 villages valid, both variants, no errors.

**The result reverses, and a second bug was caught in the process.** Ran `scl_vs_qa60_comparison.py` against the corrected file. Result: SCL-masked (n=251, corrected classes) mean change +0.00112, Wilcoxon p=0.28797 — not significant. QA60 on the identical 251 villages: mean change -0.00090, p=0.43583 — also not significant. The two masks now agree, both null — reversing the Entry 33 finding, which was built on the buggy classes. Village-level agreement between the masks also rose sharply (Spearman rho=0.734, up from the pre-fix 0.544). But the comparison script's own print statements and JSON output were hardcoded to the old narrative ("the mask choice ALONE flips this result... 93% Arunachal Pradesh...") and printed that false story even against the new, agreeing numbers — a second bug, this time introduced by an earlier edit of my own, caught by actually reading the script rather than trusting its output. Rewrote `scl_vs_qa60_comparison.py` so every printed/saved claim is computed from the real p-values (`masks_agree_on_significance`, dynamic significant/not-significant labels) instead of a fixed string, and removed the now-false "93% Arunachal" coverage claim rather than leave an assumption from one run baked into the next.

**One thing not fully explained.** SCL-valid coverage went from 200/258 (pre-fix) to 251/258 (post-fix) once snow was excluded from the clear-class list — the opposite of what should mechanically happen, since dropping a class from "clear" should only ever hold coverage steady or reduce it, never increase it. The likely explanation, given this project's own history with Sentinel-2 archive backfill (Entries 21-22), is that more scenes became available in the collection between the two extractions, independent of the class-list fix. Not confirmed directly — flagged as open in `ANALYSIS_FREEZE.md` rather than assumed.

**Documents updated in this entry.** `ANALYSIS_FREEZE.md` (items 10 and 11 rewritten, multiplicity-family section extended); `BO_Research_Paper.md` (§6.10 table row, §6.12 fully rewritten, §8 Conclusion and Abstract both corrected, new VIIRS limitations-table row); `README.md` (SCL paragraph and honest-headline paragraph rewritten, independence-language fix); `BO_Executive_Summary.md` (Project Overview, Finding #3, results table, checklist, both Honest Limitation paragraphs, RTI scope paragraph, all rewritten); `CITATION.cff` (abstract rewritten, version 1.4.0 → 1.5.0); `DATA_DICTIONARY.md` (SCL file sections rewritten for the new corrected/strict files, old file marked superseded); `pages/5_Statistical_Validation.py` (caption rewritten); `src/acquisition/extract_scl_cloud_mask_ndbi.py` (class fix, two-variant rewrite); `src/analysis/scl_vs_qa60_comparison.py` (dynamic narrative rewrite). All Python files reverified with `python3 -m py_compile` after editing.

**Not done in this entry.** PDF rebuild via `build_docs_pdfs.sh` — deferred until this entry's own text is finalized, then run once, same as Entry 33's pattern. The larger Anara-suggested extensions (covariate matching, Cloud Score+, DW thresholds, extended panel, visual audit) remain logged as future work, not started. The RTI remains unfiled — now disclosed as a permanent scope boundary rather than an open item, per the decision above.
