#!/usr/bin/env python3
"""Guarded copy polish for the visible text of `svg_output/*.svg`.

- `extract` writes every text line per page to a JSON file — the input for a
  polish pass that the main agent writes as an edits file.
- `apply` replaces a line only when the new text keeps the same numbers,
  number+unit pairs and Latin words (names, acronyms) as the old text, and
  only when the old text is exactly one text node on that page (a line that
  spans styled runs is edited by hand). Everything else is rejected and
  listed. Files keep their bytes — line endings included — apart from the
  edit. Results go to `<project>/copy_polish.json`.

Usage:
    svg_copy.py extract <project_path> -o <copy.json>
    svg_copy.py apply <project_path> <edits.json>

Edits file: a JSON list of {"page": "07", "old": "<exact line>", "new": "<line>"}.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from xml.sax.saxutils import escape

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svg_quality_checker import parse_text_elements  # noqa: E402

_NUMBER_RE = re.compile(r"\d+(?:[.,]\d+)*")
_UNIT_RE = re.compile(r"\d+(?:[.,]\d+)*\s*(%p|%|pp|bp|조|억|만|천|원|배|x|×|명|개|건|년|월|일|분기|대)")
_LATIN_RE = re.compile(r"[A-Za-z][A-Za-z0-9&+\-]*")


def _pages(project: Path) -> dict[str, Path]:
    return {f.stem.split("_")[0]: f for f in sorted((project / "svg_output").glob("*.svg"))}


def _protected(text: str) -> tuple[Counter, Counter, Counter]:
    return (Counter(_NUMBER_RE.findall(text)),
            Counter(u.replace(" ", "") for u in _UNIT_RE.findall(text)),
            Counter(_LATIN_RE.findall(text)))


def _reject_reason(old: str, new: str) -> str | None:
    labels = ("numbers", "number+unit pairs", "Latin words")
    for label, before, after in zip(labels, _protected(old), _protected(new)):
        if before != after:
            return f"changes {label}: {sorted(before.elements())} -> {sorted(after.elements())}"
    return None


def cmd_extract(project: Path, out: Path) -> int:
    pages = {page: {"file": f.name,
                    "lines": [line[5] for line in parse_text_elements(
                        f.read_bytes().decode("utf-8"))]}
             for page, f in _pages(project).items()}
    out.write_text(json.dumps(pages, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Wrote {sum(len(p['lines']) for p in pages.values())} lines "
          f"from {len(pages)} pages to {out}")
    return 0


def cmd_apply(project: Path, edits_path: Path) -> int:
    edits = json.loads(edits_path.read_text(encoding="utf-8-sig"))
    files = _pages(project)
    applied, rejected = [], []
    for edit in edits:
        page = str(edit.get("page", "")).zfill(2)
        old, new = str(edit.get("old", "")), str(edit.get("new", ""))
        reason = None if page in files else f"no page {page}"
        reason = reason or _reject_reason(old, new)
        if reason is None:
            raw = files[page].read_bytes().decode("utf-8")  # bytes keep the line endings
            node = re.compile(r">(\s*)" + re.escape(escape(old)) + r"(\s*)<")
            hits = len(node.findall(raw))
            if hits != 1:
                reason = ("old text is not one exact text node on the page "
                          f"(found {hits}); edit by hand if it spans styled runs")
            else:
                raw = node.sub(lambda m: f">{m.group(1)}{escape(new)}{m.group(2)}<", raw)
                files[page].write_bytes(raw.encode("utf-8"))
        item = {**edit, "page": page}
        if reason:
            rejected.append({**item, "reason": reason})
        else:
            applied.append(item)
    report = project / "copy_polish.json"
    report.write_text(json.dumps({"applied": applied, "rejected": rejected},
                                 ensure_ascii=False, indent=1), encoding="utf-8")
    for item in rejected:
        print(f"[REJECTED] {item['page']}: {item['old']!r} — {item['reason']}")
    print(f"\nCopy polish: {len(applied)} applied, {len(rejected)} rejected; report {report}")
    for page in sorted({item["page"] for item in applied}):
        print(f"Re-check: svg_quality_checker.py {files[page]} --all-warnings")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Guarded copy polish for svg_output/.")
    sub = parser.add_subparsers(dest="command", required=True)
    p_extract = sub.add_parser("extract", help="write every text line per page to JSON")
    p_extract.add_argument("project")
    p_extract.add_argument("-o", "--output", required=True)
    p_apply = sub.add_parser("apply", help="apply edits that keep numbers, units and Latin words")
    p_apply.add_argument("project")
    p_apply.add_argument("edits")
    args = parser.parse_args(argv)
    project = Path(args.project)
    if not (project / "svg_output").is_dir():
        print(f"[ERROR] no svg_output/ under {project}", file=sys.stderr)
        return 1
    if args.command == "extract":
        return cmd_extract(project, Path(args.output))
    return cmd_apply(project, Path(args.edits))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
