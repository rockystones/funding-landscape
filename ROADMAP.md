# Roadmap

Phases carry exit criteria and a failure mode. Nothing advances until the gate
passes. `python scripts/build.py --check` must pass at every phase commit.

> **Scope note, 2026-09-18.** The project's goal has three parts: (1) what funding
> exists and am I eligible, (2) how do I apply, (3) how do I make the application
> better. **The research brief only ever scoped part 1.** P0–P4 below all serve
> part 1. Parts 2 and 3 are addressed by P7–P10, which are new and largely
> unresearched. `docs/SCOPE.md` maps what is covered to what is not, with counts.

---

## P0 — Repo and baseline  ✅ complete 2026-09-17

Vault, build script, gates, docs, first visualization.

**Exit:** `--check` green on all 190 rows · derived numeric layer graded and its
error rate measured · assessment written.
**Result:** 0 errors, 0 warnings. Award parse 121 clean / 18 heuristic / 51
unparsed; holdout accuracy 14/16.

---

## P1 — Durability layer  ✅ complete 2026-09-18

The dataset cannot currently say a programme has ended, and 48% of it is federal.

1. Add `status` (`active` | `paused` | `terminated` | `unknown`), `valid_to`,
   `status_checked`. Bump `SCHEMA_VERSION`; log in `DECISIONS.md`.
2. Move provenance from row-level to field-level for the four drift-sensitive
   fields: `typical_award_size`, `eligibility_window`, `identity_targeting`,
   `review_criteria_official`. Each gets its own `_checked` date.
3. Backfill `status` for the 91 federal / defense / mission rows.
4. Re-admit the informative absences (Ford, NYSTEM) as `terminated` rows rather
   than silent omissions.

**Exit:** every federal row carries a `status` with a source · no row's
drift-sensitive field is older than 90 days without being flagged · build emits
a staleness worklist.
**Failure mode:** `status` becomes a guess. A `terminated` claim needs a source
the same way an amount does — an absent web page is not evidence of termination.

**Result:** all four steps done across fourteen verification waves.
**Every one of the 177 enumerated rows carries a sourced status** — 172 active,
3 paused, 2 terminated — and the 16 guidance rows are exempt by D-012. Three
genuine pauses found (NSF SPRF, NIST/NRC associateships, Microsoft Research
Fellowship, the last suspended since 2023); Ford and NYSTEM re-admitted as
terminated; Hertz added. Eleven rows cited documents that could no longer
establish anything and nine had `source_url` repointed — none of them turned out
to be a dead programme.

**Exit criteria met:** every federal row has a sourced status · no drift-sensitive
field older than 90 days · the build emits a ranked worklist · no status written
without evidence (gate-enforced, plus a negative control on the ambiguity guard).

**Carried forward** (see `research/2026-09-17-status-backfill/FINDINGS.md`): the
PECASE row's `source_url` is still a 2012 news release, two recorded renames are
unapplied because they change the dedup key, and Fulbright-Hays DDRA rests on the
weakest evidence in the corpus.

---

## P2 — Coverage  ◐ in progress (step 1 largely done)

1. **Humanities / arts / social sciences.** Mellon, ACLS, Guggenheim, NEH
   divisions, Russell Sage, Spencer, W.T. Grant, RWJF, Luce, Getty. Target ~25–35
   rows.
2. **Catalogue depth.** Re-run the brief §2.2 traversal for the 63 funders with
   exactly one logged programme. Target 60–120 rows.
3. Record a per-funder programme count so breadth is auditable, not asserted.

**Exit:** no domain below 10 rows · single-row funders under 30 · per-funder
counts published.
**Failure mode:** breadth-padding. Low-confidence stubs with no verifiable source
are not rows; watch the confidence distribution, not the row count.

**Done 2026-09-18 (step 1, three waves, 26 rows): the domain floor is met.**
social_sciences 15 → 31, humanities 4 → **16**, arts 1 → **10**. 219 rows, 108
funders, confidence 140 high / 74 medium / 5 low. Funders added: Spencer (4 rows),
W.T. Grant (3), Russell Sage (4), Guggenheim, ACLS (5, with Mellon and Luce as
co-funders), Getty (2, both paused for 2027-28), NEH (2 more), Creative Capital
(2), United States Artists, NEA Creative Writing, NYFA/NYSCA.
**Remaining in step 1:** arts sits exactly at the floor — Doris Duke, Mellon's
arts programmes, regional arts organisations beyond NYFA. ACLS publishes 19
competitions against 5 rows. Mellon has no direct rows (its grantmaking is largely
institutional, so decide deliberately whether it is `guidance`). RWJF, Luce direct,
MacArthur, Keck, Kavli and Templeton remain absent.

---

## P3 — Usability

1. The companion guide deferred from v0.1 (brief §9 artifact 2): filter
   instructions, one paragraph per category, availability-bias caveat, 5–7 worked
   personas.
2. Structure `years_since_degree_max` — separate "no time gate" from "not
   captured" — and split `prior_funding_exclusion` into a boolean plus
   disqualifying/preserved sets.
3. Excel-facing `utf-8-sig` export (D-005).

**Exit:** `years_since_degree_max` unambiguous on every row · guide published ·
Excel export opens clean on Windows.

---

## P4 — Curated numerics

Replace the heuristic award parse with curated `award_annual_usd` /
`award_total_usd` columns for the rows that have a stated figure; keep the parser
as a cross-check that flags disagreement.

**Exit:** curated columns on all `clean` and `heuristic` rows · parser
disagreement reported each build · a fresh holdout audit with a recorded seed.
**Failure mode:** curating a number the funder never published. `unspecified`
stays `unspecified`.

---

## P5 — Live layer  → superseded by P9

Folded into **P9**, which states the same thing plus the review arc and notes
that 81 rows already carry a real date in `status_evidence` to seed it from.

---

## P6 — Country swap

Canada first (brief §10 template; tri-agency + CRC + CFI + provincial). EU after,
supranational pass first (ERC / MSCA / EIC), then a scoped national pass.

---

## P7 — Eligibility you can compute  ← highest value per unit of work

The corpus already records prior-funding conflicts well, but as prose, so the
question people actually ask cannot be answered mechanically.

1. **Structure the conflicts.** Add `excludes_awards` and `preserves_eligibility`
   as delimited lists. The content mostly exists: 15 rows already spell out the
   R01/K interaction including carve-outs, and the ESI-preservation rule is
   recorded as an enhancement rather than an exclusion.
2. **Close Hole A.** 16 rows state a time-since-degree limit in
   `eligibility_window` prose that never reached `years_since_degree_max`. Parse
   them, and add an explicit `no_time_gate` marker so blank stops meaning both
   "no gate" and "not captured".
3. Extend the conflict fields beyond NIH: 60 rows still say `unspecified`.

**Exit:** given a person's held awards, the build can list what they are locked
out of and what preserves their eligibility · no row's time gate lives only in
prose.
**Failure mode:** inventing an exclusion. `unspecified` means the funder did not
say, and must not become `no`.

---

## P8 — Submission requirements and resubmission

Neither exists in the schema today; one row in 219 mentions page limits and one
mentions resubmission.

1. Fields for what you must produce: page limits, required documents, biosketch
   or equivalent, LOI/pre-proposal stage (13 rows mention it, none structure it).
2. Fields for resubmission: `resubmission_allowed`, `resubmission_policy`,
   `resubmission_limit`. NIH's A1 single-resubmission rule is the anchor case.
3. Research pass per major funder, starting with NIH, NSF and the foundations
   that already have the most rows.

**Exit:** every `confidence = high` row states its submission route *and* what a
submission consists of · resubmission answered for all NIH and NSF rows.
**Failure mode:** these are the fastest-drifting facts in the whole corpus after
amounts. Stamp them with their own `*_checked` dates or do not record them.

---

## P9 — The calendar layer (the brief's §8, finally)

Build `live_opportunities_us.csv` per brief §8: separate file, disposable,
re-pulled on demand, keyed to durable rows, never merged.

**Seed it from what already exists:** 81 of 219 rows carry a real calendar date
inside `status_evidence`, captured as a by-product of the P1 backfill. Roughly
40% of the hardest field is already in the vault as unstructured text.

Add the review arc, which nothing currently records: submission → study section /
panel → council → award, with the typical lag per funder (NIH is roughly nine
months end to end; NSF targets six).

**Exit:** a person can see, for any row, when to submit and when money would
plausibly arrive · the live file never contaminates the durable one.
**Failure mode:** dates rot fastest of anything here. If the live file cannot be
re-pulled cheaply, it should not exist.

---

## P10 — The application guide (question 3)

**Not a corpus problem.** Grant-writing craft, tailoring to a mechanism, worked
examples and format rules do not belong in a spreadsheet. This is the companion
document P3 already scoped, grown up: its spine is `review_criteria_official`,
which is populated on 191/219 rows and is the corpus's real contribution to the
question — what each funder says it is actually judging.

Decide the artifact before researching it. Do not start by adding columns.

---

## Open items — do not silently resolve

- **`biomedical_health` vs `life_sciences` overlap.** Only 6 rows are sole
  `life_sciences`. Either merge the labels or write the boundary rule — do not
  keep coding rows into both by reflex.
- **The "and-joined alternatives" parser class.** "$27,000/yr (undergraduate) and
  $37,000/yr (graduate)" sums instead of ranging when a `+` appears elsewhere in
  the string. Known-wrong; superseded by P4 rather than patched.
- **Guidance rows are not comparable to enumerated ones.** 19 rows describe
  typical ranges rather than a specific programme. Any aggregate that mixes them
  with enumerated rows is measuring two different things.
- **`prior_funding_exclusion` says `unspecified` on 60 rows and `no` on 22.**
  Those are different claims and only one of them is checkable. Do not let a P7
  backfill flatten them.
- **Post-SFFA identity coding** is current as of 2026-07-18 only, except the 13
  identity-gated rows re-verified 2026-09-17. Re-verify before any use that
  depends on it, and see F-004 for four rows whose coding is under question.
- **`source_url` rot is unmeasured.** Eleven rows checked in wave 2 turned up one
  archived solicitation (NSF MRI) and one stale redirect (lrp.nih.gov). This is a
  separate failure mode from termination and nothing detects it. Candidate build
  check: fetch every `source_url`, flag archive labels, redirects and 404s —
  without ever letting a fetch failure imply a status.
