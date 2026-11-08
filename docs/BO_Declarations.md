# BORDER OPTICS: Declarations

**Evaluating a Place-Based Border Programme from Space: Evidence and Indicator Limits from India's Vibrant Villages Programme**

Sakshi D. Maske · Independent Geospatial Researcher · ORCID [0009-0002-5683-5966](https://orcid.org/0009-0002-5683-5966)

Version 2.1.0  
Earlier preprint: [EarthArXiv](https://eartharxiv.org/repository/view/14830/) · Code and data: [github.com/sakshimaske303-commits/BORDER_OPTICS](https://github.com/sakshimaske303-commits/BORDER_OPTICS)

## Highlights

- 220 geocoded priority villages of the Vibrant Villages Programme in Arunachal Pradesh and Uttarakhand are compared with 628 non-priority villages in the same 13 districts, 2021–2025.
- Sentinel-2 NDBI, VIIRS night lights and Sentinel-1 radar show no priority–comparison difference (all p ≥ 0.33).
- That null cannot rule out construction: buildings cover a median 0.32% of a 500 m buffer, so doubling a village's buildings would move NDBI by about 0.002, less than a fifth of the smallest effect the design can detect.
- Dynamic World built-up probability shows a small positive difference in the summer window, roughly 1,900 m² of built-up surface per village, which holds under every check; the full-year estimate is not significant.
- A pooled link between change and distance to the border disappears or reverses when villages are compared within their own district.

## Who did what, and who paid

The study is mine alone: I framed the questions, assembled and geocoded the village lists, selected the comparison villages, extracted the satellite data, ran and checked the models, and wrote the paper and dashboard (CRediT: Conceptualization, Methodology, Software, Validation, Formal analysis, Investigation, Data curation, Writing – original draft, Writing – review and editing, Visualization). It had no external funding; I covered every cost. I declare no competing interests, and I have no connection with the programme or with any body that runs or evaluates it. The study works with public lists and satellite data at village level, with no participants or personal data, so it did not require ethical approval.

## Use of AI tools

The research design, the choice of primary and secondary analyses and the interpretation of the results are my own. I used Claude (Anthropic), an AI assistant, in a supporting role throughout the project. Its main use was to check that the estimates reported in the paper, executive summary, README, results stability table and dashboard remained consistent with the analysis outputs after each round of corrections. I also consulted it when a script failed or produced output I could not explain, and for the layout of the project pages. After the independent review of version 2.0, I used it to re-run the analysis scripts, to verify the documents and dashboard against the outputs, and to draft the script for the Holm correction (Development Log Entry 50). I also used it to suggest corrections and clearer wording for parts of this paper and to structure these declarations. I reviewed every suggestion before using it. The assistant was not used to geocode villages, select comparison villages, extract satellite data, design the statistical models or decide which results to report. I take full responsibility for the content of this paper.

## Sources, sharing and licences

Village lists come from Ministry of Home Affairs replies to Parliament, the Arunachal Pradesh list of identified villages and a secondary Uttarakhand list matched to official counts. Villages were geocoded with OpenStreetMap Nominatim and ISRO Bhuvan, and comparison villages were taken from OpenStreetMap. Satellite inputs, all through Google Earth Engine, are Sentinel-2, Sentinel-1, VIIRS night lights, Dynamic World and Google Open Buildings. Boundary lines are from Natural Earth and are cartographic only; the Line of Actual Control is disputed, so distances to it are comparative. Text, figures and my own code are released under CC BY 4.0, while files derived from OpenStreetMap remain under the Open Database Licence.

## Rerunning the work

The dashboard and the statistical scripts run from the files in the repository; only the extraction scripts need a Google Earth Engine account. `ANALYSIS_FREEZE.md` records exactly which data and code produced the reported numbers, and `tests/test_data_integrity.py` checks 16 invariants of the data. The primary difference-in-differences is implemented twice, in statsmodels and in NumPy, and the two agree to machine precision.

## How the results changed

The headline results moved several times as I found and fixed errors, and every movement is kept in `BO_Results_Stability_Table.md`. An early significant summer NDBI increase disappeared once an incomplete extraction, which had returned no summer scenes for Sikkim, was redone. A significant full-year night-light result disappeared after 23 comparison villages that duplicated priority villages were removed. An apparent disagreement between cloud masks turned out to be a coding error that counted snow as clear sky. Version 2.0 followed an independent review of the whole project: the primary analysis became the difference-in-differences, a detectability analysis and small-cluster inference were added, and the earlier reading of the border-distance correlations as robust was withdrawn. Version 2.1 followed a second review of the code and data. Most of the comparison villages for Sikkim turned out to lie outside the district, many in Nepal, Bhutan or West Bengal, so Sikkim was taken out of the analysis; and the model was changed so that villages are compared only within their own district. With these corrections the full-year Dynamic World result is no longer significant, and the other results stand. Two limits remain open: completed works are not observed, only priority designation, and the positional accuracy of the geocoded villages has not yet been verified on imagery.

## Citation

Citation metadata are in `CITATION.cff`.
