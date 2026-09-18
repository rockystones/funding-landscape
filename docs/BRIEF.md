# Reusable Research Brief: National Research-Funding Landscape

**Purpose of this document.** A country-agnostic pipeline for building a comprehensive, filterable map of research-funding mechanisms across all funder types, domains, and career stages. Run it once per jurisdiction. Only the *Country Parameter Block* changes between runs; everything else (schema, taxonomy, phases, QC) is fixed. First run: **United States**. Swap templates for **Canada** and **EU** are at the end.

---

## 1. Objective and scope

Produce a structured dataset in which **one row = one standing funding mechanism**, plus a navigable companion document, such that a person at any career stage in any research domain can filter to the set of mechanisms they are eligible to pursue.

- **In scope:** standing/recurring mechanisms and mechanism families across every funder category in Section 5.
- **Out of scope (by default):** individual live solicitations with a single expiring deadline. These belong to the optional live layer (Section 8), kept in a separate file.
- **All research domains**, not one. Domain is a field, not a filter on inclusion.

---

## 2. Operating principles (read before starting)

1. **Mechanism level, not solicitation level.** Capture the durable program (e.g., "NIH K99/R00 Pathway to Independence"), not this cycle's NOFO number. Give each distinct standing program its own row: split variants across sub-agencies into separate rows whenever they differ in any filterable field (eligibility, career stage, purpose, award size). Collapse to a single row with variants in `notes` only when they are genuinely identical except for name.
2. **Stopping rule: maximize durable-program count.** Complete coverage of every funder *category* (Section 5) and every *major* funder within each; then, within each funder, log as many distinct standing programs as you can find, not just the flagship families. The floor is the durable/solicitation boundary: descend to named programs, activity codes, and standing award lines, and stop only where the next level down is individual dated calls (those route to the live layer, Section 8). Operationally: for each major funder, traverse its own program index / funding-opportunities catalog and log every standing program listed, rather than stopping at representative examples. For funders with no native catalog (most foundations, societies, industry), use aggregators (e.g., Candid/Foundation Directory, Pivot-RP, agency databases) only to *discover* programs, then verify and source each from the funder's own page. Guard against quality collapse: every logged row must still satisfy the minimum field set in principle 5. A low-confidence stub with no verifiable source is not a row.
3. **Structured output is primary.** The spreadsheet/CSV (Section 7 schema) is the deliverable. The prose companion is secondary and thin.
4. **Availability-bias correction (mandatory).** Two categories are real but poorly represented on the open web: **institutional internal funding** and **bespoke industry funding**. Do not skip them because they are hard to crawl. Populate them as *guidance rows*: typical ranges, how to access, and the enumerable subset (named corporate fellowships; whatever internal mechanisms are publicly documented). Mark these rows `coverage_type = guidance`.
5. **Provenance discipline.** Every row carries a source URL, a confidence flag, and a checked date. Amounts and eligibility windows drift; verify against the funder's own site, not aggregators. If a value is estimated, mark it.
6. **Checkpoint per category.** Write results to the growing dataset after each funder category completes, so intermediate state is inspectable and the run is resumable.
7. **Eligibility gates are structured, not prose.** Populate the gate columns in Section 4 (citizenship, time-since-degree window, identity targeting with its `restricted_to`/`prioritizes` modifier, topic restriction, submission path, prior-funding exclusion, institution-type restriction) as their own fields so the sheet filters to a person's actual eligibility; `eligibility_notes` holds only the residual. For identity restrictions, especially race/ethnicity-based, verify current criteria on the funder's own page and stamp a recent `checked_date`. This is a fast-drifting area in the US after SFFA v. Harvard (2023), and several formerly restricted programs have revised eligibility; do not carry forward historical status. Prior-funding exclusions are a special case: they are rare, concentrate in career-development and early-career mechanisms, and live in the NOFO/solicitation eligibility section rather than on summary pages, so they must be actively searched by opening the actual NOFO, and recorded with both the disqualifying awards and the awards that preserve eligibility (a bare "excluded" boolean is not enough to answer "does my R21 disqualify me").
8. **Capture design intent and review criteria, split by provenance.** Beyond who can apply, record what each mechanism is *for* and how it is *judged*: `stated_purpose`/`design_notes`, `review_criteria_official`/`review_signals_informal`, and the `research_stage` facet. Keep official (funder's own words, sourced) separate from commonly-known (community knowledge, marked, never fabricated), mirroring the sourced/informal distinction used elsewhere. The activity-code or mechanism letter often encodes intent before the purpose text does: at NIH, R = investigator-initiated research project (no substantial agency involvement), U = cooperative agreement (substantial agency involvement), K = career development, F = individual fellowship, T = institutional training; classify U-series as `cooperative_agreement` in `mechanism_type` and explain the involvement in `design_notes` rather than mislabeling it as a translation vehicle. Commercialization/translation lives in SBIR/STTR (R41–R44) and phased milestone-driven awards (UG3/UH3, UH2/UH3), not U01. Keep the vocabulary funder-agnostic: NSF judges on Intellectual Merit and Broader Impacts; ERC on scientific excellence alone with an explicit high-risk/high-gain remit; foundations typically weight mission-fit and PI trajectory. Review frameworks drift: NIH moved to its simplified three-factor framework for due dates on or after January 25, 2025, so `review_criteria_official` must reflect the current framework with a recent `checked_date`, not a legacy model.

---

## 3. Country Parameter Block — fill this per run

```yaml
country: United States
currency: USD
citizenship_rule_notes: >
  Many federal fellowships (NSF GRFP, NDSEG, NIH F-series) require US
  citizen / national / permanent-resident status; most project grants
  (R01, NSF standard) do not restrict PI citizenship but require a US
  institution. Foundations vary. Capture per row.
has_supranational_layer: false   # true only for EU
national_pass_scope: n/a         # EU only: all_member_states | largest_n | single_country
priority_funders_seed:           # anchors to guarantee coverage; expand during run
  federal_research: [NIH, NSF, DOE Office of Science, NASA, USDA-NIFA, NIST, ARPA-H, ARPA-E]
  defense_security: [DARPA, ONR, ARO, AFOSR, IARPA, CDMRP, DTRA]
  professional_societies: [American Heart Association, American Cancer Society,
                           ACS Petroleum Research Fund, IEEE, APS, ASME]
  private_foundations: [HHMI, Burroughs Wellcome Fund, Sloan, Simons, Moore,
                        Packard, Pew, Damon Runyon, Chan Zuckerberg Initiative]
  disease_advocacy: [Cystic Fibrosis Foundation, JDRF, Michael J. Fox Foundation,
                     ALS Association, Susan G. Komen]
  institutional: [startup packages, internal seed/pilot grants, bridge funding,
                  core-facility vouchers]   # guidance rows
  industry: [Google/NVIDIA/Meta/IBM/Amazon PhD & postdoc fellowships,
             pharma investigator-initiated programs, sponsored research
             agreements, gifts, NSF GOALI, SBIR/STTR partners]  # partly guidance
  international_mobility: [Fulbright, HFSP, EMBO (life sci), NATO SPS]
  state_regional: [CIRM (CA stem cell), NYSTEM, state health research funds]
```

---

## 4. Schema (fixed, country-invariant)

One row per mechanism. Use the controlled vocabularies exactly so the result is filterable.

| Field | Type / vocabulary |
|---|---|
| `program_name` | free text |
| `funder` | free text (organization) |
| `funder_category` | `federal_research` \| `defense_security` \| `mission_applied` \| `professional_society` \| `private_foundation` \| `disease_advocacy` \| `institutional` \| `industry` \| `international_mobility` \| `state_regional` |
| `jurisdiction` | from Country Parameter Block |
| `career_stage` | multi-select: `undergraduate` \| `graduate_predoc` \| `postdoc` \| `early_career_faculty` \| `midcareer` \| `senior_established` \| `no_stage_restriction` \| `transition` \| `physician_scientist` \| `reentry` |
| `mechanism_type` | `research_grant` \| `fellowship` \| `career_development_award` \| `training_grant` \| `cooperative_agreement` \| `contract` \| `prize` \| `loan_repayment` \| `seed_pilot` \| `infrastructure_equipment` \| `travel_conference` |
| `purpose` | multi-select: `research_project` \| `salary_stipend` \| `training` \| `career_development` \| `equipment` \| `commercialization` \| `travel` \| `community` |
| `domain` | multi-select: `biomedical_health` \| `life_sciences` \| `physical_sciences` \| `engineering` \| `computing_math` \| `social_sciences` \| `humanities` \| `arts` \| `domain_agnostic` |
| `stated_purpose` | free text (official, sourced): the funder's own stated objective for the mechanism, e.g., "exploratory/developmental grant supporting early-stage, high-risk research" |
| `design_notes` | free text (commonly-known, marked as community knowledge, never fabricated): positioning not in the official blurb, e.g., "R21 requires no preliminary data; R01 expects feasibility data; U-series signals substantial agency involvement" |
| `research_stage` | `exploratory_highrisk` \| `feasibility_pilot` \| `hypothesis_driven_mature` \| `translational_productdev` \| `infrastructure_resource` \| `coordinated_network` \| `career_training` \| `dissemination_implementation` \| `unspecified` |
| `typical_award_size` | range + currency; suffix `(est.)` if estimated |
| `typical_duration` | e.g., "5 yr", "2 yr" |
| `citizenship_residency` | `citizen_national_pr_required` \| `residency_required` \| `mobility_required` \| `host_country_institution_required` \| `open_any_nationality` \| `other`; add note |
| `years_since_degree_max` | integer years, or null if no time gate (enables numeric filtering) |
| `eligibility_window` | human-readable: anchor + limit + extensions, e.g., "≤7 yr from PhD; extensions for career interruptions/parental leave" |
| `identity_targeting` | multi: `none` \| `women` \| `underrepresented_minorities` \| `disability` \| `first_generation` \| `veterans` \| `other` |
| `identity_gate_type` | `restricted_to` \| `prioritizes` \| `n/a` (hard exclusionary gate vs. soft preference/encouragement) |
| `topic_restricted` | boolean |
| `specific_topic` | free text when `topic_restricted` is true, e.g., "cystic fibrosis only"; blank otherwise |
| `submission_path` | `individual_direct` \| `institutional_nomination_limited` \| `by_invitation` \| `other` (limited-submission changes the application route) |
| `prior_funding_exclusion` | boolean + note capturing BOTH the disqualifying set and the explicit carve-outs, e.g., "excludes current/former PIs of R01/P01/P50 or equivalent incl. non-NIH grants >$100k direct/yr; R03/R21/R36/SBIR-STTR remain eligible" |
| `institution_type_restriction` | `none` \| `us_institution` \| `pui_only` \| `msi_hbcu_targeted` \| `small_business` \| `nonprofit_only` \| `r1_or_equiv` \| `other`; add note |
| `eligibility_notes` | residual idiosyncratic gates not captured above (degree type, host location, appointment specifics) |
| `application_cadence` | `rolling` \| `annual` \| `biennial` \| `irregular` (do NOT store specific dated deadlines here) |
| `selectivity` | success rate or "unspecified" (often undocumented; do not fabricate) |
| `review_criteria_official` | free text (sourced, drift-sensitive, stamp `checked_date`): the funder's current scored criteria, e.g., NIH simplified three-factor framework (Importance; Rigor & Feasibility; Expertise & Resources), NSF (Intellectual Merit; Broader Impacts), ERC (scientific excellence only) |
| `review_signals_informal` | free text, **sparse and blank-by-default**: populate only where the signal is genuinely well-established (e.g., NSF Broader Impacts as make-or-break; NIH Factor 1 capping the impact score, which is in reviewer guidance). Mark as community knowledge, default `confidence = low`, never fabricate. A blank cell is a correct answer; an invented signal is a failure |
| `coverage_type` | `enumerated` \| `guidance` |
| `source_url` | funder's own page preferred |
| `confidence` | `high` \| `medium` \| `low` |
| `checked_date` | ISO date |
| `notes` | variants, sub-agency spread, caveats |

---

## 5. Funder-category taxonomy (the top-level decomposition)

Work these in order. Each is a bounded sub-task; checkpoint after each.

1. **`federal_research`** — national science/health agencies. US anchors: NIH (R-series R01/R21/R03; K-series K01/K08/K23/K99-R00; F-series F31/F32; T32 training; U-series cooperative; R35/MIRA; LRP), NSF (CAREER, GRFP, standard/continuing grants, MRI instrumentation, postdoctoral fellowships by directorate), DOE Office of Science (incl. CSGF), NASA, USDA-NIFA, NIST, ARPA-H, ARPA-E, SBIR/STTR (cross-agency, `commercialization`).
2. **`defense_security`** — US-heavy: DARPA, ONR, ARO, AFOSR (each with its own Young Investigator Program), IARPA, CDMRP (disease-specific congressional programs), DTRA. Note this category is large in the US and much smaller/differently shaped elsewhere.
3. **`mission_applied`** — sector agencies with research money: DOT, DHS, EPA, NIH-adjacent institutes; catch-all for applied/mission funding not in (1) or (2).
4. **`professional_society`** — discipline-specific, often career-stage-graded (many run explicit early-career awards). AHA, ACS (incl. Petroleum Research Fund), IEEE, APS, ASME, etc.
5. **`private_foundation`** — frequently the source of prestige early-career and high-risk funding. HHMI (Investigator, Hanna Gray), Burroughs Wellcome (CASI, PDEP), Sloan Research Fellowship, Simons, Moore, Packard, Pew Scholars, Beckman Young Investigator, Damon Runyon, CZI.
6. **`disease_advocacy`** — patient/cause organizations funding targeted research: CF Foundation, JDRF, Michael J. Fox, ALS Association, Komen. Overlaps (5) but track separately; domain is narrow by design.
7. **`institutional`** — **guidance rows.** Startup packages, internal seed/pilot, bridge funding, core-facility vouchers, internal fellowships. Not enumerable per institution on the open web: give typical ranges by institution type and career stage, and "how to access" (chair/dean negotiation, internal grants office, VP-research seed calls).
8. **`industry`** — **mixed.** Enumerable: named corporate PhD/postdoc fellowships (Google, NVIDIA, Meta, IBM, Amazon), pharma investigator-initiated/ISR programs, NSF GOALI, SBIR/STTR industry partnerships. Guidance: sponsored research agreements, unrestricted gifts, consortia (relationship-driven, mark `guidance`).
9. **`international_mobility`** — cross-border collaboration/mobility: Fulbright, HFSP (postdoc + program grants), EMBO (life-sci fellowships + Young Investigator), NATO SPS, bilateral programs.
10. **`state_regional`** — geographically bounded: CIRM, NYSTEM, state health research funds; (provincial for CA; regional/structural for EU).

---

## 6. Career-stage cross-reference (seed + validation)

Use this to (a) seed early rows and (b) validate coverage: after the run, confirm every stage below has multiple entries across multiple funder categories. If a stage is thin, coverage is incomplete.

- **undergraduate:** NSF REU, institutional UROP.
- **graduate_predoc:** NSF GRFP, NDSEG, Ford Foundation, Hertz, DOE CSGF, NIH F31.
- **postdoc:** NIH F32, K99/R00, NSF directorate postdoctoral fellowships, Burroughs Wellcome PDEP/CASI, HHMI Hanna Gray, Damon Runyon, EMBO/HFSP.
- **early_career_faculty:** NSF CAREER, NIH ESI-flagged R01 / R00 activation, DoD YIP (ONR/ARO/AFOSR), Sloan, Packard, Pew, Beckman.
- **midcareer:** NIH R35/MIRA, HHMI Investigator, society mid-career awards.
- **senior_established:** NIH R35, endowed programs, major prizes.
- **transition:** K99/R00 (postdoc→faculty), NIH LRP (loan repayment).
- **physician_scientist:** NIH K08/K23, disease-foundation clinical investigator awards.

Verify exact eligibility windows and current amounts in-session; treat the above as anchors, not final values.

---

## 7. Phased execution plan

1. **Phase 0 — Scaffold.** Create the empty dataset with the Section 4 columns and the controlled-vocabulary lists. Load the Country Parameter Block.
2. **Phase 1 — Category sweep.** For each of the 10 categories in order: enumerate every major funder, then for each funder traverse its full program catalog and log every distinct standing program to the stopping rule (Section 2.2), not just flagship families. Checkpoint (write file) after each category, and record a per-funder program count so under-covered funders are visible.
3. **Phase 2 — Gap categories.** Explicitly produce `institutional` and `industry` guidance rows per principle 4. Do not let the crawler skip them.
4. **Phase 3 — Career-stage validation.** Run the Section 6 checklist against the dataset; fill any thin stage/category cells.
5. **Phase 4 — QC and assembly.** Apply Section 9 acceptance criteria; deduplicate; then generate the companion doc.

---

## 8. Optional live-opportunity layer (toggle off by default)

If current deadlines are wanted, run this as a **separate file** (`live_opportunities_<country>.csv`), never merged into the durable dataset. The durable/solicitation boundary is the operative floor of the Phase 1 sweep: anything that is a standing program goes in the main dataset; anything that exists only as a specific dated call goes here. Source: Grants.gov / agency portals (US), TARA/funders (CA), Funding & Tenders Portal (EU). Columns: `program_name`, `funder`, `open_date`, `close_date`, `link`, `linked_mechanism` (FK to the durable row). This file is disposable and re-pulled on demand.

---

## 9. Output artifacts and acceptance criteria

**Artifacts:**
1. `funding_landscape_<country>.csv` (or `.xlsx`) — the schema-conformant dataset, primary deliverable.
2. `funding_landscape_<country>_guide.md` — thin companion: how to filter the sheet, one short paragraph per funder category, the availability-bias caveat restated, and 5–7 worked "if you are an X, look at Y" personas spanning career stages.

**Acceptance criteria (all must hold):**
- All 10 funder categories present with ≥1 major funder each; none empty.
- Every major funder in the seed list traversed at its program-catalog level, with a logged program count per funder (breadth is auditable, not asserted).
- Every `career_stage` value in the vocabulary appears in ≥2 rows across ≥2 categories.
- `institutional` and `industry` each have guidance rows; not silently dropped.
- Dedup key = (`funder`, `program_name`); no duplicate keys after assembly.
- No row stores a dated deadline in `application_cadence`; standing programs only in the main file.
- Every row has `source_url`, `confidence`, `checked_date`; estimated amounts marked `(est.)`.
- Confidence distribution reported (counts by `high`/`medium`/`low`); a run that is mostly `low` signals shallow breadth-padding and fails QC.
- Every gating factor in a program's actual rules is captured in its structured column, not buried in `eligibility_notes` (a `restricted_to` program with blank `identity_targeting`, or a disease-specific funder with `topic_restricted = false`, is a defect).
- Identity-restricted rows (`identity_gate_type = restricted_to`) carry a `checked_date` within the current run window, given post-SFFA drift.
- For mentored and career-development mechanisms, `prior_funding_exclusion` is populated from the NOFO eligibility section (not left `false` by default), with disqualifying and preserved awards both recorded.
- `stated_purpose` and `research_stage` populated for every mechanism (not left blank/`unspecified` where the funder's own description makes the intent clear).
- `stated_purpose` and `review_criteria_official` carry a source; `design_notes` and `review_signals_informal` are marked as community knowledge and contain no fabricated criteria. `review_signals_informal` is left blank wherever the signal is not well-established (a blank cell passes QC; a plausible-but-unsourced invented signal fails).
- `review_criteria_official` reflects the funder's current framework (e.g., NIH simplified three-factor post-Jan-2025; NSF two-criterion; ERC excellence-only), not a legacy or NIH-shaped default, with `checked_date`.
- No fabricated selectivity or amounts; unknowns say "unspecified".

---

## 10. Country swap templates

**Canada (`country: Canada`, `currency: CAD`, `has_supranational_layer: false`)**
- `federal_research`: Tri-agency — CIHR, NSERC, SSHRC (Project/Discovery/Insight grants); Canada Research Chairs (Tier 1 senior / Tier 2 early-career); CFI (`infrastructure`); Vanier CGS (`graduate_predoc`); Banting (`postdoc`); New Frontiers in Research Fund.
- `defense_security`: DRDC/IDEaS (smaller than US).
- `state_regional`: provincial — e.g., Ontario (ORF), Quebec (FRQ streams), Alberta.
- Citizenship: several fellowships restrict to Canadian citizens/PRs; grants generally require a Canadian institution. Verify per row.

**EU (`country: EU`, `currency: EUR`, `has_supranational_layer: true`, `national_pass_scope: <choose>`)**
- Treat the **supranational layer as its own category pass** first: Horizon Europe — ERC (Starting / Consolidator / Advanced / Synergy / Proof-of-Concept, mapping cleanly to career stage), MSCA (Doctoral Networks `graduate_predoc`, Postdoctoral Fellowships `postdoc`), EIC (Pathfinder/Transition/Accelerator, `commercialization`).
- Then the **national pass**, scoped by `national_pass_scope`: `all_member_states` (heavy), `largest_n` (e.g., DFG-Germany, ANR-France, NWO-Netherlands, and similar), or `single_country`.
- `international_mobility`: EMBO, HFSP apply here too.
- `defense_security`: European Defence Fund + national MoDs (differently shaped from US).
- Citizenship/eligibility: MSCA has mobility rules (recruitment across borders); ERC is portable to any EU/associated-country host. Capture the mobility constraint in `eligibility_constraints`.
