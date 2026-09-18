#!/usr/bin/env python3
"""Apply a verified status-backfill file to the vault.

    python scripts/apply_status.py research/<session>/verify/status-updates.json [--dry-run]

Every change is driven by a file that carries its own evidence, so the diff on the
vault and the justification for it live together and can be reviewed as a pair.
Re-running is a no-op: a row already carrying the target values is left alone.

The script refuses to write a status without `status_evidence` and
`status_source`, mirroring the build gate — the failure mode this phase guards
against is a status asserted from a dead link.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VAULT = ROOT / "data" / "mechanisms.csv"


class Ambiguous(Exception):
    """More than one row matched. Never guess which one was meant."""


def find_row(rows: list[dict], spec: dict) -> dict | None:
    """Locate the one row a spec addresses, or raise if the spec is ambiguous.

    The vault's dedup key is (funder, program_name), not program_name alone:
    'Career Development Award' and 'Postdoctoral Fellowship' each exist twice,
    once for the American Heart Association and once for Breakthrough T1D. A
    matcher that returned the first hit would silently write a verified status
    onto the wrong funder's row, so add `funder` to the spec to disambiguate.
    """
    name, how = spec["program_name"], spec.get("match", "exact")
    funder = spec.get("funder")
    hits = []
    for r in rows:
        pn = r["program_name"].strip()
        if not ((how == "exact" and pn == name) or
                (how == "startswith" and pn.startswith(name)) or
                (how == "contains" and name in pn)):
            continue
        if funder and funder.lower() not in r["funder"].lower():
            continue
        hits.append(r)

    if len(hits) > 1:
        raise Ambiguous(
            f"{name!r} matches {len(hits)} rows "
            f"({', '.join(h['funder'][:30] for h in hits)}) — add a 'funder' key")
    return hits[0] if hits else None


def main(path: Path, dry_run: bool) -> int:
    if not path.exists():
        print(f"FAIL: {path} not found", file=sys.stderr)
        return 1

    payload = json.loads(path.read_text(encoding="utf-8"))
    checked = payload["checked"]

    with VAULT.open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        fields = list(reader.fieldnames or [])
        rows = list(reader)

    changed = added = skipped = 0

    for spec in payload.get("updates", []):
        try:
            row = find_row(rows, spec)
        except Ambiguous as e:
            print(f"  AMBIG   {e}", file=sys.stderr)
            return 1
        if row is None:
            print(f"  MISS    no row matches {spec['program_name']!r}", file=sys.stderr)
            return 1

        status = spec.get("status")
        if status and status != "unknown":
            if not (spec.get("status_evidence") and spec.get("status_source")):
                print(f"  REFUSE  {spec['program_name'][:44]}: status without evidence",
                      file=sys.stderr)
                return 1

        before = dict(row)
        for key, value in spec.items():
            if key in ("program_name", "match", "funder", "notes_append"):
                continue
            if key not in fields:
                print(f"  FAIL    unknown column {key!r}", file=sys.stderr)
                return 1
            row[key] = value
        if status and status != "unknown":
            row["status_checked"] = checked

        extra = spec.get("notes_append")
        if extra and extra not in (row.get("notes") or ""):
            row["notes"] = (row["notes"] + " " if row.get("notes") else "") + extra

        if row == before:
            skipped += 1
        else:
            changed += 1
            moved = [k for k in row if row[k] != before.get(k)]
            print(f"  update  {row['program_name'][:46]:48s} "
                  f"status={row['status']:10s} [{', '.join(moved[:4])}]")

    for spec in payload.get("new_rows", []):
        try:
            clash = find_row(rows, {"program_name": spec["program_name"],
                                    "funder": spec.get("funder")})
        except Ambiguous as e:
            print(f"  AMBIG   {e}", file=sys.stderr)
            return 1
        if clash:
            skipped += 1
            continue
        missing = [f for f in fields if f not in spec]
        if missing:
            print(f"  FAIL    new row {spec['program_name'][:40]!r} missing {missing}",
                  file=sys.stderr)
            return 1
        rows.append({f: spec[f] for f in fields})
        added += 1
        print(f"  add     {spec['program_name'][:46]:48s} status={spec['status']}")

    print(f"\n{changed} updated · {added} added · {skipped} already current "
          f"· {len(rows)} rows total")

    if dry_run:
        print("dry run — nothing written")
        return 0

    tmp = VAULT.with_suffix(".csv.tmp")
    with tmp.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    tmp.replace(VAULT)
    print(f"wrote {VAULT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("updates", type=Path)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    sys.exit(main(a.updates, a.dry_run))
