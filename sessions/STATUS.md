# Status

**Last session:** 2026-09-17 — P0 scaffold + baseline audit, then P1 durability layer.
**Phase:** P1 ◐ schema done, backfill started. **Next:** P1 step 3, the bulk backfill.

## Where things stand

- Repo initialised from the four delivered files; house P0 layout adopted (D-002).
  Commit authorship is the `noreply` identity; `backup/pre-rewrite` holds the old
  chain locally and must never be pushed.
- **Schema 0.3.0** (D-008): `status`, `status_valid_to`, `status_evidence`,
  `status_source`, `status_checked`, plus per-field `award_/eligibility_/identity_/
  review_criteria_checked`. Migration is idempotent (`scripts/migrate_0_3_0.py`).
- **Build gates a status claim** (D-010): non-`unknown` status requires evidence,
  source and date; `scripts/apply_status.py` refuses to write one without them.
  `--check` is green: **0 errors, 0 warnings on 193 rows**.
- **Backfill wave 1 done:** 13 identity-gated rows verified against funder pages,
  3 rows added. Status now active=13, paused=1, terminated=2, **unknown=177**.
- Findings in `research/2026-09-17-status-backfill/FINDINGS.md` — five, the
  sharpest being F-003 (a wrong hard identity gate, corrected) and F-004 (four
  rows whose URM coding looks stale, deliberately **not** changed).
- Explorer republished with the durability layer visible:
  https://claude.ai/artifact/Qq9sngHh7tdhQUnERzMMvD

## Gated on the user

- Nothing is blocked.
- **F-004 wants a decision**: four rows (HHMI Hanna Gray / Gilliam / Freeman
  Hrabowski, NSF PRFB) are coded `underrepresented_minorities` + `prioritizes`,
  but their current pages carry only general "all backgrounds" language. Resolving
  it needs the full application guidance read, not the landing page.

## Next session opens with

1. `python scripts/build.py --check` (expect 0 errors, 193 rows).
2. P1 step 3: work down `dist/corpus.json` → `worklist.top`, highest score first.
   177 rows are `unknown`, 89 of them federal. Same loop as wave 1: fetch the
   row's `source_url`, apply D-009's existence test, write the result into a new
   `research/<date>-status-backfill/verify/status-updates.json`, apply, rebuild.
