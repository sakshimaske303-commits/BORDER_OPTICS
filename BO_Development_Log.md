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
