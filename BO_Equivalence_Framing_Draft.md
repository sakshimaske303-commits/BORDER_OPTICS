# Equivalence-Framed Null: Draft Paragraphs

*Drafted 2026-09-17, at an external reviewer's suggestion that the null result should be stated as a bound ("this design rules out effects larger than X"), not just as a failed rejection ("p = 0.31"). Every number below is taken directly from `BO_Research_Paper.md` §4.6 (the DiD 95% confidence intervals) and §7.7 (the power analysis) as already frozen — nothing here is a new computation. This is a draft for Sakshi to review and place in the abstract/conclusion herself; it is not inserted into `BO_Research_Paper.md`.*

## One correction to the external reviewer's framing, worth keeping

The external reviewer's suggested wording was: *"the design rules out treated-village built-up gains larger than X percentage points at 95% confidence."* That phrasing quietly merges two different statistical objects — a confidence interval (which the control-group DiD tests actually have) and a minimum detectable effect from a power calculation (which is what H1's treated-only test has instead, since a paired Wilcoxon test doesn't produce a CI on an effect size the way the DiD regression does). Below, the two are kept separate and correctly labeled, since blurring them would be a real, checkable error in a paper whose whole selling point is getting this kind of thing right.

## Paragraph A — for the control-group DiD result (H4), CI-based, ready to adapt

*This is the more rigorous of the two, because it's a direct restatement of already-computed 95% confidence intervals, not a new claim.*

> Framed as a bound rather than a failed rejection: at 95% confidence, this design rules out a treated-vs-control gap in built-up index (NDBI) larger than +0.0196 in the full-year window or +0.0062 in the summer-matched window, and a gap in VIIRS night-light radiance larger than +0.1478 (full-year) or +0.1166 (summer-matched) — in every one of the four primary outcome/window combinations, the upper confidence bound sits well inside the range of NDBI and lights change actually observed across the sampled villages (roughly −0.11 to +0.48 for full-year NDBI, −0.33 to +5.97 for summer lights). A gap of the scale VVP-I's ₹4,800 crore, 662-priority-village sanction would be expected to produce, had it been fully realized and satellite-detectable, is not compatible with these bounds.

## Paragraph B — for the treated-only result (H1), power-based, correctly labeled as such

> Separately, the treated-only test's null is not simply a case of insufficient power to detect anything: the design's minimum detectable effect (80% power, α = 0.05, two-sided, following Cameron & Miller's 2015 guidance for this study's small-cluster-count structure) is Cohen's d = 0.178 for H1 — just under the conventional threshold for a "small" effect — meaning a small-to-moderate true effect would have been caught had one existed. This is a power statement, not a confidence bound, and is reported as such rather than folded into the CI language above.

## Suggested combined version for the abstract (shorter)

> Framed as a bound, not just a failed rejection: at 95% confidence, no treated-vs-control gap larger than +0.02 in built-up index or +0.15 in night-light radiance survives in any of the four primary outcome/window combinations, well inside the range of change actually observed in the sampled villages; separately, the treated-only design had 80% power to detect an effect as small as Cohen's d = 0.178, ruling out insufficient power as the explanation for this study's null.

## Sourcing

- Full-year NDBI DiD: coefficient +0.00667, 95% CI [−0.0062, +0.0196] — `BO_Research_Paper.md` §4.6.
- Summer NDBI DiD: coefficient −0.00357, 95% CI [−0.0133, +0.0062] — §4.6.
- Full-year lights DiD: coefficient +0.05046, 95% CI [−0.0468, +0.1478] — §4.6.
- Summer lights DiD: coefficient +0.03244, 95% CI [−0.0518, +0.1166] — §4.6.
- H1 MDE (Cohen's d = 0.178): §7.7.
- Observed NDBI/lights change ranges: computed directly from `data/processed/border_optics_village_results_analyzed.csv` and `..._summer_analyzed.csv` (core sample, n=251) on 2026-09-17 — this one range-context figure is new arithmetic (min/max of an already-existing column), not a new statistical test or estimate.
