# Working rules

Read order on resume: `sessions/STATUS.md` → `ROADMAP.md` → `ASSESSMENT.md`.

## Invariants

1. **`data/mechanisms.csv` is the only hand-edited layer.** Scripts read it and
   never write it. Everything in `dist/` is derived and disposable.
2. **Derived fields are never stored in the vault.** Award amounts in USD,
   duration in years and staleness are computed at build time, not typed in.
3. **One row = one standing programme.** Dated solicitations belong to the live
   layer (`docs/BRIEF.md` §8), in a separate file, never merged in.
4. **Provenance on every row**: `source_url`, `confidence`, `checked_date`. A row
   without a verifiable source is not a row.
5. **Never fabricate a number.** Unknown selectivity says "unspecified"; an
   estimate is suffixed `(est.)`. A blank cell is a correct answer.
6. **`review_signals_informal` stays blank by default.** Populate only where the
   signal is genuinely well-established, and mark it community knowledge.
7. **Re-verify identity gates before relying on them.** Post-SFFA (2023) this is
   the fastest-drifting field in the dataset.
8. **`python scripts/build.py --check` passes before any commit.**
9. **Every threshold and parser gets a negative control**, and its measured error
   rate is published rather than asserted.
10. **Filters dim, never remove.** A person should see the mechanisms they are
    excluded from, not a silently shortened list.

## Conventions

- Vocabulary changes bump `SCHEMA_VERSION` in `scripts/build.py` and get a
  `DECISIONS.md` entry. Additive only.
- Amounts in USD. Dates ISO `yyyy-mm-dd`. Multi-select cells are `;`-separated.
- The CSV is UTF-8 **without** BOM and holds em dashes and `≥`/`≤`. Excel on
  Windows mis-renders that; see D-005 before "fixing" any encoding.
