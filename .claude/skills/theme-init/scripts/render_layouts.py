#!/usr/bin/env python3
"""Render theme-parametric layout templates into a concrete theme directory.

Reads `_source/*.tpl.svg` and a theme descriptor (`references/theme-active.json`),
substitutes every `{{TOKEN:<dotted.path>}}` placeholder with the resolved token
value, and writes the result to `templates/layouts/<theme.name>/*.svg`.

Content placeholders (e.g., `{{TITLE}}`, `{{PAGE_TITLE}}`) — any `{{...}}` that
does NOT start with `TOKEN:` — are left untouched so the Executor can fill them
per slide.

Usage:
    python3 render_layouts.py
    python3 render_layouts.py --theme /path/to/theme-active.json
    python3 render_layouts.py --source /path/to/_source --out /path/to/layouts
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[2] / "slide"
DEFAULT_THEME_PATH = SKILL_ROOT / "references" / "theme-active.json"
DEFAULT_SOURCE_DIR = SKILL_ROOT / "templates" / "layouts" / "_source"
DEFAULT_OUT_BASE   = SKILL_ROOT / "templates" / "layouts"

TOKEN_RE = re.compile(r"\{\{TOKEN:([a-zA-Z0-9_.\-]+)\}\}")


def resolve_path(theme: dict, dotted: str):
    """Walk a dotted path in the theme dict. Raises KeyError on miss."""
    node = theme
    for part in dotted.split("."):
        if isinstance(node, dict) and part in node:
            node = node[part]
        else:
            raise KeyError(f"Token path not found in theme: {dotted!r}")
    return node


def format_value(val) -> str:
    """Render a value as it should appear inside an SVG attribute.

    - Integers render without a trailing `.0`.
    - Floats render with minimal precision (strip trailing zeros).
    - Strings render verbatim (font-chain preserves its quotes).
    """
    if isinstance(val, bool):
        return "true" if val else "false"
    if isinstance(val, int):
        return str(val)
    if isinstance(val, float):
        if val.is_integer():
            return str(int(val))
        formatted = f"{val:.4f}".rstrip("0").rstrip(".")
        return formatted
    return str(val)


def render_template(tpl: str, theme: dict) -> tuple[str, list[str]]:
    """Return (rendered_svg, unresolved_paths_for_debug)."""
    missing: list[str] = []

    def sub(match: re.Match) -> str:
        path = match.group(1)
        try:
            value = resolve_path(theme, path)
        except KeyError:
            missing.append(path)
            return match.group(0)
        return format_value(value)

    return TOKEN_RE.sub(sub, tpl), missing


def render_directory(source_dir: Path, out_dir: Path, theme: dict) -> dict:
    """Render every `*.tpl.svg` under source_dir into out_dir as `*.svg`."""
    out_dir.mkdir(parents=True, exist_ok=True)
    results = {"rendered": [], "missing_tokens": {}}

    for tpl_path in sorted(source_dir.glob("*.tpl.svg")):
        out_name = tpl_path.name.replace(".tpl.svg", ".svg")
        out_path = out_dir / out_name

        tpl_text = tpl_path.read_text(encoding="utf-8")
        rendered, missing = render_template(tpl_text, theme)
        out_path.write_text(rendered, encoding="utf-8")

        results["rendered"].append(str(out_path))
        if missing:
            results["missing_tokens"][tpl_path.name] = missing

    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--theme", type=Path, default=DEFAULT_THEME_PATH,
                        help="Path to theme-active.json (default: slide/references/theme-active.json)")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE_DIR,
                        help="Path to templates/_source/ directory")
    parser.add_argument("--out-base", type=Path, default=DEFAULT_OUT_BASE,
                        help="Parent directory for the rendered theme folder (output path = <out-base>/<theme.name>)")
    parser.add_argument("--out", type=Path, default=None,
                        help="Override output directory (ignores <out-base>/<theme.name>)")
    parser.add_argument("--dry-run", action="store_true", help="Print what would be rendered; do not write.")
    args = parser.parse_args(argv)

    if not args.theme.exists():
        print(f"error: theme file not found: {args.theme}", file=sys.stderr)
        return 2
    if not args.source.exists():
        print(f"error: source directory not found: {args.source}", file=sys.stderr)
        return 2

    theme = json.loads(args.theme.read_text(encoding="utf-8"))
    theme_name = theme.get("name")
    if not theme_name:
        print("error: theme-active.json is missing 'name'", file=sys.stderr)
        return 2

    out_dir = args.out if args.out is not None else (args.out_base / theme_name)

    if args.dry_run:
        print(f"[dry-run] theme={theme_name} source={args.source} out={out_dir}")
        for tpl_path in sorted(args.source.glob("*.tpl.svg")):
            print(f"  would render: {tpl_path.name} -> {out_dir / tpl_path.name.replace('.tpl.svg', '.svg')}")
        return 0

    results = render_directory(args.source, out_dir, theme)

    print(f"Rendered theme '{theme_name}' into {out_dir}")
    for path in results["rendered"]:
        print(f"  {path}")
    if results["missing_tokens"]:
        print("warning: some {{TOKEN:...}} placeholders had no value in the theme:", file=sys.stderr)
        for filename, paths in results["missing_tokens"].items():
            for path in paths:
                print(f"  {filename}: {path}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
