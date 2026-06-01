#!/usr/bin/env python3
"""Check that the active theme's primary font has matching files on disk.

The slide pipeline writes the theme's `typography.font-chain` verbatim into
every SVG `<text>` font-family attribute and into the HTML gallery CSS.
If the primary family has no OTF/TTF/WOFF files under `assets/fonts/`, the
gallery falls through the rest of the chain — so we want Arial sitting
somewhere in that chain as a guaranteed system fallback.

This script:
    1. Reads the primary family from `typography.font-chain`.
    2. Scans `assets/fonts/` for matching `<family>-<weight>.<ext>` files.
    3. If files exist → prints OK summary, exits 0.
    4. If no files exist:
       - prints a warning,
       - if "Arial" is NOT already in the chain, rewrites the theme JSON to
         insert "Arial" right before the final generic family
         (`sans-serif` / `serif` / `monospace`),
       - exits 0 anyway (missing fonts are a warning, not a hard fail).

Idempotent — running it twice does not re-inject Arial, since the second
pass sees Arial already present.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[2] / "slide"
REPO_ROOT = SKILL_ROOT.parents[2]
DEFAULT_THEME = SKILL_ROOT / "references" / "theme-active.json"
DEFAULT_FONTS_DIR = REPO_ROOT / "assets" / "fonts"

WEIGHT_SUFFIXES = {
    "Thin", "ExtraLight", "Light", "Regular",
    "Medium", "SemiBold", "Bold", "ExtraBold", "Black",
}
FONT_EXTS = {".otf", ".ttf", ".woff", ".woff2"}
GENERIC_FAMILIES = {"sans-serif", "serif", "monospace", "system-ui"}


def parse_chain(chain: str) -> list[str]:
    """Split a CSS font-family chain into individual family tokens (quotes stripped)."""
    return [tok.strip().strip("'\"") for tok in chain.split(",") if tok.strip()]


def primary_family(chain: str) -> str:
    families = parse_chain(chain)
    return families[0] if families else "Arial"


def has_arial(chain: str) -> bool:
    return any(f.lower() == "arial" for f in parse_chain(chain))


def count_font_files(family: str, fonts_dir: Path) -> int:
    if not fonts_dir.is_dir():
        return 0
    n = 0
    for path in fonts_dir.iterdir():
        if not path.is_file() or path.suffix.lower() not in FONT_EXTS:
            continue
        stem = path.stem
        if "-" not in stem:
            continue
        prefix, _, suffix = stem.rpartition("-")
        if prefix == family and suffix in WEIGHT_SUFFIXES:
            n += 1
    return n


def inject_arial(chain: str) -> str:
    """Insert 'Arial' before the trailing generic family, preserving the rest.

    "Pretendard, 'Apple SD Gothic Neo', sans-serif"
        → "Pretendard, 'Apple SD Gothic Neo', Arial, sans-serif"

    If no generic tail is found, append "Arial, sans-serif" to be safe.
    """
    raw_tokens = [t.strip() for t in chain.split(",") if t.strip()]
    if not raw_tokens:
        return "Arial, sans-serif"
    tail = raw_tokens[-1].strip("'\"").lower()
    if tail in GENERIC_FAMILIES:
        return ", ".join(raw_tokens[:-1] + ["Arial", raw_tokens[-1]])
    return ", ".join(raw_tokens + ["Arial", "sans-serif"])


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--theme", type=Path, default=DEFAULT_THEME)
    ap.add_argument("--fonts-dir", type=Path, default=DEFAULT_FONTS_DIR)
    args = ap.parse_args()

    if not args.theme.exists():
        print(f"theme not found: {args.theme}", file=sys.stderr)
        return 2

    theme = json.loads(args.theme.read_text(encoding="utf-8"))
    chain = theme.get("typography", {}).get("font-chain", "")
    family = primary_family(chain)
    n_files = count_font_files(family, args.fonts_dir)

    if n_files > 0:
        print(f"[validate_fonts] OK: '{family}' — {n_files} weight file(s) under {args.fonts_dir.relative_to(REPO_ROOT)}")
        return 0

    print(f"[validate_fonts] WARN: primary font '{family}' has no files under {args.fonts_dir.relative_to(REPO_ROOT)}")
    print(f"[validate_fonts]   the HTML gallery and SVG output will fall through the rest of the font-chain")

    if has_arial(chain):
        print(f"[validate_fonts]   Arial is already in the chain — generic system fallback in place")
        return 0

    new_chain = inject_arial(chain)
    theme["typography"]["font-chain"] = new_chain
    args.theme.write_text(json.dumps(theme, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"[validate_fonts]   injected 'Arial' as fallback")
    print(f"[validate_fonts]     before: {chain}")
    print(f"[validate_fonts]     after:  {new_chain}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
