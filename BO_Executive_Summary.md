# BORDER OPTICS
### A Satellite-Based Verification Framework for India's Vibrant Villages Programme (VVP-I)

Executive Summary · DOI: 10.5281/zenodo.21759970 · Sakshi D. Maske

## Project Overview

The origins of BORDER OPTICS lie in one line in a Parliamentary reply. Responding directly to the question, the Ministry of Home Affairs said that no impact assessment has ever been conducted for the Vibrant Villages Programme — this despite the scheme having already sanctioned roughly Rs. 4,800 crore across 2,967 villages, covering five Himalayan border states and union territories from Arunachal Pradesh to Ladakh. There's an intersection of three fields that I don't want to consider separately — the gap that I'm digging to fill. It starts with political science, given that VVP is a textbook example of infrastructure that does double duty as both civilian welfare and geopolitical signaling. The next is economics, a large-scale public investment that has never been costed against the results it delivers. And the third is geospatial science, because satellite imagery lets the Government's implicit claim of development be directly tested instead of taken on faith. So, I tested it — 258 individually geocoded villages benchmarked against a matched non-VVP control group of 753 villages in the same districts, using two equally defensible ways of compositing the same satellite record. There wasn't a simple yes or no that came back. One measurement option shows a real, significant rise in built-up area; the other shows no growth at all — and that instability is itself the major thing this project found, exactly the kind of ambiguity an actual impact assessment should have resolved before Rs. 4,800 crore went out the door. Wherever the surviving result could be pressure-tested — against the control group, through a third year, through three buffer sizes — it held. If cost translated to results, ten times the money should have bought ten times the outcome — it didn't. Parliament said no one had been looking. This is what looking actually turns up.

## The Question

When directly asked in a Lok Sabha Unstarred Question (Lok Sabha Question No. 508, 3 February 2026) whether any impact assessment had been done of the Vibrant Villages Programme, the Ministry of Home Affairs responded, "No impact assessment has been carried out." The question this project set out to answer traces back to that gap: did India's Rs. 4,800 crore border-village development scheme produce measurable physical development on the ground — and can the answer be trusted, or does it depend on which measurement choice you make?

## The Method

258 individually geocoded villages, benchmarked against a matched non-VVP control group of 753 villages in the same 14 districts, were tested across 5 Himalayan border states and UTs. The satellite record was provided by Sentinel-2 built-up-area change (NDBI) and VIIRS night-lights, 2021–2025. In each case, two independent compositing windows were used, specifically full-year and summer-matched. The before/after change was addressed by Wilcoxon signed-rank tests, the budget/border-proximity relationships were addressed by Spearman correlations, and the comparison with the control group was addressed using a district fixed-effects Difference-in-Differences model. Two more checks are added to the core design: the 2021/2025 comparison is expanded to a 3-point 2021/2023/2025 trend, and the fixed extraction buffer of 500m is compared to alternative extraction buffers of 250m and 1km.

## The Finding

Finally, the built-up-area result can be summarily said to be compositing-window sensitive and not confirmed. There is no significant change seen in a full-year composite, but there is a very significant change in the same villages recomposited to a June–September summer-matched window. The dichotomy traces to the type of artifact present on either side: snow-cover contamination in the full-year window, and monsoon cloud cover in the summer window, effectively eliminating Sikkim's data. Three additional stress tests were applied to this significant summer result, and it survived all three — it is significantly larger than the change seen in a matched district-FE non-VVP control group (p = 0.0021), it holds at 250m and 1km buffer radii as well as 500m, and it survives Holm-Bonferroni correction for multiple testing. It isn't a steady trend, though: a three-point 2021/2023/2025 extension reveals the bulk of the change is concentrated in a 2023-to-2025 recovery.

| Test | Full-Year Window | Summer-Matched Window |
|---|---|---|
| NDBI change (Wilcoxon) | p = 1.000 — not significant | p < 0.000001 — highly significant |
| Night-lights change (Wilcoxon) | p = 0.050 | p = 0.9999 |
| Control-group DiD (NDBI, H4) | p = 0.215 — not significant | p = 0.0021 — significant |
| Budget vs. measured change | ~10x budget gap (AP vs. UK) → nearly identical mean change (same in both windows) | ~10x budget gap (AP vs. UK) → nearly identical mean change (same in both windows) |

Night-lights is also more important as a proxy here than the headline NDBI indicator, for the opposite reason: it is the more reliable, consistent measure that isn't affected by the seasonal confounding factor that disrupts NDBI. Budget also tells its own story: Arunachal Pradesh's sanctioned budget of Rs. 2,749.74 crore comes close to ten times Uttarakhand's Rs. 270.58 crore. Despite this gap in size, the two states' average measured built-up change is practically indistinguishable descriptively, consistent with implementation that doesn't track budget size.

## Validation & Robustness Checklist

* ✓ Dual compositing-window test (full-year + summer-matched)
* ✓ Two independent metrics tested separately (NDBI + VIIRS)
* ✓ Matched non-VVP control group (753 villages, same 14 districts, DiD design)
* ✓ Three-point multi-year trend (2021/2023/2025), not a single before/after pair
* ✓ Buffer-radius sensitivity swept (250m/500m/1km)
* ✓ Cross-checked against sanctioned budget (Parliamentary record)
* ✓ Every data gap disclosed (Ladakh, HP, Uttarakhand caveats)
* ⚠ NDBI result flagged as window-sensitive — and, once significant, shown to be concentrated in 2023–2025 rather than sustained since sanction

## Honest Limitation

This is not a clean confirmation, this is an instability disclosure. The Himalayas introduce their own seasonally driven measurement artifacts: snow cover in winter months confounds the full-year window, and monsoon cloud cover wipes out usable summer data for Sikkim entirely. Those artifacts alone are enough to make a single compositing choice unreliable evidence. Comparing to the control villages strengthens the remaining signal, but the comparison itself rests on an imbalance in NDBI level before treatment relative to the control group, without any actual proof of a common pre-trend. Due to limitations on sample size and geometry, the "border-proximity" correlation (H3) is treated as exploratory rather than confirmatory. The data gaps – the "unresolved" villages in Ladakh, the "partial" sample in HP, and the "block" confusion in Uttarakhand – are not glossed over here.

## Real-World Relevance

Parliament was told no independent impact study exists for a Rs. 4,800 crore government scheme spanning 2,967 sanctioned villages — this project is that study. It demonstrates the feasibility and necessity of satellite methods for verifying public infrastructure projects, and it demonstrates something else: when two of the most defensible measurement options yield opposite results, the useful answer for a policymaker isn't to side-step or overlook the doubt that raises, but to examine both independently — first revealing whether there's any instability, then stress-testing whichever result stands up against a control group, a multi-year sweep, and a sensitivity analysis of the methodology.

---

GitHub: github.com/sakshimaske303-commits/BORDER_OPTICS | Live Dashboard: borderoptics-bkx3lpcvfghdpa2hmuqwsg.streamlit.app | Zenodo DOI: 10.5281/zenodo.21759970

Sakshi D. Maske — Independent Geospatial Researcher
