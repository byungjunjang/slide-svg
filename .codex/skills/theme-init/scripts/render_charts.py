#!/usr/bin/env python3
"""Render the tokenized chart sources into themed chart templates.

Reads `templates/charts/_source/*.tpl.svg` (the single-accent, token-driven
sources produced once by tokenize_charts.py) and substitutes every
`{{TOKEN:<dotted.path>}}` with the active theme's value, writing the result to
`templates/charts/*.svg`. Re-running after a `/theme-init` swap re-colors every
chart to the new active accent — which is the whole point: charts are no longer
frozen to the upstream ppt-master palette.

Token substitution reuses render_layouts' engine (same `{{TOKEN:...}}` grammar
and value formatting as the layout shells), so chart rendering and shell
rendering can never drift apart.

Usage:
    python3 render_charts.py
    python3 render_charts.py --theme /path/to/theme-active.json
    python3 render_charts.py --source /path/to/_source --out /path/to/charts
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Parity with validate_charts.py / init_theme.py: force UTF-8 so a standalone run
# on a non-UTF-8 console (Windows cp949) can't crash on a non-ASCII status line.
try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    sys.stderr.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except (AttributeError, ValueError):
    pass

import render_layouts

SKILL_ROOT = Path(__file__).resolve().parents[2] / "slide"
DEFAULT_THEME_PATH = SKILL_ROOT / "references" / "theme-active.json"
DEFAULT_CHARTS_DIR = SKILL_ROOT / "templates" / "charts"
DEFAULT_SOURCE_DIR = DEFAULT_CHARTS_DIR / "_source"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--theme", type=Path, default=DEFAULT_THEME_PATH,
                    help="path to theme-active.json (default: slide/references/theme-active.json)")
    ap.add_argument("--source", type=Path, default=DEFAULT_SOURCE_DIR,
                    help="dir of tokenized *.tpl.svg sources (default: templates/charts/_source)")
    ap.add_argument("--out", type=Path, default=DEFAULT_CHARTS_DIR,
                    help="dir to write themed *.svg (default: templates/charts)")
    ap.add_argument("--dry-run", action="store_true",
                    help="list what would be rendered; do not write")
    args = ap.parse_args(argv)

    if not args.theme.exists():
        print(f"error: theme file not found: {args.theme}", file=sys.stderr)
        return 2
    if not args.source.is_dir():
        print(f"error: chart source dir not found: {args.source}", file=sys.stderr)
        return 2

    theme = json.loads(args.theme.read_text(encoding="utf-8"))

    sources = sorted(args.source.glob("*.tpl.svg"))
    if args.dry_run:
        print(f"[dry-run] {len(sources)} chart(s) {args.source} -> {args.out}")
        for p in sources:
            print(f"  would render: {args.out / p.name.replace('.tpl.svg', '.svg')}")
        return 0

    results = render_layouts.render_directory(args.source, args.out, theme)
    print(f"rendered {len(results['rendered'])} chart(s) -> {args.out}")
    if results["missing_tokens"]:
        print("warning: unresolved {{TOKEN:...}} placeholders:", file=sys.stderr)
        for filename, paths in results["missing_tokens"].items():
            for path in paths:
                print(f"  {filename}: {path}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
