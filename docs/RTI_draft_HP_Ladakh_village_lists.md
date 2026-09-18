# Draft RTI Application — VVP-I Village-Wise Lists for Himachal Pradesh and Ladakh

**Not filed, and not planned to be.** This was drafted in support of Section 7.4
of `BO_Research_Paper.md`, but Sakshi has decided not to file it — the cost and
multi-month reply timeline aren't justified for this project's scope. Kept here
only as a transparency record of what was considered, not as an open task.
Confirmed (September 2026) that no public source substitutes for it either:
PIB releases, MHA's own parliamentary replies, and Ladakh's district
administration all give only aggregate project counts and budgets, never
village names, for either jurisdiction. This study's core sample is scoped to
Arunachal Pradesh, Sikkim, and Uttarakhand accordingly — see
`ANALYSIS_FREEZE.md` item 11.

Original draft below, unfiled:

Read before filing:
- File under the **Right to Information Act, 2005**.
- The Public Authority is the **Ministry of Home Affairs** (Border Management
  Division handles VVP-I).
- Filed either online at **rtionline.gov.in** (select Ministry/Department:
  "Ministry of Home Affairs") or physically by post to the CPIO address given
  in the template.
- Standard fee: ₹10 (as of this drafting — check the current fee schedule on
  rtionline.gov.in before filing, since fees are occasionally revised).
  Online filing accepts payment by the portal's own gateway; postal filing
  needs an Indian Postal Order or demand draft in favour of the Accounts
  Officer, Ministry of Home Affairs, payable at New Delhi.
- Under Section 7(1), the CPIO must respond within **30 days** (35 days if
  the request is transferred to another public authority under Section 6(3)).
- If no response, or an unsatisfactory one, arrives in time, the next step is
  a **first appeal** to the department's own Appellate Authority (Section
  19(1)), not a fresh RTI — worth knowing going in, not something to figure
  out only if this stalls.
- Keep this specific and factual, citing exact prior parliamentary answers by
  question number and date (already done below) — a specific request tied to
  information the Ministry has already partially disclosed on the record is
  harder to deflect than an open-ended one, and matches this study's own
  standing practice of checking every claim against a primary source rather
  than taking anything on trust.

---

## Combined application (recommended — one fee, one submission)

**To:**
The Central Public Information Officer
Ministry of Home Affairs
Border Management Division
Government of India
North Block, New Delhi – 110001

**Subject:** Request for village-wise list of priority villages sanctioned under the Vibrant Villages Programme (Phase I) in Himachal Pradesh and the Union Territory of Ladakh

**Application under the Right to Information Act, 2005**

Sir/Madam,

I am writing to request the following information under the Right to Information Act, 2005, regarding the Vibrant Villages Programme (VVP-I), approved by the Union Cabinet in February 2023 for the development of border villages in five Himalayan border States/Union Territories.

1. **Himachal Pradesh:** The Ministry's own replies to Lok Sabha Unstarred Question No. 2104 (2023) and Rajya Sabha Question No. 3251 (2023) confirm that 75 villages in Himachal Pradesh have been identified as priority villages under VVP-I, but do not list these villages by name. I request the complete, village-wise list of all 75 priority villages sanctioned for Himachal Pradesh under VVP-I, including the name of each village, its district, and its block/tehsil.

2. **Ladakh:** The Ministry's reply to Lok Sabha Unstarred Question No. 4360 (2025) confirms that 35 villages in the Union Territory of Ladakh have been sanctioned under VVP-I, but does not list these villages by name. I request the complete, village-wise list of all 35 sanctioned villages for Ladakh under VVP-I, including the name of each village and its district (Leh/Kargil).

3. If either list has changed in number since the parliamentary replies cited above (for example, through subsequent additions, exclusions, or corrections), I request the currently correct and up-to-date village-wise list for each, along with a note of what changed and when, if readily available.

If this information is held by a different division, office, or public authority than the one this application is addressed to, I request that it be transferred to the appropriate CPIO under Section 6(3) of the Act, with notice to me of that transfer.

I enclose the prescribed fee of ₹10 [by Indian Postal Order / Demand Draft No. _______ dated _______, payable to the Accounts Officer, Ministry of Home Affairs, New Delhi / paid online via the RTI Online Portal, reference no. _______] (retain whichever applies and delete the rest).

I request that the information be provided within the time limit prescribed under Section 7(1) of the Act.

Yours sincerely,

Sakshi D. Maske
Independent Geospatial Researcher
[Address]
[Email]
[Phone]
[Date]

---

## When to split into two applications instead

File two separate applications (same template, one covering only Himachal
Pradesh, the other only Ladakh) if:
- The RTI Online Portal's own form restricts a single application to one
  clearly-defined subject and a combined HP+Ladakh request risks being
  treated as two matters bundled together (this has, in practice, drawn
  first-appeal pushback in some Ministries on the grounds that a single
  application should ask about a single matter — Ladakh being a separate
  Union Territory from Himachal Pradesh's State administration is a
  plausible split point).
- A first response to the combined application answers one half and stays
  silent on the other — refile the unanswered half on its own rather than
  appealing the whole application.

---

## After a response arrives

Whatever village names come back, cross-check them the same way this study's
own geocoding pipeline already does for every other state (Section 3.3): run
them through the Nominatim/Bhuvan geocoding pipeline, manually validate each
district match, and only add successfully geocoded villages to the sample —
not as a new, separate procedure, but as the same one `geocode_villages.py`
and `geocode_villages_bhuvan.py` already apply to Arunachal Pradesh, Sikkim,
and Uttarakhand. This closes the two largest named gaps in Section 6.1
("Village Coverage Gaps") if it succeeds, and is worth logging as its own
Development Log entry either way — including if the RTI is refused, delayed,
or answered incompletely, per this study's own standing practice of
recording what was tried, not only what worked.
