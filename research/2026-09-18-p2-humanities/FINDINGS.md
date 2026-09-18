# P2 wave 1–2 — the humanities and social-science gap

**Session:** 2026-09-18 · **Phase:** P2 step 1 · **Rows added:** 21
**Target:** `ASSESSMENT.md` §3.4, which found the corpus contradicting the brief's
own "all research domains" scope — humanities 4 rows, arts 1, social sciences 15.

## Result

| Domain | Before | After |
|---|---:|---:|
| social_sciences | 15 | **31** |
| humanities | 4 | **14** |
| arts | 1 | **5** |

214 rows, 105 funders. Funders added: Spencer Foundation, William T. Grant
Foundation, Russell Sage Foundation, Guggenheim, ACLS (with Mellon and Luce as
co-funders), Getty Research Institute, plus two more NEH programmes.

**The roadmap's exit criterion — no domain below 10 rows — is met for humanities
and social sciences but not for arts (5).** Named as unfinished rather than
rounded up.

## P2-001 — The gap was real and the funders were where the assessment said

Every name the assessment listed as absent turned out to run several standing
programmes, not one. Spencer alone yielded four rows (Large, Small,
Research-Practice Partnerships, NAEd/Spencer Dissertation), W.T. Grant three,
Russell Sage four, ACLS five — and ACLS publishes **19** competitions, so its
catalogue is nowhere near exhausted.

This is the same "broad but shallow" pattern §3.5 found in the biomedical half.
The difference is that here the funders were missing entirely, so the shallowness
compounded: a humanities scholar filtering the v0.1 sheet saw four rows.

## P2-002 — A fourth and fifth pause: the Getty Center is closing

The Getty Research Institute's own page carries two labels at once:

> Status: **Active** · 1985 – present

and, further down:

> **Applicants for 2027-2028 (Paused)** — linked to the "temporary closure of the
> Getty Center from March 15, 2027 through spring 2028".

Both Getty rows (pre/postdoctoral fellowships and the senior Scholars Program)
are coded `paused`, following the **applicant-facing** label rather than the
project-level one, because the applicant-facing label is what someone acts on. A
2026–27 cohort is in residence, so this is a suspended cycle with a stated
horizon, not a wind-down.

That brings the corpus to five paused programmes. Two of the five are in the arts
and humanities — a category that had one row yesterday.

## P2-003 — Deadlines are published; amounts often are not

Eleven of the 21 new rows carry `typical_award_size = unspecified`. This is not
laziness: ACLS's competition-deadlines page lists 19 competitions with exact
deadlines to the minute and **no figures at all**, and NEH's grants listing does
the same. The funders publish when to apply far more readily than what you get.

Rather than infer amounts from aggregator sites, those rows say `unspecified`,
carry `confidence = medium`, and leave `award_checked` blank so the build's
"never checked" counter surfaces them (it went from 3 to 16). They are a concrete
worklist for a P4 amounts pass.

## P2-004 — neh.gov and acs.org cannot be read at all

Extending F-014: `neh.gov` refuses both a plain fetch and a rendering browser
(HTTP 403), so the two new NEH rows rest on NEH's own grants listing as surfaced
through the search index, with `source_url` pointing at the listing rather than a
programme page. Each says so in its notes. The same applies to `acs.org`.

This is worth stating plainly: **two federal humanities programmes are in this
corpus on weaker evidence than any federal science programme**, purely because of
how their site treats automated clients.

## What this leaves open

- **Arts is still at 5 rows**, below the roadmap's floor of 10. Candidates not yet
  researched: NEA's other grant lines, Creative Capital, United States Artists,
  Doris Duke, Mellon's arts programmes.
- **ACLS has 19 competitions and 5 rows.** The Robert H. N. Ho Family Foundation
  Buddhist Studies suite alone is five more.
- **Mellon Foundation has no rows of its own** — it appears only as a co-funder of
  ACLS programmes. Its direct grantmaking is largely institutional, which may
  make it a `guidance` row rather than an enumerated one; that is a judgement to
  make deliberately.
- **RWJF, Luce (direct), MacArthur, Keck, Kavli, Templeton** remain absent, as
  §3.4 listed them.
- Eleven rows need an amounts pass; eight need an eligibility pass.
