# Source documents

Funder PDFs that could not be reached by an automated client and were saved by
hand from a browser download prompt. They are kept on disk because they are the
only direct source for what they cover, and **gitignored** rather than committed:
one is a third-party society's document, and the repo should not carry
redistributable copies of other people's publications. The *facts* extracted from
them live in `data/mechanisms.csv` with the document named in `notes`.

Read them with `python scripts/pdf_text.py <file>`, or with `pypdf` when the PDF
uses a CID font that the stdlib extractor cannot decode (the ACS one does).

| File | What it is | Why it had to be fetched by hand |
|---|---|---|
| `acs-prf-application-components-fall-2026.pdf` | ACS PRF, "Grant Application Components", Fall 2026 | `acs.org` refuses both a plain fetch and a rendering browser (F-014). This is the corpus's first direct ACS source; the three PRF rows previously rested on the search index. |
| `nifa-afri-project-and-grant-types-faq-2026-01.pdf` | USDA NIFA, "AFRI Project and Grant Types FAQ", January 2026 | Reached via a download prompt during a fetch. Federal guidance, public domain. |
| `Individual NOFO combined_040126.pdf` | NEH, Notice of Funding Opportunity — Awards to Individuals (combined), pub. 2026-03-02, upd. 2026-04-01 | `neh.gov` refuses both a plain fetch and a rendering browser. Covers four NEH programmes at once. |
| `Fellowships 2026 program announcement 040126.pdf` | NEH Fellowships Program Announcement, deadline 2026-04-22 | same |
| `Fellowships.pdf` | NEH Fellowships programme page (print) | same — carries the $60,000 / $5,000-per-month figure and the list of published sample narratives |
| `NEH.AI_.Policy-10.23.24.pdf` | NEH, Policy on the Use of Artificial Intelligence for NEH Grant Proposals | same |
| `AHA_Research_Funding_Application_Instructions_AC.pdf` | AHA 2027 Research Funding Application Instructions (rev. 2026-09-14), 57pp | Covers all five AHA rows at once: ProposalCentral, membership gate, format enforcement, referee rules. |
| `2026-American-Heart-Association-Postdoctoral-Fellowship.pdf` | AHA Postdoctoral Fellowship announcement, 2026 cycle | Carries the full calendar arc and the five-page research-plan limit. |
| `Harry-Shwachman-CF-Clinical-Investigator-Award-Policies-and-Guidelines.pdf` | CFF Harry Shwachman award RFA, December 2025, 18pp | CFF key dates, formatting, resubmission. |
| `Pilot-and-Feasibility-Awards-Policies-and-Guidelines.pdf` | CFF Pilot & Feasibility award RFA, Spring 2026, 15pp | Same, plus the explicit "Letter of Intent: Not applicable to this RFA". |
| `FY27-CCR-LOI-Announcement_FINALv2.pdf` | Komen Career Catalyst Research 2026-2027 LOI announcement, 13pp | The limited-submission cascade: institution opt-in, LOI, then application. A byte-identical duplicate (`FY27-CCR-LOI.pdf`) was deleted. |
| `ALS Association Grants Policy Statement_April 2026.pdf` | ALS Association Grants Policy Statement, April 2026, 26pp | POST-AWARD administration only (carryover, rebudgeting, PI change) — no application-stage content. Recorded so nobody mines it again expecting one. |
| `FFSB-Policies.pdf` | Policies of the J. William Fulbright Foreign Scholarship Board, 201pp | Not yet mined; governs the two Fulbright rows. |
| `opportunity-*-attachments.zip` (10) | Grants.gov attachment bundles for NIH NOFOs | **Nine are meta-refresh stubs, not documents** — they redirect to `grants.nih.gov/grants/guide/pa-files/<NOFO>.html`, which turns out to be directly fetchable, so these are not needed. Only `PA-27-037` carries a real 182KB announcement. |

## What they gave the corpus

**ACS PRF** — the first submission-requirements and resubmission content in the
corpus (P8). Technical-proposal format and the 4,000-word narrative limit, five
word-limited statements, the minimum-six-suggested-reviewers rule with its
48-month conflict window, four budget caps, and the resubmission policy: an
initial application plus **at most two resubmissions on the same topic**, each
requiring a statement of modifications, with prior reviewers barred from being
suggested again. Also the per-grant-type differences (DNI/UNI need complete
publication lists, ND/UR five years; teaching section for UR/UNI only; Co-PI for
ND/UR only; postdoc salary support for ND/DNI only).

**NIFA AFRI** — the predoctoral advancement-to-candidacy documentation
requirement and the two-sided postdoctoral degree-date window, both keyed to the
live NOFO. Plus the FASE set-aside: **3.75% of annual AFRI grant funds** go to
pre- and post-doctoral fellowships, which is a real denominator for a row whose
`selectivity` is otherwise unspecified.

It also named AFRI grant types the corpus does not carry — New Investigator
(Standard and Seed) and the Strengthening family (Seed, Sabbatical, Equipment,
Standard, CAP, Workshop). Logged as P2 step 2 candidates.


## Method note, 2026-09-18 — what does NOT need fetching by hand

Two routes were found to be open, which removes most of the reason to download
anything manually:

- **`grants.nih.gov/grants/guide/pa-files/<NOFO>.html`** returns the complete NIH
  announcement to a plain fetch. Tested on PA-24-194 (K99/R00): resubmission rule,
  standard due dates, required mentor and reference letters, and the
  applicant-organisation-versus-PD/PI structure all came back in one request. The
  nine stub ZIPs above exist only because Grants.gov wraps that same URL in a
  redirect.
- **`simpler.grants.gov`** serves both single opportunities
  (`/opportunity/<uuid>`) and **search** (`/search?query=…`) with results in the
  HTML, giving NOFO number, agency, post/close/archive dates and the eligible-
  applicant list. This is the route to the calendar layer for every federal row.

What still needs a human: `neh.gov`, `acs.org`, and anything behind a login or a
cookie wall a rendering browser cannot clear.
