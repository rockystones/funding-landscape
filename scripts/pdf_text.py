#!/usr/bin/env python3
"""Extract readable text from a PDF, standard library only.

    python scripts/pdf_text.py <file.pdf> [max_chars] [--grep WORD]

Several rows in this corpus cite PDFs (CDMRP programme announcements, state RFAs,
AFOSR notices) and the fetch tool returns them as raw bytes. This pulls the text
operators out of the content streams so a status check can quote the document
rather than guess from its filename.

It is deliberately small: it handles Flate-compressed streams and the common text
operators, which covers every PDF met so far. It does not do fonts, encodings
beyond Latin-1, or encrypted files -- when it returns nothing useful, say so and
leave the row unknown rather than inferring.
"""
from __future__ import annotations

import argparse
import re
import sys
import zlib
from pathlib import Path

STREAM = re.compile(rb"stream\r?\n(.*?)endstream", re.S)
# A PDF string literal: parenthesised, with backslash escapes.
STRING = re.compile(rb"\((?:\\.|[^()\\])*\)", re.S)
ESCAPE = re.compile(rb"\\([()\\])")
# Kerning gaps inside TJ arrays large enough to mean a space.
TJ_GAP = re.compile(rb"\)\s*(-?\d{3,})\s*\(")


def extract(raw: bytes) -> str:
    chunks: list[str] = []
    for m in STREAM.finditer(raw):
        body = m.group(1)
        try:
            body = zlib.decompress(body)
        except zlib.error:
            continue  # not Flate-compressed, or an image stream
        body = TJ_GAP.sub(rb") ( ", body)
        for s in STRING.finditer(body):
            text = ESCAPE.sub(rb"\1", s.group(0)[1:-1])
            text = text.replace(rb"\n", b" ").replace(rb"\r", b" ")
            chunks.append(text.decode("latin-1", errors="replace"))
    out = "".join(chunks)
    out = out.replace("\x00", "")
    return re.sub(r"[ \t]{2,}", " ", out).strip()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("pdf", type=Path)
    ap.add_argument("max_chars", nargs="?", type=int, default=3000)
    ap.add_argument("--grep", help="print only windows around this word")
    a = ap.parse_args()

    if not a.pdf.exists():
        print(f"FAIL: {a.pdf} not found", file=sys.stderr)
        return 1

    text = extract(a.pdf.read_bytes())
    if not text:
        print("no extractable text (encrypted, image-only, or unsupported filter)",
              file=sys.stderr)
        return 2

    if a.grep:
        hits = 0
        for m in re.finditer(re.escape(a.grep), text, re.I):
            lo, hi = max(0, m.start() - 110), m.end() + 110
            print("..." + text[lo:hi].replace("\n", " ") + "...")
            hits += 1
            if hits >= 12:
                break
        if not hits:
            print(f"(no occurrence of {a.grep!r} in {len(text)} chars)")
    else:
        print(text[:a.max_chars])
    return 0


if __name__ == "__main__":
    sys.exit(main())
