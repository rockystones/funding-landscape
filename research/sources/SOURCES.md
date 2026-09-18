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
