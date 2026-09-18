#!/usr/bin/env python3
"""Harvest a Workflow run's agent results straight from its journal.

    python scripts/harvest_workflow.py <journal.jsonl> <out_dir>

A workflow's return value only reaches the session that launched it, and a long
run can outlive the context that started it. The journal on disk is the durable
record: every agent's `started` entry carries its label and phase, and its
`result` entry carries what the agent actually returned. Joining the two on
agentId reconstructs the whole run without depending on the return value.

Writes one JSON file per phase plus a manifest, so the research is committable
the moment it exists rather than when the orchestrator happens to finish.
"""
from __future__ import annotations

import io
import json
import sys
from collections import defaultdict
from pathlib import Path


def main(journal: Path, out_dir: Path) -> int:
    if not journal.exists():
        print(f"FAIL: {journal} not found", file=sys.stderr)
        return 1

    meta: dict[str, dict] = {}
    results: dict[str, object] = {}
    failed: list[str] = []

    with io.open(journal, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            t, aid = d.get("type"), d.get("agentId")
            if not aid:
                continue
            if t == "started":
                meta[aid] = {"label": d.get("label"), "phase": d.get("phase")}
            elif t == "result":
                results[aid] = d.get("result")
            elif t == "failed":
                failed.append(aid)

    by_phase: dict[str, list] = defaultdict(list)
    empty = 0
    for aid, value in results.items():
        m = meta.get(aid, {})
        if value in (None, "", {}, []):
            empty += 1
        by_phase[m.get("phase") or "unphased"].append(
            {"agent_id": aid, "label": m.get("label"), "result": value})

    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "journal": journal.name,
        "agents_started": len(meta),
        "agents_with_results": len(results),
        "agents_failed": len(failed),
        "empty_results": empty,
        "phases": {},
    }
    for phase, rows in sorted(by_phase.items()):
        # Stable order so re-harvesting a longer run produces a clean diff.
        rows.sort(key=lambda r: (r["label"] or "", r["agent_id"]))
        slug = phase.lower().replace(" ", "-")
        dest = out_dir / f"{slug}.json"
        dest.write_text(json.dumps(rows, ensure_ascii=False, indent=1),
                        encoding="utf-8")
        manifest["phases"][phase] = {"agents": len(rows),
                                     "file": dest.name,
                                     "kb": dest.stat().st_size // 1024}
        print(f"  {phase:14s} {len(rows):4d} agents -> {dest.name} "
              f"({dest.stat().st_size // 1024} KB)")

    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nstarted {len(meta)} · results {len(results)} · failed {len(failed)} "
          f"· empty {empty}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__, file=sys.stderr)
        sys.exit(2)
    sys.exit(main(Path(sys.argv[1]), Path(sys.argv[2])))
