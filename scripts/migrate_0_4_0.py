#!/usr/bin/env python3
"""Schema 0.3.0 -> 0.4.0: what a submission actually consists of.

Adds four columns. Additive and idempotent -- re-running is a no-op.

    python scripts/migrate_0_4_0.py [--dry-run]

Why now: `docs/SCOPE.md` measured the gap. One row in 219 mentioned page limits
and one mentioned resubmission, because no column existed to hold either. Both
are things an applicant must know before they start, and resubmission is the
single most actionable fact for anyone who has been scored and not funded.

`resubmission_allowed` starts at `unspecified` on every row for the same reason
`status` started at `unknown` (D-008): nobody had asked the question, and any
other default would be a guess. `no` is a claim about the funder and must be
sourced like any other.
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VAULT = ROOT / "data" / "mechanisms.csv"

# Inserted after `application_cadence`, next to the other how-to-apply fields.
NEW_COLUMNS = [
    "submission_requirements",   # components, page/word limits, formats, letters
    "resubmission_allowed",      # yes | no | limited | unspecified
    "resubmission_policy",       # how many, what must change, what is barred
    "submission_checked",        # ISO date these three were last verified
]

DEFAULTS = {
    "submission_requirements": "",
    "resubmission_allowed": "unspecified",
    "resubmission_policy": "",
    "submission_checked": "",
}


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
        print(f"already at 0.4.0 — {len(rows)} rows unchanged")
        return 0
    if already:
        print(f"FAIL: partial migration, {already} already present", file=sys.stderr)
        return 1

    at = fields.index("application_cadence") + 1
    new_fields = fields[:at] + NEW_COLUMNS + fields[at:]

    for r in rows:
        for c in NEW_COLUMNS:
            r[c] = DEFAULTS[c]

    print(f"rows            {len(rows)}")
    print(f"columns         {len(fields)} -> {len(new_fields)}")
    print(f"resubmission    unspecified x {len(rows)} (no row claims a policy without a source)")

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
