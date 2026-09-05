# BORDER OPTICS — Satellite Verification of India's Vibrant Villages Programme

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21759970.svg)](https://doi.org/10.5281/zenodo.21759970)

**Testing whether India's ₹4,800 crore border-villages programme produced verifiable development — and whether a single satellite-composite choice can flip the answer.**

## Live Dashboard

**[View the interactive dashboard →](https://borderoptics-bkx3lpcvfghdpa2hmuqwsg.streamlit.app/)**

## Project Documentation

| Document | What's Inside |
|---|---|
| [`BO_Executive_Summary.md`](./BO_Executive_Summary.md) | Project overview, question, method, headline finding, robustness checklist, and links (start here). Source for `BO_Executive_Summary.pdf`, the styled one-page PDF generated from it |
| [`BO_Research_Paper.md`](./BO_Research_Paper.md) | Formal academic paper — literature review, statistical methodology, results, discussion |
| [`BO_Development_Log.md`](./BO_Development_Log.md) | Full technical development log — every bug, debugging session, and methodology iteration |

---

Established as an independent research project, BORDER OPTICS is a verification tool that assesses and measures the physical development on the ground of India's Vibrant Villages Programme (VVP-I), a Rs. 4,800 crore investment in border areas across five Himalayan states/UTs. Built-up area change (NDBI) and night-time light growth (VIIRS) are tested as two separate and distinct hypotheses – in order to determine if the result is due to the hypothesis rather than the data – and no result is handed over for trust without first being tested under two separate compositing windows (full-year and summer-matched) – specifically to determine if the answer changes depending on window choice – then a further test is performed on a matched non-VVP control sample, a multi-year three-point trend, and a buffer-radius sensitivity sweep across 250m, 500m, and 1km – before it is trusted.

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
Static figures + interactive maps (src/visualization/) ──► BO_Research_Paper.md / BO_Project_Report.md
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
- To separate out a programme-attributable effect from the region's own trend, a change in the change that took place among treated villages was compared against a matched non-VVP control group of 753 villages, also in the 14 districts, using a difference in differences model with a district fixed-effect model.
- Adds a three-point 2021-vs-2023-vs-2025 comparison to the core trend, and compares the fixed 500m trend extraction buffer with 250m and 1km buffers to see if the results of another extreme year or buffer size preference are skewing the results
- Presents all information on a multi-page interactive Streamlit dashboard via live recalculating statistical tests, embedded Folium (interactive) maps and Plotly (interactive) plots

## Interactive Maps & Plots

Each map and the three statistical charts at the head of the dashboard are not flat pictures but readable and interactive: hover them and toggle them either together as part of the dashboard's **[Interactive Maps & Plots page](https://borderoptics-bkx3lpcvfghdpa2hmuqwsg.streamlit.app/Interactive_Maps)**, or on individual map/plot viewers provided by the portfolio site link.

## Key Findings

Built-up area change is not confirmed, but sensitive to the size of the compositing window. A full-year composite does not show any significant change in NDBI (Wilcoxon signed-rank, p = 1.000); a composite of just the summer months (June–September) on the same villages shows a highly significant increase in NDBI instead (Wilcoxon signed-rank, p < 0.000001). The opposite conclusion is drawn, partly because the full-year window is snow-cover contaminated and partly because the summer window excludes data from Sikkim. Not either of these outcomes alone, but this instability, is reported as the project's focus.

Against a matched non-VVP control group of 753 villages across the same region, results from the summer-matched sample are statistically different (district-fixed-effects DiD, p = 0.0021), whereas those from the full-year sample are not (p = 0.215) — the same window-sensitivity pattern, now shown to hold after controlling for each region's own trend. This also holds at 250m and 1km buffer radii, so it isn't an artifact of the 500m radius used everywhere (all p < 0.002 on a sample-matched comparison), and it survives Holm-Bonferroni correction for multiple testing.

But as a general trend the change is not consistent. The reported increase is also mostly in a recoverable sub-period (2023 to 2025) after an earlier down period (2021 to 2023): the latter three-year comparison is not statistically significant, therefore the two-point comparison (2021 to 2025) is to be interpreted as "a late-window effect" rather than sustained growth since the programme sanctioned.

Tested similarly for both windows, the VIIRS radiance results indicate no significant change either way (p = 0.050 full-year, p = 0.9999 summer-matched), a more consistent null result, given more weight than the window-sensitive NDBI result.

An arithmetical comparison of the mean measured built-up change in the two states shows Arunachal Pradesh (+0.0284) and Uttarakhand (+0.0293) landing almost identical — despite Arunachal Pradesh's sanctioned budget (₹2,749.74 crore) running roughly ten times Uttarakhand's (₹270.58 crore). The two states' measured change tracks each other far more closely than their budgets do, giving an intuitive picture of budget-independent implementation.

The full methodological approach, including all of the hypotheses tested as well as the "robustness" check of the compositing window and the control group/multi-year/buffer-radius checks taken throughout, can be found on the Methodology & Limitations page of the dashboard and in `BO_Project_Report.md`.

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
├── BO_Project_Report.md
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