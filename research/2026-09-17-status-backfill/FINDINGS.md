# Status backfill — findings

**Session:** 2026-09-17 · **Phase:** P1 · **Rows touched:** 13 verified + 3 added
**Method:** each row's own `source_url` fetched and read for (a) whether the funder
still presents the programme as existing, and (b) the current eligibility wording.
Batch chosen by the worklist's own ranking: the 13 identity-gated rows carry the
highest drift weight (3.0), and the brief flags them as the fastest-drifting field
in the corpus post-SFFA.

---

## F-001 — `status` means *exists*, not *open for applications*

Nine of the thirteen pages showed only past deadlines or an explicit "closed"
label, because most of these programmes run one cycle a year and were fetched
between cycles. Reading those as `paused` would have marked half the corpus
suspended on no evidence at all.

The definition adopted, and now written into `docs/SCHEMA.md`:

| value | means | test |
|---|---|---|
| `active` | the programme exists | the funder presents it as a current offering and posts no termination notice — a closed cycle is not evidence of anything |
| `paused` | the funder states it is suspended | an explicit hold with no next cycle, e.g. "waiting for a new publication" |
| `terminated` | the funder states it has ended | an explicit wind-down, sunset or elimination |
| `unknown` | not assessed, or evidence does not settle it | the default; a dead link lands here, never in `terminated` |

Whether a programme is *currently accepting applications* is a different question
and `application_cadence` already answers it.

## F-002 — One programme is genuinely paused: NSF SPRF

> "Program 23-500 is currently waiting for a new publication." · "No upcoming due
> dates." · Status header: "Waiting for new publication."

The only non-`active` status among the thirteen, and exactly the state the old
schema could not express. NSF PRFB, checked the same day, is explicitly marked
"Active funding opportunity — This document is the current version" with a
deadline of 2026-09-29, so this is a programme-level hold, not an NSF-wide one.

## F-003 — A hard identity gate in the corpus is wrong, and it is one of only two

`M. Hildred Blewett Fellowship` is coded `identity_gate_type = restricted_to`,
`identity_targeting = women`. The APS page says:

> "the fellowship is designed for assisting women, but is **open to any physicist**
> making a transition back into a professional career."

The eligibility list names citizenship, a completed PhD and institutional proof —
not gender. This is a direct contradiction of the coding, not an ambiguity, so it
is corrected to `prioritizes` in this session. It matters more than one row: the
corpus contained only two `restricted_to` rows, and this was one of them. A wrong
hard gate tells an eligible person not to apply.

The other, `AAUW Career Development Grants`, is **confirmed correct**:

> "Applicants must identify as a woman."

## F-004 — Four rows' URM coding may be stale, and is NOT changed here

On these pages the identity language is now general-audience, with no
race/ethnicity criterion in the eligibility section:

| Row | Current page wording |
|---|---|
| HHMI Hanna H. Gray Fellows | "HHMI seeks a broad applicant pool. We encourage applications from individuals of all backgrounds..." |
| HHMI Gilliam Fellowships | same wording |
| HHMI Freeman Hrabowski Scholars | same wording |
| NSF PRFB | no demographic language in the eligibility section |

All four are coded `identity_targeting = underrepresented_minorities`,
`identity_gate_type = prioritizes`.

**Not changed.** Absence of language on one page is weaker evidence than the
direct contradiction in F-003 — the programme's intent may live in a separate
eligibility or FAQ page, and Gilliam in particular is built around
adviser–student pairs at institutions serving those students. Recorded as an open
item; resolving it needs the full application guidance, not the landing page.

Two rows point the other way and also stay unchanged: `ACM SIGHPC` reads
*"Specifically targeted at women or students from racial/ethnic backgrounds that
have not traditionally participated in the computing field"*, which is stronger
than the `prioritizes` it carries, and `BWF PDEP` still states it supports
*"underrepresented postdoctoral fellows"*, confirming its coding.

## F-005 — Three anchors were missing; all three are informative

The brief's own §6 anchor list named Hertz, Ford and NYSTEM, and v0.1 logged none
of them. The reason differs per row, and only one is a plain omission:

- **Hertz Fellowship — active, and simply missing.** "2027 Hertz Fellowship
  Application Now Open" (posted 2026-08-31); up to $250,000 over up to five years;
  first- or second-year PhD students; US citizens or permanent residents. Added.
- **Ford Foundation Fellowship Program — terminated.** The foundation's own
  words: *"we would wind down the Ford Fellowships program by 2028, and we began
  working with the National Academies to put a sunset plan in place"*; last new
  fellowships awarded 2024. Added as `terminated`, `valid_to = 2024-12-31`.
- **NYSTEM — terminated.** Eliminated in the New York State budget approved in
  2021; new funding halted and the programme scheduled to end in 2025 as existing
  contracts expired. Added as `terminated`, `valid_to = 2025-12-31`.

This is the point of the durability layer. Under the old schema the only way to
represent Ford and NYSTEM was to leave them out, which reads identically to never
having researched them.

**Provenance note:** NYSTEM is the one row here sourced to a secondary outlet
(Science/AAAS) rather than the funder, because the programme's own site no longer
exists. That is the honest exception, and it is flagged rather than dressed up as
a funder-page citation.

---

## What this leaves open

- 177 rows remain `status = unknown`, 91 of them in the volatile federal /
  defense / mission categories. The worklist ranks them.
- F-004's four rows need the full application guidance read, not the landing page.
- `review_criteria_checked` is blank on the three added rows: that field was not
  verified for them, and blank honestly says "never checked" rather than
  inheriting a date the work did not earn.
