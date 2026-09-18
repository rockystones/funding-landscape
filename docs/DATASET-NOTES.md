# US Research-Funding Landscape — dataset notes

**Deliverable:** `funding_landscape_united_states.xlsx` (delivered in chat) / `.csv` (in this project). One row = one standing funding mechanism, schema per the reusable research brief (Section 4). **190 mechanisms.** `checked_date` = 2026-07-18 on every row.

**Method:** 12 parallel research agents (one per funder category; NIH, NSF, and other-federal split out because federal is the largest), each traversing funder program catalogs; a pipelined adversarial verifier per category re-checked drift-sensitive fields against the funder's own page; deterministic assembly + Section 9 QC; one gap-fill agent added the `reentry` career stage and verified NDSEG prior-funding. ~1.95M subagent tokens; 24 workflow agents, 0 errors.

**Coverage (rows / category):** federal_research 63, private_foundation 21, defense_security 17, professional_society 17, disease_advocacy 16, state_regional 13, international_mobility 12, mission_applied 11, industry 11, institutional 9.

**QC (all Section 9 gates pass):** confidence 132 high / 54 medium / 4 low; all 10 career-stage values present in ≥2 rows across ≥2 categories (reentry: 5 rows / 4 categories); guidance rows institutional 9 + industry 3 (availability-bias categories, brief principle 4); dedup key (funder, program_name), 0 duplicates; 0 structural defects (topic/identity/cadence/provenance); no dated deadlines in `application_cadence`.

**Caveats:**
- Identity coding is post-SFFA (2023), current as of 2026-07-18. All underrepresented-minority-linked programs (HHMI Gilliam / Hanna Gray / Freeman Hrabowski, BWF PDEP, AACR diversity award, NSF PRFB/SPRF) are coded `identity_gate_type = prioritizes` (commitment/holistic), not `restricted_to`. Only 2 hard `restricted_to` rows remain, both sex-based (APS Blewett, AAUW), which SFFA did not reach. Re-verify before relying.
- `review_criteria_official` reflects NIH's simplified three-factor framework (due dates on/after 2025-01-25), NSF two-criterion, ERC excellence-only.
- Amounts and selectivity drift; `(est.)` marks estimates, "unspecified" where undocumented.
- Live dated-solicitation layer (brief Section 8) intentionally excluded from this durable dataset.

**Deferred:** companion guide (`funding_landscape_united_states_guide.md`) with filter instructions, one paragraph per funder category, the availability-bias caveat, and 5–7 worked "if you are an X, look at Y" personas. Not yet produced (user deferred it to after reviewing the data).