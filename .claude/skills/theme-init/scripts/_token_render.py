"""Shared placeholder renderer for theme-init template → reference files.

Placeholder grammar:
    {{TOKEN:<dotted.path>}}              — raw token value
    {{TOKEN:<dotted.path>|<filter>}}     — value run through a named filter
    {{IF:<dotted.path>}}...{{/IF}}       — render inner block iff token is truthy
    {{IFNOT:<dotted.path>}}...{{/IF}}    — render inner block iff token is falsy
    {{IF:<dotted.path>=<value>}}...{{/IF}}    — render iff str(token) == <value>
    {{IFNOT:<dotted.path>=<value>}}...{{/IF}} — render iff str(token) != <value>

Truthiness for IF/IFNOT: a token is falsy when missing, null, an empty string,
or an empty list — otherwise truthy. This lets optional tokens (e.g. the
narrative-shell band group `colors.shell-bg`/`shell-spectrum`) gate whole
documentation sections without raising on monochrome themes that omit them.

Equality form (`=value`): the token is compared as a string to <value>; a
missing path counts as "not equal" (so an absent optional token like
`surface.card_style` drops every `{{IF:...=...}}` branch instead of raising).
This drives the mutually-exclusive card-treatment guidance blocks in the
reference templates.

Dotted paths walk dicts and also integer list indices, e.g.
`colors.shell-spectrum.0` resolves the first spectrum hue.

Supported filters:
    rgb       — hex string  → "r, g, b" decimal tuple (for rgba() literals)
    bulleted  — list         → newline-joined markdown bullets
    csv       — list         → comma-joined inline enumeration (e.g. `"a", "b"`)
    optional  — any          → str(value) or "_(not provided)_" when value is null
    cap       — any          → str(value) with the first character capitalized
                               (e.g. theme `name` "montage" → "Montage")

Called by render_anti_slop_theme.py, render_design_system.py, render_prompts.py.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

_PLACEHOLDER_RE = re.compile(r"\{\{TOKEN:([a-zA-Z0-9_.\-]+)(?:\|([a-z]+))?\}\}")
# Non-greedy block match; DOTALL so blocks may span multiple lines. Conditionals
# do not nest (a flat block model is enough for the reference templates).
_BLOCK_RE = re.compile(
    r"\{\{(IF|IFNOT):([a-zA-Z0-9_.\-]+)(?:=([^}]*))?\}\}(.*?)\{\{/IF\}\}", re.DOTALL)


def _lookup(theme: dict[str, Any], dotted: str) -> Any:
    cur: Any = theme
    for part in dotted.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        elif isinstance(cur, list) and part.isdigit() and int(part) < len(cur):
            cur = cur[int(part)]
        else:
            raise KeyError(f"missing theme token: {dotted}")
    return cur


def _truthy(theme: dict[str, Any], dotted: str) -> bool:
    """A token is truthy unless missing, null, an empty string, or an empty list."""
    try:
        value = _lookup(theme, dotted)
    except KeyError:
        return False
    if value is None:
        return False
    if isinstance(value, (str, list, dict)) and len(value) == 0:
        return False
    return True


def _equals(theme: dict[str, Any], dotted: str, expected: str) -> bool:
    """str(token) == expected; a missing path counts as not-equal (no raise)."""
    try:
        value = _lookup(theme, dotted)
    except KeyError:
        return False
    return str(value) == expected


def _render_conditionals(tpl_text: str, theme: dict[str, Any]) -> str:
    def _sub(match: re.Match[str]) -> str:
        kind, dotted, eq_value, body = (
            match.group(1), match.group(2), match.group(3), match.group(4))
        if eq_value is not None:
            keep = _equals(theme, dotted, eq_value)
        else:
            keep = _truthy(theme, dotted)
        if kind == "IFNOT":
            keep = not keep
        return body if keep else ""

    return _BLOCK_RE.sub(_sub, tpl_text)


def _hex_to_rgb(hex_str: str) -> str:
    h = hex_str.lstrip("#")
    if len(h) not in (6, 8):
        raise ValueError(f"expected 6- or 8-digit hex, got {hex_str!r}")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"{r}, {g}, {b}"


def _format(value: Any, fmt: str | None) -> str:
    if fmt is None:
        return str(value)
    if fmt == "optional":
        if value is None:
            return "_(not provided)_"
        return str(value)
    if fmt == "cap":
        return str(value).capitalize()
    if fmt == "rgb":
        if not isinstance(value, str):
            raise ValueError(f"|rgb expects hex string, got {type(value).__name__}")
        return _hex_to_rgb(value)
    if fmt == "bulleted":
        if not isinstance(value, list):
            raise ValueError(f"|bulleted expects array, got {type(value).__name__}")
        if not value:
            return "- _(none specified)_"
        return "\n".join(f"- {item}" for item in value)
    if fmt == "csv":
        if not isinstance(value, list):
            raise ValueError(f"|csv expects array, got {type(value).__name__}")
        if not value:
            return "_(none)_"
        return ", ".join(f'"{item}"' for item in value)
    raise ValueError(f"unknown format filter: {fmt}")


def render(tpl_text: str, theme: dict[str, Any]) -> str:
    # 1. Resolve conditional blocks first so pruned branches never have their
    #    placeholders looked up (a null shell token inside a dropped {{IF}}
    #    must not raise).
    tpl_text = _render_conditionals(tpl_text, theme)

    def _sub(match: re.Match[str]) -> str:
        dotted, fmt = match.group(1), match.group(2)
        value = _lookup(theme, dotted)
        return _format(value, fmt)

    return _PLACEHOLDER_RE.sub(_sub, tpl_text)


def load_theme(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))
