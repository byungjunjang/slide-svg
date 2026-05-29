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
    6. Light-mode lock: the content shell must NOT use the narrative-band fill
       (`shell-bg`) or any `shell-spectrum` hue. The light-mode relaxation is
       scoped to the narrative shells (cover / chapter / closing) only.

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

    # 6. Light-mode lock on the content shell — no band fill / spectrum hues.
    if name == CONTENT_SHELL:
        bg = _resolve(theme, "colors.bg")
        shell_bg = _resolve(theme, "colors.shell-bg")
        if shell_bg and shell_bg != bg and shell_bg.upper() in text.upper():
            errors.append(f"{name}: content shell uses narrative band fill {shell_bg} "
                          "— content must stay light (band is narrative-shell only)")
        spectrum = _resolve(theme, "colors.shell-spectrum") or []
        for hue in spectrum:
            if hue.upper() in text.upper():
                errors.append(f"{name}: content shell uses shell-spectrum hue {hue} "
                              "— spectrum is narrative-shell decoration only")


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
