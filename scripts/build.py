#!/usr/bin/env python3
"""Validate the mechanism vault, derive the numeric layer, emit one compiled artifact.

    python scripts/build.py           # validate + derive + write dist/corpus.json
    python scripts/build.py --check   # validate only; exit 1 on any gate failure

House rules honoured here:
  - data/mechanisms.csv is the only hand-edited layer. Nothing here writes to it.
  - Derived fields (award_*_usd, duration_years, staleness_days) are NEVER stored
    in the vault. They live only in dist/corpus.json and are recomputed each build.
  - The money/duration parsers are heuristics. Every derived number carries a
    `basis` and the raw source string, so a reader can always see what was parsed.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VAULT = ROOT / "data" / "mechanisms.csv"
OUT = ROOT / "dist" / "corpus.json"

SCHEMA_VERSION = "0.5.0"

# How fast each field goes stale, and therefore how hard the worklist pushes to
# re-check it. Drawn from the brief's own observations: identity gates are the
# fastest-drifting field in the corpus post-SFFA, amounts drift each cycle, purpose
# and review frameworks change rarely.
DRIFT_WEIGHT = {
    "identity_checked": 3.0,
    "award_checked": 2.0,
    "eligibility_checked": 1.5,
    "review_criteria_checked": 1.5,
}
# Federal money moved unusually in 2025-26; those rows earn a re-check sooner.
VOLATILE_CATEGORIES = {"federal_research", "defense_security", "mission_applied"}
STALE_AFTER_DAYS = 90

# ---------------------------------------------------------------- vocabularies
# Frozen from docs/BRIEF.md Section 4. Bump SCHEMA_VERSION on any change here
# and record the change in DECISIONS.md (P0 rule 6, version ceremony).
MULTI = {"career_stage", "purpose", "domain", "identity_targeting"}

VOCAB = {
    "funder_category": {
        "federal_research", "defense_security", "mission_applied",
        "professional_society", "private_foundation", "disease_advocacy",
        "institutional", "industry", "international_mobility", "state_regional",
    },
    "career_stage": {
        "undergraduate", "graduate_predoc", "postdoc", "early_career_faculty",
        "midcareer", "senior_established", "no_stage_restriction", "transition",
        "physician_scientist", "reentry",
    },
    "mechanism_type": {
        "research_grant", "fellowship", "career_development_award",
        "training_grant", "cooperative_agreement", "contract", "prize",
        "loan_repayment", "seed_pilot", "infrastructure_equipment",
        "travel_conference",
    },
    "purpose": {
        "research_project", "salary_stipend", "training", "career_development",
        "equipment", "commercialization", "travel", "community",
    },
    "domain": {
        "biomedical_health", "life_sciences", "physical_sciences", "engineering",
        "computing_math", "social_sciences", "humanities", "arts",
        "domain_agnostic",
    },
    "research_stage": {
        "exploratory_highrisk", "feasibility_pilot", "hypothesis_driven_mature",
        "translational_productdev", "infrastructure_resource",
        "coordinated_network", "career_training", "dissemination_implementation",
        "unspecified",
    },
    "citizenship_residency": {
        "citizen_national_pr_required", "residency_required", "mobility_required",
        "host_country_institution_required", "open_any_nationality", "other",
    },
    "identity_targeting": {
        "none", "women", "underrepresented_minorities", "disability",
        "first_generation", "veterans", "other",
    },
    "identity_gate_type": {"restricted_to", "prioritizes", "n/a"},
    "submission_path": {
        "individual_direct", "institutional_nomination_limited", "by_invitation",
        "other",
    },
    "institution_type_restriction": {
        "none", "us_institution", "pui_only", "msi_hbcu_targeted",
        "small_business", "nonprofit_only", "r1_or_equiv", "other",
    },
    "application_cadence": {"rolling", "annual", "biennial", "irregular"},
    "coverage_type": {"enumerated", "guidance"},
    "confidence": {"high", "medium", "low"},
    "status": {"active", "paused", "terminated", "unknown"},
    "resubmission_allowed": {"yes", "no", "limited", "unspecified"},
    "applicant_of_record": {
        "individual", "institution_for_individual",
        "institution_then_appointed", "institution_only", "unspecified",
    },
}

# Every date column, so a malformed stamp is caught wherever it appears.
DATE_FIELDS = ["checked_date", "status_checked", "status_valid_to",
               "award_checked", "eligibility_checked", "identity_checked",
               "review_criteria_checked", "submission_checked"]

REQUIRED = ["program_name", "funder", "funder_category", "source_url",
            "confidence", "checked_date"]


def split_multi(value: str) -> list[str]:
    return [v.strip() for v in re.split(r"[;,|]", value or "") if v.strip()]


# ------------------------------------------------------------- money parsing
# Free-text award strings carry three shapes that a naive "find every $N" scan
# gets wrong, each verified against the vault before being handled here:
#   composite  "$37,000 stipend + $16,000 allowance"  -> one award of $53,000,
#              not a $16K-$37K range (52/190 rows).
#   cohort     "$11.5M across 23 awardees"            -> a programme total that
#              must never enter a per-award envelope (3/190 rows).
#   trailing   "$1-2M", "$8-15M+"                     -> the scale word binds to
#   scale       both ends of the range (4/190 rows).
_SCALE = {"million": 1e6, "m": 1e6, "billion": 1e9, "b": 1e9,
          "thousand": 1e3, "k": 1e3}

# A range first ("$1-2M", "$250,000-$500,000", "$1 to $2 million"), so the
# trailing scale word is applied to both endpoints rather than only the last.
_RANGE = re.compile(
    r"\$\s*(\d[\d,]*(?:\.\d+)?)\s*(million|billion|thousand|[MmKkBb])?\s*"
    r"(?:[-–—]|\bto\b)\s*"
    r"\$?\s*(\d[\d,]*(?:\.\d+)?)\s*(million|billion|thousand|[MmKkBb])?(?![a-zA-Z])",
    re.I)
_SINGLE = re.compile(
    r"\$\s*(\d[\d,]*(?:\.\d+)?)\s*(million|billion|thousand|[MmKkBb])?(?![a-zA-Z])",
    re.I)

_ANNUAL_CUE = re.compile(
    r"(/\s*yr|/\s*year|per\s+year|per\s+yr|a\s+year|annually|/\s*annum|"
    r"each\s+year|per\s+annum|yearly|\bannual\b|/\s*mo|per\s+month|monthly)", re.I)
_TOTAL_CUE = re.compile(
    r"(total|over\s+(?:the\s+)?\d|over\s+the\s+award|cumulative|"
    r"lifetime\s+of\s+the\s+award)", re.I)
_MONTHLY_CUE = re.compile(r"(/\s*mo\b|per\s+month|monthly)", re.I)
# Figures describing a whole competition rather than one award.
_COHORT_CUE = re.compile(
    r"(across\b|all\s+awardees|total\s+program|program\s+total|"
    r"announcement\s+was|class\s+was|budget\s+of\s+the\s+program)", re.I)


def _scale_for(token: str | None) -> float:
    return _SCALE.get(token.lower(), 1.0) if token else 1.0


def _num(s: str) -> float:
    return float(s.replace(",", ""))


def _basis_of(clause: str) -> str:
    if _ANNUAL_CUE.search(clause):
        return "annual"
    if _TOTAL_CUE.search(clause):
        return "total"
    return "unknown"


def parse_amounts(text: str) -> list[dict]:
    """Return one entry per *clause*, each an award envelope with its basis.

    The string is split on `;` into clauses, because rows routinely state an
    annual figure and a total in the same cell. Within a clause, figures joined
    by `+` are components of a single award and are summed; figures joined by a
    dash or "to" are the ends of a range. Cohort figures are dropped.
    """
    if not text:
        return []
    # A parenthetical holding money *after* money has already been stated is a
    # restatement of it -- "$240,000 total ($80,000/yr: ...)", "$7,810 stipend
    # ($710/week)" -- so it is dropped rather than added or ranged against. A
    # parenthetical that opens the figure ("monthly stipend (~$41k/yr)") is the
    # only statement there is, and is kept.
    def drop_restatement(m: re.Match) -> str:
        before = text[:m.start()]
        if "$" not in m.group(0) or "$" not in before:
            return m.group(0)
        # "+ a return award (~$70,000)" adds money rather than restating it, so a
        # parenthetical reached through a "+" is kept.
        if "+" in before[-40:]:
            return m.group(0)
        return ""

    text = re.sub(r"\([^()]*\)", drop_restatement, text)
    # What survives and holds no money is prose ("(escalating by year)"). Strip it
    # rather than letting it split a clause and strand one half of a "+" sum.
    text = re.sub(r"\((?![^()]*\$)[^()]*\)", " ", text)

    out: list[dict] = []
    for clause in re.split(r";", text):
        clause = clause.strip(" ,.")
        if not clause or _COHORT_CUE.search(clause):
            continue

        # "$80,000/yr: $60,000 stipend + $20,000 allowance" — a figure before the
        # colon means what follows is its breakdown, not further money. With no
        # figure before the colon ("Varies by stage: Discovery ~$1-2M") the
        # figures live after it and the whole clause is kept.
        head, sep, tail = clause.partition(":")
        if sep and _SINGLE.search(head):
            clause = head

        # A clause carrying both "/mo" and "/yr" states one stipend twice. Keep
        # the annual statement and drop the monthly one rather than converting.
        both_units = bool(_MONTHLY_CUE.search(clause)) and bool(
            re.search(r"/\s*yr|/\s*year|per\s+year|k/yr", clause, re.I))

        lo_parts: list[float] = []
        hi_parts: list[float] = []
        consumed: list[tuple[int, int]] = []

        def keep(start: int, end: int) -> bool:
            """With both units present, keep only figures cued as annual."""
            if not both_units:
                return True
            return bool(re.match(r"\s*(?:k)?\s*/\s*(?:yr|year)|\s*per\s+year",
                                 clause[end:end + 12], re.I))

        for m in _RANGE.finditer(clause):
            if not keep(m.start(), m.end()):
                consumed.append((m.start(), m.end()))
                continue
            lo_parts.append(_num(m.group(1)) * _scale_for(m.group(2) or m.group(4)))
            hi_parts.append(_num(m.group(3)) * _scale_for(m.group(4) or m.group(2)))
            consumed.append((m.start(), m.end()))

        for m in _SINGLE.finditer(clause):
            if any(s <= m.start() < e for s, e in consumed):
                continue
            if not keep(m.start(), m.end()):
                continue
            v = _num(m.group(1)) * _scale_for(m.group(2))
            lo_parts.append(v)
            hi_parts.append(v)

        if not lo_parts:
            continue

        basis = _basis_of(clause)
        # "+" means components of one award: sum them. Otherwise the figures are
        # alternatives (tiers, variants) and the envelope spans them.
        if "+" in clause and len(lo_parts) > 1:
            lo, hi = sum(lo_parts), sum(hi_parts)
        else:
            lo, hi = min(lo_parts), max(hi_parts)

        if not both_units and _MONTHLY_CUE.search(clause):
            lo, hi, basis = lo * 12, hi * 12, "annual"

        out.append({"min": lo, "max": hi, "basis": basis, "clause": clause[:120]})
    return out


_DURATION = re.compile(
    r"(\d+(?:\.\d+)?)\s*(?:-|–|—|\s+to\s+)?\s*(\d+(?:\.\d+)?)?\s*"
    r"(year|yr|month|mo)s?\b", re.I)


def parse_duration(text: str) -> dict | None:
    """Longest duration mentioned, in years. 'up to 5 years' -> 5.0."""
    if not text:
        return None
    best = None
    for m in _DURATION.finditer(text):
        lo = float(m.group(1))
        hi = float(m.group(2)) if m.group(2) else lo
        unit = m.group(3).lower()
        if unit.startswith("mo"):
            lo, hi = lo / 12.0, hi / 12.0
        if best is None or hi > best["max_years"]:
            best = {"min_years": round(lo, 2), "max_years": round(hi, 2)}
    if best:
        best["raw"] = text.strip()
    return best


# Prose that means the funder itself declines to state a figure. A number sitting
# next to these words is an illustration, not the award envelope.
_VAGUE_CUE = re.compile(r"\bvaries\b|\bunspecified\b|\bcommonly\b|\bvary\s+widely\b", re.I)


def derive_award(row: dict) -> dict:
    """Normalise award size into annual / total USD envelopes.

    `award_parse` grades how far the result can be trusted:
      clean      a figure was parsed and the string carries none of the shapes
                 known to defeat the parser -> safe for a value axis.
      heuristic  a figure was parsed but the string is vague or component-laden
                 -> usable as an order of magnitude, shown but flagged.
      unparsed   no dollar figure at all -> excluded from value views entirely,
                 never treated as zero.
    """
    raw = (row.get("typical_award_size") or "").strip()
    clauses = parse_amounts(raw)
    dur = parse_duration(row.get("typical_duration") or "")

    d: dict = {
        "award_raw": raw,
        "award_estimated": "(est." in raw.lower(),
        "duration": dur,
    }
    if not clauses:
        d["award_parse"] = "unparsed"
        return d

    def envelope(basis: str):
        sel = [c for c in clauses if c["basis"] == basis]
        return (min(c["min"] for c in sel), max(c["max"] for c in sel)) if sel else None

    annual, total = envelope("annual"), envelope("total")
    unknown = envelope("unknown")

    # An uncued figure is annual when the row's only other cue is annual,
    # otherwise it is the total. Rows with no cue at all default to total,
    # which is how a bare "$125,000 over 2 years" reads.
    if unknown:
        if annual and not total:
            annual = (min(annual[0], unknown[0]), max(annual[1], unknown[1]))
        elif total:
            total = (min(total[0], unknown[0]), max(total[1], unknown[1]))
        else:
            total = unknown

    if annual:
        d["annual_min_usd"], d["annual_max_usd"] = annual
    if total:
        d["total_min_usd"], d["total_max_usd"] = total

    # Bridge the bases so every priced row has a comparable total.
    if not total and annual and dur:
        d["total_min_usd"] = annual[0] * dur["min_years"]
        d["total_max_usd"] = annual[1] * dur["max_years"]
        d["total_derived_from"] = "annual x duration"
    elif not annual and total and dur and dur["max_years"] >= 1:
        d["annual_min_usd"] = total[0] / dur["max_years"]
        d["annual_max_usd"] = total[1] / dur["max_years"]
        d["annual_derived_from"] = "total / duration"

    flags = []
    if _VAGUE_CUE.search(raw):
        flags.append("vague_prose")
    if _COHORT_CUE.search(raw):
        flags.append("cohort_figure_present")
    if "+" in raw:
        flags.append("composite_summed")
    if d["award_estimated"]:
        flags.append("funder_estimate")
    d["award_flags"] = flags

    # Only vagueness and stray cohort figures undermine the envelope; a summed
    # composite or a marked estimate is still a real per-award number.
    unreliable = {"vague_prose", "cohort_figure_present"}
    d["award_parse"] = "heuristic" if unreliable.intersection(flags) else "clean"
    return d


# ------------------------------------------------------------------- gates
def validate(rows: list[dict]) -> tuple[list[str], list[str], dict]:
    """Return (errors, warnings, stats). Errors fail --check; warnings do not."""
    errors: list[str] = []
    warnings: list[str] = []

    for i, r in enumerate(rows, start=2):  # +2: header is line 1
        tag = f"row {i} ({r.get('program_name', '?')[:40]})"

        for f in REQUIRED:
            if not (r.get(f) or "").strip():
                errors.append(f"{tag}: required field '{f}' is empty")

        for field, allowed in VOCAB.items():
            val = (r.get(field) or "").strip()
            if not val:
                continue
            vals = split_multi(val) if field in MULTI else [val]
            for v in vals:
                if v not in allowed:
                    errors.append(f"{tag}: {field}='{v}' not in controlled vocabulary")

        tr = (r.get("topic_restricted") or "").strip().lower()
        if tr not in ("true", "false"):
            errors.append(f"{tag}: topic_restricted='{tr}' is not a boolean")
        elif tr == "true" and not (r.get("specific_topic") or "").strip():
            errors.append(f"{tag}: topic_restricted=true but specific_topic is blank")

        if re.search(r"\b(20\d\d-\d\d-\d\d|january|february|march|april|may|june|"
                     r"july|august|september|october|november|december)\b",
                     r.get("application_cadence") or "", re.I):
            errors.append(f"{tag}: dated deadline in application_cadence "
                          f"(belongs in the live layer, brief S8)")

        for f in DATE_FIELDS:
            v = (r.get(f) or "").strip()
            if v and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", v):
                errors.append(f"{tag}: {f} '{v}' is not ISO yyyy-mm-dd")

        # --- the durability gate -------------------------------------------
        # A status is a claim about the world and is sourced like any other. The
        # failure mode this guards against is a `terminated` row asserted from a
        # dead link: an absent page is not evidence that a programme ended.
        st = (r.get("status") or "").strip()
        ev = (r.get("status_evidence") or "").strip()
        src = (r.get("status_source") or "").strip()
        sck = (r.get("status_checked") or "").strip()
        if st and st != "unknown":
            for f, v in (("status_evidence", ev), ("status_source", src),
                         ("status_checked", sck)):
                if not v:
                    errors.append(f"{tag}: status='{st}' requires {f}")
        elif st == "unknown" and (ev or src or sck):
            errors.append(f"{tag}: status='unknown' but carries evidence "
                          f"— record the status it supports")
        if (r.get("status_valid_to") or "").strip() and st not in ("terminated", "paused"):
            errors.append(f"{tag}: status_valid_to set but status='{st}'")
        if st == "terminated" and not (r.get("status_valid_to") or "").strip():
            warnings.append(f"{tag}: terminated without a status_valid_to date")

        if (r.get("identity_gate_type") or "").strip() == "restricted_to":
            idt = split_multi(r.get("identity_targeting") or "")
            if not idt or idt == ["none"]:
                errors.append(f"{tag}: identity_gate_type=restricted_to but "
                              f"identity_targeting is none/blank")

        aor = (r.get("applicant_of_record") or "").strip()
        if aor and aor != "unspecified" and not (r.get("applicant_of_record_note") or "").strip():
            errors.append(f"{tag}: applicant_of_record='{aor}' without a note explaining it")

        ra = (r.get("resubmission_allowed") or "").strip()
        if ra and ra != "unspecified" and not (r.get("submission_checked") or "").strip():
            errors.append(f"{tag}: resubmission_allowed='{ra}' without a submission_checked date")

        ysd = (r.get("years_since_degree_max") or "").strip()
        if ysd and not re.fullmatch(r"\d+(\.\d+)?", ysd):
            warnings.append(f"{tag}: years_since_degree_max '{ysd}' is not numeric")

    # --- dedup key (funder, program_name)
    key = Counter((r["funder"].strip(), r["program_name"].strip()) for r in rows)
    for k, n in key.items():
        if n > 1:
            errors.append(f"duplicate dedup key {k!r} appears {n} times")

    # --- brief Section 9 coverage gates
    cats = Counter(r["funder_category"].strip() for r in rows)
    for c in VOCAB["funder_category"]:
        if not cats.get(c):
            errors.append(f"coverage gate: funder_category '{c}' has 0 rows")

    stage_cats = defaultdict(set)
    stage_n = Counter()
    for r in rows:
        for s in split_multi(r["career_stage"]):
            stage_n[s] += 1
            stage_cats[s].add(r["funder_category"].strip())
    for s in VOCAB["career_stage"]:
        if stage_n[s] < 2 or len(stage_cats[s]) < 2:
            errors.append(f"coverage gate: career_stage '{s}' has {stage_n[s]} row(s) "
                          f"across {len(stage_cats[s])} category/ies (need >=2 / >=2)")

    for c in ("institutional", "industry"):
        n = sum(1 for r in rows
                if r["funder_category"].strip() == c
                and r["coverage_type"].strip() == "guidance")
        if n == 0:
            errors.append(f"availability-bias gate: '{c}' has no guidance rows")

    conf = Counter(r["confidence"].strip() for r in rows)
    if conf["low"] > len(rows) * 0.25:
        errors.append(f"confidence gate: {conf['low']}/{len(rows)} rows are low "
                      f"(>25% signals breadth-padding)")

    stats = {
        "rows": len(rows),
        "funders": len({r["funder"].strip() for r in rows}),
        "by_category": dict(cats.most_common()),
        "by_confidence": dict(conf),
        "by_career_stage": dict(stage_n.most_common()),
    }
    return errors, warnings, stats


# --------------------------------------------------------------- worklist
def staleness_worklist(records: list[dict], today: dt.date) -> dict:
    """Rank what to re-check, by consequence rather than by age alone.

    A flat "older than 90 days" rule treats a foundation's stated purpose and an
    NIH eligibility window as equally urgent. They are not: the score below is
    age x how fast the field drifts x whether the funder sits in the part of the
    landscape that moved in 2025-26.
    """
    items = []
    never = []
    # Which vault field each provenance stamp vouches for, so an empty stamp is
    # only "never checked" when there is actually something to check.
    VOUCHES_FOR = {
        "award_checked": "typical_award_size",
        "eligibility_checked": "eligibility_window",
        "identity_checked": "identity_targeting",
        "review_criteria_checked": "review_criteria_official",
    }
    for r in records:
        volatile = r["funder_category"] in VOLATILE_CATEGORIES
        for field, weight in DRIFT_WEIGHT.items():
            stamp = (r.get(field) or "").strip()
            if not stamp:
                # A populated field with no stamp has never been verified, which
                # is worse than one verified a long time ago -- rank it apart
                # rather than letting it fall out of the worklist silently.
                vouched = r.get(VOUCHES_FOR[field])
                # Multi-select fields arrive as lists; "none" is a coded answer,
                # not content that needs verifying.
                if isinstance(vouched, list):
                    has_content = bool([v for v in vouched if v != "none"])
                else:
                    has_content = bool((vouched or "").strip())
                if has_content:
                    never.append({"program_name": r["program_name"],
                                  "funder": r["funder"], "field": field})
                continue
            try:
                age = (today - dt.date.fromisoformat(stamp)).days
            except ValueError:
                continue
            items.append({
                "program_name": r["program_name"],
                "funder": r["funder"],
                "funder_category": r["funder_category"],
                "field": field,
                "age_days": age,
                "score": round(age * weight * (1.5 if volatile else 1.0), 1),
                "overdue": age > STALE_AFTER_DAYS,
            })
    items.sort(key=lambda i: -i["score"])

    # A `guidance` row describes a class of funding -- startup packages, sponsored
    # research agreements -- not a named programme with a funder page to check.
    # "Does it still exist" is not the same question there, so those rows are
    # counted apart instead of inflating the re-check debt forever.
    unknown_status = [r for r in records
                      if r.get("status") == "unknown"
                      and r.get("coverage_type") != "guidance"]
    guidance_no_status = [r for r in records
                          if r.get("status") == "unknown"
                          and r.get("coverage_type") == "guidance"]
    return {
        "generated": today.isoformat(),
        "stale_after_days": STALE_AFTER_DAYS,
        "never_checked_count": len(never),
        "never_checked": never[:40],
        "overdue_count": sum(1 for i in items if i["overdue"]),
        "unknown_status_count": len(unknown_status),
        "guidance_no_status_count": len(guidance_no_status),
        "unknown_status_volatile": sum(
            1 for r in unknown_status if r["funder_category"] in VOLATILE_CATEGORIES),
        "top": items[:60],
    }


# ------------------------------------------------------------------- build
def build(check_only: bool = False) -> int:
    if not VAULT.exists():
        print(f"FAIL: vault not found at {VAULT}", file=sys.stderr)
        return 1

    with VAULT.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))

    errors, warnings, stats = validate(rows)

    today = dt.date.today()
    records = []
    for r in rows:
        rec = {k: (v or "").strip() for k, v in r.items()}
        for f in MULTI:
            rec[f] = split_multi(r.get(f, ""))
        rec["topic_restricted"] = (r.get("topic_restricted") or "").strip().lower() == "true"
        aor = (r.get("applicant_of_record") or "").strip()
        if aor and aor != "unspecified" and not (r.get("applicant_of_record_note") or "").strip():
            errors.append(f"{tag}: applicant_of_record='{aor}' without a note explaining it")

        ra = (r.get("resubmission_allowed") or "").strip()
        if ra and ra != "unspecified" and not (r.get("submission_checked") or "").strip():
            errors.append(f"{tag}: resubmission_allowed='{ra}' without a submission_checked date")

        ysd = (r.get("years_since_degree_max") or "").strip()
        rec["years_since_degree_max"] = float(ysd) if re.fullmatch(r"\d+(\.\d+)?", ysd) else None
        rec.update(derive_award(r))
        try:
            checked = dt.date.fromisoformat(rec["checked_date"])
            rec["staleness_days"] = (today - checked).days
        except ValueError:
            rec["staleness_days"] = None
        records.append(rec)

    parse_counts = Counter(r["award_parse"] for r in records)
    stats["award_parse"] = dict(parse_counts)
    stats["by_status"] = dict(Counter(r.get("status") or "unset" for r in records))
    work = staleness_worklist(records, today)
    stats["overdue_fields"] = work["overdue_count"]
    stats["unknown_status"] = work["unknown_status_count"]
    stats["guidance_no_status"] = work["guidance_no_status_count"]
    stats["with_duration"] = sum(1 for r in records if r.get("duration"))
    stats["max_staleness_days"] = max(
        (r["staleness_days"] for r in records if r["staleness_days"] is not None),
        default=None)

    print(f"rows            {stats['rows']}")
    print(f"funders         {stats['funders']}")
    print(f"award parse     " + ", ".join(f"{k}={v}" for k, v in sorted(parse_counts.items())))
    print(f"duration parsed {stats['with_duration']}/{stats['rows']}")
    print(f"staleness       up to {stats['max_staleness_days']} days")
    print(f"status          " + ", ".join(f"{k}={v}" for k, v in
                                          sorted(stats["by_status"].items())))
    print(f"re-check debt   {work['unknown_status_count']} enumerated rows of unknown "
          f"status ({work['unknown_status_volatile']} volatile), "
          f"{work['guidance_no_status_count']} guidance rows n/a, "
          f"{work['overdue_count']} fields past {STALE_AFTER_DAYS}d, "
          f"{work['never_checked_count']} never checked")
    print(f"errors          {len(errors)}")
    print(f"warnings        {len(warnings)}")

    for e in errors[:40]:
        print(f"  ERROR   {e}")
    if len(errors) > 40:
        print(f"  ... and {len(errors) - 40} more errors")
    for w in warnings[:15]:
        print(f"  warn    {w}")
    if len(warnings) > 15:
        print(f"  ... and {len(warnings) - 15} more warnings")

    if check_only:
        return 1 if errors else 0

    OUT.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "built": today.isoformat(),
        "source": "data/mechanisms.csv",
        "stats": stats,
        "gate_errors": errors,
        "gate_warnings": warnings,
        "worklist": work,
        "mechanisms": records,
    }
    with OUT.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
    print(f"wrote           {OUT.relative_to(ROOT)} "
          f"({OUT.stat().st_size // 1024} KB)")
    return 1 if errors else 0


# Fields the explorer needs. Everything else stays in corpus.json: the page is
# inlined into one artifact, so its payload is trimmed rather than complete.
VIZ_FIELDS = [
    "program_name", "funder", "funder_category", "career_stage", "domain",
    "mechanism_type", "purpose", "research_stage", "citizenship_residency",
    "institution_type_restriction", "submission_path", "identity_targeting",
    "identity_gate_type", "topic_restricted", "specific_topic",
    "typical_duration", "eligibility_window", "years_since_degree_max",
    "selectivity", "confidence", "coverage_type", "source_url", "checked_date",
    "award_raw", "award_parse", "award_flags", "annual_min_usd",
    "annual_max_usd", "total_min_usd", "total_max_usd", "staleness_days",
    "status", "status_valid_to", "status_evidence", "status_source",
    "status_checked", "submission_requirements", "resubmission_allowed",
    "resubmission_policy", "submission_checked", "applicant_of_record",
    "applicant_of_record_note",
]


def write_viz_payload() -> Path:
    """Trim dist/corpus.json down to what the explorer renders."""
    with OUT.open(encoding="utf-8") as fh:
        full = json.load(fh)
    slim = []
    for r in full["mechanisms"]:
        row = {k: r[k] for k in VIZ_FIELDS if k in r and r[k] not in ("", None, [])}
        purpose = (r.get("stated_purpose") or "").strip()
        if purpose:
            row["stated_purpose"] = purpose[:260] + ("..." if len(purpose) > 260 else "")
        slim.append(row)
    dest = OUT.parent / "viz-data.json"
    with dest.open("w", encoding="utf-8") as fh:
        json.dump({"built": full["built"], "stats": full["stats"],
                   "mechanisms": slim}, fh, ensure_ascii=False, separators=(",", ":"))
    print(f"wrote           {dest.relative_to(ROOT)} "
          f"({dest.stat().st_size // 1024} KB)")
    return dest


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="validate only; do not write dist/")
    ap.add_argument("--viz", action="store_true",
                    help="also write the trimmed explorer payload")
    args = ap.parse_args()
    code = build(args.check)
    if args.viz and not args.check:
        write_viz_payload()
    sys.exit(code)
