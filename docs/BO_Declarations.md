# BORDER OPTICS: Declarations

**Did India's Vibrant Villages Programme Change Its Border Villages? A Multi-Sensor Difference-in-Differences Assessment, 2021–2025**

Sakshi D. Maske · Independent Geospatial Researcher · ORCID [0009-0002-5683-5966](https://orcid.org/0009-0002-5683-5966)

Version 2.0.0  
Earlier preprint: [EarthArXiv](https://eartharxiv.org/repository/view/14830/) · Code and data: [github.com/sakshimaske303-commits/BORDER_OPTICS](https://github.com/sakshimaske303-commits/BORDER_OPTICS)

## Highlights

- 251 geocoded priority villages of the Vibrant Villages Programme in Arunachal Pradesh, Sikkim and Uttarakhand are compared with 721 non-priority villages in the same 14 districts, 2021–2025.
- Sentinel-2 NDBI, VIIRS night lights and Sentinel-1 radar show no priority–comparison difference (all p ≥ 0.31).
- That null cannot rule out construction: buildings cover a median 0.33% of a 500 m buffer, so doubling a village's buildings would move NDBI by about 0.002, a seventh of the smallest effect the design can detect.
- Dynamic World built-up probability shows a small positive difference, equivalent to roughly 800–2,100 m² of built-up surface per village; the summer estimate holds under every check, the full-year one depends on Sikkim.
- A pooled link between change and distance to the border disappears or reverses when villages are compared within their own district.

## Who did what, and who paid

The study is mine alone: I framed the questions, assembled and geocoded the village lists, selected the comparison villages, extracted the satellite data, ran and checked the models, and wrote the paper and dashboard (CRediT: Conceptualization, Methodology, Software, Validation, Formal analysis, Investigation, Data curation, Writing – original draft, Writing – review and editing, Visualization). It had no external funding; I covered every cost. I declare no competing interests, and I have no connection with the programme or with any body that runs or evaluates it. The study works with public lists and satellite data at village level, with no participants or personal data, so it did not require ethical approval.

## Sources, sharing and licences

Village lists come from Ministry of Home Affairs replies to Parliament, the Arunachal Pradesh list of identified villages and a secondary Uttarakhand list matched to official counts. Villages were geocoded with OpenStreetMap Nominatim and ISRO Bhuvan, and comparison villages were taken from OpenStreetMap. Satellite inputs, all through Google Earth Engine, are Sentinel-2, Sentinel-1, VIIRS night lights, Dynamic World and Google Open Buildings. Boundary lines are from Natural Earth and are cartographic only; the Line of Actual Control is disputed, so distances to it are comparative. Text, figures and my own code are released under CC BY 4.0, while files derived from OpenStreetMap remain under the Open Database Licence.

## Rerunning the work

The dashboard and the statistical scripts run from the files in the repository; only the extraction scripts need a Google Earth Engine account. `ANALYSIS_FREEZE.md` records exactly which data and code produced the reported numbers, and `tests/test_data_integrity.py` checks 15 invariants of the data. The primary difference-in-differences is implemented twice, in statsmodels and in NumPy, and the two agree to machine precision.

## How the results changed

The headline results moved several times as I found and fixed errors, and every movement is kept in `BO_Results_Stability_Table.md`. An early significant summer NDBI increase disappeared once an incomplete extraction, which had returned no summer scenes for Sikkim, was redone. A significant full-year night-light result disappeared after 23 comparison villages that duplicated priority villages were removed. An apparent disagreement between cloud masks turned out to be a coding error that counted snow as clear sky. Version 2.0 followed an independent review of the whole project: the primary analysis became the difference-in-differences, a detectability analysis and small-cluster inference were added, and the earlier reading of the border-distance correlations as robust was withdrawn. Two limits remain open: completed works are not observed, only priority designation, and the positional accuracy of the geocoded villages has not yet been verified on imagery.

## Use of an AI assistant

Over the course of the project I used Claude (Anthropic), an AI assistant, as a working aid rather than as a source of findings. Much of what I asked of it was cross-checking: whether a p-value, a detectable effect or a building-equivalent area quoted in the paper, summary, README, stability table or dashboard still matched the JSON and CSV outputs after a round of corrections, since this project went through many. When an extraction or analysis script failed in a way I could not explain, I sometimes asked it to help me locate the cause, and I also used it for the layout of the project pages. I wrote the paper and the other documents; I asked it to mark sentences that were unclear or overly technical, gaps where something seemed missing, and punctuation, and I decided what to change. The independent review behind version 2.0 was not done by the assistant. For the consistency pass after it (Development Log Entry 50), the assistant re-ran the analysis scripts, checked the documents, dashboard and portfolio pages against the outputs, and drafted the wording corrections and the Holm-correction script, which I reviewed before accepting. It did not geocode villages, select comparison villages, pull satellite data or run the models, and the research design, the choice of primary and secondary analyses and every interpretation are mine. I checked each suggestion before using it and am responsible for the whole of the content.

## Citation

Citation metadata are in `CITATION.cff`.
