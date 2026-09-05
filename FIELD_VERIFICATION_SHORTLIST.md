# BORDER OPTICS — Field Verification Shortlist

Top 3 villages per state, ranked by the largest measured built-up-area increase (`ndbi_change`, 2021→2025) — these are the villages where the satellite shows the strongest "development" signal, so they're the most worth confirming on the ground.

## Arunachal Pradesh (summer-matched window)

| Rank | Village | District | Block | NDBI change | Lights change | Distance to border | Coordinates |
|---|---|---|---|---|---|---|---|
| 1 | Ramu | Kurung Kumey | Damin | +0.131 | −0.145 | 33.6 km | 28.108404, 93.419110 |
| 2 | Katuk | Kurung Kumey | Damin | +0.112 | −0.109 | 25.3 km | 28.118909, 93.250140 |
| 3 | Nisuk | Kurung Kumey | Damin | +0.105 | −0.185 | 33.4 km | 28.108182, 93.414929 |

All three sit in the same Damin block — that's not a selection artifact, it's genuinely where the strongest signal clusters.

## Uttarakhand (summer-matched window)

| Rank | Village | District | Block | NDBI change | Lights change | Distance to border | Coordinates |
|---|---|---|---|---|---|---|---|
| 1 | Mana | Chamoli | Joshimath | +0.086 | +0.132 | 5.9 km | 30.967123, 79.410969 |
| 2 | Dharali | Uttarkashi | Bhatwari | +0.074 | +1.270 | 27.4 km | 31.040847, 78.781531 |
| 3 | Sukki | Uttarkashi | Bhatwari | +0.072 | +0.301 | 31.2 km | 31.014000, 78.710800 |

## Himachal Pradesh (summer-matched window — illustrative 7-village case study, not part of the core statistical sample)

| Rank | Village | District | Block | NDBI change | Lights change | Distance to border | Coordinates |
|---|---|---|---|---|---|---|---|
| 1 | Chhitkul | Kinnaur | Unknown | +0.278 | +0.037 | 24.8 km | 31.388100, 78.462190 |
| 2 | Pooh | Kinnaur | Unknown | +0.023 | +0.331 | 8.3 km | 31.761590, 78.583932 |
| 3 | Chango | Kinnaur | Unknown | +0.004 | +0.105 | 8.3 km | 31.977757, 78.594402 |

Chhitkul's +0.278 is the single largest NDBI jump in the whole dataset — worth prioritizing if only one call is possible.

## Sikkim (full-year window — the summer-matched window has zero usable images for every Sikkim village, per BO_Development_Log.md Entry 5, so this state can only be ranked on full-year data)

| Rank | Village | District | Block | NDBI change | Lights change | Distance to border | Coordinates |
|---|---|---|---|---|---|---|---|
| 1 | Tung | North | Chungthang | +0.023 | −0.016 | 9.1 km | 27.547500, 88.649300 |
| 2 | Chungthang | North | Chungthang | +0.013 | +0.664 | 11.2 km | 27.604236, 88.646520 |
| 3 | Lachen | North | Lachen | +0.001 | −0.558 | 26.4 km | 27.730546, 88.546905 |

Sikkim's changes are much smaller than the other three states even at the top of the ranking — worth keeping in mind when comparing what people on the ground actually report.

## Notes

- `ndbi_change` is the built-up-index change between the 2021 and 2025 satellite composites — a positive number means the satellite sees more construction/built-up surface now than in 2021.
- `lights_change` is the same before/after comparison for night-time light brightness (VIIRS); it doesn't always move the same direction as NDBI, which is itself part of what the project is testing.
- Coordinates are geocoded village centroids (OpenStreetMap Nominatim, with ISRO Bhuvan as fallback) — good enough to place a call or find the panchayat, not survey-grade.
