# BORDER OPTICS — Satellite Evidence on India's Vibrant Villages Programme

[![EarthArXiv](https://img.shields.io/badge/EarthArXiv-Preprint-B7410E.svg)](https://eartharxiv.org/repository/view/14830/)

**Did India's ₹4,800 crore Vibrant Villages Programme (VVP-I) change its border villages, and how much change could satellites actually detect?**

**[Interactive dashboard →](https://borderoptics-bkx3lpcvfghdpa2hmuqwsg.streamlit.app/)**

| Document | Contents |
|---|---|
| [`BO_Executive_Summary.md`](./docs/BO_Executive_Summary.md) | Two-page summary: question, method, findings, limitations (start here) |
| [`BO_Research_Paper.md`](./docs/BO_Research_Paper.md) | Full paper (v2.0) |
| [`BO_Development_Log.md`](./docs/BO_Development_Log.md) | Complete development record, including every error found and fixed |
| [`BO_Results_Stability_Table.md`](./docs/BO_Results_Stability_Table.md) | Every result that changed between versions, and why |
| [`ANALYSIS_FREEZE.md`](./docs/ANALYSIS_FREEZE.md) | Exact data and code state behind the reported numbers |
| [`BO_Declarations.pdf`](./docs/BO_Declarations.pdf) | Authorship, funding, interests, data licences, corrections and AI use |
| [`DATA_DICTIONARY.md`](./docs/DATA_DICTIONARY.md) | Every data file and column |
| [`BORDER_OPTICS_Maps_and_Plots.pdf`](./docs/BORDER_OPTICS_Maps_and_Plots.pdf) | All figures and maps in one printable file |
| [`NEXT_STEPS_EARTH_ENGINE.md`](./docs/NEXT_STEPS_EARTH_ENGINE.md) | Prepared analyses that need a live Earth Engine session |

## Research question

In February 2026 the Ministry of Home Affairs told Parliament that no impact assessment of VVP-I had been carried out (Lok Sabha Unstarred Question No. 508). This project asks:

> **Did VVP-I priority villages show more satellite-observed built-up and night-light change between 2021 and 2025 than non-priority villages in the same districts?**

It also asks what change each satellite measure could actually detect, and whether change concentrates near the international boundary.

## Data and method

- **Villages.** 251 priority villages geocoded in Arunachal Pradesh, Sikkim and Uttarakhand (7 Himachal Pradesh villages shown as illustrations), plus 721 comparison villages from OpenStreetMap in the same 14 districts.
- **Measures.** All inside a 500 m buffer, for 2019, 2021, 2023 and 2025, in full-year and June–September composites (Google Earth Engine):
  - Sentinel-2 NDBI
  - VIIRS night lights
  - Sentinel-1 VV/VH
  - Dynamic World built-up probability
  - Google Open Buildings footprints
- **Design.** District fixed-effects difference-in-differences with inference for 14 clusters (t with 13 df and an exact wild cluster bootstrap). Plus a 2019–2021 placebo, leave-one-district-out, randomization inference, a detectability analysis in physical units, and a within-district analysis of border distance.

## Key findings (v2.0)

1. **NDBI, night lights and radar show no priority–comparison difference** (all p ≥ 0.31).
2. **That null cannot rule out construction.** Buildings cover a median 0.33% of a 500 m buffer, so doubling a typical village's buildings would move buffer-mean NDBI by about 0.002, 13–14% of the smallest detectable effect.
3. **Dynamic World built-up probability, the most building-sensitive measure, shows a small positive difference** in both windows. It is equivalent to about 800–2,100 m² of built-up surface per village (bootstrap p = 0.041 full year, 0.008 summer). The summer result is robust to every check; the full-year result depends on Sikkim.
4. **No consistent border-proximity pattern.** Pooled correlations with border distance come from differences between districts and disappear or reverse within districts.

See the paper for full numbers, robustness checks and limitations.

## Repository structure

```text
BORDER_OPTICS/
├── README.md, LICENSE, CITATION.cff, requirements*.txt
├── app.py, pages/, utils/        Streamlit dashboard (home + 8 pages)
├── static/                       PDFs served by the dashboard's document viewer
├── docs/                         Paper, executive summary, development log, declarations (.md + .pdf),
│                                 results stability table, analysis freeze, data dictionary,
│                                 maps-and-plots PDF, next steps, RTI draft, review record
├── data/raw/                     Official village lists, Natural Earth boundaries
├── data/processed/               Geocoded villages, Earth Engine extractions, DiD panels, summaries
├── src/acquisition/              Geocoding, control selection, Earth Engine extraction
│   ├── extract_settlement_masked.py      footprint-zone outcomes + 2026 window (not yet run)
│   └── check_s2_archive_ingestion.py     test of the Sikkim "archive backfill" explanation
├── src/analysis/                 Statistics
│   ├── did_model.py                      primary DiD (statsmodels)
│   ├── did_numpy.py                      same DiD in NumPy + t(13) + wild bootstrap
│   ├── measurement_sensitivity.py        detectability, building-equivalent area, equivalence
│   ├── dynamic_world_robustness.py       bootstrap, leave-one-out, composition checks
│   ├── triangulation_holm.py             Holm correction across the triangulation DiDs
│   ├── h3_within_district.py             border distance: pooled vs within-district
│   ├── compute_lac_distance.py           distance to the China boundary only
│   ├── sample_qa_sensitivity.py          duplicates, building-free buffers, pipeline swap
│   └── settlement_masked_did.py          DiD on footprint-zone outcomes, once extracted
├── src/visualization/            Figures, maps, and the PDF builders
│   ├── build_docs_pdfs.sh                rebuilds the paper, summary and log PDFs (docs/ + static/)
│   └── build_maps_plots_pdf.py           rebuilds docs/BORDER_OPTICS_Maps_and_Plots.pdf
├── outputs/                      Figures, maps, JSON/CSV results
├── tests/test_data_integrity.py  Data invariants (15 checks)
└── archive/                      Superseded files kept as an audit trail
```

## Running locally

```bash
git clone https://github.com/sakshimaske303-commits/BORDER_OPTICS.git
cd BORDER_OPTICS
pip install -r requirements-lock.txt
streamlit run app.py                      # dashboard (no Earth Engine needed)
python tests/test_data_integrity.py       # data checks
python src/analysis/measurement_sensitivity.py
python src/analysis/h3_within_district.py
python src/analysis/triangulation_holm.py
bash src/visualization/build_docs_pdfs.sh        # rebuild document PDFs (needs pandoc + wkhtmltopdf)
python src/visualization/build_maps_plots_pdf.py # rebuild the maps-and-plots PDF
```

The extraction scripts in `src/acquisition/` need a Google Earth Engine account (`earthengine authenticate`, `EE_PROJECT` in `.env`). The scripts added in v2.0 under `src/analysis/` need only NumPy, pandas and SciPy.

## Data sources and attribution

| Data | Provider / licence |
|---|---|
| Village lists | Ministry of Home Affairs parliamentary replies; Arunachal Pradesh identified-villages list; secondary Uttarakhand list matched to official counts |
| Geocoding | OpenStreetMap Nominatim (© OpenStreetMap contributors, ODbL); ISRO Bhuvan |
| Comparison villages | OpenStreetMap Overpass API (© OpenStreetMap contributors, ODbL) |
| Sentinel-2 SR Harmonized, Sentinel-1 GRD | Contains modified Copernicus Sentinel data (ESA), via Google Earth Engine |
| VIIRS DNB monthly composites | Earth Observation Group / NOAA, via Google Earth Engine |
| Dynamic World V1 | Google / World Resources Institute (CC BY 4.0) |
| Open Buildings v3 | Google Research (CC BY 4.0 / ODbL) |
| Boundary lines | Natural Earth (public domain); cartographic only, the LAC is disputed |

## Declarations

The complete statement is in [`BO_Declarations.pdf`](./docs/BO_Declarations.pdf) (source: [`BO_Declarations.md`](./docs/BO_Declarations.md)). Briefly:

- **Author and funding:** a single author carried out every stage; there was no external funding and there are no competing interests.
- **Ethics:** public village lists and satellite data at village level only; no participants or personal data.
- **Corrections:** each change to a headline result, and the version 2.0 changes made after an independent review, is listed, with the full record in `BO_Results_Stability_Table.md`.
- **AI use:** see the AI-use section of [`BO_Declarations.pdf`](./docs/BO_Declarations.pdf).

## Licence

Text, figures and original code are released under [CC BY 4.0](./LICENSE). Files derived from OpenStreetMap (the control-village lists and their extractions) remain subject to the Open Database License (ODbL) and must be shared under it.

## Author

**Sakshi D. Maske** — Independent Geospatial Researcher
