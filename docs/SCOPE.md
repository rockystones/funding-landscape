# What this corpus answers, and what it does not

Written 2026-09-18, after the project's actual goal was stated for the first time.
Every figure recomputed from `data/mechanisms.csv` (219 rows).

The goal has three parts. **The research brief only ever scoped the first one.**

| Question | Covered by | State |
|---|---|---|
| 1. What funding exists for my stage, and am I eligible? | the corpus | **mostly built** — two named holes |
| 2. How do I apply? (timeline, logistics, programme officers, sponsors) | nothing yet | **unbuilt**; the brief deferred the timing half to an optional live layer (§8) and never scoped the rest |
| 3. How do I make the application better? (writing, format, requirements, tailoring, examples) | nothing yet | **unbuilt**; never in the brief at all |

This is not a criticism of the brief. It was written to build a *map of
mechanisms*, and it did. But a map of mechanisms is roughly a third of what
someone actually needs to win a grant, and the roadmap should say so.

---

## 1. Eligibility — mostly covered

| Field | Rows carrying a real value | Filterable? |
|---|---:|---|
| `career_stage` | 219/219 | yes |
| `citizenship_residency` | 219/219 | yes |
| `submission_path` | 219/219 | yes |
| `eligibility_notes` | 215/219 | prose |
| `eligibility_window` | 170/219 | prose |
| `specific_topic` | 120/219 | prose |
| `topic_restricted` | 112/219 | yes |
| `institution_type_restriction` | 111/219 | yes |
| `years_since_degree_max` | **32/219** | yes |
| `identity_targeting` / `identity_gate_type` | 14/219 | yes |

**Hole A — the numeric career-stage gate is two-thirds missing.**
`years_since_degree_max` exists precisely so the sheet can answer "am I still
early-career enough for this?" numerically. 48 rows carry a time-since-degree
gate; only 32 have it in the numeric field. The other **16 state a year limit in
prose that never reached the column** — MIRA "within 10 yr", HHMI Hanna Gray and
Freeman Hrabowski "no more than 7 years", DARPA YFA "within 3 years", AHA
Established Investigator "no more than 15 years", and others. A blank here is
ambiguous between "no gate" and "not captured", and 16 of them are the second.

**Hole B — identity gates are thin, but probably correctly thin.** Only 14 rows,
and all 13 of the pre-existing ones were re-verified against the funder's page in
P1. Post-SFFA this is a small set by reality, not by omission.

## 2. Eligibility conflicts between grants — the strongest part of the corpus

The brief's principle 7 demanded that prior-funding exclusions record *both* the
disqualifying awards and the carve-outs, because "a bare `excluded` boolean is not
enough to answer 'does my R21 disqualify me?'". That was honoured. Fifteen rows
spell out R01-related conflicts, including the inverse rules:

- **Mentored K awards (K01, K08, K23, K25)** — ineligible if current or former
  PD/PI of an R01, P01, P50 or other major independent/career award (including
  DP1/DP2/DP5 and prior K awards), *with carve-outs* naming R03, R21 and others
  that preserve eligibility.
- **K99/R00** — ineligible if ever an independent PD/PI on an NIH research grant
  (R01, R03, R21), any K award, or another peer-reviewed grant over $100,000.
- **DP2 New Innovator** — ESI gate: must not have received an R01-equivalent.
- **ESI/NI-flagged R01** — the *enhancement* rule, recorded as such: R03, R21,
  R34/U34, R15, R36, SBIR/STTR and all F and K awards **preserve** ESI status;
  winning an R01 ends it.
- **K24 Midcareer** — inverted: *requires* current independent support as PD/PI.
- **MIRA** — mutually exclusive with other NIGMS research project grants.
- Non-NIH too: the AHA Career Development Award excludes K99/R00 and R01 holders;
  Damon Runyon's Clinical Investigator Award excludes R01 holders but *permits*
  K-type awards; the ACS Research Scholar Grant allows at most one R01.

**The limits.** Only 39/219 rows state any exclusion at all; 60 say `unspecified`
and 22 say `no`. And every one of them is **free prose**, so the question a person
actually asks — *"I hold an R01. What am I now locked out of?"* — cannot be
computed, only read row by row.

## 3. Submission requirements — not covered

No column exists for page limits, required documents, formats, biosketch rules or
forms. One row in 219 mentions any of it. `submission_path` records only the
*route* (individual / institutional nomination / by invitation), not what you
must produce.

The LOI or pre-proposal stage is mentioned in passing in 13 rows and structured
in none, even though it changes the whole timeline where it exists (RSF, Spencer's
research-practice partnerships, AACR, BWF).

## 4. Resubmission — not covered

**No column, and one row in 219 mentions it.** Nothing records NIH's A1
single-resubmission rule, what a resubmission must include, how NSF treats a
resubmitted proposal, or which funders forbid resubmission outright. For anyone
who has been scored and not funded — which is most applicants most of the time —
this is the single most actionable thing missing.

## 5. Calendar and review timeline — out of scope by design, partly recoverable

`application_cadence` is deliberately coarse (annual 153 · rolling 39 · irregular
22 · biennial 5) and the brief **forbids** dated deadlines in the durable dataset:
§8 puts them in a separate, disposable `live_opportunities_us.csv` that was never
built. That was a sound call — dates rot fastest of anything here — but it means
the corpus cannot answer "when do I submit, when is review, when would money
arrive".

Nothing records the review arc at all: NIH's study-section → council → award
sequence (roughly nine months from submission), NSF's six-month target, or the
gap between notification and start date.

**One thing already exists.** The P1 status backfill quoted a funder's own words
as evidence, and **81 of 219 rows now carry a real calendar date inside
`status_evidence`** — "14 July 2026", "November 19, 2026", "6 February 2029". It
was a by-product, not a goal, but it is a free head start: roughly 40% of the live
layer's hardest field is already sitting in the vault as unstructured text.

---

## What would close each gap

| Gap | Work | Size |
|---|---|---|
| Numeric career-stage gate (Hole A) | parse the 16 prose windows into `years_since_degree_max`; separate "no gate" from "not captured" with an explicit `no_time_gate` marker | small, mechanical |
| Eligibility conflicts as prose | add `excludes_awards` / `preserves_eligibility` as delimited lists; backfill from the existing prose, which is already good | medium; the content mostly exists |
| Submission requirements | new fields (page limits, required documents, LOI stage) + a research pass per major funder | large, new research |
| Resubmission | new fields (`resubmission_allowed`, `resubmission_policy`) + research pass | medium |
| Calendar / review timeline | build the brief's §8 live layer; seed it from the 81 dates already in `status_evidence` | medium, and partly pre-paid |
| Application craft (question 3) | not a corpus problem — a separate guide, with the corpus's `review_criteria_official` (87% populated) as its spine | large, different in kind |

The first, second and fifth are extensions of what exists. The third and fourth
need new schema. The sixth is a different artifact and should not be forced into
a spreadsheet.
