# US Research-Funding Landscape

A filterable map of standing research-funding mechanisms in the United States.
**One row = one durable funding programme**, not one dated solicitation.

    190 mechanisms · 92 funders · 10 funder categories · snapshot 2026-07-18

The question the dataset exists to answer: *given my career stage, domain,
citizenship and institution, which mechanisms can I actually pursue?*

## Layout

| Path | What it is |
|---|---|
| `data/mechanisms.csv` | **The vault.** The only hand-edited layer. |
| `docs/BRIEF.md` | The reusable, country-agnostic research brief the dataset was built from. |
| `docs/SCHEMA.md` | Schema decisions, vocabularies, and what the schema cannot yet express. |
| `docs/DATASET-NOTES.md` | Method and caveats from the v0.1 research run. |
| `scripts/build.py` | Validate → derive → emit `dist/corpus.json`. |
| `dist/` | Derived artifacts. Never hand-edited. |
| `viz/index.template.html` | Source of the explorer; `scripts/make_viz.py` inlines the payload. |
| `ASSESSMENT.md` | Independent review of v0.1: what holds, what does not. |
| `ROADMAP.md` | Phases with exit criteria. |
| `DECISIONS.md` | Append-only decision log. |

## Build

```bash
python scripts/build.py           # validate, derive, write dist/corpus.json
python scripts/build.py --check   # validate only; non-zero exit on gate failure
python scripts/build.py --viz     # also write the trimmed explorer payload
python scripts/make_viz.py        # inline it -> viz/index.html (self-contained)
```

**Explorer:** https://claude.ai/artifact/Qq9sngHh7tdhQUnERzMMvD

Standard library only — no pandas, no openpyxl.

## Before you trust a number

- Every row is a **snapshot of 2026-07-18**. Amounts, eligibility windows and
  review criteria drift. Re-verify against the funder's own page before relying.
- `typical_award_size` is free text. The numeric layer in `dist/corpus.json` is a
  **parse of that text**, measured at ~88% on a 16-row holdout. Use it for
  distributions; never quote a single programme's amount from it without
  reading `award_raw`.
- `selectivity` is "unspecified" on 81% of rows. That is honest, not missing.
- Two categories (`institutional`, `industry`) are deliberately **guidance rows**,
  not enumerations — see the availability-bias note in `docs/BRIEF.md` §2.4.
