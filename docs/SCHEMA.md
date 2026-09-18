# Schema decisions

Answers to the ten P0 decisions in the house new-project schema checklist,
for this corpus. Deviations from the house default are marked **[deviation]**.

## 1. Record grain

**Flat registry: one row = one standing funding mechanism.** No dated events, no
typed links between records, so the v4 timeline kernel does not apply (D-003).
The closest house pattern is a sibling measured-data project's schema-validated registry with a source
on every record.

Natural key: `(funder, program_name)`. No surrogate ids — the pair is stable and
human-readable, and dedup is enforced at build.

## 2. Evidence axes

**[deviation]** The corpus inherited a single coarse `confidence`
(high/medium/low) from `docs/BRIEF.md` rather than the house T1–T4 ×
documented/attested/inferred/contested pair. It is not being retrofitted, because
the existing labels were applied consistently by a verifier pass. Mapping for
anyone reading across projects:

| House | This corpus |
|---|---|
| T1 primary | `source_url` on the funder's own domain (the documented norm here) |
| T2–T4 | aggregator-sourced rows, which the brief forbids as a final source |
| documented | `confidence = high` + funder-page source |
| attested | `confidence = medium` |
| inferred | `confidence = low`, or any `(est.)` amount |
| contested | not represented — see open items |

Build-enforced ceiling in place: a run where `low` exceeds 25% of rows fails QC.

## 3. Ignorance conventions

- `"unspecified"` is a first-class value, not a gap: 153/190 on `selectivity`,
  14/190 on `typical_award_size`. Never replaced with an estimate.
- `(est.)` suffix marks an estimated amount; surfaced as `award_estimated`.
- `coverage_type = guidance` marks the 19 rows that describe a *class* of funding
  (institutional internal money, bespoke industry money) rather than a named
  programme. These are the mandated availability-bias correction, and they are
  **not comparable to enumerated rows** in any aggregate.
- `review_signals_informal` is blank-by-default (167/190 blank). A blank cell is
  a correct answer; an invented signal is a failure.
- **[gap]** No `source_attempts` ledger. Coverage claims in `ASSESSMENT.md` are
  therefore stated as row counts, never as "we looked and found nothing".

## 4. IDs and identity

Natural composite key, exact-equality dedup, no fuzzy matching anywhere — so no
similarity threshold and no negative control is needed for identity. The only
threshold in the codebase is the award-text parser, which *does* carry a measured
error rate (§ below and D-006).

## 5. Derived vs stored

**Never stored in the vault; always recomputed:**

| Derived field | From |
|---|---|
| `annual_min_usd` / `annual_max_usd` | `typical_award_size` + `typical_duration` |
| `total_min_usd` / `total_max_usd` | same |
| `award_parse`, `award_flags`, `award_estimated` | `typical_award_size` |
| `duration.min_years` / `.max_years` | `typical_duration` |
| `staleness_days` | `checked_date` vs build date |

`scripts/build.py` opens the vault read-only. Nothing writes back.

## 6. Kernel and version ceremony

Vocabularies live in one place — `VOCAB` in `scripts/build.py` — transcribed from
`docs/BRIEF.md` §4. Unknown values are build errors, not warnings.

Ceremony: any enum or shape change bumps `SCHEMA_VERSION`, gets a `DECISIONS.md`
entry with a named approver, and is additive. Current: **0.2.0** (0.1.0 was the
delivered CSV; 0.2.0 adds the derived layer and the grading).

## 7. Research pipeline contract

v0.1 ran gatherer → adversarial verifier → deterministic assembly across 24
agents. For P2 coverage work, re-adopt the ai-good-practice folder contract:
`research/<date>-<slug>/{BRIEF,SOURCES,FINDINGS,SESSION-LOG}.md`, agents writing
only to `gather/` and `verify/`, full-file rewrite every 8–10 items, waves ≤3.

## 8. Gates with numbers

Implemented in `scripts/build.py::validate` — every criterion in brief §9. Run
`--check` before any commit.

**Measured, not asserted:** the award parser was audited on a random sample
(n=22, seed 917) at 20/22, then on an independent holdout (n=16, seed 4471) at
14/16 ≈ 88%. Both failure classes from the first sample and one from the second
were fixed; the "and-joined alternatives" class remains open and is listed in
`ROADMAP.md`. Post-fix accuracy is **unmeasured** — a fresh audit with a new
recorded seed is a P4 exit criterion. The parser's grading (`clean` / `heuristic`
/ `unparsed`) exists so consumers can exclude what it cannot read, rather than
silently treating unparsed money as zero.

## 9. Presentation grammar

Frozen before the first UI, per house rule:

| Channel | Encodes |
|---|---|
| horizontal position | career stage (fixed order, undergraduate → senior) |
| vertical position | funder category (fixed order, federal → state) |
| cell fill intensity | row count in that cell |
| hue | funder category family |
| opacity | filter state — **dimmed, never removed** |
| border style | `coverage_type`: solid = enumerated, dashed = guidance |
| explicit label | `confidence`, shown at every layer |

`dist/corpus.json` is the single compiled input. Layout is deterministic: no
force simulation, no random seeds, same input → same pixels.

**Filters dim rather than remove** so a reader sees the funding they are *not*
eligible for. For this corpus that is the point, not a nicety.

## 10. Correction and review conditions

- Corrections are commits against `data/mechanisms.csv` with a message naming the
  field and the source that prompted the change.
- **Temporal validity (added 0.3.0).** `status` + `status_valid_to` record
  whether a programme still exists and when it stopped. The vocabulary is about
  *existence*, not about whether applications are open today:

  | value | means | test |
  |---|---|---|
  | `active` | the programme exists | funder presents it as current, no termination notice; a closed cycle proves nothing |
  | `paused` | the funder states it is suspended | explicit hold with no next cycle |
  | `terminated` | the funder states it has ended | explicit wind-down, sunset or elimination |
  | `unknown` | not assessed, or evidence inconclusive | the default; a dead link lands here, never in `terminated` |

  Enforced at build: any non-`unknown` status requires `status_evidence`,
  `status_source` and `status_checked`; `status_valid_to` is only legal on
  `terminated` or `paused`. See D-009 and D-010.

  **Guidance rows are exempt.** A `coverage_type = guidance` row describes a class
  of funding, not a programme, so it has no status to verify; those rows stay
  `unknown` and the build counts them apart from the re-check debt (D-012).
- **Field-level provenance (added 0.3.0).** `award_checked`,
  `eligibility_checked`, `identity_checked` and `review_criteria_checked` split
  the single row-level `checked_date` across the four fields that drift, so a
  re-check can target one field rather than re-doing a whole row. A **blank**
  stamp on a populated field means never verified, and the build's worklist ranks
  those separately from merely old ones.
- **[struck]** No review-conditions log. There is no human accept/dismiss loop in
  this corpus to calibrate; re-add if one appears (D-007).
