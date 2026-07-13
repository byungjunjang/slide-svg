#!/usr/bin/env python3
"""render_chart.py — data → slide-ready SVG chart, styled by slide-svg tokens.

Usage:
  python3 .claude/skills/chart-design/scripts/render_chart.py spec.json -o chart.svg
  python3 ... spec.json -o chart.svg --standalone     # preview with bg padding
  python3 ... spec.json --validate-only               # judgment gates + spec check
  python3 ... --list-types
  echo '{...}' | python3 ... - -o chart.svg           # spec on stdin

Output (default): a <g id="…" data-chart-type="…"> fragment sized to
spec.width × spec.height — paste into a 1280×720 slide SVG and position with
--pos X,Y (adds a translate) or your own transform.

All colors, fonts, radii, and strokes come from the ACTIVE slide-svg theme
(slide/references/theme-active.json). There are no built-in style defaults:
a missing/invalid theme is a hard error by design.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from chartlib.renderers import RENDERERS, ChartJudgmentError, SpecError, render
from chartlib.svgutil import wrap_fragment, wrap_standalone
from chartlib.tokens import TokenResolutionError, resolve_style


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("spec", nargs="?", help="path to spec JSON, or '-' for stdin")
    p.add_argument("-o", "--output", help="output SVG path (default: stdout)")
    p.add_argument("--standalone", action="store_true",
                   help="wrap in a full <svg> document with theme bg (preview)")
    p.add_argument("--pos", metavar="X,Y",
                   help="translate the fragment to slide coordinates")
    p.add_argument("--theme", help="override theme JSON path (testing only)")
    p.add_argument("--id", dest="gid", help="fragment group id "
                   "(default: chart_<type>)")
    p.add_argument("--validate-only", action="store_true",
                   help="run spec + judgment checks without writing output")
    p.add_argument("--list-types", action="store_true")
    args = p.parse_args(argv)

    if args.list_types:
        for name in sorted(RENDERERS):
            print(name)
        return 0
    if not args.spec:
        p.error("spec is required (path or '-')")

    try:
        raw = (sys.stdin.read() if args.spec == "-"
               else Path(args.spec).read_text(encoding="utf-8"))
        spec = json.loads(raw)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Error: cannot read spec: {exc}", file=sys.stderr)
        return 2

    try:
        style = resolve_style(args.theme)
        inner = render(spec, style)
    except TokenResolutionError as exc:
        print(f"TokenResolutionError: {exc}", file=sys.stderr)
        return 3
    except ChartJudgmentError as exc:
        print(f"ChartJudgmentError [{spec.get('type')}]: {exc}", file=sys.stderr)
        return 4
    except SpecError as exc:
        print(f"SpecError [{spec.get('type')}]: {exc}", file=sys.stderr)
        return 2

    if args.validate_only:
        print(f"OK: {spec.get('type')} spec valid "
              f"(theme: {style.theme_name} @ {style.source_path})")
        return 0

    x = y = 0.0
    if args.pos:
        try:
            x, y = (float(v) for v in args.pos.split(","))
        except ValueError:
            print("Error: --pos expects X,Y numbers", file=sys.stderr)
            return 2
    gid = args.gid or f"chart_{spec.get('type')}"
    out = wrap_fragment(gid, str(spec.get("type")), inner, x, y)
    if args.standalone:
        out = wrap_standalone(style, out,
                              float(spec.get("width", 720)),
                              float(spec.get("height", 420)))

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(out + "\n", encoding="utf-8")
        print(f"Wrote {args.output}")
    else:
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
