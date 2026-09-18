# Decisions

Append-only. Newest last. Each entry: what was decided, why, and what it rules out.

---

**D-001 — The CSV is the vault; the workbook is a release artifact.** (2026-09-17)
`data/mechanisms.csv` is canonical and hand-edited. The delivered `.xlsx` is a
frozen snapshot of v0.1 kept in `dist/`. *Rules out* editing the workbook and
expecting the change to survive; it will be overwritten or drift silently.

**D-002 — Adopt the house P0 layout, not a bespoke one.** (2026-09-17)
Structure follows the house new-project schema checklist (vault /
scripts / dist / docs / sessions / research). *Rules out* inventing a new
project shape for what is a standard registry corpus.

**D-003 — Record grain is a flat registry, not the v4 timeline kernel.** (2026-09-17)
One row = one standing mechanism. There are no dated events and no typed links,
so the v4 kernel does not apply. The closest house pattern is a sibling measured-data project's
schema-validated registry with provenance on every record. *Rules out* reusing
`corpus.schema.json` / `build.py` from the timeline corpora.

**D-004 — The v0.1 workbook is committed even though it is derived.** (2026-09-17)
It cannot be regenerated in this environment (no `openpyxl`), and it is the
artifact that was actually delivered. Committing it preserves what the user
received. *Rules out* treating `dist/` as wholly disposable.

**D-005 — The CSV stays UTF-8 without BOM; the Excel export gets the BOM.** (2026-09-17)
The vault holds 132 non-ASCII characters (— – ≥ ≤ →). Without a BOM, Excel on
Windows renders these as mojibake, but adding one breaks naive `csv` readers and
diff tooling. The vault therefore stays clean UTF-8 and any Excel-facing export
is written separately with `utf-8-sig`. *Rules out* "fixing" the vault encoding
in response to an Excel display bug.

**D-006 — The numeric award layer is derived and graded, not curated.** (2026-09-17)
`typical_award_size` is free text and stays that way for now. `scripts/build.py`
parses it into annual/total USD envelopes and grades each row `clean`,
`heuristic` or `unparsed`. Measured 14/16 on a holdout sample (seed 4471) before
a further fix; the "and-joined alternatives get summed" class is still open.
*Rules out* presenting any single parsed amount as authoritative, and *requires*
`award_raw` to be visible wherever a derived amount is shown.

**D-007 — Struck from the house P0 checklist.** (2026-09-17)
Following the D-010 right-sizing pattern, these were deliberately not built:
per-claim ULIDs (rows have a natural key), a validation/attestation ledger (no
personal-trust layer), `valid_from`/`valid_to` on individual claims (deferred to
the row-level `status` field in ROADMAP P1), and the gatherer/verifier research
contract (v0.1 already ran one; re-adopt it for P2 coverage work).
