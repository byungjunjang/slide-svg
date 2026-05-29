#!/usr/bin/env python3
"""Render the composed shells to reviewable PNGs for the Step 5 review checkpoint.

/theme-init Step 5 ("Shell Composition") is gated on a render-first review: the
agent composes `_shell_src/`, render_layouts.py produces the final shells, then
this script fills the content placeholders with neutral sample text and
rasterizes each shell to a PNG so the agent (and user) see the ACTUAL composed
geometry / band / typography — not an ASCII sketch. The agent then collects
feedback, revises `_shell_src/`, and re-renders until approved.

Rasterizer follows the project's documented fallback chain: cairosvg if present,
else svglib + reportlab. Both are optional system deps (CLAUDE.md dual-mode
note); if neither is installed the script writes the filled SVGs and tells the
caller to open them in a browser instead.

Usage:
    python3 preview_shells.py
    python3 preview_shells.py --theme /path/to/theme-active.json
    python3 preview_shells.py --layouts-dir /path/to/templates/layouts/<theme>
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
ASSETS_FONTS_DIR = Path(__file__).resolve().parents[4] / "assets" / "fonts"

SHELL_FILES = ["01_cover.svg", "02_chapter.svg", "03_content.svg", "04_ending.svg"]


def _ensure_static_ttf(var_ttf: Path) -> Path | None:
    """Instance a (possibly variable) TTF to a static Regular-weight TTF and
    cache it under the OS temp dir. reportlab/renderPM cannot rasterize the
    bundled CFF/OTF weights, nor a raw variable font's glyphs (→ tofu); a static
    glyf instance renders Hangul correctly. Returns the static path or None.
    """
    try:
        import tempfile
        from fontTools import ttLib  # type: ignore
        from fontTools.varLib import instancer  # type: ignore
    except Exception:
        return None
    cache_dir = Path(tempfile.gettempdir()) / "slide-svg-preview-fonts"
    try:
        cache_dir.mkdir(parents=True, exist_ok=True)
        static = cache_dir / f"{var_ttf.stem}-static.ttf"
        if static.exists() and static.stat().st_mtime >= var_ttf.stat().st_mtime:
            return static
        try:
            f = ttLib.TTFont(str(var_ttf))
            instancer.instantiateVariableFont(f, {"wght": 400}).save(str(static))
        except Exception:
            # Not a variable font (or instancing failed) — copy through as-is.
            ttLib.TTFont(str(var_ttf)).save(str(static))
        return static
    except Exception:
        return None


def register_preview_fonts(theme: dict) -> str | None:
    """Best-effort: make the svglib/reportlab fallback render Hangul instead of
    tofu (□) in the Step 5 review PNGs.

    Two things are required and easy to get wrong: (1) reportlab can't load the
    bundled CFF/OTF weights or a raw variable TTF, so we instance a static TTF
    (`_ensure_static_ttf`); (2) svglib IGNORES `pdfmetrics.registerFont` — its
    text path resolves families through its own map, so we must call
    `svglib.register_font`. cairosvg, when present, uses system fontconfig and
    needs none of this. Returns the registered family name, or None when
    svglib/fonttools or a usable .ttf is unavailable (then Hangul shows as □ and
    the caller should point the reviewer at cairosvg / a browser).
    """
    try:
        import svglib.svglib as svglib_mod  # type: ignore
    except Exception:
        return None
    if not ASSETS_FONTS_DIR.is_dir():
        return None
    var_ttf = next(iter(sorted(ASSETS_FONTS_DIR.glob("*.ttf"))), None)
    if var_ttf is None:
        return None
    static = _ensure_static_ttf(var_ttf)
    if static is None:
        return None
    chain = (theme.get("typography") or {}).get("font-chain", "") or ""
    families = [x.strip().strip("'\"") for x in chain.split(",") if x.strip()]
    generic = {"sans-serif", "serif", "monospace", "arial"}
    # The active theme's primary family (svglib resolves the first family) + a
    # Pretendard alias as a CJK glyph source.
    targets = [x for x in families if x.lower() not in generic][:1] + ["Pretendard"]
    # svglib keys its FontMap by family + the RAW font-weight string, so a numeric
    # weight in the SVG (font-weight="800") looks up "Family-800" — NOT "Family" or
    # "Family-Bold". Even "400" becomes "Family-400". So register the static
    # instance under every weight the active theme actually emits (plus
    # normal/bold). One static instance backs all of them — preview weight is
    # approximate, but Hangul renders for every text element instead of tofu.
    typ = theme.get("typography") or {}
    weights = {"normal", "bold"}
    for scale in typ.values():
        if isinstance(scale, dict) and scale.get("weight") is not None:
            weights.add(str(scale["weight"]))
    registered: str | None = None
    for fam in dict.fromkeys(targets):
        for weight in sorted(weights):
            try:
                svglib_mod.register_font(font_name=fam, font_path=str(static), weight=weight)
                registered = registered or fam
            except Exception:
                pass
    return registered

# Neutral sample content so the composed shell reads as a real page. The body of
# the content shell is intentionally left empty — Step 5 reviews the shell frame
# (header / title / GM / footer / band), not body composition.
SAMPLE = {
    "EYEBROW": "강의 시리즈 · 01",
    "TITLE": "활성 테마 셸 구성 프리뷰",
    "TITLE_ACCENT": "Shell Composition",
    "SUBTITLE": "내러티브 셸 밴드와 콘텐츠 라이트 셸을 함께 확인",
    "PRESENTER": "장병준",
    "DATE": "2026",
    "CHAPTER_NUMBER": "01",
    "CHAPTER_LABEL": "SECTION",
    "CHAPTER_TITLE": "챕터 디바이더 셸",
    "CHAPTER_SUMMARY": "섹션 전환을 알리는 내러티브 셸",
    "PAGE_TITLE": "콘텐츠 셸 헤더라인",
    "PAGE_EYEBROW": "CONTENT",
    "PAGE_NUM": "03 / 12",
    "GOVERNING_MESSAGE": "거버닝 메시지는 모든 콘텐츠 슬라이드 하단에 한 줄",
    "CLOSING_LABEL": "CLOSING",
    "CLOSING_HEADLINE": "마무리 셸",
    "CLOSING_ACCENT": "Thank you",
    "CONTACT_LINE": "contact@example.com",
}


def fill_sample(svg_text: str) -> str:
    """Replace {{CONTENT}} placeholders with sample text; blank any leftovers."""
    def sub(m: re.Match) -> str:
        key = m.group(1)
        return SAMPLE.get(key, "")
    # Only non-TOKEN placeholders remain at this point (tokens were resolved by
    # render_layouts); replace by exact key, default to empty string.
    return re.sub(r"\{\{([A-Z_]+)\}\}", sub, svg_text)


def rasterize(svg_text: str, svg_path: Path, png_path: Path) -> str | None:
    """Write filled SVG, rasterize to PNG. Returns renderer name or None."""
    svg_path.write_text(svg_text, encoding="utf-8")
    try:
        import cairosvg  # type: ignore
        cairosvg.svg2png(bytestring=svg_text.encode("utf-8"),
                         write_to=str(png_path), output_width=1280, output_height=720)
        return "cairosvg"
    except ImportError:
        pass
    except Exception as e:  # missing native cairo lib, malformed SVG, etc.
        print(f"  cairosvg unavailable on {svg_path.name}: {str(e).splitlines()[0]}", file=sys.stderr)
    try:
        from svglib.svglib import svg2rlg  # type: ignore
        from reportlab.graphics import renderPM  # type: ignore
        drawing = svg2rlg(str(svg_path))
        if drawing is not None:
            renderPM.drawToFile(drawing, str(png_path), fmt="PNG")
            return "svglib"
    except ImportError:
        pass
    except Exception as e:
        print(f"  svglib unavailable on {svg_path.name}: {str(e).splitlines()[0]}", file=sys.stderr)
    return None


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--theme", type=Path, default=DEFAULT_THEME)
    ap.add_argument("--layouts-dir", type=Path, default=None)
    args = ap.parse_args(argv)

    if not args.theme.exists():
        print(f"error: theme file not found: {args.theme}", file=sys.stderr)
        return 2
    theme = json.loads(args.theme.read_text(encoding="utf-8"))
    # Register a Hangul-capable font for the svglib fallback BEFORE rasterizing
    # (no-op when cairosvg is present or no usable .ttf / fonttools is available).
    font_family = register_preview_fonts(theme)
    layouts_dir = args.layouts_dir or (LAYOUTS_BASE / theme.get("name"))
    if not layouts_dir.is_dir():
        print(f"error: layout dir not found: {layouts_dir}", file=sys.stderr)
        return 2

    preview_dir = layouts_dir / "_preview"
    preview_dir.mkdir(parents=True, exist_ok=True)

    pngs: list[Path] = []
    svgs: list[Path] = []
    renderer: str | None = None
    for shell in SHELL_FILES:
        src = layouts_dir / shell
        if not src.exists():
            print(f"  skip {shell}: not rendered yet", file=sys.stderr)
            continue
        filled = fill_sample(src.read_text(encoding="utf-8"))
        stem = shell.replace(".svg", "")
        svg_out = preview_dir / f"{stem}.svg"
        png_out = preview_dir / f"{stem}.png"
        r = rasterize(filled, svg_out, png_out)
        svgs.append(svg_out)
        if r:
            renderer = r
            pngs.append(png_out)

    # Optional 2×2 montage when PNGs + PIL are available.
    montage = None
    if len(pngs) == 4:
        try:
            from PIL import Image  # type: ignore
            tiles = [Image.open(p) for p in pngs]
            w, h = tiles[0].size
            board = Image.new("RGB", (w * 2, h * 2), "white")
            for i, t in enumerate(tiles):
                board.paste(t, ((i % 2) * w, (i // 2) * h))
            montage = preview_dir / "shells.png"
            board.save(montage)
        except Exception:
            montage = None

    print(f"\n[preview_shells] preview written to {preview_dir}")
    if renderer:
        print(f"  renderer: {renderer}")
        if renderer == "svglib":
            if font_family:
                print(f"  Hangul font registered for svglib: {font_family} (static instance)")
            else:
                print("  note: Hangul may render as □ (no svglib/fonttools or usable .ttf). "
                      "For a faithful preview: pip install cairosvg, or open the filled SVGs "
                      "in a browser (they carry the full font chain).")
        for p in pngs:
            print(f"  PNG: {p}")
        if montage:
            print(f"  montage (2×2): {montage}")
        print("  → Read the montage (or per-shell PNGs) to review the composition, "
              "then present it to the user for the Step 5 checkpoint.")
    else:
        print("  no SVG rasterizer (cairosvg / svglib) available — Step 5c PNG review is degraded.")
        print("  → install one and re-run for PNG thumbnails:  pip install cairosvg")
        print("     (or: pip install -r .claude/skills/slide/requirements.txt)")
        print("  meanwhile, open the filled SVGs in a browser:")
        for p in svgs:
            print(f"  SVG: {p}")
        print(f"  e.g.  python3 -m http.server -d {preview_dir} 8000")
    return 0


if __name__ == "__main__":
    sys.exit(main())
