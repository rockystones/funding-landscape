#!/usr/bin/env python3
"""Schema 0.4.0 -> 0.5.0: who is the applicant of record.

    python scripts/migrate_0_5_0.py [--dry-run]

`submission_path` conflates three different situations, and 178 of 219 rows sit
in one bucket (`individual_direct`) doing almost no work. The distinction that
actually changes what a person DOES is who the funder treats as the applicant:

  individual                  The person registers and submits. NEH Fellowships
                              requires a Grants.gov "individual applicant"
                              profile; Guggenheim and ACLS take applications
                              from people.

  institution_for_individual  The person is the named PD/PI and writes the
                              science, but the institution submits and holds the
                              award. Every NIH F and K award is here -- grants.gov
                              lists their eligible applicants as organizations
                              only. Practical consequence: you need eRA Commons,
                              a sponsored-programs office, and an INTERNAL
                              deadline that falls before the funder's.

  institution_then_appointed  The institution applies; individuals are selected
                              and appointed by that institution afterwards and
                              never apply to the funder at all. T32, K12, REU
                              Sites, CyberCorps SFS, CIRM Bridges. For a trainee
                              the action is not "apply" -- it is "find out whether
                              my department holds one, and ask the programme
                              director how appointments are made."

  institution_only            The award is to an organisation with no individual
                              beneficiary pathway.

  unspecified                 Not established. The default; nobody had asked.

This does not replace `submission_path`, which still records limited submission
and nomination-only routes. It answers a different question.
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VAULT = ROOT / "data" / "mechanisms.csv"

NEW_COLUMNS = ["applicant_of_record", "applicant_of_record_note"]
DEFAULTS = {"applicant_of_record": "unspecified", "applicant_of_record_note": ""}


def main(dry_run: bool = False) -> int:
    if not VAULT.exists():
        print(f"FAIL: {VAULT} not found", file=sys.stderr)
        return 1

    with VAULT.open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        fields = list(reader.fieldnames or [])
        rows = list(reader)

    already = [c for c in NEW_COLUMNS if c in fields]
    if len(already) == len(NEW_COLUMNS):
        print(f"already at 0.5.0 — {len(rows)} rows unchanged")
        return 0
    if already:
        print(f"FAIL: partial migration, {already} present", file=sys.stderr)
        return 1

    at = fields.index("submission_path") + 1
    new_fields = fields[:at] + NEW_COLUMNS + fields[at:]
    for r in rows:
        for c in NEW_COLUMNS:
            r[c] = DEFAULTS[c]

    print(f"rows            {len(rows)}")
    print(f"columns         {len(fields)} -> {len(new_fields)}")
    print(f"applicant       unspecified x {len(rows)} — populated only where sourced")

    if dry_run:
        print("dry run — nothing written")
        return 0

    tmp = VAULT.with_suffix(".csv.tmp")
    with tmp.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=new_fields, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    tmp.replace(VAULT)
    print(f"wrote           {VAULT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    sys.exit(main(ap.parse_args().dry_run))
