# Status

**Last session:** 2026-09-17 — P0 repo scaffold + baseline audit + first viz.
**Phase:** P0 complete. **Next:** P1 durability layer (see `ROADMAP.md`).

## Where things stand

- Repo initialised from the four delivered files; house P0 layout adopted (D-002).
- `scripts/build.py` implements every brief §9 gate: **0 errors, 0 warnings** on
  all 190 rows. The v0.1 dataset passes independent re-validation.
- Derived numeric layer added (award USD envelopes, duration years, staleness).
  Graded 121 clean / 18 heuristic / 51 unparsed; holdout accuracy 14/16 (seed
  4471) before a final fix. Known-open failure class recorded in ROADMAP.
- `ASSESSMENT.md` written: six substantive findings, prioritised next steps.
- Coverage explorer published as an Artifact: https://claude.ai/artifact/Qq9sngHh7tdhQUnERzMMvD
  Built from `viz/index.template.html` + the trimmed payload, inlined into one
  self-contained file by `scripts/make_viz.py`.

## Gated on the user

- Nothing is blocked. P1 is scoped and ready to start on a go.
- The v0.1 → P1 schema change bumps `SCHEMA_VERSION`; wants a named approver per
  the house version ceremony.

## Next session opens with

1. `python scripts/build.py --check` (expect 0 errors).
2. `ROADMAP.md` P1, step 1: the `status` enum.
