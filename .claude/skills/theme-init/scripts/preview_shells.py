#!/usr/bin/env python3
"""Build a single self-contained HTML preview for the /theme-init approval gate.

After the render chain finishes, this assembles ONE page
(`templates/layouts/<theme>/_preview/index.html`) that shows:

  1. a theme spec header — palette swatches + type scale from theme-active.json,
  2. the four rendered boilerplate shells (cover / chapter / content / ending)
     filled with neutral sample content, and
  3. tokenized content-body samples (scripts/preview_samples/*.tpl.svg) rendered
     in the active palette — so the user sees real body composition, not just
     the shell frame.

The SVG is inlined into the HTML, so the browser resolves the font chain itself
(Pretendard -> Apple SD Gothic Neo -> Malgun Gothic -> Arial). That means Hangul
renders correctly with NO rasterizer / fonttools dependency — the previous
cairosvg/svglib tofu failure mode is gone by construction.

Usage:
    python3 preview_shells.py
    python3 preview_shells.py --theme /path/to/theme-active.json
    python3 preview_shells.py --layouts-dir /path/to/templates/layouts/<theme>
"""
from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path

from _token_render import load_theme, render as render_tokens

SKILL_ROOT = Path(__file__).resolve().parents[2] / "slide"
DEFAULT_THEME = SKILL_ROOT / "references" / "theme-active.json"
LAYOUTS_BASE = SKILL_ROOT / "templates" / "layouts"
SAMPLES_DIR = Path(__file__).resolve().parent / "preview_samples"

SHELL_FILES = ["01_cover.svg", "02_chapter.svg", "03_content.svg", "04_ending.svg"]
SHELL_LABELS = {
    "01_cover.svg": "Cover shell",
    "02_chapter.svg": "Chapter divider shell",
    "03_content.svg": "Content shell",
    "04_ending.svg": "Ending shell",
}

# Neutral sample content so each shell reads as a real page.
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
    """Replace {{CONTENT}} placeholders with sample text; blank any leftovers.

    Only non-TOKEN placeholders should remain when this runs (tokens are resolved
    first). Replace by exact key from SAMPLE, default unknown keys to empty.
    """
    def sub(m: "re.Match") -> str:
        return SAMPLE.get(m.group(1), "")
    return re.sub(r"\{\{([A-Z_]+)\}\}", sub, svg_text)


def _swatches_html(theme: dict) -> str:
    colors = theme.get("colors") or {}
    cells = []
    for name, val in colors.items():
        if not isinstance(val, str) or not val.startswith("#"):
            continue
        label = html.escape(f"{name}  {val}")
        cells.append(
            f'<div class="swatch"><span class="chip" style="background:{html.escape(val)}">'
            f'</span><code>{label}</code></div>'
        )
    return "\n".join(cells)


def _typescale_html(theme: dict) -> str:
    typ = theme.get("typography") or {}
    rows = []
    for name, scale in typ.items():
        if not isinstance(scale, dict):
            continue
        size = scale.get("size")
        weight = scale.get("weight")
        if size is None:
            continue
        rows.append(
            f'<tr><td>{html.escape(str(name))}</td>'
            f'<td>{html.escape(str(size))}</td>'
            f'<td>{html.escape(str(weight))}</td></tr>'
        )
    if not rows:
        return ""
    return ("<table class=\"typescale\"><thead><tr><th>tier</th><th>size</th>"
            "<th>weight</th></tr></thead><tbody>" + "".join(rows) + "</tbody></table>")


def _shell_cards(layouts_dir: Path) -> "tuple[list[str], list[str]]":
    """Return (card-html list, missing-shell list) for the 4 rendered shells."""
    cards, missing = [], []
    for shell in SHELL_FILES:
        src = layouts_dir / shell
        if not src.exists():
            missing.append(shell)
            continue
        svg = fill_sample(src.read_text(encoding="utf-8"))
        label = html.escape(SHELL_LABELS.get(shell, shell))
        cards.append(f'<figure class="page"><figcaption>{label}</figcaption>'
                     f'<div class="frame">{svg}</div></figure>')
    return cards, missing


def _sample_cards(theme: dict) -> "list[str]":
    """Render content-body samples: tokens first, then content placeholders."""
    cards = []
    for src in sorted(SAMPLES_DIR.glob("*.tpl.svg")):
        svg = fill_sample(render_tokens(src.read_text(encoding="utf-8"), theme))
        label = html.escape(src.stem.replace("_", " ") + " (sample content)")
        cards.append(f'<figure class="page"><figcaption>{label}</figcaption>'
                     f'<div class="frame">{svg}</div></figure>')
    return cards


def build_preview_html(theme: dict, layouts_dir: Path) -> "tuple[str, list[str]]":
    """Assemble the self-contained preview page. Returns (html, missing_shells)."""
    name = html.escape(str(theme.get("display_name") or theme.get("name") or "theme"))
    accent = html.escape(str((theme.get("colors") or {}).get("accent", "")))
    shell_cards, missing = _shell_cards(layouts_dir)
    sample_cards = _sample_cards(theme)
    doc = f"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8">
<title>{name} — theme preview</title>
<style>
  body {{ margin:0; padding:32px; background:#11151a0d; font-family:system-ui,sans-serif; }}
  h1 {{ font-size:22px; margin:0 0 4px; }}
  .sub {{ color:#666; margin:0 0 24px; }}
  .spec {{ display:flex; gap:32px; flex-wrap:wrap; margin-bottom:32px; }}
  .swatches {{ display:flex; gap:12px; flex-wrap:wrap; }}
  .swatch {{ display:flex; align-items:center; gap:8px; }}
  .chip {{ width:28px; height:28px; border-radius:6px; border:1px solid #0002; display:inline-block; }}
  code {{ font-size:12px; color:#333; }}
  table.typescale {{ border-collapse:collapse; font-size:13px; }}
  table.typescale th, table.typescale td {{ border:1px solid #ddd; padding:3px 10px; text-align:left; }}
  .grid {{ display:grid; grid-template-columns:1fr 1fr; gap:24px; }}
  figure.page {{ margin:0; }}
  figcaption {{ font-size:13px; color:#555; margin-bottom:6px; }}
  .frame {{ border:1px solid #ccc; box-shadow:0 1px 4px #0001; background:#fff; }}
  .frame svg {{ display:block; width:100%; height:auto; }}
  .missing {{ color:#b00; font-size:13px; }}
  h2 {{ font-size:15px; margin:32px 0 12px; color:#444; }}
</style></head><body>
<h1>{name} — theme preview</h1>
<p class="sub">활성 액센트 {accent} · 아래 셸과 샘플을 확인하고 승인/피드백을 주세요.</p>
<div class="spec">
  <div><strong>Palette</strong><div class="swatches">{_swatches_html(theme)}</div></div>
  <div><strong>Type scale</strong>{_typescale_html(theme)}</div>
</div>
<h2>Boilerplate shells</h2>
<div class="grid">{''.join(shell_cards)}</div>
<h2>Sample content layouts</h2>
<div class="grid">{''.join(sample_cards)}</div>
{('<p class="missing">missing shells: ' + ', '.join(missing) + '</p>') if missing else ''}
</body></html>"""
    return doc, missing


def main(argv: "list[str] | None" = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--theme", type=Path, default=DEFAULT_THEME)
    ap.add_argument("--layouts-dir", type=Path, default=None)
    args = ap.parse_args(argv)

    if not args.theme.exists():
        print(f"error: theme file not found: {args.theme}", file=sys.stderr)
        return 2
    theme = load_theme(args.theme)
    layouts_dir = args.layouts_dir or (LAYOUTS_BASE / theme.get("name"))
    if not layouts_dir.is_dir():
        print(f"error: layout dir not found: {layouts_dir}", file=sys.stderr)
        return 2

    preview_dir = layouts_dir / "_preview"
    preview_dir.mkdir(parents=True, exist_ok=True)
    doc, missing = build_preview_html(theme, layouts_dir)
    out = preview_dir / "index.html"
    out.write_text(doc, encoding="utf-8")

    print(f"\n[preview_shells] preview written to {out}")
    if missing:
        print(f"  note: {len(missing)} shell(s) not rendered yet: {', '.join(missing)}")
    print("  -> open it for the Step 6.5 approval gate:")
    print(f"     python3 -m http.server -d {preview_dir} 8000   # then http://localhost:8000/")
    print("  (or open the file directly in a browser — it is self-contained)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
