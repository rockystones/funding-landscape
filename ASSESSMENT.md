# Assessment of v0.1

Independent review, 2026-09-17. Every number below was recomputed from
`data/mechanisms.csv`, not taken from the delivery notes.

---

## 1. What exists

190 standing mechanisms, 92 distinct funders, 33 fields, all 10 funder
categories populated. Built 2026-07-18 by a 24-agent run with a per-category
adversarial verifier.

| Category | Rows | | Category | Rows |
|---|---:|---|---|---:|
| federal_research | 63 | | state_regional | 13 |
| private_foundation | 21 | | international_mobility | 12 |
| defense_security | 17 | | mission_applied | 11 |
| professional_society | 17 | | industry | 11 |
| disease_advocacy | 16 | | institutional | 9 |

Confidence: 132 high · 54 medium · 4 low.

## 2. What holds up

**The dataset passes its own acceptance criteria under independent
re-validation.** `scripts/build.py --check` implements every gate in
`docs/BRIEF.md` §9 and reports **zero errors** across 190 rows:

- no controlled-vocabulary violations in any of 14 enumerated fields;
- no duplicate `(funder, program_name)` keys;
- no dated deadlines leaking into `application_cadence`;
- every `career_stage` value present in ≥2 rows across ≥2 categories;
- `institutional` and `industry` both carry guidance rows;
- no `restricted_to` row with blank `identity_targeting`;
- every row carries `source_url`, `confidence` and `checked_date`.

That is an unusually clean result for a 190-row multi-agent research run, and it
is the main reason the corpus is worth building on rather than rebuilding.

**Coverage against the brief's own anchor list: 28 of 31.** The three absent
anchors are Hertz, Ford Foundation and NYSTEM — and two of those are
*informative* absences (Ford discontinued its fellowship; NYSTEM wound down),
which is precisely the situation the schema cannot currently represent. See §3.1.

**The restraint is real.** `selectivity` is "unspecified" on 153/190 rows and
`review_signals_informal` is blank on 167/190. Both were specified as
blank-by-default, and both were genuinely left blank rather than padded with
plausible invention. That discipline is worth more than the rows it cost.

## 3. What does not hold up

### 3.1 The schema cannot say a programme has ended — and 48% of it is federal

91 of 190 rows (48%) are `federal_research`, `defense_security` or
`mission_applied`. The dataset was stamped 2026-07-18 and has **no `status`
field and no validity interval**. A cancelled programme, a paused competition
and a thriving one are indistinguishable. For a US federal corpus assembled
across 2025–26, that is the single most consequential gap: the most likely way
this dataset misleads someone is by listing something that no longer exists.

The Ford and NYSTEM absences show the workaround the v0.1 run fell back on —
silently omitting wound-down programmes. That loses information. A reader
looking for the Ford fellowship cannot tell "not researched" from "no longer
exists".

**This is the highest-value change available** and it is cheap: one `status`
enum, one `valid_to`, one `status_source`.

> **Update 2026-09-18 — resolved.** Schema 0.3.0 added the columns and the build
> gates them: a status without evidence and a source fails. The backfill then ran
> to completion — **all 177 enumerated rows carry a sourced status** (172 active,
> 3 paused, 2 terminated), with the 16 guidance rows exempt by D-012. Ford and
> NYSTEM are back as `terminated` rows instead of silent omissions, and three
> genuine pauses surfaced that the old schema could not have expressed, including
> a Microsoft fellowship suspended since 2023.
>
> The backfill also inverted the expected finding. Almost nothing had ended; what
> had rotted were the **citations**. Eleven rows pointed at archived
> solicitations, expired notices, 404s or a renamed programme, and all eleven
> turned out to describe live funding. The most consequential single fact found
> was not a termination either: NSF skipped the **entire FY2026 MRI competition**,
> returning proposals without review, with the next window opening 15 October 2026.
> Details in `research/2026-09-17-status-backfill/FINDINGS.md`.

### 3.2 Provenance is row-level, but the fields drift at different speeds

> **Update 2026-09-17 — addressed in schema 0.3.0.** The four drift-sensitive
> fields now carry their own `*_checked` dates, and the build emits a worklist
> ranked by age × drift-rate × whether the funder sits in the volatile federal
> band, with never-verified fields ranked apart from merely old ones.

Each row carries one `source_url`, one `confidence`, one `checked_date` for all
33 fields. But `stated_purpose` is near-static while `typical_award_size` and
`identity_targeting` drift fast. A single row-level stamp cannot express "the
purpose is still right, the amount is a year stale" — so re-verification has to
re-do whole rows, and staleness cannot be targeted where it matters.

### 3.3 The numeric fields are prose, so nothing can be computed

| Field | State | Consequence |
|---|---|---|
| `typical_award_size` | free text, 190/190 | no value axis without parsing |
| `typical_duration` | free text, inconsistent case | no duration axis |
| `years_since_degree_max` | **blank on 160/190 (84%)** | the one field built for numeric filtering is mostly empty |
| `selectivity` | "unspecified" on 153/190 (81%) | no competitiveness axis |

`scripts/build.py` now derives an annual/total USD envelope from the award text
and grades it — **121 clean, 18 heuristic, 51 unparsed**. Measured accuracy on a
16-row holdout was 14/16 before a further fix. That is enough for distributions
and orders of magnitude; it is *not* enough to quote a programme's amount. The
underlying fix is curation, not a better regex.

`years_since_degree_max` is the worse problem, because blank is ambiguous: it
means both "no time gate" and "not captured". Those must be separated.

### 3.4 Domain coverage contradicts the brief's stated scope

The brief opens with "**All research domains**, not one. Domain is a field, not a
filter on inclusion." The data does not honour that:

| Domain | Rows | Sole-domain rows |
|---|---:|---:|
| biomedical_health | 91 | 38 |
| life_sciences | 78 | 6 |
| engineering | 43 | 2 |
| physical_sciences | 43 | 4 |
| computing_math | 31 | 4 |
| social_sciences | 15 | 4 |
| **humanities** | **4** | 2 |
| **arts** | **1** | 1 |

Absent entirely: **Mellon** (the largest US humanities funder), **ACLS**,
**Guggenheim**, **Russell Sage**, **Spencer**, **W.T. Grant**, **Robert Wood
Johnson** (the largest US health-policy philanthropy), **Ford**, **MacArthur**,
**Keck**, **Kavli**, **Templeton**, **Getty**, **Luce**.

This is not a rounding error. A humanities scholar filtering this sheet gets
four rows and would reasonably conclude the dataset is not for them.

### 3.5 Catalogue depth is thin outside the big federal agencies

**63 of 92 funders (68%) have exactly one logged programme.** The brief's
stopping rule (§2.2) is explicit: traverse each funder's own programme index and
log every standing programme, not representative examples. NIH (28 rows) and NSF
(15) were traversed properly. Most foundations and societies were not — AHA has
5 rows against a catalogue of roughly a dozen standing awards; most societies
have one.

So the corpus is **broad across funders and shallow within them**. Both the
`biomedical_health` skew and the single-row funders point the same way: breadth
was achieved, depth was not.

### 3.6 Smaller things

- **Excel mojibake.** The CSV is valid UTF-8 without a BOM and holds 132
  non-ASCII characters (— – ≥ ≤ →). Excel on Windows renders these as garbage.
  Fixed by exporting a `utf-8-sig` copy for Excel, not by touching the vault
  (D-005).
- **`biomedical_health` vs `life_sciences` is not a real boundary.** They
  co-occur on most rows (91 and 78 appearances, but only 6 sole `life_sciences`
  rows). Two labels are doing one label's work.
- **`prior_funding_exclusion` is prose where the schema promised structure.**
  Values include "unspecified" (32), "no" (22), "none.", "not applicable",
  "varies by mechanism". It cannot be filtered, which defeats its purpose — the
  brief built this field specifically to answer "does my R21 disqualify me?".
- **`source_url` rot, now measured.** 11 of 177 enumerated rows (6%) cited a
  document that could no longer establish current status. All eleven described
  live funding; nine have been repointed (D-013). Nothing in the schema detects
  this, and it is a distinct failure mode from a programme ending.
- **The companion guide was never produced.** `docs/BRIEF.md` §9 lists it as
  artifact 2 of 2, with 5–7 worked personas. It remains deferred.

---

## 4. What to do next, in priority order

Ordered by *consequence per unit of work*, not by size.

1. **Durability layer** (P1). Add `status` (`active` / `paused` / `terminated` /
   `unknown`), `valid_to`, `status_checked`. Backfill against the 91 federal
   rows first. Fixes the way this dataset is most likely to mislead.
2. **Re-verification pass** (P1). Every row is stamped 2026-07-18, now 61 days
   old. Re-check the drift-sensitive fields — amounts, eligibility windows,
   identity gates — rather than whole rows. Needs §3.2 first to be efficient.
3. **Humanities, arts and social sciences** (P2). Roughly 25–35 rows across
   Mellon, ACLS, Guggenheim, NEH's remaining divisions, Russell Sage, Spencer,
   W.T. Grant, RWJF. The cheapest large gain in usefulness.
4. **Catalogue depth for the 63 single-row funders** (P2). Re-run the §2.2
   traversal per funder. Expect 60–120 additional rows.
5. **The companion guide** (P3). Already scoped in the brief; genuinely useful
   once §3.4 is fixed, and misleading before then.
6. **Structured `years_since_degree_max` and `prior_funding_exclusion`** (P3).
   Separate "no gate" from "not captured"; split the exclusion prose into a
   boolean plus a disqualifying/preserved pair.

## 5. What can be expanded

Beyond filling gaps — the directions where this corpus becomes something the
spreadsheet is not:

- **The live layer** (brief §8). A separate, disposable
  `live_opportunities_us.csv` keyed to durable rows, re-pulled on demand. Turns
  a reference map into something with deadlines you can act on.
- **Country swap.** The brief was written country-agnostic with Canada and EU
  templates ready (§10). Canada is the cheaper second run; the EU needs the
  supranational pass (ERC/MSCA/EIC) first. A three-jurisdiction corpus answers
  "where should I do this work?", which no single-country sheet can.
- **Eligibility as a computable predicate.** The gate columns are already
  structured. Given a person's stage, years-since-degree, citizenship, domain and
  institution type, the set of mechanisms they can pursue is *derivable*. That is
  a function over the existing schema — the main blocker is §3.3's blank
  `years_since_degree_max`.
- **Funder-portfolio view.** With catalogue depth (§3.5), each funder becomes a
  ladder of programmes across career stages, and the gaps in a funder's own
  ladder become visible — useful to the funders themselves.
- **Success-rate layer.** NIH reports success rates per activity code and
  institute; NSF publishes them by directorate. For the federal half, the 81%
  "unspecified" in `selectivity` is fillable from published data rather than
  guessed.

---

## 6. Bottom line

v0.1 is a sound, well-QC'd, unusually honest corpus that is **broad across
funders and shallow within them**, **skewed biomedical against its own stated
scope**, and **unable to say whether a programme still exists** — in a period
when that last question matters more than usual for the 48% of it that is
federal. The structure is worth keeping. The next unit of work belongs in the
durability layer, not in more rows.
