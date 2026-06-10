#!/usr/bin/env python3
"""Build the glyph-advance metrics cache consumed by svg_to_pptx/font_metrics.py.

Dev-only tool (requires fontTools — NOT a runtime dependency). Reads the theme
font OTFs from assets/fonts/ and writes a compact JSON cache into the skill
package so the claude.ai bundle ships metrics without shipping fonts.

Per weight bucket the cache stores:
  - ascii: 95 advance widths (font units) for U+0020..U+007E
  - cjk:   single advance for CJK/Hangul (Pretendard's Hangul syllables are
           monospaced; the build verifies uniformity and falls back to the
           sample mean if a font ever breaks that assumption)
  - default: mean printable-ASCII advance, used for uncovered codepoints

Usage:
    python3 .claude/skills/slide/scripts/dev/build_font_metrics.py
    # then commit .claude/skills/slide/scripts/svg_to_pptx/font_metrics.json
    # re-run after /theme-init if the new theme changes the primary font
"""
from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[5]
FONTS_DIR = REPO_ROOT / "assets" / "fonts"
OUT_PATH = (Path(__file__).resolve().parents[1]
            / "svg_to_pptx" / "font_metrics.json")

FONT_FAMILY = "Pretendard"
# weight bucket -> OTF style name. 400/500/600/700 covers every weight the
# executor emits; font_metrics.py maps other weights to the nearest bucket.
WEIGHT_FILES = {
    "400": "Pretendard-Regular.otf",
    "500": "Pretendard-Medium.otf",
    "600": "Pretendard-SemiBold.otf",
    "700": "Pretendard-Bold.otf",
}
HANGUL_SYLLABLES = (0xAC00, 0xD7A3)
HANGUL_SAMPLE_STEP = 13  # ~860 of 11,172 syllables — plenty to prove uniformity


def _advance(font, cmap, hmtx, cp: int) -> int | None:
    glyph = cmap.get(cp)
    if glyph is None:
        return None
    return hmtx[glyph][0]


def extract_weight(otf_path: Path) -> dict:
    from fontTools.ttLib import TTFont

    font = TTFont(str(otf_path), lazy=True)
    upm = font["head"].unitsPerEm
    cmap = font.getBestCmap()
    hmtx = font["hmtx"]

    ascii_widths = []
    for cp in range(0x20, 0x7F):
        adv = _advance(font, cmap, hmtx, cp)
        if adv is None:
            raise SystemExit(f"{otf_path.name}: missing ASCII glyph U+{cp:04X}")
        ascii_widths.append(adv)

    hangul = [
        adv for cp in range(*HANGUL_SYLLABLES, HANGUL_SAMPLE_STEP)
        if (adv := _advance(font, cmap, hmtx, cp)) is not None
    ]
    if not hangul:
        raise SystemExit(f"{otf_path.name}: no Hangul syllable coverage")
    if len(set(hangul)) == 1:
        cjk = hangul[0]
    else:
        cjk = round(statistics.mean(hangul))
        print(f"[WARN] {otf_path.name}: Hangul advances not uniform "
              f"({len(set(hangul))} distinct) — using sample mean {cjk}")

    default = round(statistics.mean(ascii_widths[1:]))  # skip space
    font.close()
    return {"upm": upm, "ascii": ascii_widths, "cjk": cjk, "default": default}


def main() -> int:
    weights = {}
    upm = None
    for weight, filename in WEIGHT_FILES.items():
        otf = FONTS_DIR / filename
        if not otf.exists():
            raise SystemExit(f"font not found: {otf}")
        data = extract_weight(otf)
        if upm is None:
            upm = data["upm"]
        elif data["upm"] != upm:
            raise SystemExit(
                f"{filename}: unitsPerEm {data['upm']} != {upm} — "
                f"per-weight upm not supported by the cache format")
        weights[weight] = {k: data[k] for k in ("ascii", "cjk", "default")}
        print(f"[OK] {filename}: upm={data['upm']} cjk={data['cjk']} "
              f"default={data['default']}")

    cache = {"font_family": FONT_FAMILY, "upm": upm, "weights": weights}
    OUT_PATH.write_text(
        json.dumps(cache, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"[OK] wrote {OUT_PATH} ({OUT_PATH.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
