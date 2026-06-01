#!/usr/bin/env python3
"""Generate `references/colors_and_type.css` from `theme-active.json`.

The HTML visual-reference gallery (`references/jangpm-patterns/*.html`) loads
`_slide.css`, which `@import`s `../colors_and_type.css`. By writing this file
at `references/colors_and_type.css` (the correct path for that import), all
29 gallery HTMLs automatically reskin to match the active theme — no HTML
file rewriting required.

This also fixes a latent bug: the import previously resolved to a missing
file. The gallery was shipping with no variable definitions.

Usage:
    python3 reskin_gallery.py
    python3 reskin_gallery.py --theme /path/to/theme-active.json
    python3 reskin_gallery.py --out /path/to/colors_and_type.css
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[2] / "slide"
REPO_ROOT = SKILL_ROOT.parents[2]
ASSETS_FONTS_DIR = REPO_ROOT / "assets" / "fonts"
DEFAULT_THEME_PATH = SKILL_ROOT / "references" / "theme-active.json"
DEFAULT_OUT_PATH = SKILL_ROOT / "references" / "colors_and_type.css"

# Gallery HTML files under references/jangpm-patterns/ load _slide.css which
# @imports ../colors_and_type.css. From that file's location the path back to
# repo-root assets/fonts/ is four levels up.
FONT_URL_PREFIX = "../../../../assets/fonts/"

# Map common filename suffixes to CSS font-weights. Used to construct
# @font-face entries from whatever files actually live in assets/fonts/.
WEIGHT_BY_SUFFIX: dict[str, int] = {
    "Thin":       100,
    "ExtraLight": 200,
    "Light":      300,
    "Regular":    400,
    "Medium":     500,
    "SemiBold":   600,
    "Bold":       700,
    "ExtraBold":  800,
    "Black":      900,
}

FORMAT_BY_EXT: dict[str, str] = {
    ".otf": "opentype",
    ".ttf": "truetype",
    ".woff":  "woff",
    ".woff2": "woff2",
}


HEAD_BANNER = """/* ============================================================
   {display_name} Slide Design System — Colors & Typography
   Generated from references/theme-active.json by theme-init/reskin_gallery.py.
   DO NOT EDIT BY HAND — rerun the reskin script to refresh.
   ============================================================ */
"""


def _primary_font_name(font_chain: str) -> str:
    """Extract the first family name from a CSS font-family chain.

    e.g. "Pretendard, 'Apple SD Gothic Neo', Arial, sans-serif" → "Pretendard".
    Strips wrapping quotes; falls back to "Arial" if the chain is empty.
    """
    if not font_chain:
        return "Arial"
    first = font_chain.split(",", 1)[0].strip()
    return first.strip("'\"") or "Arial"


def _scan_font_files(family: str) -> list[tuple[str, int, str]]:
    """Find weight-suffixed font files for `family` under assets/fonts/.

    Returns a sorted list of (filename, weight, format) tuples. Only files
    whose stem matches `<family>-<Suffix>` (case-insensitive on the suffix,
    exact on the family) are returned; variable fonts and non-weighted
    files are skipped because @font-face needs a discrete weight per face.
    """
    if not ASSETS_FONTS_DIR.is_dir():
        return []
    matches: list[tuple[str, int, str]] = []
    for path in sorted(ASSETS_FONTS_DIR.iterdir()):
        if not path.is_file():
            continue
        ext = path.suffix.lower()
        if ext not in FORMAT_BY_EXT:
            continue
        stem = path.stem
        if "-" not in stem:
            continue
        prefix, _, suffix = stem.rpartition("-")
        if prefix != family:
            continue
        weight = WEIGHT_BY_SUFFIX.get(suffix)
        if weight is None:
            continue
        matches.append((path.name, weight, FORMAT_BY_EXT[ext]))
    matches.sort(key=lambda t: t[1])
    return matches


def build_font_face_block(theme: dict) -> str:
    """Build an @font-face block driven by theme primary font + assets/fonts/.

    If matching files are present, emit one @font-face per weight. If the
    primary font cannot be found on disk, emit a notice comment so the gallery
    falls through to the rest of the CSS font-family chain (Arial / sans-serif).
    """
    family = _primary_font_name(theme.get("typography", {}).get("font-chain", ""))
    files = _scan_font_files(family)

    header = (
        "/* ---------- FONTS ----------\n"
        f"   Primary font for the active theme: {family}.\n"
        "   @font-face entries below are auto-generated from the files in\n"
        "   `assets/fonts/` matching `<family>-<weight>.{otf,ttf,woff,woff2}`.\n"
        "   Missing weights silently fall through to the next family in the\n"
        "   --font-sans chain (Arial → sans-serif).\n"
        "*/\n"
    )

    if not files:
        return (
            header
            + f"/* No files for '{family}' found under assets/fonts/. The HTML gallery\n"
              f"   will render using the next family in the chain (typically Arial). */\n"
        )

    lines = [header]
    for filename, weight, fmt in files:
        url = FONT_URL_PREFIX + filename
        lines.append(
            f"@font-face {{ font-family: '{family}'; font-weight: {weight}; "
            f"font-style: normal; font-display: swap; "
            f"src: url('{url}') format('{fmt}'); }}"
        )
    return "\n".join(lines) + "\n"

# Structural CSS that does not depend on theme values. Written verbatim.
STRUCTURAL_TAIL = """
/* ============================================================
   SEMANTIC TYPOGRAPHY CLASSES
   Structural — do not edit per theme. Colors/sizes come from tokens above.
   ============================================================ */
html { font-family: var(--font-sans); color: var(--text); background: var(--bg); }
body { font-family: var(--font-sans); }

.display {
  font-size: var(--fs-display);
  font-weight: var(--fw-display);
  line-height: var(--lh-display);
  letter-spacing: var(--ls-display);
  color: var(--text);
}
.display-sm {
  font-size: var(--fs-display-sm);
  font-weight: var(--fw-display-sm);
  line-height: var(--lh-display-sm);
  letter-spacing: var(--ls-display-sm);
  color: var(--text);
}
.headline, h2.headline {
  font-size: var(--fs-headline);
  font-weight: var(--fw-headline);
  line-height: var(--lh-headline);
  letter-spacing: var(--ls-headline);
  color: var(--text);
}
.title {
  font-size: var(--fs-title);
  font-weight: var(--fw-title);
  line-height: var(--lh-title);
  color: var(--text);
}
.body, p {
  font-size: var(--fs-body);
  font-weight: var(--fw-body);
  line-height: var(--lh-body);
  color: var(--text);
}
.caption {
  font-size: var(--fs-caption);
  font-weight: var(--fw-caption);
  line-height: var(--lh-caption);
  color: var(--text-secondary);
}
.label-caption {
  font-size: var(--fs-caption);
  font-weight: var(--fw-title);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-secondary);
}
code, .mono {
  font-family: var(--font-mono);
  font-size: 0.9em;
}

/* Utility color */
.text-primary   { color: var(--text); }
.text-secondary { color: var(--text-secondary); }
.text-tertiary  { color: var(--text-tertiary); }
.text-accent    { color: var(--accent); }
.trend-positive { color: var(--positive); }
.trend-negative { color: var(--negative); }
.trend-warning  { color: var(--warning); }
"""


def px_to_rem(px: float, base: float = 16.0) -> str:
    """Format pixel value as rem with minimal precision."""
    rem = px / base
    if rem == int(rem):
        return f"{int(rem)}rem"
    return f"{rem:.4f}".rstrip("0").rstrip(".") + "rem"


def px_str(px: float) -> str:
    """Format pixel value with minimal precision."""
    if float(px) == int(px):
        return f"{int(px)}px"
    return f"{float(px):.4f}".rstrip("0").rstrip(".") + "px"


def build_root_block(theme: dict) -> str:
    c = theme["colors"]
    t = theme["typography"]
    r = theme["radius"]
    s = theme["spacing"]

    lines: list[str] = [":root {"]
    lines.append("  /* ---------- CORE COLOR TOKENS ---------- */")
    for key in [
        "bg", "surface", "surface-alt", "text", "text-secondary", "text-tertiary",
        "border", "border-strong", "accent", "accent-soft", "accent-ink",
    ]:
        lines.append(f"  --{key}: {c[key]};")
    lines.append("")
    lines.append("  /* ---------- SEMANTIC (data only) ---------- */")
    for key in ["positive", "positive-soft", "negative", "negative-soft", "warning", "warning-soft"]:
        lines.append(f"  --{key}: {c[key]};")
    lines.append("")
    lines.append("  /* ---------- TYPOGRAPHY ---------- */")
    # Build CSS font-family chains. Primary = theme font-chain.
    lines.append(f"  --font-sans: {t['font-chain']};")
    lines.append("  --font-mono: 'SF Mono', 'JetBrains Mono', 'Fira Code', Menlo, Consolas, monospace;")
    lines.append("")

    scale_keys = ["display", "display-sm", "headline", "title", "body", "caption", "label"]
    lines.append("  /* Size scale */")
    for key in scale_keys:
        lines.append(f"  --fs-{key}: {px_to_rem(t[key]['size'])};")
    lines.append("")
    lines.append("  /* Weight scale */")
    for key in scale_keys:
        lines.append(f"  --fw-{key}: {t[key]['weight']};")
    lines.append("")
    lines.append("  /* Line-height scale */")
    for key in scale_keys:
        lines.append(f"  --lh-{key}: {t[key]['line-height']};")
    lines.append("")
    lines.append("  /* Letter-spacing scale (px) */")
    for key in scale_keys:
        ls = t[key].get("letter-spacing", 0)
        lines.append(f"  --ls-{key}: {px_str(ls)};")
    lines.append("")

    lines.append("  /* ---------- SPACING ---------- */")
    # Map numeric keys to --space-N: value in rem.
    for key in sorted(s.keys(), key=lambda k: int(k)):
        lines.append(f"  --space-{key}: {px_to_rem(s[key])};")
    lines.append("")

    lines.append("  /* ---------- RADIUS ---------- */")
    for key in ["xs", "sm", "md", "lg", "xl", "pill"]:
        val = r[key]
        lines.append(f"  --radius-{key}: {px_str(val)};")
    lines.append("")

    lines.append("  /* ---------- ELEVATION (sparse) ---------- */")
    lines.append("  --shadow-sm: 0 1px 2px rgba(26,26,26,0.04);")
    lines.append("  --shadow-md: 0 2px 8px rgba(26,26,26,0.06);")
    lines.append("  --shadow-lg: 0 8px 24px rgba(26,26,26,0.08);")
    lines.append("")

    lines.append("  /* ---------- CARD ---------- */")
    lines.append("  --card-padding: var(--space-6);")
    lines.append("  --card-gap:     var(--space-6);")
    lines.append("  --card-radius:  var(--radius-lg);")
    lines.append("}")
    return "\n".join(lines)


def build_css(theme: dict) -> str:
    banner = HEAD_BANNER.format(display_name=theme.get("display_name") or theme["name"].title())
    parts = [banner, build_font_face_block(theme), build_root_block(theme), STRUCTURAL_TAIL]
    return "\n".join(parts) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--theme", type=Path, default=DEFAULT_THEME_PATH)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT_PATH)
    parser.add_argument("--stdout", action="store_true", help="Print CSS to stdout instead of writing.")
    args = parser.parse_args(argv)

    if not args.theme.exists():
        print(f"error: theme file not found: {args.theme}", file=sys.stderr)
        return 2

    theme = json.loads(args.theme.read_text(encoding="utf-8"))
    css = build_css(theme)

    if args.stdout:
        sys.stdout.write(css)
        return 0

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(css, encoding="utf-8")
    print(f"Wrote {args.out} ({len(css)} bytes) for theme '{theme['name']}'")
    return 0


if __name__ == "__main__":
    sys.exit(main())
