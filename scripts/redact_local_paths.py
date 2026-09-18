#!/usr/bin/env python3
"""Strip absolute local filesystem paths out of harvested agent output.

    python scripts/redact_local_paths.py <dir-of-json>

Workflow agents that downloaded and extracted PDFs recorded where they put the
text, which means absolute paths carrying a Windows username, an AppData layout
and the session UUID. That is machine detail, not research, and this repo is
public. The fact survives ("extracted locally with pypdf"); the layout does not.

Operates on decoded JSON strings rather than raw file text, so Windows
backslashes are handled once instead of through several layers of escaping.

BE SURGICAL. An earlier version matched any `<letter>:<slash>` run and therefore
ate the `s:` in every `https://`, destroying the source URLs that are the whole
provenance layer. Only paths that actually contain a user directory are touched,
and a guard below refuses to run if the result would damage URLs.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

# Only real user-directory paths. `(?<![A-Za-z])` keeps the drive letter from
# matching the tail of a scheme like "https:".
WIN_USER = re.compile(
    r"(?<![A-Za-z])[A-Za-z]:[\\/]{1,2}Users[\\/]{1,2}[^\s\"'<>|,;)]*")
NIX_HOME = re.compile(r"/home/[A-Za-z0-9_.-]+(?:/[^\s\"'<>|,;)]*)?")
UUID = re.compile(
    r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b", re.I)

count = 0


def scrub(text: str) -> str:
    global count

    def repl(m: re.Match) -> str:
        global count
        count += 1
        return ("<local-scratchpad-file>"
                if re.search(r"scratchpad", m.group(0), re.I) else "<local-path>")

    out = WIN_USER.sub(repl, text)
    out = NIX_HOME.sub(repl, out)

    def urepl(_m: re.Match) -> str:
        global count
        count += 1
        return "<session-id>"

    return UUID.sub(urepl, out)


def walk(node):
    if isinstance(node, str):
        return scrub(node)
    if isinstance(node, list):
        return [walk(x) for x in node]
    if isinstance(node, dict):
        return {k: walk(v) for k, v in node.items()}
    return node


def main(d: Path) -> int:
    if not d.is_dir():
        print(f"FAIL: {d} is not a directory", file=sys.stderr)
        return 1

    for f in sorted(d.glob("*.json")):
        raw = f.read_text(encoding="utf-8")
        before_urls = raw.count("https://") + raw.count("http://")
        data = json.loads(raw)
        start = count
        cleaned = walk(data)
        out = json.dumps(cleaned, ensure_ascii=False, indent=1)
        after_urls = out.count("https://") + out.count("http://")
        # Negative control: redaction must never reduce the URL count.
        if after_urls < before_urls:
            print(f"REFUSED {f.name}: URL count {before_urls} -> {after_urls}; "
                  f"the pattern is eating links", file=sys.stderr)
            return 1
        f.write_text(out, encoding="utf-8")
        print(f"  {f.name:20s} {count - start:3d} redactions, "
              f"{after_urls} URLs intact")
    print(f"\n{count} total redactions")
    return 0


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1] if len(sys.argv) > 1 else ".")))
