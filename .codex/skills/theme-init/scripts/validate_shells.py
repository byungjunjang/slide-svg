#!/usr/bin/env python3
"""Validate the rendered layout shells against the permanent slide-svg locks.

Run after render_layouts.py (whether the shells came from the global baseline
`_source/` or a per-theme `_shell_src/` composed by /theme-init Step 5). Every
lock here is theme-INDEPENDENT — it holds for stock jangpm and for any composed
theme alike, so this checker is safe to run on every /theme-init.

Locks enforced (see CLAUDE.md "핵심 제약" + references/shared-standards.md §1):
    1. All four shells present (01_cover / 02_chapter / 03_content / 04_ending).
    2. Canvas locked to 1280×720 (viewBox + width/height).
    3. No banned SVG features (<style>/class/@font-face/<foreignObject>/textPath/
       <script>/<animate*>/<set>/<symbol>/<iframe>/<mask>/rgba()).
    4. Every <text> carries the active-theme font chain verbatim.
    5. The content shell carries the {{GOVERNING_MESSAGE}} placeholder (GM line).
    6. Light-mode lock: the content shell must NOT carry a LARGE narrative-band
       fill (`shell-bg`) or `shell-spectrum` fill that covers most of the canvas.
       Judged by GEOMETRY, not by a raw hex match — a single small accent cue
       (e.g. a 48×2 rule) is a legitimate content accent even when the theme
       sets shell-bg == accent (single-brand-colour design systems). The
       light-mode relaxation is scoped to the narrative shells (cover / chapter
       / closing) only.

Usage:
    python3 validate_shells.py
    python3 validate_shells.py --theme /path/to/theme-active.json
    python3 validate_shells.py --layouts-dir /path/to/templates/layouts/<theme>
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[2] / "slide"
DEFAULT_THEME = SKILL_ROOT / "references" / "theme-active.json"
LAYOUTS_BASE = SKILL_ROOT / "templates" / "layouts"

SHELL_FILES = ["01_cover.svg", "02_chapter.svg", "03_content.svg", "04_ending.svg"]
CONTENT_SHELL = "03_content.svg"
NARRATIVE_SHELLS = {"01_cover.svg", "02_chapter.svg", "04_ending.svg"}

# Banned features → human label. Matched as substrings / simple patterns; the
# converter breaks on any of these. marker-* and clipPath are conditionally
# allowed (shared-standards §1.1/§1.2) and intentionally NOT listed here.
BANNED = [
    (re.compile(r"<style[\s>]"),                  "<style> embedded stylesheet"),
    (re.compile(r"\sclass\s*="),                  "class= attribute"),
    (re.compile(r"@font-face"),                   "@font-face declaration"),
    (re.compile(r"<foreignObject[\s>]"),          "<foreignObject>"),
    (re.compile(r"textPath[\s>]"),                "textPath"),
    (re.compile(r"<script[\s>]"),                 "<script>"),
    (re.compile(r"<animate"),                     "<animate*>"),
    (re.compile(r"<set[\s>]"),                    "<set>"),
    (re.compile(r"<symbol[\s>]"),                 "<symbol>"),
    (re.compile(r"<iframe[\s>]"),                 "<iframe>"),
    (re.compile(r"<mask[\s>]"),                   "<mask>"),
    (re.compile(r"rgba\("),                       "rgba() literal (use fill-opacity)"),
]

_TEXT_TAG_RE = re.compile(r"<text\b.*?>", re.DOTALL)
_VIEWBOX_RE = re.compile(r'viewBox\s*=\s*"([^"]*)"')
_WIDTH_RE = re.compile(r'\bwidth\s*=\s*"([^"]*)"')
_HEIGHT_RE = re.compile(r'\bheight\s*=\s*"([^"]*)"')

# Narrative-band geometry: a band / large decorative fill covers most of the
# 1280×720 canvas. Check #6 flags only such large fills, so a small accent cue
# (e.g. a 48×2 rule) on the content shell is fine even when the theme sets
# shell-bg == accent. Bands in the shells are always <rect>s.
_RECT_TAG_RE = re.compile(r"<rect\b[^>]*?/?>", re.DOTALL)
_BAND_MIN_W = 960.0   # ≥ 75% of canvas width
_BAND_MIN_H = 300.0   # ≥ ~42% of canvas height


def _attr(tag: str, name: str) -> str | None:
    m = re.search(rf'\b{name}\s*=\s*"([^"]*)"', tag)
    return m.group(1) if m else None


def _dim(raw: str | None, full: float) -> float | None:
    """Parse an SVG length to user units; '%' is relative to the canvas axis."""
    if raw is None:
        return None
    raw = raw.strip()
    if raw.endswith("%"):
        try:
            return float(raw[:-1]) / 100.0 * full
        except ValueError:
            return None
    m = re.match(r"-?\d+(?:\.\d+)?", raw)
    return float(m.group(0)) if m else None


def _rect_fill(tag: str) -> str | None:
    fill = _attr(tag, "fill")
    if fill:
        return fill
    style = _attr(tag, "style")
    if style:
        m = re.search(r"fill\s*:\s*([^;]+)", style)
        if m:
            return m.group(1).strip()
    return None


def _large_rect_fills(text: str):
    """Yield UPPER-cased fill of every <rect> that covers most of the canvas."""
    for tag in _RECT_TAG_RE.findall(text):
        w = _dim(_attr(tag, "width"), 1280.0)
        h = _dim(_attr(tag, "height"), 720.0)
        if w is None or h is None or w < _BAND_MIN_W or h < _BAND_MIN_H:
            continue
        fill = _rect_fill(tag)
        if fill:
            yield fill.upper()


def _resolve(theme: dict, dotted: str):
    cur = theme
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def check_shell(path: Path, name: str, theme: dict, errors: list[str]) -> None:
    text = path.read_text(encoding="utf-8")

    # 2. Canvas lock — the root <svg> tag.
    head = text[:400]
    vb = _VIEWBOX_RE.search(head)
    if not vb or vb.group(1).split() != ["0", "0", "1280", "720"]:
        errors.append(f"{name}: viewBox must be '0 0 1280 720' (got {vb.group(1) if vb else 'none'})")
    w, h = _WIDTH_RE.search(head), _HEIGHT_RE.search(head)
    if not (w and w.group(1) == "1280" and h and h.group(1) == "720"):
        errors.append(f"{name}: root <svg> must be width=1280 height=720")

    # 3. Banned features.
    for pat, label in BANNED:
        if pat.search(text):
            errors.append(f"{name}: banned SVG feature — {label}")

    # 4. Font chain on every <text>.
    chain = _resolve(theme, "typography.font-chain")
    for tag in _TEXT_TAG_RE.findall(text):
        if "font-family=" not in tag:
            errors.append(f"{name}: a <text> element is missing font-family")
        elif chain and chain not in tag:
            errors.append(f"{name}: a <text> font-family is not the active theme chain")

    # 5. GM line on the content shell.
    if name == CONTENT_SHELL and "{{GOVERNING_MESSAGE}}" not in text:
        errors.append(f"{name}: content shell must carry the {{{{GOVERNING_MESSAGE}}}} GM placeholder")

    # 6. Light-mode lock on the content shell — no LARGE narrative-band / spectrum
    #    fill. Judged by GEOMETRY (a band covers most of the canvas), not by a raw
    #    hex match: a single small accent cue (e.g. a 48×2 rule) is a legitimate
    #    content accent even when the theme sets shell-bg == accent.
    if name == CONTENT_SHELL:
        bg = _resolve(theme, "colors.bg")
        shell_bg = _resolve(theme, "colors.shell-bg")
        spectrum = _resolve(theme, "colors.shell-spectrum") or []
        band_reason: dict[str, str] = {}
        if shell_bg and shell_bg != bg:
            band_reason[shell_bg.upper()] = (
                f"narrative band fill {shell_bg} — content must stay light "
                "(band is narrative-shell only)")
        for hue in spectrum:
            if hue and hue != bg:
                band_reason.setdefault(hue.upper(),
                    f"shell-spectrum hue {hue} — spectrum is narrative-shell decoration only")
        if band_reason:
            seen: set[str] = set()
            for fill in _large_rect_fills(text):
                if fill in band_reason and fill not in seen:
                    seen.add(fill)
                    errors.append(f"{name}: large canvas fill uses {band_reason[fill]}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--theme", type=Path, default=DEFAULT_THEME)
    ap.add_argument("--layouts-dir", type=Path, default=None,
                    help="Rendered theme layout dir (default: templates/layouts/<theme.name>)")
    args = ap.parse_args(argv)

    if not args.theme.exists():
        print(f"error: theme file not found: {args.theme}", file=sys.stderr)
        return 2
    theme = json.loads(args.theme.read_text(encoding="utf-8"))
    name = theme.get("name")
    layouts_dir = args.layouts_dir or (LAYOUTS_BASE / name)

    if not layouts_dir.is_dir():
        print(f"error: layout dir not found: {layouts_dir}", file=sys.stderr)
        return 2

    errors: list[str] = []
    for shell in SHELL_FILES:
        path = layouts_dir / shell
        if not path.exists():
            errors.append(f"{shell}: missing (expected at {path})")
            continue
        check_shell(path, shell, theme, errors)

    if errors:
        print(f"\n[validate_shells] {len(errors)} lock violation(s) in {layouts_dir}:", file=sys.stderr)
        for e in errors:
            print(f"  ✗ {e}", file=sys.stderr)
        return 1

    print(f"[validate_shells] OK — 4 shells pass all locks ({layouts_dir})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
