# BORDER OPTICS — Satellite Verification of India's Vibrant Villages Programme

[![EarthArXiv](https://img.shields.io/badge/EarthArXiv-Preprint-B7410E.svg)](https://eartharxiv.org/repository/view/14830/) [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21759970.svg)](https://doi.org/10.5281/zenodo.21759970)

**Testing whether India's ₹4,800 crore border-villages programme produced verifiable development — and whether a single satellite-composite choice, or an incomplete extraction, can make it look like it did.**

## Live Dashboard

**[View the interactive dashboard →](https://borderoptics-bkx3lpcvfghdpa2hmuqwsg.streamlit.app/)**

## Project Documentation

| Document | What's Inside |
|---|---|
| [`BO_Executive_Summary.md`](./BO_Executive_Summary.md) | Project overview, question, method, headline finding, robustness checklist, and links (start here). Source for `BO_Executive_Summary.pdf`, the styled one-page PDF generated from it |
| [`BO_Research_Paper.md`](./BO_Research_Paper.md) | Formal academic paper — literature review, statistical methodology, results, discussion |
| [`BO_Development_Log.md`](./BO_Development_Log.md) | Full technical development log — every bug, debugging session, and methodology iteration |

---

Established as an independent research project, BORDER OPTICS is a verification tool that assesses and measures the physical development on the ground of India's Vibrant Villages Programme (VVP-I), a Rs. 4,800 crore investment in border areas across five Himalayan states/UTs. Built-up area change (NDBI) and night-time light growth (VIIRS) are tested as two separate and distinct hypotheses – in order to determine if the result is due to the hypothesis rather than the data – and no result is handed over for trust without first being tested under two separate compositing windows (full-year and summer-matched) – specifically to determine if the answer changes depending on window choice – then a further test is performed on a district-restricted non-VVP control sample, a multi-year three-point trend, and a buffer-radius sensitivity sweep across 250m, 500m, and 1km – before it is trusted.

This project exists to fill that exact gap: responding to Parliament's direct enquiry into whether VVP's effect had ever been assessed, the Ministry of Home Affairs replied: *"No impact assessment has been carried out"* (Lok Sabha Unstarred Question No. 508, 3 February 2026). Each of the hypotheses presented here has been tested thoroughly, and any result that could be defended by one of two possible measurements is presented both ways — no claimed result is hidden in the "don't know/other" bucket.

**Coverage note:** VVP-I spans five Himalayan states/UTs, but this study's core statistical sample (251 villages) is limited to the three states with officially confirmed, name-level village lists — Arunachal Pradesh, Sikkim, and Uttarakhand. Himachal Pradesh contributes a separate 7-village illustrative case study (not part of the core sample, since only aggregate priority-village counts, not names, are on parliamentary record for it). Ladakh has zero village-level representation here — its 35 sanctioned villages are officially confirmed in aggregate but no publicly indexed source names them, and closing that gap would require an RTI request this project deliberately chose not to pursue (see `BO_Research_Paper.md` §3, §6.1, and §7.4 for the full reasoning).

---

## Architecture

```text
Government sources (VVP-I portals, Rajya Sabha/Lok Sabha Q&A) + OSM/Bhuvan
        │
        ▼
Village compilation & geocoding (src/acquisition/) ──► Non-VVP control villages
        │                                              via Overpass API, same
        ▼                                              14 districts
Google Earth Engine extraction — primary: NDBI + VIIRS, two compositing windows,
three time points (2021/2023/2025), three buffer radii (250m/500m/1km);
triangulation: Sentinel-1 SAR VV/VH backscatter, Dynamic World built-up
probability; ground truth: Google Open Buildings footprint counts; a second
pre-treatment (2019) pull for a genuine placebo test
(src/acquisition/extract_*.py)
        │
        ▼
Border-distance computation (src/analysis/compute_border_distance.py)
        │
        ▼
Statistical testing — Wilcoxon, Spearman, district-FE DiD, multi-year trend,
buffer sensitivity, exact wild cluster bootstrap, spatial-autocorrelation-
corrected permutation test, pre-trends placebo DiD, cross-proxy triangulation,
building-footprint validation (src/analysis/)
        │
        ▼
Static figures + interactive maps (src/visualization/) ──► BO_Research_Paper.md
        │
        ▼
Streamlit dashboard (app.py + 8 pages)
```

---

## What This Project Does

- Assists in collating a village-level extant data base of villages identified as VVP-I priority villages for five Himalayan border states/UTs and calibrates them with the aggregate numbers given by officials
- Geocodes 258 villages using a dual source pipeline (OpenStreetMap Nominatim and ISRO's Bhuvan Village Geocoding API with Census linked fallback option)
- Treats built-up area change (NDBI) and night-time light growth (VIIRS) as two hypotheses and not a combined assumption for a baseline of 2021-2025.
- Examines if there is a relationship between actual change and the budget for VVP-I for each state, or if the actual changes departs from it
- Tests if proximity to the border/Line of Actual Control is correlated to the pace of development, which is within the prediction of securitization theory of borders where proximity to the border – not developmental need – drives priority
- Explicitly tests the robustness of "compositing-window sensitive" (full-year vs. summer matched) as its own robustness test, instead of relying on a single satellite comparison
- To separate out a programme-attributable effect from the region's own trend, a change in the change that took place among treated villages was compared against a district-restricted non-VVP control group of 732 villages, also in the 14 districts, using a difference in differences model with a district fixed-effect model.
- Adds a three-point 2021-vs-2023-vs-2025 comparison to the core trend, and compares the fixed 500m trend extraction buffer with 250m and 1km buffers, all pulled the same day, to see if the results of another extreme year, buffer size, or archive-timing preference are skewing the results
- Re-checks the district fixed-effects DiD's reliance on only 14 clusters with an exact wild cluster bootstrap (16,384 sign-flip combinations) rather than trusting the standard cluster-robust asymptotics alone
- Stress-tests the border-proximity correlation once flagged as a fresh, unchecked finding — leave-one-district-out, randomization inference, and a spatial-autocorrelation-calibrated permutation test, since the 251 sample villages are not independent observations for ordinary significance purposes
- Extracts a genuine second pre-treatment year (2019) for both treated and control villages so a real parallel-pre-trends placebo test can be run, not just a same-year baseline-level check
- Triangulates the primary NDBI/night-lights design against two secondary proxies of different kinds — Sentinel-1 SAR backscatter (a genuinely different sensor, radar not optical) and Dynamic World's machine-learned built-up probability (a different algorithm, but still derived from the same Sentinel-2 imagery as NDBI, so algorithm-independent, not sensor-independent) — and validates all of them against an independent, non-satellite ground truth: Google Open Buildings footprint counts, plus three specific villages with confirmed real construction
- Presents all information on a multi-page interactive Streamlit dashboard via live recalculating statistical tests, embedded Folium (interactive) maps and Plotly (interactive) plots

## Interactive Maps & Plots

Each map and the three statistical charts at the head of the dashboard are not flat pictures but readable and interactive: hover them and toggle them either together as part of the dashboard's **[Interactive Maps & Plots page](https://borderoptics-bkx3lpcvfghdpa2hmuqwsg.streamlit.app/Interactive_Maps)**, or on individual map/plot viewers provided by the portfolio site link.

## Key Findings

An earlier version of this project reported built-up area change as compositing-window sensitive: no significant change in a full-year composite (Wilcoxon signed-rank, p = 1.000), but a highly significant increase in the same villages recomposited to summer months (June–September, p < 0.000001). That summer result depended on an incomplete extraction — at the time it was run, all 31 Sikkim villages returned zero usable summer imagery, a gap since traced to the Sentinel-2 archive still backfilling scenes for those exact dates, not to any real absence of change (full account in `BO_Development_Log.md`, Entries 21–22). Once the extraction was completed — pulled the same day as the control group's own data — the summer result reversed to a null (p = 0.436), matching the full-year window. **Both compositing windows now agree: no significant built-up-area change either way.**

Against a district-restricted non-VVP control group of 732 villages across the same region, the same reversal holds: the summer-window NDBI gap that was once significant (district-fixed-effects DiD, p = 0.00033) is now null (p = 0.473, coefficient sign flipped), matching the full-year window's own null result (p = 0.310). Every check built around the old result was rerun on the complete data and agrees — the buffer-radius sweep at 250m/500m/1km, all pulled the same day, is null at all three, the result does not hold under leave-one-district-out (0 of 14 reruns), and randomization inference agrees. Night-lights follows the same pattern for its summer-window control-group gap (p = 0.450). Its full-year gap had, for a while, been the one control-group result in this study still significant under any specification — but that estimate turned out to rest on a contaminated control group, and once the contamination was removed and the control list regenerated to 732 villages, that gap went null too (`BO_Development_Log.md`, Entries 23–25).

This round added a stricter test the earlier robustness checks didn't cover: with only 14 district clusters — below the 30–40+ usually recommended for cluster-robust standard errors' own asymptotics to be trustworthy — an exact wild cluster bootstrap (16,384 sign-flip combinations, not an approximation) was run on all four outcome/window DiD estimates. All four remain non-significant (p = 0.32–0.50), meaning the small-cluster count is not itself manufacturing a false null. A genuine parallel-pre-trends placebo test was also added: a second pre-treatment year (2019) was pulled for both treated and control villages, since the original design's single pre-period (2021) could only support a same-year baseline-*level* check, not a pre-*trend* one. Three of the four resulting placebo comparisons are clean (full-year NDBI p=0.864, full-year lights p=0.755, summer lights p=0.968); the fourth (summer NDBI, p=0.064) is borderline and reported as borderline, not rounded up to a pass, alongside the raw unadjusted comparison for that same combination being sharply significant (p=0.00001).

Two findings from this round are not restatements of the null. First, the border-proximity correlation flagged in an earlier version of this project as new and unchecked has now been run through leave-one-district-out (14 of 14 significant, both directions found), randomization inference (p≈0.0005), and — the more conservative test, since the 251 sample villages are not spatially independent observations — a spatial-autocorrelation-calibrated permutation test (p=0.0295 summer-NDBI, p=0.0035 full-year-lights). It survives all three and is now a real secondary finding, still correlational, running opposite to what a securitization account of border development would predict.

Second, triangulating the primary NDBI/lights design against two secondary satellite proxies — one sensor-independent, one not — did not simply confirm the null. Sentinel-1 SAR backscatter, a genuinely different sensor (radar, not optical), agrees — null in both windows, both polarizations. Dynamic World's machine-learned built-up probability — a different algorithm, but still derived from the same Sentinel-2 imagery as NDBI, so not sensor-independent — does not: its control-group DiD is significant in both windows (full-year p=0.0117, summer p=0.0013). That disagreement is not easily dismissed, because Dynamic World also validates far more strongly against an independent, non-satellite ground truth — Google Open Buildings footprint counts (Spearman ρ=0.808, vs. NDBI's ρ=0.399 and lights' ρ=0.478) — and because at three specific villages this project separately confirmed underwent real construction (Kaho, Walong, Musai), Dynamic World and night-lights both correctly registered an increase at all three while NDBI moved in the wrong direction at all three. A village-level check found the three proxies agreeing on direction of change in only about a third to two-thirds of individual villages, depending on the pair and window — near chance. Whether this means NDBI under-detects a real, modest effect, or Dynamic World's DiD is itself a different kind of false positive, is reported here as an open question rather than resolved in either direction — see `BO_Development_Log.md` (Entries 26–32) and `BO_Research_Paper.md` Section 4.10/7.2/7.3 for the full account.

Third, and unrelated to proxy choice: cross-checking the QA60 cloud mask used throughout against an alternative SCL-band mask initially looked like it surfaced a genuine instability in the primary NDBI measure — QA60 null (p=0.449), SCL significant and positive (p=0.0000045) on the identical 200 villages both masks could produce a valid summer composite for. It turned out to be a bug, caught by external review rather than this project's own checks: the SCL mask was letting snow pixels through as "clear" (class 11 in the Sentinel-2 Scene Classification Layer is snow/ice, not clear ground), a real risk for June–September composites over Himalayan villages. Fixed and rerun against live Earth Engine, SCL coverage rose to 251/258 villages (matching QA60's own coverage, no longer skewed toward Arunachal Pradesh) and the SCL result is no longer significant (mean change +0.00112, p=0.288) — matching QA60's own null on the identical 251 villages (p=0.436). The two masks now agree. Reported here as a bug this project's own external review caught and fixed, not as an unresolved measurement tension (`BO_Development_Log.md`, Entries 33–34; `BO_Research_Paper.md` Section 6.12).

As a general trend the primary NDBI/lights measure is not consistent either way: the three-point 2021/2023/2025 extension shows a decline from 2021 to 2023 followed by a recovery from 2023 to 2025 that nets out to a non-significant overall trend — consistent with, not contradicting, the now-null two-point comparison.

Budget still doesn't track measured outcome: Arunachal Pradesh's roughly tenfold larger sanctioned budget (₹2,749.74 crore vs. Uttarakhand's ₹270.58 crore) corresponds to a smaller mean NDBI change, and Sikkim's smallest budget of the three corresponds to a negative one — descriptive only at n=3, and the correlation's direction itself flips between compositing windows at this sample size.

The honest headline: on its primary measure, no satellite-detectable effect of VVP-I survives being checked two ways, across two compositing windows, against a control group, at three buffer radii, under a small-cluster-robust bootstrap, under a genuine pre-treatment placebo test, or under an alternative cloud-masking convention once that check's own bug was fixed — a real answer to a question Parliament's own record says was never asked. One further check complicated that null rather than confirming it: triangulating against an independent, ground-truth-validated proxy (Dynamic World) surfaced a genuine tension this project has not resolved. A second apparent tension, in the cloud-masking cross-check, turned out under external review to be a coding bug rather than a real disagreement. A border-proximity pattern once flagged as unchecked has, by contrast, since survived every stress test applied to it. Full account of what changed and why is in `BO_Development_Log.md` (Entries 21–34).

The full methodological approach, including all of the hypotheses tested as well as the "robustness" check of the compositing window and the control group/multi-year/buffer-radius checks taken throughout, can be found on the Methodology & Limitations page of the dashboard.

## Repository Structure

```text
BORDER_OPTICS/
├── app.py                          # Streamlit dashboard entry point (Home page)
├── pages/                          # Dashboard sub-pages (Study Design, Theoretical
│                                    #   Foundations, Built-Up Change, Night-Lights,
│                                    #   Statistical Validation, Explore Trends,
│                                    #   Interactive Maps & Plots, Methodology & Limitations)
├── utils/
│   ├── theme.py                    # Shared dashboard styling
│   └── data.py                     # Shared data-loading functions
├── data/
│   ├── raw/                        # Raw village lists per state
│   └── processed/                  # Geocoded villages, GEE satellite exports, analyzed results
├── src/
│   ├── acquisition/                # Geocoding, GEE extraction (treated + control group,
│   │                                #   multi-year, buffer-radius sweep, SAR, Dynamic World,
│   │                                #   building footprints, pre-treatment baseline, SCL mask)
│   ├── analysis/                   # Statistical testing, border-distance computation,
│   │                                #   DiD model, multi-year trend, buffer sensitivity,
│   │                                #   wild cluster bootstrap, spatial/Moran's I correction,
│   │                                #   triangulation, building-footprint validation,
│   │                                #   pre-trends placebo test, extended robustness checks
│   └── visualization/              # Static chart + interactive map/plot generation
├── outputs/
│   ├── figures/                    # Static PNG charts (incl. triangulation & footprint validation)
│   ├── *.json / *.csv               # Robustness, triangulation, and validation results
│   └── interactive_maps/
│       ├── maps/                   # Folium interactive HTML maps
│       └── plots/                  # Plotly interactive HTML charts
├── BO_Research_Paper.md
├── BO_Development_Log.md
├── DATA_DICTIONARY.md
├── ANALYSIS_FREEZE.md
└── requirements.txt
```

## Tech Stack

Python · Pandas · GeoPandas · SciPy · Folium · Plotly · Streamlit · Google Earth Engine · OpenStreetMap Nominatim · ISRO Bhuvan API · Natural Earth

## Data Sources

| Dataset | Provider |
|---|---|
| Village Lists | State VVP-I portals; Rajya Sabha / Lok Sabha Q&A annexures |
| Geocoding | OpenStreetMap Nominatim; ISRO Bhuvan Village Geocoding API |
| Non-VVP Control Villages | OpenStreetMap Overpass API, district-matched |
| Built-Up Index (NDBI) | Sentinel-2 SR Harmonized (Google Earth Engine) |
| Night-Lights | VIIRS DNB monthly composites (Google Earth Engine) |
| SAR Backscatter (triangulation) | Sentinel-1 GRD (Google Earth Engine) |
| Built-up probability (triangulation) | Dynamic World V1 (Google Earth Engine) |
| Building footprint ground truth | Google Open Buildings v3 (Google Earth Engine) |
| Border/LAC Geometry | Natural Earth 10m Admin-0 Boundary Lines |
| Budget / Project Counts | Parliamentary record (Rajya Sabha / Lok Sabha Q&A) |

## Running Locally

```bash
git clone https://github.com/sakshimaske303-commits/BORDER_OPTICS.git
cd BORDER_OPTICS
pip install -r requirements.txt
streamlit run app.py
```

`requirements.txt` pins the direct dependencies this project imports. For an exact, full-transitive-closure environment (every sub-dependency pinned too), use `pip install -r requirements-lock.txt` instead. The satellite-extraction scripts under `src/acquisition/` additionally need a Google Earth Engine account with API access enabled and an authenticated session (`earthengine authenticate`, or a service-account key referenced via `.env` / `python-dotenv`) — the Streamlit dashboard itself does not require this, since it reads from the already-extracted CSVs in `data/processed/`.

## Author

**Sakshi D. Maske**

Independent Geospatial Researcher

## License

This project is licensed under [CC BY 4.0](./LICENSE) — you are free to share and adapt this work for any purpose, including commercially, with attribution.

---

*This project's full development process — including every debugging session, methodology iteration, and technical decision — is documented in `BO_Development_Log.md` for full transparency and reproducibility.*