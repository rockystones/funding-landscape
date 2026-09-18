# Status

**Last session:** 2026-09-17/18 — P0 scaffold + baseline audit, then P1 complete.
**Phase:** P0 ✅ · P1 ✅ · P2 ◐ step 1 largely done. **Next:** finish P2 step 1 (arts), then catalogue depth.

## Where things stand

- Repo follows the house P0 layout (D-002). Commit authorship is the `noreply`
  identity; `backup/pre-rewrite` holds the old chain locally and is never pushed.
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
- **P2 step 1 started and largely done:** 21 rows added across Spencer, W.T. Grant,
  Russell Sage, Guggenheim, ACLS, Getty and NEH. **214 rows, 105 funders.**
  social_sciences 15 → 31, humanities 4 → 14, arts 1 → 5. Two more pauses found
  (both Getty, suspended for 2027-28 while the Getty Center closes), taking the
  corpus to 5 paused. Findings in `research/2026-09-18-p2-humanities/FINDINGS.md`.
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
2. `ROADMAP.md` P2, remaining in step 1: **arts is still at 5 rows, below the
   floor of 10** (NEA's other lines, Creative Capital, United States Artists,
   Doris Duke). ACLS publishes 19 competitions against 5 rows. Mellon has no
   direct rows — decide deliberately whether its institutional grantmaking is a
   `guidance` row. RWJF, MacArthur, Keck, Kavli, Templeton still absent.
3. Then P2 step 2, catalogue depth for the single-programme funders.
4. A P4 amounts pass has a ready worklist: the build's "never checked" counter
   went 3 → 16, and 11 new rows carry `typical_award_size = unspecified` because
   ACLS and NEH publish deadlines without figures.
