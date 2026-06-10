#!/usr/bin/env python3
"""Fill null / missing token values in a partial theme JSON with safe defaults.

The `/theme-init` skill is agent-driven: the calling Claude agent reads the
design guide and produces the theme JSON directly — no internal API call.
The agent is allowed (and encouraged) to emit `null` for any token the guide
doesn't specify, so this script fills those holes with monochrome grayscale
defaults before validation.

Usage:
    # Pipe partial JSON from the agent's scratch file:
    python3 fill_theme_defaults.py < /tmp/partial.json > theme-active.json

    # Explicit paths:
    python3 fill_theme_defaults.py --input /tmp/partial.json \
        --out .claude/skills/slide/references/theme-active.json

    # Also tolerates prose-wrapped / fenced JSON (e.g., pasted agent output):
    python3 fill_theme_defaults.py --input /tmp/messy.txt --out theme.json

The output always has every token in the v1 contract populated; a downstream
`validate_theme.py` run should succeed unless the agent produced a malformed
value (wrong hex shape, non-numeric size, etc.).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

SKILL_ROOT = Path(__file__).resolve().parents[2] / "slide"
DEFAULT_OUT = SKILL_ROOT / "references" / "theme-active.json"

# Monochrome grayscale safe defaults — used only for tokens the agent left as
# null (or omitted entirely). The goal is a readable-if-bland theme rather
# than a half-populated one that fails validation.
SAFE_DEFAULTS: dict[str, Any] = {
    "version": "1.0",
    "colors": {
        "bg":             "#FAFAF9",
        "surface":        "#FFFFFF",
        "surface-alt":    "#F5F5F4",
        "text":           "#1A1A1A",
        "text-secondary": "#6B7280",
        "text-tertiary":  "#9CA3AF",
        "border":         "#E5E7EB",
        "border-strong":  "#D4D4D4",
        "accent":         "#111111",
        "accent-soft":    "#F0F0F0",
        "accent-ink":     "#000000",
        "positive":       "#059669",
        "positive-soft":  "#ECFDF5",
        "negative":       "#E11D48",
        "negative-soft":  "#FFF1F2",
        "warning":        "#D97706",
        "warning-soft":   "#FFFBEB",
        # Optional narrative-shell band tokens (v1.1, additive). Default null /
        # empty so monochrome themes stay light (no band) and the schema's
        # additionalProperties:false round-trips. render_layouts.py falls back
        # null shell-* to the matching base token (text/text-secondary/accent),
        # so a theme that sets only shell-bg still renders safely.
        "shell-bg":             None,
        "shell-text":           None,
        "shell-text-secondary": None,
        "shell-accent":         None,
        "shell-spectrum":       [],
    },
    "typography": {
        "font-chain": "system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif",
        "display":    {"size": 56,   "weight": 800, "line-height": 1.08, "letter-spacing": -1.68, "transform": "none"},
        "display-sm": {"size": 40,   "weight": 800, "line-height": 1.10, "letter-spacing": -0.80, "transform": "none"},
        "headline":   {"size": 32,   "weight": 700, "line-height": 1.20, "letter-spacing": -0.64, "transform": "none"},
        "title":      {"size": 18.4, "weight": 600, "line-height": 1.30, "letter-spacing":  0.00, "transform": "none"},
        "body":       {"size": 15.2, "weight": 400, "line-height": 1.60, "letter-spacing":  0.00, "transform": "none"},
        "caption":    {"size": 12.8, "weight": 500, "line-height": 1.40, "letter-spacing":  0.00, "transform": "none"},
        "label":      {"size": 12.8, "weight": 600, "line-height": 1.40, "letter-spacing":  0.64, "transform": "uppercase"},
    },
    "radius":  {"xs": 4, "sm": 8, "md": 12, "lg": 12, "xl": 20, "pill": 9999},
    "stroke":  {"icon": 2, "divider": 1, "emphasis": 2},
    "spacing": {"1": 4, "2": 8, "3": 12, "4": 16, "5": 20, "6": 24,
                "8": 32, "10": 40, "12": 48, "14": 56, "16": 64},
    "assets":  {"icon-pack-default": "tabler-outline",
                "icon-pack-fallback": "tabler-filled",
                "character": None,
                # Theme-owned reference artifacts (ownership manifest): the
                # pattern gallery survives theme swaps (reskin_gallery.py
                # re-skins its CSS), but the reference text is voice-specific
                # — replace it for the new theme or leave null to disable.
                "gallery": None,
                "reference-text": None},
    "voice":   {"tone": "editorial, analytical, declarative",
                "pov":  "third-person institutional",
                "register": "report / lecture",
                "forbidden_phrases": [],
                "gm_style_hint": "One declarative sentence stating the so-what / takeaway."},
    # v1.1 additive tokens (optional in the contract). chromatic + hairline
    # reproduce the stock behaviour, so an agent that omits them gets exactly
    # today's output.
    "palette_mode": "chromatic",
    "surface": {"card_style": "hairline"},
}


def _merge_fill_nulls(extracted: Any, defaults: Any) -> Any:
    """Recursively replace None/missing values in `extracted` with `defaults`.

    - dict: prefer extracted non-null values, fall back to defaults; add
      missing keys from defaults.
    - list/scalar: if extracted is None, use defaults; otherwise keep.
    """
    if isinstance(defaults, dict):
        out = {}
        src = extracted if isinstance(extracted, dict) else {}
        for k, d in defaults.items():
            out[k] = _merge_fill_nulls(src.get(k), d)
        return out
    if extracted is None:
        return deepcopy(defaults)
    return extracted


def _extract_json(text: str) -> dict[str, Any]:
    """Tolerant JSON extraction. Handles four input shapes:

        {...}                      bare object
        ```json\n{...}\n```        fenced
        Here's the result:\n{...}  prose-prefixed bare
        Prose\n```json\n{...}\n``` prose-prefixed fenced

    Finds the outermost {...} via brace depth counting (string-literal aware)
    and parses just that.
    """
    text = text.strip()
    fence = re.search(r"```(?:json)?\s*\n?(\{.*?\})\s*```", text, flags=re.DOTALL)
    if fence:
        return json.loads(fence.group(1))

    start = text.find("{")
    if start < 0:
        raise json.JSONDecodeError("no JSON object found", text, 0)
    depth = 0
    in_str = False
    esc = False
    for i in range(start, len(text)):
        c = text[i]
        if esc:
            esc = False
            continue
        if c == "\\" and in_str:
            esc = True
            continue
        if c == '"':
            in_str = not in_str
            continue
        if in_str:
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return json.loads(text[start : i + 1])
    raise json.JSONDecodeError("unmatched braces", text, start)


def _derive_monochrome_semantics(filled: dict[str, Any], partial: dict[str, Any]) -> None:
    """For a monochrome palette, replace UNSPECIFIED semantic hues with ink tones.

    A hue-free brand encodes positive/negative/warning via direction / icon, not
    colour — so the green/red/orange defaults would be off-brand. Only tokens the
    agent left null (or omitted) are overridden; an explicit hue is respected.
    Idempotent: a second pass sees the derived (non-null) values and skips them.
    """
    pcolors = partial.get("colors") or {}
    colors = filled["colors"]
    ink = colors.get("text")
    soft = colors.get("surface-alt")
    for base in ("positive", "negative", "warning"):
        if pcolors.get(base) is None:
            colors[base] = ink
        if pcolors.get(f"{base}-soft") is None:
            colors[f"{base}-soft"] = soft


def fill(partial: dict[str, Any]) -> dict[str, Any]:
    """Fill nulls and missing tokens in a partial theme dict with defaults.

    Preserves `name`, `display_name`, and `description` from the input (these
    are not in SAFE_DEFAULTS because they're theme-identity fields).
    """
    filled = _merge_fill_nulls(partial, SAFE_DEFAULTS)
    if not filled.get("name"):
        filled["name"] = partial.get("name") or "unnamed"
    if not filled.get("display_name"):
        filled["display_name"] = partial.get("display_name") or filled["name"].title()
    if "description" in partial and partial["description"]:
        filled["description"] = partial["description"]
    if filled.get("palette_mode") == "monochrome":
        _derive_monochrome_semantics(filled, partial)
    return filled


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--input", type=Path,
                    help="partial theme JSON path (omit to read stdin)")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT,
                    help=f"output path (default: {DEFAULT_OUT})")
    ap.add_argument("--stdout", action="store_true",
                    help="print to stdout instead of writing --out")
    args = ap.parse_args()

    raw = args.input.read_text(encoding="utf-8") if args.input else sys.stdin.read()
    if not raw.strip():
        print("empty input", file=sys.stderr)
        return 2

    try:
        partial = _extract_json(raw)
    except json.JSONDecodeError as e:
        print(f"could not parse input as JSON: {e}", file=sys.stderr)
        return 1

    filled = fill(partial)
    serialized = json.dumps(filled, indent=2, ensure_ascii=False)

    if args.stdout:
        print(serialized)
    else:
        args.out.write_text(serialized + "\n", encoding="utf-8")
        print(f"wrote {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
