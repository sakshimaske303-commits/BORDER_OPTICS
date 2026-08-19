# BORDER OPTICS — Satellite Verification of India's Vibrant Villages Programme

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21759970.svg)](https://doi.org/10.5281/zenodo.21759970)

**Testing whether India's ₹4,800 crore border-villages programme produced verifiable development — and whether a single satellite-composite choice can flip the answer.**

## Live Dashboard

**[View the interactive dashboard →](https://borderoptics-bkx3lpcvfghdpa2hmuqwsg.streamlit.app/)**

## Project Documentation

| Document | What's Inside |
|---|---|
| [`BO_Executive_Summary.pdf`](./BO_Executive_Summary.pdf) | One-page snapshot — question, method, headline finding, robustness checklist, and links (fastest overview) |
| [`BO_Project_Report.md`](./BO_Project_Report.md) | Polished project summary — methodology, findings, conclusions (start here) |
| [`BO_Research_Paper.md`](./BO_Research_Paper.md) | Formal academic paper — literature review, statistical methodology, results, discussion |
| [`BO_Development_Log.md`](./BO_Development_Log.md) | Full technical development log — every bug, debugging session, and methodology iteration |

---

BORDER OPTICS is an independent satellite-verification framework that tests whether India's Vibrant Villages Programme (VVP-I) — a ₹4,800 crore border-area development scheme sanctioned across 2,967 villages in five Himalayan states/UTs — has produced measurable physical development on the ground. Rather than trusting a single satellite comparison, built-up area change (NDBI) and night-time light growth (VIIRS) are tested as two independent hypotheses, every result is run under two separate compositing windows (full-year and summer-matched) specifically to test whether the methodology choice itself changes the answer, and the significant result that survives is further checked against a matched non-VVP control group, a three-point multi-year trend, and a buffer-radius sensitivity sweep before being trusted.

This project exists because, asked directly in Parliament whether VVP's impact had ever been assessed, the Ministry of Home Affairs answered without qualification: *"No impact assessment has been carried out"* (Lok Sabha Unstarred Question No. 508, 3 February 2026). Every hypothesis here is tested rigorously, and every finding — including where a result reverses between two equally defensible measurement choices — is reported honestly rather than resolved by citing whichever version looks cleanest.

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

- Compiles a verified, village-level dataset of VVP-I priority villages across five Himalayan border states/UTs, cross-checked against officially reported aggregate counts
- Geocodes 258 villages via a dual-source pipeline (OpenStreetMap Nominatim, with ISRO's Bhuvan Village Geocoding API as a Census-linked fallback)
- Independently tracks **built-up area change (NDBI)** and **night-time light growth (VIIRS)** across a 2021–2025 baseline — treating them as two separate hypotheses, not one combined assumption
- Tests whether measured change correlates with each state's sanctioned VVP-I budget, or diverges from it
- Tests whether proximity to the border/Line of Actual Control predicts the pace of development, consistent with securitization theory's prediction that border proximity — not developmental need — drives priority
- Explicitly tests **compositing-window sensitivity** (full-year vs. summer-matched) as its own robustness check, rather than trusting a single satellite comparison
- Benchmarks treated-village change against a matched **non-VVP control group** of 753 villages in the same 14 districts, via a district-fixed-effects Difference-in-Differences model, to isolate a programme-attributable effect from the region's own trend
- Extends the core 2021-vs-2025 comparison to a **three-point 2021/2023/2025 trend**, and tests the fixed 500m extraction buffer against 250m and 1km alternatives, so neither a single anomalous year nor a single buffer choice can be driving the result unnoticed
- Presents all findings through a multi-page interactive Streamlit dashboard with live-recalculating statistical tests, embedded Folium interactive maps, and Plotly interactive plots

## Interactive Maps & Plots

Every village-level map and the three headline statistical charts are hoverable and toggleable, not flat images — view them together on the dashboard's **[Interactive Maps & Plots page](https://borderoptics-bkx3lpcvfghdpa2hmuqwsg.streamlit.app/Interactive_Maps)**, or via the map/plot viewers linked from the portfolio site.

## Key Findings

**Built-up area change is compositing-window sensitive, not confirmed.** A full-year composite shows no significant increase in NDBI (Wilcoxon signed-rank, p = 1.000); a season-matched (June–September) composite on the same villages shows a highly significant increase (p < 0.000001) — the opposite conclusion, traced to snow-cover contamination in the full-year window and monsoon cloud cover eliminating Sikkim's data entirely in the summer window. This instability, not either single result, is reported as the project's central finding.

**The summer-matched result survives three further stress tests.** Against a matched 753-village non-VVP control group in the same districts, the summer-matched treated-vs-control gap is significant (district-fixed-effects DiD, p = 0.0021) while the full-year gap is not (p = 0.215) — the same window-sensitivity pattern, now shown to hold after controlling for the region's own trend. The result also holds at 250m and 1km buffer radii, not just the 500m radius used throughout (all p < 0.002 on a sample-matched comparison), and survives Holm-Bonferroni correction for multiple testing.

**But the change is not a steady trend.** A three-point 2021/2023/2025 extension shows the reported increase is concentrated in a 2023-to-2025 recovery following an earlier 2021-to-2023 decline — the overall three-year trend is not itself statistically significant, so the two-point 2021-vs-2025 comparison should be read as a late-window effect, not sustained growth since programme sanction.

**Night-lights, the more temporally stable proxy, shows no confirmed increase.** Tested identically under both windows, VIIRS radiance shows no significant change either way (p = 0.050 full-year, p = 0.9999 summer-matched) — a consistent null that carries more weight than the window-sensitive NDBI result.

**Budget scale does not appear to predict development scale.** Arunachal Pradesh's sanctioned budget (₹2,749.74 crore) is roughly ten times Uttarakhand's (₹270.58 crore), yet the two states' mean measured built-up change is nearly identical (+0.0284 vs. +0.0293) — descriptively consistent with budget-independent implementation.

Full methodology, including every hypothesis tested, the compositing-window robustness check, and the control-group/multi-year/buffer-radius checks applied throughout, is documented in the dashboard's Methodology & Limitations page and in `BO_Project_Report.md`.

## Repository Structure

```text
BORDER_OPTICS/
├── app.py                          # Streamlit dashboard entry point (Home page)
├── pages/                          # Dashboard sub-pages (Study Design, Built-Up Change,
│                                    #   Night-Lights, Statistical Validation, Explore Trends,
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