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

---

## Architecture

```text
Government sources (VVP-I portals, Rajya Sabha/Lok Sabha Q&A) + OSM/Bhuvan
        │
        ▼
Village compilation & geocoding (src/acquisition/) ──► Non-VVP control villages
        │                                              via Overpass API, same
        ▼                                              14 districts
Google Earth Engine extraction — NDBI + VIIRS, two compositing windows,
three time points (2021/2023/2025), three buffer radii (250m/500m/1km)
(src/acquisition/extract_*.py)
        │
        ▼
Border-distance computation (src/analysis/compute_border_distance.py)
        │
        ▼
Statistical testing — Wilcoxon, Spearman, district-FE DiD, multi-year trend,
buffer sensitivity (src/analysis/)
        │
        ▼
Static figures + interactive maps (src/visualization/) ──► BO_Research_Paper.md
        │
        ▼
Streamlit dashboard (app.py + 7 pages)
```

---

## What This Project Does

- Assists in collating a village-level extant data base of villages identified as VVP-I priority villages for five Himalayan border states/UTs and calibrates them with the aggregate numbers given by officials
- Geocodes 258 villages using a dual source pipeline (OpenStreetMap Nominatim and ISRO's Bhuvan Village Geocoding API with Census linked fallback option)
- Treats built-up area change (NDBI) and night-time light growth (VIIRS) as two hypotheses and not a combined assumption for a baseline of 2021-2025.
- Examines if there is a relationship between actual change and the budget for VVP-I for each state, or if the actual changes departs from it
- Tests if proximity to the border/Line of Actual Control is correlated to the pace of development, which is within the prediction of securitization theory of borders where proximity to the border – not developmental need – drives priority
- Explicitly tests the robustness of "compositing-window sensitive" (full-year vs. summer matched) as its own robustness test, instead of relying on a single satellite comparison
- To separate out a programme-attributable effect from the region's own trend, a change in the change that took place among treated villages was compared against a district-restricted non-VVP control group of 735 villages, also in the 14 districts, using a difference in differences model with a district fixed-effect model.
- Adds a three-point 2021-vs-2023-vs-2025 comparison to the core trend, and compares the fixed 500m trend extraction buffer with 250m and 1km buffers to see if the results of another extreme year or buffer size preference are skewing the results
- Presents all information on a multi-page interactive Streamlit dashboard via live recalculating statistical tests, embedded Folium (interactive) maps and Plotly (interactive) plots

## Interactive Maps & Plots

Each map and the three statistical charts at the head of the dashboard are not flat pictures but readable and interactive: hover them and toggle them either together as part of the dashboard's **[Interactive Maps & Plots page](https://borderoptics-bkx3lpcvfghdpa2hmuqwsg.streamlit.app/Interactive_Maps)**, or on individual map/plot viewers provided by the portfolio site link.

## Key Findings

An earlier version of this project reported built-up area change as compositing-window sensitive: no significant change in a full-year composite (Wilcoxon signed-rank, p = 1.000), but a highly significant increase in the same villages recomposited to summer months (June–September, p < 0.000001). That summer result depended on an incomplete extraction — at the time it was run, all 31 Sikkim villages returned zero usable summer imagery, a gap since traced to the Sentinel-2 archive still backfilling scenes for those exact dates, not to any real absence of change (full account in `BO_Development_Log.md`, Entries 21–22). Once the extraction was completed — pulled the same day as the control group's own data — the summer result reversed to a null (p = 0.436), matching the full-year window. **Both compositing windows now agree: no significant built-up-area change either way.**

Against a district-restricted non-VVP control group of 735 villages across the same region, the same reversal holds: the summer-window NDBI gap that was once significant (district-fixed-effects DiD, p = 0.00033) is now null (p = 0.447, coefficient sign flipped), matching the full-year window's own null result (p = 0.275). Every check built around the old result was rerun on the complete data and agrees — the buffer-radius sweep at 250m/500m/1km is now null at all three (was significant at all three), the result no longer holds under leave-one-district-out (0 of 14 reruns, was 14 of 14), and randomization inference agrees (p = 0.115, was p = 0.0005). Night-lights follows the same pattern for its summer-window control-group gap (now p = 0.366, was p = 0.0044); its full-year gap is the one result in this study still significant under any specification (p = 0.036 under fixed effects), but it also carries this study's worst treated-vs-control baseline imbalance and only holds in 10 of 14 leave-one-district-out reruns — a fragile, not a confirmed, result. One new finding appeared in the same complete summer data: built-up change now correlates with distance to the border/LAC, in the opposite direction from what the securitization hypothesis predicted — flagged as an open question, not yet stress-tested, rather than folded into the headline.

As a general trend the change is not consistent either way: the three-point 2021/2023/2025 extension shows a decline from 2021 to 2023 followed by a recovery from 2023 to 2025 that nets out to a non-significant overall trend — consistent with, not contradicting, the now-null two-point comparison.

Budget still doesn't track measured outcome: with all three core states now having valid summer data (previously two, before Sikkim's was recovered), Arunachal Pradesh's roughly tenfold larger sanctioned budget (₹2,749.74 crore vs. Uttarakhand's ₹270.58 crore) corresponds to a smaller mean NDBI change, and Sikkim's smallest budget of the three corresponds to a negative one — descriptive only at n=3, and the correlation's direction itself flips between compositing windows at this sample size.

The honest headline, once the extraction is complete: no satellite-detectable effect of VVP-I survives being checked two ways, across two proxies, against a control group, and at three buffer radii — a real answer to a question Parliament's own record says was never asked, and a reminder that a result surviving every robustness check still isn't confirmed if the underlying extraction wasn't complete. Full account of what changed and why is in `BO_Development_Log.md` (Entries 21–22).

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
│   │                                #   multi-year, buffer-radius sweep)
│   ├── analysis/                   # Statistical testing, border-distance computation,
│   │                                #   DiD model, multi-year trend, buffer sensitivity
│   └── visualization/              # Static chart + interactive map/plot generation
├── outputs/
│   ├── figures/                    # Static PNG charts
│   └── interactive_maps/
│       ├── maps/                   # Folium interactive HTML maps
│       └── plots/                  # Plotly interactive HTML charts
├── BO_Research_Paper.md
├── BO_Development_Log.md
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
| Border/LAC Geometry | Natural Earth 10m Admin-0 Boundary Lines |
| Budget / Project Counts | Parliamentary record (Rajya Sabha / Lok Sabha Q&A) |

## Running Locally

```bash
git clone https://github.com/sakshimaske303-commits/BORDER_OPTICS.git
cd BORDER_OPTICS
pip install -r requirements.txt
streamlit run app.py
```

## Author

**Sakshi D. Maske**

Independent Geospatial Researcher

## License

This project is licensed under [CC BY 4.0](./LICENSE) — you are free to share and adapt this work for any purpose, including commercially, with attribution.

---

*This project's full development process — including every debugging session, methodology iteration, and technical decision — is documented in `BO_Development_Log.md` for full transparency and reproducibility.*