# Status

**Last session:** 2026-09-17/18 — P0 scaffold + baseline audit, then P1 complete.
**Phase:** P0 ✅ · P1 ✅ · P2 ◐ step 1 done (domain floor met). **Next:** P2 step 2, catalogue depth.

## Where things stand

- **PUBLISHED 2026-09-18** to `github.com/rockystones/funding-landscape` (PUBLIC),
  branch `main`, head `03c2cf6`, 15 commits. Apache-2.0 carried forward from the
  repo's initial commit byte-identically (blob `261eeb9`). The placeholder commit
  `adf2ecc` was replaced with `--force-with-lease=main:adf2ecc5…`.
  **Two local-only tags must never be pushed** — `backup/pre-rewrite` (pre-noreply
  chain) and `pre-neutralize-backup` (pre-redaction chain). Neither is reachable
  from `main`; the remote carries 0 tags.
- Repo follows the house P0 layout (D-002). Commit authorship is the `noreply`
  identity throughout.
- **Schema 0.3.0** (D-008): `status`, `status_valid_to`, `status_evidence`,
  `status_source`, `status_checked` plus per-field `*_checked` dates.
- **`--check` is green: 0 errors, 0 warnings on 193 rows.**
- **P1 backfill complete.** All 177 enumerated rows carry a sourced status:
  **172 active, 3 paused, 2 terminated.** The 16 guidance rows are exempt (D-012).
  Fourteen verification waves, every claim carrying the quote that justifies it in
  `research/2026-09-17-status-backfill/verify/status-updates-wave*.json`.
- Sixteen findings in that session's `FINDINGS.md`. The headline ones: source rot
  was the real problem rather than programmes ending (11 rows, all live, 9
  repointed); NSF skipped the entire FY2026 MRI competition; three genuine pauses;
  two silent renames; 15 of 15 spot-checked amounts matched the vault.
- **P2 step 1 done — the domain floor is met.** 26 rows added across Spencer,
  W.T. Grant, Russell Sage, Guggenheim, ACLS, Getty, NEH, Creative Capital, United
  States Artists, NEA Creative Writing and NYFA/NYSCA. **219 rows, 108 funders**,
  confidence 140 high / 74 medium / 5 low.
  **social_sciences 15 → 31, humanities 4 → 16, arts 1 → 10.** Two more pauses
  found (both Getty, suspended for 2027-28 while the Getty Center closes), taking
  the corpus to 5 paused. Findings in
  `research/2026-09-18-p2-humanities/FINDINGS.md`.
- Explorer published: https://claude.ai/artifact/Qq9sngHh7tdhQUnERzMMvD

## Tooling added this session

| Script | What it does |
|---|---|
| `scripts/build.py` | validate → derive → emit `dist/corpus.json` + worklist |
| `scripts/migrate_0_3_0.py` | idempotent schema migration |
| `scripts/apply_status.py` | applies an evidence-carrying updates file; refuses unsourced or ambiguous writes |
| `scripts/next_batch.py` | stateless: prints the next slice of unverified rows |
| `scripts/pdf_text.py` | stdlib PDF text extraction, for the rows that cite PDFs |
| `scripts/make_viz.py` | inlines the payload into the explorer |

## Pre-push review (2026-09-18)

Every blob reachable from `main` (88) plus all commit metadata and messages were
scanned. Clean on: personal email, real name, hostname, Windows/user paths,
session directories, credentials, IP addresses. One finding, fixed before the
push: **28 references to non-public sibling projects** (`loom/docs/knowledge-schema/
NEW-PROJECT-P0.md` and `echemlab`) across all 14 commits in `DECISIONS.md` and
`docs/SCHEMA.md`. Because they were in multiple blob versions, HEAD-only editing
would have left them in public history, so history was rewritten with
`filter-branch` to describe those things generically instead. `ai-good-practice`
was deliberately retained — it is a public repo, so the reference is a citation a
reader can follow. The delivered `.xlsx` was checked separately: its embedded
`docProps` carry `creator: openpyxl` and an empty `lastModifiedBy`, no personal data.

## Gated on the user

- Nothing is blocked.
- **Two editorial calls wait on a decision**, both recorded rather than made:
  1. F-004 — four rows (HHMI Hanna Gray / Gilliam / Freeman Hrabowski, NSF PRFB)
     are coded `underrepresented_minorities` + `prioritizes`, but their pages now
     carry only general "all backgrounds" language.
  2. F-013 — two programmes have been renamed (AARF → AARFA; APS FPD → Doc Brown
     Future of Physics Days). Renaming a row changes the dedup key.

## Next session opens with

1. `python scripts/build.py --check` (expect 0 errors, 193 rows).
2. `ROADMAP.md` P2 step 2: catalogue depth for the single-programme funders.
   ACLS alone publishes 19 competitions against 5 rows. Mellon still has no direct
   rows — decide deliberately whether its institutional grantmaking is a `guidance`
   row. RWJF, MacArthur, Keck, Kavli and Templeton remain absent.
3. Arts sits at exactly 10, the floor rather than a finish: Doris Duke, Mellon's
   arts programmes and regional arts organisations beyond NYFA are unresearched.
4. A P4 amounts pass has a ready worklist: the build's "never checked" counter
   went 3 → 18, and 11 rows carry `typical_award_size = unspecified` because ACLS
   and NEH publish deadlines without figures.
5. One row is flagged for re-verification or removal: the Creative Capital State
   of the Art Prize, the corpus's weakest (P2-006).
