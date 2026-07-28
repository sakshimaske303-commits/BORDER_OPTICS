# 🛰️ BORDER OPTICS — Satellite Verification of India's Vibrant Villages Programme

**Testing whether India's ₹4,800 crore border-villages programme produced verifiable development — and whether a single satellite-composite choice can flip the answer.**

## 🔗 Live Dashboard

**[View the interactive dashboard →](#)** *(https://borderoptics-bkx3lpcvfghdpa2hmuqwsg.streamlit.app/)*

## 📄 Project Documentation

| Document | What's Inside |
|---|---|
| 📘 [`Project_Journal.md`](./Project_Journal.md) | Polished project summary — methodology, findings, conclusions (start here) |
| 📗 [`Research_Paper.md`](./Research_Paper.md) | Formal academic paper — literature review, statistical methodology, results, discussion |
| 📙 [`Development_Log.md`](./Development_Log.md) | Full technical development log — every bug, debugging session, and methodology iteration |

---

BORDER OPTICS is an independent satellite-verification framework that tests whether India's Vibrant Villages Programme (VVP-I) — a ₹4,800 crore border-area development scheme sanctioned across 2,967 villages in five Himalayan states/UTs — has produced measurable physical development on the ground. Rather than trusting a single satellite comparison, built-up area change (NDBI) and night-time light growth (VIIRS) are tested as two independent hypotheses, and every result is run under two separate compositing windows (full-year and summer-matched) specifically to test whether the methodology choice itself changes the answer.

This project exists because a government reply on parliamentary record states explicitly that no impact assessment has ever been carried out for VVP. Every hypothesis here is tested rigorously, and every finding — including where a result reverses between two equally defensible measurement choices — is reported honestly rather than resolved by citing whichever version looks cleanest.

---

## 📊 What This Project Does

- Compiles a verified, village-level dataset of VVP-I priority villages across five Himalayan border states/UTs, cross-checked against officially reported aggregate counts
- Geocodes 258 villages via a dual-source pipeline (OpenStreetMap Nominatim, with ISRO's Bhuvan Village Geocoding API as a Census-linked fallback)
- Independently tracks **built-up area change (NDBI)** and **night-time light growth (VIIRS)** across a 2021–2025 baseline — treating them as two separate hypotheses, not one combined assumption
- Tests whether measured change correlates with each state's sanctioned VVP-I budget, or diverges from it
- Tests whether proximity to the border/Line of Actual Control predicts the pace of development, consistent with securitization theory's prediction that border proximity — not developmental need — drives priority
- Explicitly tests **compositing-window sensitivity** (full-year vs. summer-matched) as its own robustness check, rather than trusting a single satellite comparison
- Presents all findings through a multi-page interactive Streamlit dashboard with live-recalculating statistical tests and embedded Folium interactive maps

## 🔬 Key Findings

**Built-up area change is compositing-window sensitive, not confirmed.** A full-year composite shows no significant increase in NDBI (Wilcoxon signed-rank, p = 1.000); a season-matched (June–September) composite on the same villages shows a highly significant increase (p < 0.000001) — the opposite conclusion, traced to snow-cover contamination in the full-year window and monsoon cloud cover eliminating Sikkim's data entirely in the summer window. This instability, not either single result, is reported as the project's central finding.

**Night-lights, the more temporally stable proxy, shows no confirmed increase.** Tested identically under both windows, VIIRS radiance shows no significant change either way (p = 0.050 full-year, p = 0.9999 summer-matched) — a consistent null that carries more weight than the window-sensitive NDBI result.

**Budget scale does not appear to predict development scale.** Arunachal Pradesh's sanctioned budget (₹2,749.74 crore) is roughly ten times Uttarakhand's (₹270.58 crore), yet the two states' mean measured built-up change is nearly identical (+0.0284 vs. +0.0293) — descriptively consistent with budget-independent implementation.

Full methodology, including every hypothesis tested and the compositing-window robustness check applied throughout, is documented in the dashboard's Methodology & Limitations page and in `Project_Journal.md`.

## 🗂️ Repository Structure

```text
BORDER_OPTICS/
├── app.py                          # Streamlit dashboard entry point (Home page)
├── pages/                          # Dashboard sub-pages (Study Design, Built-Up Change,
│                                    #   Night-Lights, Statistical Validation, Explore Trends,
│                                    #   Interactive Maps, Methodology & Limitations)
├── utils/
│   ├── theme.py                    # Shared dashboard styling
│   └── data.py                     # Shared data-loading functions
├── data/
│   ├── raw/                        # Raw village lists per state
│   └── processed/                  # Geocoded villages, GEE satellite exports, analyzed results
├── src/
│   ├── acquisition/                # Geocoding scripts (Nominatim, Bhuvan, merge)
│   ├── analysis/                   # Statistical testing, border-distance computation
│   └── visualization/              # Static chart + interactive map generation
├── outputs/
│   ├── figures/                    # Static PNG charts
│   └── interactive_maps/maps/      # Folium interactive HTML maps
├── Project_Journal.md
├── Research_Paper.md
├── Development_Log.md
└── requirements.txt
```

## 🛠️ Tech Stack

Python · Pandas · GeoPandas · SciPy · Folium · Plotly · Streamlit · Google Earth Engine · OpenStreetMap Nominatim · ISRO Bhuvan API · Natural Earth

## 📚 Data Sources

| Dataset | Provider |
|---|---|
| Village Lists | State VVP-I portals; Rajya Sabha / Lok Sabha Q&A annexures |
| Geocoding | OpenStreetMap Nominatim; ISRO Bhuvan Village Geocoding API |
| Built-Up Index (NDBI) | Sentinel-2 SR Harmonized (Google Earth Engine) |
| Night-Lights | VIIRS DNB monthly composites (Google Earth Engine) |
| Border/LAC Geometry | Natural Earth 10m Admin-0 Boundary Lines |
| Budget / Project Counts | Parliamentary record (Rajya Sabha / Lok Sabha Q&A) |

## ▶️ Running Locally

```bash
git clone https://github.com/sakshimaske303-commits/BORDER_OPTICS.git
cd BORDER_OPTICS
pip install -r requirements.txt
streamlit run app.py
```

## 👤 Author

**Sakshi D. Maske**

Independent Geospatial Researcher

---

*This project's full development process — including every debugging session, methodology iteration, and technical decision — is documented in `Development_Log.md` for full transparency and reproducibility.*