#!/usr/bin/env python3
"""Print the next batch of rows whose status is still unknown.

    python scripts/next_batch.py [N] [--category federal_research] [--guidance]

Stateless: it reads the vault, so whatever has already been verified drops out
on its own. Enumerated rows come first because a `guidance` row describes a class
of funding rather than a named programme, and "does it still exist" does not mean
the same thing for one.
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VAULT = ROOT / "data" / "mechanisms.csv"

# Federal money moved most in 2025-26, so it is verified first.
CATEGORY_ORDER = [
    "federal_research", "defense_security", "mission_applied", "state_regional",
    "private_foundation", "disease_advocacy", "professional_society",
    "international_mobility", "industry", "institutional",
]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("n", nargs="?", type=int, default=8)
    ap.add_argument("--category")
    ap.add_argument("--guidance", action="store_true",
                    help="list guidance rows instead of enumerated ones")
    a = ap.parse_args()

    with VAULT.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))

    pool = [r for r in rows if r["status"].strip() == "unknown"]
    pool = [r for r in pool
            if (r["coverage_type"] == "guidance") == a.guidance]
    if a.category:
        pool = [r for r in pool if r["funder_category"] == a.category]
    pool.sort(key=lambda r: (CATEGORY_ORDER.index(r["funder_category"])
                             if r["funder_category"] in CATEGORY_ORDER else 99,
                             r["funder"], r["program_name"]))

    remaining = len(pool)
    for r in pool[:a.n]:
        print(f"{r['program_name']}\t{r['source_url']}")
    print(f"\n# {min(a.n, remaining)} shown · {remaining} unknown left in this slice",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
