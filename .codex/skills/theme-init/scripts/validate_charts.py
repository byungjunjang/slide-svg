#!/usr/bin/env python3
"""Single-accent stale-hex gate over the rendered chart templates.

The charts under `templates/charts/*.svg` are machine-generated from the
tokenized `_source/*.tpl.svg`, so they must be perfectly on-theme: the only
colors allowed are the active accent family + the theme neutrals. Anything else
— a leftover ppt-master hue, the theme's own status colors (a banned *second*
hue in a chart), a gradient def, or a drop-shadow filter — is a finding.

This enforces the single-accent invariant: "after a theme swap, charts render in the active accent
single-hue + stale-hex scan == 0." Wired into init_theme.py right after
render_charts, it fails the pipeline loudly if a swap ever produces off-theme
charts.

Usage:
    python3 validate_charts.py
    python3 validate_charts.py --theme /path/to/theme-active.json --charts-dir /path/to/charts
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Status lines use an em-dash; on a non-UTF-8 console (Windows cp949) that raises
# UnicodeEncodeError mid-print. Force UTF-8 for our own streams so a standalone
# run is as safe as the PYTHONUTF8-wrapped subprocess init_theme.py launches.
try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    sys.stderr.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except (AttributeError, ValueError):
    pass

SKILL_ROOT = Path(__file__).resolve().parents[2] / "slide"
DEFAULT_THEME_PATH = SKILL_ROOT / "references" / "theme-active.json"
DEFAULT_CHARTS_DIR = SKILL_ROOT / "templates" / "charts"

# A chart may use the accent family + theme neutrals only. The theme's status
# hues (positive / negative / warning) are deliberately excluded — using one in
# a chart is a second hue, which the single-accent rule forbids.
_ALLOWED_KEYS = {
    "accent", "accent-soft", "accent-ink",
    "bg", "surface", "surface-alt",
    "text", "text-secondary", "text-tertiary",
    "border", "border-strong",
}

_HEX_RE = re.compile(r"#[0-9A-Fa-f]{6}")
_GRADIENT_RE = re.compile(r"<(?:linear|radial)Gradient\b")
_FILTER_RE = re.compile(r"<filter\b|feGaussianBlur")


def allowed_hexes(theme: dict) -> set[str]:
    colors = theme.get("colors", {})
    return {
        v.upper()
        for k, v in colors.items()
        if k in _ALLOWED_KEYS and isinstance(v, str) and _HEX_RE.fullmatch(v)
    }


def validate_svg(name: str, text: str, allowed: set[str]) -> list[str]:
    findings: list[str] = []
    for hexv in sorted({h.upper() for h in _HEX_RE.findall(text)}):
        if hexv not in allowed:
            findings.append(f"{name}: off-theme hex {hexv} (single-accent: accent family + neutrals only)")
    if _GRADIENT_RE.search(text):
        findings.append(f"{name}: gradient def (banned — flat single-accent fills only)")
    if _FILTER_RE.search(text):
        findings.append(f"{name}: drop-shadow filter (banned)")
    return findings


def validate(charts_dir: Path, theme: dict) -> list[str]:
    allowed = allowed_hexes(theme)
    findings: list[str] = []
    for svg_path in sorted(charts_dir.glob("*.svg")):
        findings += validate_svg(svg_path.name, svg_path.read_text(encoding="utf-8"), allowed)
    return findings


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--theme", type=Path, default=DEFAULT_THEME_PATH,
                    help="path to theme-active.json (default: slide/references/theme-active.json)")
    ap.add_argument("--charts-dir", type=Path, default=DEFAULT_CHARTS_DIR,
                    help="dir of rendered chart *.svg (default: templates/charts)")
    args = ap.parse_args(argv)

    if not args.theme.exists():
        print(f"error: theme file not found: {args.theme}", file=sys.stderr)
        return 2
    if not args.charts_dir.is_dir():
        print(f"error: charts dir not found: {args.charts_dir}", file=sys.stderr)
        return 2

    theme = json.loads(args.theme.read_text(encoding="utf-8"))
    findings = validate(args.charts_dir, theme)

    if findings:
        print(f"[validate_charts] {len(findings)} finding(s):", file=sys.stderr)
        for f in findings:
            print(f"  {f}", file=sys.stderr)
        return 1

    print(f"[validate_charts] clean — all charts on single-accent theme palette")
    return 0


if __name__ == "__main__":
    sys.exit(main())
