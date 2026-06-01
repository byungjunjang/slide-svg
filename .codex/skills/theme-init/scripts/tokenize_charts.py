#!/usr/bin/env python3
"""Deterministic rainbow-chart -> single-accent tokenized-template transform.

The pure transform `normalize_chart_svg` collapses an upstream ppt-master chart
(multi-hue palette, gradients, drop-shadow filters) into a `.tpl.svg` body whose
only colors are `{{TOKEN:colors.*}}` placeholders + a single-accent opacity ramp.

As a CLI this is a one-shot codegen: it reads every `templates/charts/*.svg` and
writes `templates/charts/_source/*.tpl.svg`. Those `_source` templates become the
new source of truth — `render_charts.py` renders them back to themed `*.svg` on
every /theme-init, so a theme swap re-colors the charts to the active accent.

Usage:
    python3 tokenize_charts.py                 # convert the live charts dir
    python3 tokenize_charts.py --dry-run
    python3 tokenize_charts.py --charts-dir /path/to/charts
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[2] / "slide"
DEFAULT_CHARTS_DIR = SKILL_ROOT / "templates" / "charts"

ACCENT = "{{TOKEN:colors.accent}}"

# A color counts as a brand/series HUE when its HSL saturation clears this bar.
# Saturation (not raw RGB span) is used so dark slates like #2C3E50 — which span
# 36 in RGB but read as near-neutral — classify as neutrals, while pale tints and
# vivid series colors classify as chromatic.
_SAT_THRESHOLD = 0.30


def _rgb(hex_str: str) -> tuple[int, int, int]:
    h = hex_str.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _saturation(hex_str: str) -> float:
    r, g, b = (c / 255 for c in _rgb(hex_str))
    mx, mn = max(r, g, b), min(r, g, b)
    if mx == mn:
        return 0.0
    l = (mx + mn) / 2
    denom = 1 - abs(2 * l - 1)
    return (mx - mn) / denom if denom else 0.0


def _lightness(hex_str: str) -> float:
    r, g, b = (c / 255 for c in _rgb(hex_str))
    return (max(r, g, b) + min(r, g, b)) / 2


def _is_chromatic(hex_str: str) -> bool:
    return _saturation(hex_str) >= _SAT_THRESHOLD


def _neutral_token(hex_str: str) -> str:
    """Map a near-neutral gray to a theme neutral token by luminance bucket."""
    l = _lightness(hex_str)
    if l >= 0.95:
        return "{{TOKEN:colors.surface}}"
    if l >= 0.70:
        return "{{TOKEN:colors.border}}"
    if l >= 0.36:
        return "{{TOKEN:colors.text-secondary}}"
    return "{{TOKEN:colors.text}}"


# Series ramp: 1st chromatic hue = full accent (no opacity attr), then dimmed
# tiers. A 5th+ distinct hue floors at the last tier — a single-accent deck never
# needs more than four distinguishable series weights.
_TIERS: list[str | None] = [None, "0.6", "0.4", "0.25"]

_COLOR_ATTR_RE = re.compile(r'\b(fill|stroke)="(#[0-9A-Fa-f]{6})"')

# Gradient / drop-shadow stripping. Charts inherit ppt-master gradients and
# feGaussianBlur shadows — both banned under the single-accent, flat visual
# language. We flatten a gradient to its base (first) stop hue, then route that
# hue through the same accent ramp as solid fills.
_GRADIENT_BLOCK_RE = re.compile(r"<(linear|radial)Gradient\b.*?</\1Gradient>", re.DOTALL)
_FILTER_BLOCK_RE = re.compile(r"<filter\b.*?</filter>", re.DOTALL)
_FILTER_ATTR_RE = re.compile(r'\s+filter="[^"]*"')
_GRAD_DEF_RE = re.compile(
    r'<(?:linear|radial)Gradient\b[^>]*\bid="([^"]+)"(.*?)</(?:linear|radial)Gradient>',
    re.DOTALL)
_STOP_COLOR_RE = re.compile(
    r'stop-color:\s*(#[0-9A-Fa-f]{6})|stop-color="(#[0-9A-Fa-f]{6})"')
_URL_REF_RE = re.compile(r'\b(fill|stroke)="url\(#([^)]+)\)"')
# Upstream charts carry Chinese demo annotations that name the old palette
# (e.g. "蓝色 #2196F3"); strip every comment so no stale hex survives in text.
_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)


def _gradient_base_colors(svg_text: str) -> dict[str, str]:
    """Map each gradient id to its base (first) stop color, uppercased."""
    bases: dict[str, str] = {}
    for m in _GRAD_DEF_RE.finditer(svg_text):
        gid, body = m.group(1), m.group(2)
        stop = _STOP_COLOR_RE.search(body)
        if stop:
            bases[gid] = (stop.group(1) or stop.group(2)).upper()
    return bases


def _flatten_defs(svg_text: str) -> str:
    """Strip gradient + filter defs and resolve fill/stroke url() refs to the
    gradient's base hue, so the downstream color pass sees only solid hexes."""
    bases = _gradient_base_colors(svg_text)
    svg_text = _GRADIENT_BLOCK_RE.sub("", svg_text)
    svg_text = _FILTER_BLOCK_RE.sub("", svg_text)
    svg_text = _FILTER_ATTR_RE.sub("", svg_text)

    def deref(m: re.Match) -> str:
        attr, gid = m.group(1), m.group(2)
        base = bases.get(gid)
        return f'{attr}="{base}"' if base else m.group(0)

    return _URL_REF_RE.sub(deref, svg_text)


def _chromatic_tiers(svg_text: str) -> dict[str, str | None]:
    """Map each distinct chromatic hue (first-seen order) to its ramp opacity."""
    order: list[str] = []
    for m in _COLOR_ATTR_RE.finditer(svg_text):
        hexv = m.group(2).upper()
        if _is_chromatic(hexv) and hexv not in order:
            order.append(hexv)
    return {hexv: _TIERS[min(i, len(_TIERS) - 1)] for i, hexv in enumerate(order)}


def normalize_chart_svg(svg_text: str) -> str:
    svg_text = _COMMENT_RE.sub("", svg_text)
    svg_text = _flatten_defs(svg_text)
    tiers = _chromatic_tiers(svg_text)

    def repl(m: re.Match) -> str:
        attr, hexv = m.group(1), m.group(2).upper()
        if _is_chromatic(hexv):
            opacity = tiers.get(hexv)
            if opacity is not None:
                return f'{attr}="{ACCENT}" {attr}-opacity="{opacity}"'
            return f'{attr}="{ACCENT}"'
        return f'{attr}="{_neutral_token(hexv)}"'

    return _COLOR_ATTR_RE.sub(repl, svg_text)


def convert_directory(charts_dir: Path, out_dir: Path) -> list[Path]:
    """Tokenize every top-level `*.svg` in charts_dir into out_dir as `*.tpl.svg`.

    Only the directory's own `*.svg` files are converted (non-recursive), so the
    `_source/` output subdir is never re-ingested.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for svg_path in sorted(charts_dir.glob("*.svg")):
        out_path = out_dir / f"{svg_path.stem}.tpl.svg"
        tokenized = normalize_chart_svg(svg_path.read_text(encoding="utf-8"))
        out_path.write_text(tokenized, encoding="utf-8")
        written.append(out_path)
    return written


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--charts-dir", type=Path, default=DEFAULT_CHARTS_DIR,
                    help="directory of chart *.svg templates (default: slide/templates/charts)")
    ap.add_argument("--out", type=Path, default=None,
                    help="output dir for *.tpl.svg (default: <charts-dir>/_source)")
    ap.add_argument("--dry-run", action="store_true",
                    help="list what would be written; do not write")
    args = ap.parse_args(argv)

    charts_dir = args.charts_dir
    out_dir = args.out if args.out is not None else (charts_dir / "_source")

    if not charts_dir.is_dir():
        print(f"error: charts dir not found: {charts_dir}", file=sys.stderr)
        return 2

    svgs = sorted(charts_dir.glob("*.svg"))
    if args.dry_run:
        print(f"[dry-run] {len(svgs)} chart(s) -> {out_dir}")
        for p in svgs:
            print(f"  would write: {out_dir / (p.stem + '.tpl.svg')}")
        return 0

    written = convert_directory(charts_dir, out_dir)
    print(f"tokenized {len(written)} chart(s) -> {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
