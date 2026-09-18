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

**D-008 — Schema 0.3.0: the durability layer.** (2026-09-17)
Nine columns added: `status`, `status_valid_to`, `status_evidence`,
`status_source`, `status_checked`, plus `award_checked`, `eligibility_checked`,
`identity_checked`, `review_criteria_checked`. The four field-level dates inherit
`checked_date` (the v0.1 run did verify those fields then); `status` starts
`unknown` on every row, because that question was never asked. Approver: Stone.
*Rules out* reading a blank `status` as "fine" — unknown is now explicit and
counted in the build output.

**D-009 — `status` records existence, not whether applications are open.** (2026-09-17)
`active` = the funder presents the programme as a current offering; `paused` =
the funder states it is suspended with no next cycle; `terminated` = the funder
states it has ended; `unknown` = not assessed or evidence inconclusive. A closed
application cycle is not evidence of anything — nine of the first thirteen rows
checked showed only past deadlines simply because they run annually. Whether a
programme is open right now is `application_cadence`'s job. *Rules out* marking
a programme paused because its page was fetched between cycles, and *rules out*
inferring `terminated` from a dead link: an absent page is not evidence.

**D-010 — Every status claim is sourced, enforced at build.** (2026-09-17)
A non-`unknown` status requires `status_evidence`, `status_source` and
`status_checked`, and `scripts/apply_status.py` refuses to write one without
them. Backfills are driven by a JSON file under `research/<session>/verify/`
that carries the justifying quote next to the change, so the vault diff and its
evidence are reviewed together. *Rules out* hand-editing a status into the CSV.

**D-011 — Correction: Blewett Fellowship is not identity-restricted.** (2026-09-17)
`M. Hildred Blewett Fellowship` moved from `identity_gate_type = restricted_to`
to `prioritizes`. APS states the fellowship "is designed for assisting women, but
is open to any physicist making a transition back into a professional career",
and its eligibility list names citizenship, a completed PhD and institutional
proof — not gender. This was one of only two `restricted_to` rows in the corpus;
the other (AAUW, "Applicants must identify as a woman") was re-verified and is
correct. *Rules out* carrying forward the v0.1 coding for this row. Four further
rows whose URM language has thinned were **not** changed — absence of language on
a landing page is weaker evidence than a direct contradiction (see
`research/2026-09-17-status-backfill/FINDINGS.md` F-004).

**D-012 — `status` does not apply to guidance rows.** (2026-09-18)
The 16 `coverage_type = guidance` rows describe a class of funding (startup
packages, bridge funding, sponsored research agreements, core-facility vouchers),
not a named programme with a funder page. "Has it been terminated?" is a category
error there, so they stay `unknown` and the build counts them separately
(`guidance_no_status_count`) instead of holding the re-check debt permanently
above zero. *Rules out* fabricating a status for a practice, and *rules out*
reading a non-zero unknown count as unfinished work when those rows are the cause.

**D-013 — A stale `source_url` is corrected in place, with the old one named.** (2026-09-18)
Nine rows had `source_url` repointed during the P1 backfill because the cited
document could no longer establish anything: archived NSF solicitations, a
ROSES-2022 call, an expired NIH notice, a 404, a two-cycle-old state guide, a
renamed programme. Each carries a `SOURCE REPOINTED` note naming what it used to
cite and why. Where a stable programme page exists it is preferred over a
cycle-specific PDF, so the row does not go stale every year. *Rules out* silently
swapping a citation, and *rules out* keeping a dead link because "it was the
original source".

**D-014 — A fetch failure is a tooling fact, not a finding.** (2026-09-18)
Roughly a third of sources refuse a plain text fetch (403, 404, 418, or an empty
client-rendered body) while being readable in a rendering browser. Three refuse
everything; those rows record that they were read through a search index, which
is weaker evidence, and say so in their notes. *Rules out* letting HTTP status
influence programme status in any way (see D-009), and *requires* that the method
used be recorded when it was not a direct read of the funder's page.

**D-015 — Schema 0.4.0: what a submission consists of.** (2026-09-18)
Adds `submission_requirements`, `resubmission_allowed`
(`yes`/`no`/`limited`/`unspecified`), `resubmission_policy` and
`submission_checked`. Prompted by `docs/SCOPE.md`, which measured the gap against
the project's actual goal: one row in 219 mentioned page limits and one mentioned
resubmission, because no column existed to hold either. `resubmission_allowed`
starts at `unspecified` everywhere for the same reason `status` started at
`unknown` — nobody had asked, and `no` is a claim about the funder. Build-enforced:
a non-`unspecified` value requires a `submission_checked` date. *Rules out*
inferring a resubmission policy from silence.

**D-016 — Source PDFs are kept on disk and not committed.** (2026-09-18)
Funder documents that no automated client can reach live in `research/sources/`
with their provenance in `SOURCES.md`, and the binaries are gitignored. The repo
should not carry redistributable copies of other organisations' publications, and
the *facts* belong in the vault with the document named in `notes` anyway. They
are not put in `data/`, which invariant 1 reserves for the vault. *Rules out*
treating a hand-saved PDF as a committed artifact, and *rules out* citing one
without naming it in the row.
