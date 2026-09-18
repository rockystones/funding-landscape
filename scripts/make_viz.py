#!/usr/bin/env python3
"""Inline the explorer payload into the template to produce viz/index.html.

The page ships as one self-contained file so it renders at rest with no network
round-trip -- which is what a thumbnail, a shared link and a cold open all get.

    python scripts/build.py --viz && python scripts/make_viz.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "viz" / "index.template.html"
PAYLOAD = ROOT / "dist" / "viz-data.json"
OUT = ROOT / "viz" / "index.html"
TOKEN = "/*__DATA__*/"


def main() -> int:
    for f in (TEMPLATE, PAYLOAD):
        if not f.exists():
            print(f"FAIL: missing {f.relative_to(ROOT)}", file=sys.stderr)
            return 1

    html = TEMPLATE.read_text(encoding="utf-8")
    if TOKEN not in html:
        print(f"FAIL: {TOKEN} not found in template", file=sys.stderr)
        return 1

    data = PAYLOAD.read_text(encoding="utf-8")
    json.loads(data)  # fail loudly here rather than silently in the browser
    # The payload sits inside <script type="application/json">, so the only
    # sequence that can break out of it is a literal </script>.
    data = data.replace("</", r"<\/")

    OUT.write_text(html.replace(TOKEN, data), encoding="utf-8")
    print(f"wrote viz/index.html ({OUT.stat().st_size // 1024} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
