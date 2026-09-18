#!/usr/bin/env python3
"""Schema 0.2.0 -> 0.3.0: the durability layer.

Adds nine columns to the vault. Additive and idempotent -- re-running is a no-op.

    python scripts/migrate_0_3_0.py [--dry-run]

Why these defaults:

  `status` starts at `unknown` on every row, including the 91 federal ones. The
  v0.1 run never asked whether a programme still exists, so any other value would
  be a guess, and the roadmap's failure mode for this phase is precisely that a
  `terminated` claim gets made without a source. `unknown` is the only honest
  starting value; rows move off it one at a time, each with evidence.

  The four `*_checked` dates inherit `checked_date` (2026-07-18). That is not a
  guess: the v0.1 run did verify those fields on that date against the funder's
  own page. Splitting one row-level stamp into four field-level ones loses no
  information and lets re-verification target the fields that actually drift.
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VAULT = ROOT / "data" / "mechanisms.csv"

# Inserted after `checked_date` so provenance columns stay together.
NEW_COLUMNS = [
    "status",                  # active | paused | terminated | unknown
    "status_valid_to",         # ISO date the programme stopped, if known
    "status_evidence",         # what the source actually said
    "status_source",           # URL backing the status claim
    "status_checked",          # ISO date the status question was asked
    "award_checked",           # per-field provenance for the four fields that
    "eligibility_checked",     # drift fastest, split out of checked_date so a
    "identity_checked",        # re-check can target one field instead of a row
    "review_criteria_checked",
]

INHERIT_CHECKED_DATE = {"award_checked", "eligibility_checked",
                        "identity_checked", "review_criteria_checked"}


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
        print(f"already at 0.3.0 — {len(rows)} rows unchanged")
        return 0
    if already:
        print(f"FAIL: partial migration, {already} already present", file=sys.stderr)
        return 1

    at = fields.index("checked_date") + 1
    new_fields = fields[:at] + NEW_COLUMNS + fields[at:]

    for r in rows:
        for c in NEW_COLUMNS:
            r[c] = r["checked_date"] if c in INHERIT_CHECKED_DATE else ""
        r["status"] = "unknown"

    print(f"rows            {len(rows)}")
    print(f"columns         {len(fields)} -> {len(new_fields)}")
    print(f"status          unknown x {len(rows)} (no row claims a status without evidence)")
    print(f"field dates     inherited from checked_date for "
          f"{len(INHERIT_CHECKED_DATE)} fields")

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
