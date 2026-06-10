"""Glyph-advance text measurement from the prebuilt theme-font cache.

Pure stdlib at runtime: `font_metrics.json` (built by
scripts/dev/build_font_metrics.py with fontTools) ships inside this package, so
both Claude Code and the claude.ai essentials bundle measure text with real
Pretendard advances instead of per-character heuristics.

`measure_text` returns None when metrics are unavailable — cache missing,
unreadable, or the active theme's primary font no longer matches the cached
family. Callers (drawingml_utils.estimate_text_width) fall back to the
heuristic path, so this module can never break an export.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_CACHE_PATH = Path(__file__).resolve().parent / "font_metrics.json"
_THEME_PATH = (Path(__file__).resolve().parents[2]
               / "references" / "theme-active.json")

_ASCII_LO, _ASCII_HI = 0x20, 0x7E

_WEIGHT_ALIASES = {"normal": 400, "bold": 700}


def _is_cjk_cp(cp: int) -> bool:
    """CJK/Hangul fullwidth class — mirrors drawingml_utils.is_cjk_char.

    Duplicated as plain codepoint ranges so this module stays import-free
    (drawingml_utils imports us; importing back would be circular).
    """
    return (0x4E00 <= cp <= 0x9FFF or 0x3400 <= cp <= 0x4DBF or
            0x2E80 <= cp <= 0x2EFF or 0x3000 <= cp <= 0x303F or
            0xFF00 <= cp <= 0xFFEF or 0xF900 <= cp <= 0xFAFF or
            0x20000 <= cp <= 0x2A6DF or
            0xAC00 <= cp <= 0xD7AF or 0x1100 <= cp <= 0x11FF or
            0x3130 <= cp <= 0x318F or 0xA960 <= cp <= 0xA97F or
            0xD7B0 <= cp <= 0xD7FF or
            0x3040 <= cp <= 0x309F or 0x30A0 <= cp <= 0x30FF)


def _theme_primary_font() -> str | None:
    try:
        chain = json.loads(_THEME_PATH.read_text(encoding="utf-8"))[
            "typography"]["font-chain"]
    except Exception:
        return None
    first = chain.split(",")[0].strip().strip("'\"")
    return first or None


def _load_cache() -> dict | None:
    try:
        cache = json.loads(_CACHE_PATH.read_text(encoding="utf-8"))
        weights = cache["weights"]
        if not isinstance(cache["upm"], int) or not weights:
            return None
    except Exception:
        return None
    theme_font = _theme_primary_font()
    if theme_font and theme_font.lower() != cache.get("font_family", "").lower():
        sys.stderr.write(
            f"[WARN] font_metrics: cache is for '{cache.get('font_family')}' but "
            f"active theme leads with '{theme_font}' — falling back to heuristic "
            f"text measurement. Re-run scripts/dev/build_font_metrics.py.\n")
        return None
    return cache


_cache = _load_cache()


def metrics_available() -> bool:
    """True when measure_text will return real advances (headroom can shrink)."""
    return _cache is not None


def _weight_bucket(font_weight: str | int) -> dict:
    try:
        w = _WEIGHT_ALIASES.get(str(font_weight).strip().lower()) \
            or int(float(str(font_weight)))
    except (ValueError, TypeError):
        w = 400
    buckets = _cache["weights"]
    key = min(buckets, key=lambda k: abs(int(k) - w))
    return buckets[key]


def measure_text(text: str, font_size: float, font_weight: str = "400"):
    """Text width in SVG px from real glyph advances, or None if unavailable."""
    if _cache is None:
        return None
    bucket = _weight_bucket(font_weight)
    ascii_widths = bucket["ascii"]
    cjk, default = bucket["cjk"], bucket["default"]
    units = 0
    for ch in text:
        cp = ord(ch)
        if _ASCII_LO <= cp <= _ASCII_HI:
            units += ascii_widths[cp - _ASCII_LO]
        elif _is_cjk_cp(cp):
            units += cjk
        else:
            units += default
    return units / _cache["upm"] * font_size
