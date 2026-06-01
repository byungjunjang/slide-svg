#!/usr/bin/env python3
"""Render DESIGN.md skeleton from design-md.tpl.md + theme-active.json.

Output goes to `slide/templates/layouts/<theme.name>/DESIGN.md`. The rendered
file pre-fills token-driven sections (palette table, type scale, font chain,
spacing grid, voice anchors) and leaves `<!-- AGENT-FILL §N ... -->` markers
in place for the agent invoking /theme-init to author manually.

**Existing-file protection:** if the target DESIGN.md already exists,
this script *does NOT overwrite it* without --force. This protects the
hand-authored jangpm DESIGN.md (and any hand-curated preset DESIGN.md
the operator has refined past the skeleton).

Usage:
    python3 render_design_md.py
    python3 render_design_md.py --theme /path/to/theme-active.json
    python3 render_design_md.py --force        # overwrite an existing DESIGN.md
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _token_render import load_theme, render  # noqa: E402

THEME_INIT_ROOT = Path(__file__).resolve().parents[1]
SLIDE_ROOT = THEME_INIT_ROOT.parent / "slide"

DEFAULT_TPL = THEME_INIT_ROOT / "references" / "design-md.tpl.md"
DEFAULT_THEME = SLIDE_ROOT / "references" / "theme-active.json"
DEFAULT_OUT_BASE = SLIDE_ROOT / "templates" / "layouts"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--tpl", type=Path, default=DEFAULT_TPL)
    ap.add_argument("--theme", type=Path, default=DEFAULT_THEME)
    ap.add_argument(
        "--out",
        type=Path,
        default=None,
        help="explicit output path (overrides <out-base>/<theme.name>/DESIGN.md)",
    )
    ap.add_argument(
        "--out-base",
        type=Path,
        default=DEFAULT_OUT_BASE,
        help="parent directory; output path = <out-base>/<theme.name>/DESIGN.md",
    )
    ap.add_argument(
        "--force",
        action="store_true",
        help="overwrite the target DESIGN.md if it already exists",
    )
    args = ap.parse_args()

    if not args.tpl.exists():
        print(f"template not found: {args.tpl}", file=sys.stderr)
        return 2
    if not args.theme.exists():
        print(f"theme not found: {args.theme}", file=sys.stderr)
        return 2

    theme = load_theme(args.theme)
    theme_name = theme.get("name")
    if not theme_name:
        print("error: theme-active.json is missing 'name'", file=sys.stderr)
        return 2

    out_path = args.out if args.out is not None else (args.out_base / theme_name / "DESIGN.md")

    if out_path.exists() and not args.force:
        print(
            f"[render_design_md] {out_path} already exists — skipping.\n"
            f"  This preserves hand-authored content. Re-run with --force to overwrite.",
        )
        return 0

    tpl_text = args.tpl.read_text(encoding="utf-8")

    try:
        rendered = render(tpl_text, theme)
    except (KeyError, ValueError) as e:
        print(f"render error: {e}", file=sys.stderr)
        return 1

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(rendered, encoding="utf-8")
    print(f"wrote {out_path}")

    fill_markers = rendered.count("<!-- AGENT-FILL")
    if fill_markers:
        print(
            f"\n[render_design_md] {fill_markers} AGENT-FILL marker(s) remain.\n"
            f"  The agent must author each marker before /slide-plan can consume\n"
            f"  this preset's design vocabulary."
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
