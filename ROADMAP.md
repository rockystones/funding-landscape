# Roadmap

Phases carry exit criteria and a failure mode. Nothing advances until the gate
passes. `python scripts/build.py --check` must pass at every phase commit.

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

**Done 2026-09-18 (step 1, two waves, 21 rows):** social_sciences 15 → 31,
humanities 4 → 14, arts 1 → 5. Funders added: Spencer (4 rows), W.T. Grant (3),
Russell Sage (4), Guggenheim, ACLS (5, with Mellon and Luce as co-funders), Getty
(2, both paused for 2027-28), NEH (2 more).
**Remaining in step 1:** arts is still below the floor of 10 — NEA's other lines,
Creative Capital, United States Artists, Doris Duke. ACLS publishes 19
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

## P5 — Live layer

`live_opportunities_us.csv` per brief §8, keyed to durable rows, separate file,
re-pulled on demand and never merged.

---

## P6 — Country swap

Canada first (brief §10 template; tri-agency + CRC + CFI + provincial). EU after,
supranational pass first (ERC / MSCA / EIC), then a scoped national pass.

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
- **Post-SFFA identity coding** is current as of 2026-07-18 only, except the 13
  identity-gated rows re-verified 2026-09-17. Re-verify before any use that
  depends on it, and see F-004 for four rows whose coding is under question.
- **`source_url` rot is unmeasured.** Eleven rows checked in wave 2 turned up one
  archived solicitation (NSF MRI) and one stale redirect (lrp.nih.gov). This is a
  separate failure mode from termination and nothing detects it. Candidate build
  check: fetch every `source_url`, flag archive labels, redirects and 404s —
  without ever letting a fetch failure imply a status.
