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

# Wave 2 — federal flagships

Eleven of the highest-consequence federal rows. Eight resolved to `active`;
three could not be resolved and stayed `unknown`, which is the point of having
the value.

## F-006 — Five v0.1 award figures checked against the funder, five matched

Not the goal of the wave, but the pages carried amounts, so they were compared:

| Row | Funder's current wording | Vault |
|---|---|---|
| NSF GRFP | "$37,000 stipend and a $16,000 Cost of Education allowance" | matches |
| NIH LRP | "up to $50,000 annually" | matches |
| DOE CSGF | "$45,000 annual stipend ... renewable up to four years" | matches |
| NIH K99/R00 | K99 "may not exceed $125,000"; R00 "may not exceed $249,000 per year" | matches |
| NIH Pioneer (DP1) | "$700,000 in direct costs per year for up to 5 years" | matches |

Five is a small sample and these are the best-documented programmes in the
corpus, so this is not a licence to trust every amount. But it is an independent
check that came back clean, and it says the v0.1 amounts were read carefully
rather than approximated. It says nothing about the *parser* that turns them into
numbers — that error rate is measured separately (D-006).

## F-007 — A row cites an archived solicitation

`Major Research Instrumentation (MRI) Program` has `source_url` pointing at NSF
23-519, which NSF now labels:

> "Archived funding opportunity — This solicitation is archived."

The programme itself looks alive (a 15 Oct – 16 Nov 2026 window is listed), but
the row's evidence is a superseded document. Status stays `unknown` and the row
is flagged: an archived document is not evidence in either direction. The general
lesson is that `source_url` rot is its own failure mode, separate from programme
termination, and nothing in the schema currently detects it. Candidate for a
build check: fetch every `source_url` and flag archive labels and redirects.

## F-008 — Three rows unresolved, and none of them is a termination

| Row | What happened | Resolution |
|---|---|---|
| ARPA-E OPEN | page returned no readable content (client-rendered) | `unknown` |
| NDSEG | DNS failure reaching onr.navy.mil | `unknown` |
| NSF MRI | cited solicitation archived (F-007) | `unknown` |

Each of these would have been silently miscoded as "gone" by a checker that
treats a failed fetch as a signal. They are the reason D-009 forbids it.

Worth noting for the next wave: `lrp.nih.gov` now 301-redirects to
`grants.nih.gov/funding/funding-categories/lrp`. The redirect resolved fine, but
the stored URL is stale and a batch checker should follow and record redirects
rather than treat them as errors.

---

# Waves 3-14 — the rest of the corpus

Fourteen waves, 2026-09-17 to 2026-09-18. **All 177 enumerated rows now carry a
sourced status: 172 active, 3 paused, 2 terminated.** The 16 guidance rows are
handled by policy rather than verification (F-015).

## F-009 — Three programmes are genuinely paused, and they look nothing alike

| Row | The funder's own words | Since |
|---|---|---|
| NSF SPRF | "Program 23-500 is currently waiting for a new publication." | awaiting republication |
| NIST/NRC Postdoctoral Associateships | "we are waiting for more guidance before notifying selected applicants" | no reopening date given |
| Microsoft Research Fellowship | "Microsoft Research has paused our call for proposals/nominations for the 2023 calendar year" | the 2023 cycle |

Microsoft's is the longest-standing: three years, with applicants redirected to
an AI & Society Fellows programme that is not yet a row here. Under the v0.1
schema all three were indistinguishable from thriving programmes.

## F-010 — Source rot was the dominant defect, and it is fixable

Eleven rows cited a document that could no longer establish anything: archived
NSF solicitations (MRI, GOALI), a ROSES-2022 NASA call, an expired NIH notice, a
2012 ONR news release, a 404 at the Florida Department of Health, a 2024-cycle
NJCSCR guide, a 2023 AFOSR PDF, a superseded ed.gov page, and a renamed
Alzheimer's programme.

**Every one was resolvable.** Nine had `source_url` repointed and all eleven now
carry a sourced status. Not one turned out to be a terminated programme — the
rot was in the citation, not the funding.

That is the general lesson of the backfill. The thing this corpus most needed
protection against was not programmes quietly ending; it was **links quietly
going stale while the programme carried on**. A reader following an archived NSF
solicitation would reasonably conclude the programme was dead.

## F-011 — NSF skipped the entire FY2026 MRI competition

The single most consequential fact found. On 1 July 2025 NSF announced it would
not accept Major Research Instrumentation proposals in the scheduled FY2026
window (15 Oct – 14 Nov 2025), returning any submitted **without review**, to
fund more of the FY2025 cohort. The next window is 15 October – 16 November 2026.

The programme is `active` — a skipped cycle with an announced next window — but
anyone planning an instrumentation purchase around MRI needed to know, and no
field in v0.1 could have told them. NSF's own pages label solicitation 23-519
both "Active funding opportunity" and "Status: Archived" depending on the view,
which is why this row needed the announcement rather than a page label.

## F-012 — Absence from a summarised index is not evidence

Two independent reads of NIH's activity-code index reported UG3/UH2/UH3 as
absent, while every other code in the corpus was listed. The direct activity-code
page exists and describes UG3 as current. The index summary was incomplete.

Held at `unknown` for four waves rather than drifting toward `terminated`, which
is exactly what D-009 is for. **A summarised absence must never move a row toward
terminated on its own.**

## F-013 — Two programmes have been renamed under the corpus's feet

- **AARF → "Alzheimer's Association Research Fellowship Program for All (AARFA)".**
  This is why the old page read "This grant is currently closed" with a February
  2025 deadline and no successor. The new programme's terms match the recorded
  amounts, so only the name and URL were stale.
- **APS "Future of Physics Days travel grants" → "Doc Brown Future of Physics
  Days Travel Grants"**, now tied to the APS Global Physics Summit rather than
  the March/April meetings.

Both are recorded; neither `program_name` was changed, because renaming a row
changes the dedup key and is an editorial call.

## F-014 — Half the web refuses a plain text fetch

Roughly a third of sources returned HTTP 403, 404, 418 or an empty body to the
fetch tool while being perfectly readable in a rendering browser: ARPA-E (client
-rendered), basicresearch.defense.gov, transportation.gov, ahrq.gov, sloan.org,
beckman-foundation.org, komen.org, als.org, cff.org (behind a cookie banner),
agu.org, eds.ieee.org, ncbiotech.org, cprit.texas.gov, qualcomm.com.

Three refused everything — acs.org, neh.gov and the old seagrant URL — and those
rows say in their notes that they were read through a search index rather than
fetched, which is weaker evidence and is marked as such.

**Method note for the next jurisdiction:** budget for a rendering browser from
the start, and treat a fetch failure as a tooling fact, never a finding.

## F-015 — "Does it still exist" is not a question guidance rows can answer

16 rows carry `coverage_type = guidance`: they describe a *class* of funding —
faculty startup packages, internal bridge funding, industry sponsored-research
agreements, core-facility vouchers — not a named programme with a funder page.
Asking whether a practice has been terminated is a category error, and leaving
them `unknown` would have kept the re-check debt permanently non-zero.

They are now counted apart in the build (`guidance_no_status_count`) rather than
inflating the debt. See D-012.

## F-016 — Amounts hold up under spot-checking

Across the backfill, 15 award figures were quotable from funder pages and
compared against the vault. **All 15 matched**: NSF GRFP, NIH LRP, DOE CSGF, NIH
K99/R00, NIH Pioneer, Sloan, NCBiotech Flash, ALS Safenowitz, MJFF Safra, CFF
Pilot & Feasibility, IEEE EDS, AARFA, Hertz, ACS PRF DNI and AFOSR YIP.

These are the better-documented programmes, so this is not a uniform sample. But
15/15 is a meaningful independent check on v0.1's amounts, and it is a different
question from whether the *parser* reads them correctly (D-006).

---

## What this leaves open

- **Nothing in the enumerated set.** All 177 enumerated rows carry a sourced
  status. The 16 guidance rows are `unknown` by policy (F-015, D-012).
- **The PECASE row's `source_url` is still a 2012 ONR news release.** Its status
  is sourced elsewhere, but picking a replacement is an editorial call: PECASE is
  conferred across 14 agencies and this row is filed under the DoD stream.
- **Two renames are recorded but not applied** (F-013), because changing
  `program_name` changes the dedup key.
- **Fulbright-Hays DDRA is `active` on the weakest evidence in the corpus** — ED's
  IRIS registry presents it as current, but no competition newer than FY2025 was
  found and the main ed.gov page 404s. First row to re-check.
- **Several rows rest on pages last dated 2023-2025** rather than a live deadline:
  NATO SPS (2023 page), NIJ GRF and W.E.B. Du Bois (2024), DHS COE (2025). Each
  says so in its notes.
- F-004's four rows need the full application guidance read, not the landing page.
- `review_criteria_checked` is blank on the three added rows: that field was not
  verified for them, and blank honestly says "never checked" rather than
  inheriting a date the work did not earn.
