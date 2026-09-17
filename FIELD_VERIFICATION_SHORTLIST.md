# BORDER OPTICS — Field Verification Shortlist

Top 3 villages per state, ranked by the largest measured built-up-area increase (`ndbi_change`, 2021→2025) — these are the villages where the satellite shows the strongest "development" signal, so they're the most worth confirming on the ground.

## Arunachal Pradesh (summer-matched window)

| Rank | Village | District | Block | NDBI change | Lights change | Distance to border | Coordinates |
|---|---|---|---|---|---|---|---|
| 1 | Passik | Kurung Kumey | Parsi-Parlo | +0.085 | −0.034 | 42.5 km | 28.036002, 93.470545 |
| 2 | Pagam | Kurung Kumey | Parsi-Parlo | +0.079 | +0.026 | 40.6 km | 28.049312, 93.458500 |
| 3 | Ramu | Kurung Kumey | Damin | +0.078 | −0.145 | 33.0 km | 28.108404, 93.419110 |

Two of the three sit in the same Parsi-Parlo block, next door to Damin, where the previous ranking clustered — that's not a selection artifact, it's genuinely where the strongest signal is concentrated.

## Uttarakhand (summer-matched window)

| Rank | Village | District | Block | NDBI change | Lights change | Distance to border | Coordinates |
|---|---|---|---|---|---|---|---|
| 1 | Mana | Chamoli | Joshimath | +0.070 | +0.132 | 5.9 km | 30.967123, 79.410969 |
| 2 | Bagori | Uttarkashi | Bhatwari | +0.051 | +0.123 | 64.7 km | 30.770244, 78.474632 |
| 3 | Mukhawa | Uttarkashi | Bhatwari | +0.045 | +0.094 | 25.9 km | 31.054200, 78.790100 |

## Himachal Pradesh (summer-matched window — illustrative 7-village case study, not part of the core statistical sample)

| Rank | Village | District | Block | NDBI change | Lights change | Distance to border | Coordinates |
|---|---|---|---|---|---|---|---|
| 1 | Chhitkul | Kinnaur | Unknown | +0.209 | +0.037 | 24.8 km | 31.388100, 78.462190 |
| 2 | Pooh | Kinnaur | Unknown | +0.030 | +0.331 | 8.3 km | 31.761590, 78.583932 |
| 3 | Nako | Kinnaur | Unknown | −0.007 | +0.201 | 8.1 km | 31.881375, 78.627048 |

Chhitkul's +0.209 is the single largest NDBI jump in Himachal Pradesh — worth prioritizing if only one call is possible.

## Sikkim (summer-matched window)

| Rank | Village | District | Block | NDBI change | Lights change | Distance to border | Coordinates |
|---|---|---|---|---|---|---|---|
| 1 | Lingzah-Tolung | North | Passingdang | +0.014 | −0.130 | 29.2 km | 27.571000, 88.446600 |
| 2 | Chungthang | North | Chungthang | +0.008 | +0.586 | 11.2 km | 27.604236, 88.646520 |
| 3 | Tingchim | North | Kabi Tingda | +0.007 | −0.073 | 22.6 km | 27.460759, 88.527732 |

Sikkim's changes are much smaller than the other three states even at the top of the ranking — worth keeping in mind when comparing what people on the ground actually report.

## Notes

- `ndbi_change` is the built-up-index change between the 2021 and 2025 satellite composites — a positive number means the satellite sees more construction/built-up surface now than in 2021.
- `lights_change` is the same before/after comparison for night-time light brightness (VIIRS); it doesn't always move the same direction as NDBI, which is itself part of what the project is testing.
- Coordinates are geocoded village centroids (OpenStreetMap Nominatim, with ISRO Bhuvan as fallback) — good enough to place a call or find the panchayat, not survey-grade.
- These rankings were recomputed directly from the current `data/processed/border_optics_village_results_summer_analyzed.csv` (2026-09-17). Sikkim's summer-matched window now has valid data for every village following the Entry 21-22 re-extraction (see `BO_Development_Log.md`), so this shortlist no longer needs the full-year fallback an earlier version of this file used.
