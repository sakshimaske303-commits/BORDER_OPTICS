# BORDER OPTICS — Pitch Document (Draft)

*Drafted 2026-09-17, following Anara AI's review and its suggested pitch framings. Every factual claim below was checked before inclusion — either against `BO_Research_Paper.md`/`BO_Development_Log.md` directly, or independently verified via web search where it involves a claim outside the paper itself (the VVP-II figures, specifically). Anara's original framing is used as a starting point, not copied uncritically — see the verification notes at the end. This is a draft; treat every number as something to double-check against the frozen paper yourself before sending it anywhere.*

## One-line pitch

The first independent impact evaluation of India's ₹4,800 crore Vibrant Villages Programme, using satellite proxies and a district-matched control difference-in-differences design, which finds that no effect survives rigorous robustness testing on the primary measure, while an alternative proxy disagrees, and documents exactly which measurement choices produced which answer.

## The gap, stated precisely

VVP-I was cleared by the Union Cabinet in February 2023: ₹4,800 crore for border-area development across five Himalayan states/UTs (Arunachal Pradesh, Sikkim, Uttarakhand, Himachal Pradesh, Ladakh), with 662 villages marked "priority" for Phase I. Asked directly whether the programme's effect had ever been assessed, the Ministry of Home Affairs told Parliament: *"No impact assessment has been done"* (Lok Sabha Unstarred Question No. 508, 3 February 2026). This study is the first quantitative, satellite-based attempt to answer that question independently.

## What the study actually found (do not oversimplify this)

- **Primary result, null and robust.** Neither built-up area (NDBI) nor night-lights shows a significant treated-village increase, in either of two compositing windows, against either a before/after test or a district-matched, district-fixed-effects control-group DiD. This null survives an exact wild cluster bootstrap (16,384 sign-flip combinations, addressing the study's 14-district cluster count), a genuine 2019–2021 parallel pre-trends placebo test (clean in three of four combinations, one borderline), and a same-day-extraction, fully decontaminated control group.
- **A genuine, reported tension, not a clean story.** Dynamic World's built-up classifier — validated more strongly than NDBI against independent building-footprint ground truth (Spearman ρ = 0.808 vs. 0.399) — shows a small but significant control-group effect in both windows, and correctly detects all three of the study's confirmed construction case studies (Kaho, Walong, Musai) where NDBI moved the wrong way. This is reported as an open, unresolved disagreement, not resolved into a tidy conclusion either way.
- **A secondary finding that runs against the programme's own logic.** Built-up change correlates with distance from the border — but in the opposite direction from what securitization theory predicts: villages *farther* from the border show more change, not closer ones (summer NDBI ρ = 0.291, p = 0.0000026; survives leave-one-district-out, randomization inference, and a spatial-autocorrelation-corrected permutation test).
- **Two data reversals, both caught and fixed, both disclosed.** An early summer-window result (p < 0.000001) turned out to rest on an incomplete 154-village sample missing Sikkim entirely; once complete, it went null. An early control-group night-lights result (the study's only surviving significant control-group finding) turned out to rest on a contaminated control list — 23 control villages that were physically or nominally the same settlements as treated ones; once fixed, it went null too. Both are documented with before/after numbers in `BO_Development_Log.md` and, as of this pitch, summarized in one table in `BO_Results_Stability_Table.md`.

## Why this hasn't been done before

Night-lights and DiD have been used to evaluate specific Indian development policies before — most closely, Chindarkar & Goyal's 2023 evaluation of Gujarat's Jyotigram Yojana rural electrification scheme using village-level DiD on night-time luminosity (also finding a null, published in *Energy Policy*). But no prior study has applied this template to a border-development program, used a district-matched non-program control group in Himalayan terrain, or treated the compositing-window choice itself as an object of a robustness audit the way this study does. VVP-I itself has never been evaluated by anyone — government or independent — before this.

**Correction to keep in mind when pitching this:** don't claim "nobody has ever used satellites to assess development programs" — that's false and checkable in one search. The accurate claim is narrower and still strong: nobody has assessed *this* programme, and no border-development programme anywhere has been evaluated with this design.

## Three audience-specific versions

### To a journal
*(World Development, Journal of Development Effectiveness, Remote Sensing Applications: Society and Environment, or Economic and Political Weekly for a policy audience)*

Lead with the accountability gap (Parliament asked, MHA answered "never assessed"), then the null, then the Dynamic World tension as the discussion hook — not a hedge, but the paper's most interesting open question. The pre-trends placebo and exact wild cluster bootstrap are what get a careful null past the reflexive "null = weak design" read. Consider leading the results section with the equivalence-framed statement of the null (draft in `BO_Equivalence_Framing_Draft.md`) rather than only "p = 0.31."

### To policymakers or media

Lead with the number, not the statistics: ₹4,800 crore, 662 priority villages, zero independent impact assessments ever conducted — this is the first one, and the honest answer is that satellites cannot yet confirm the promised build-out on the primary measure. The border-proximity finding (development *decreasing* with proximity to the border, the opposite of what a security-driven prioritization logic implies, and the one result that survives every stress test) is the most quotable, concrete result in the paper.

### To funders or for research-statement use

Pitch the next step. VVP-II was approved by the Union Cabinet on 4 April 2025 at a total outlay of ₹6,839 crore, covering 17 states/UTs (including Arunachal Pradesh, Sikkim, and Uttarakhand, already in this study's core sample, plus Ladakh, Assam, Bihar, Gujarat, J&K, Manipur, Meghalaya, Mizoram, Nagaland, Punjab, Rajasthan, Tripura, Uttar Pradesh, and West Bengal). The evaluation infrastructure built for VVP-I — the geocoding pipeline, the satellite extraction scripts, the district-matched control design, the full robustness stack — is directly reusable. The pitch: *"The evaluation infrastructure I built for VVP-I is directly reusable, and VVP-II is already running, before anyone has measured anything."*

## Verification notes (what was checked before this document was written)

- The Chindarkar & Goyal (2023) citation was independently verified: real, published in *Energy Policy*, exactly the DiD-on-night-lights-for-a-named-Indian-policy design described.
- VVP-II's approval date (4 April 2025), total outlay (₹6,839 crore), and the list of 17 states/UTs were independently verified against the PIB press release, not taken on Anara's word.
- The "no impact assessment has been done" quote and VVP-I's ₹4,800 crore / 662-village / five-state figures are taken directly from `BO_Research_Paper.md`'s own abstract and introduction, which already cite the underlying parliamentary questions.
- The securitization-theory framing is not an add-on for this pitch — it's already the paper's own stated theoretical frame (§2.1, keywords, H3/H4 hypotheses), so using it here doesn't misrepresent the study's design.
- Not independently re-verified here: the remaining citations in Anara's literature review (SHRUG platform, Gibson et al., Hartojo et al., Chatterjee & Ojha) — those weren't load-bearing for this pitch document, but should be checked before citing them in an actual submission.
