"""Shared placeholder renderer for theme-init template → reference files.

Placeholder grammar:
    {{TOKEN:<dotted.path>}}              — raw token value
    {{TOKEN:<dotted.path>|<filter>}}     — value run through a named filter

Supported filters:
    rgb       — hex string  → "r, g, b" decimal tuple (for rgba() literals)
    bulleted  — list         → newline-joined markdown bullets
    csv       — list         → comma-joined inline enumeration (e.g. `"a", "b"`)
    optional  — any          → str(value) or "_(not provided)_" when value is null

Called by render_anti_slop_theme.py and render_design_system.py.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

_PLACEHOLDER_RE = re.compile(r"\{\{TOKEN:([a-zA-Z0-9_.\-]+)(?:\|([a-z]+))?\}\}")


def _lookup(theme: dict[str, Any], dotted: str) -> Any:
    cur: Any = theme
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            raise KeyError(f"missing theme token: {dotted}")
        cur = cur[part]
    return cur


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
    def _sub(match: re.Match[str]) -> str:
        dotted, fmt = match.group(1), match.group(2)
        value = _lookup(theme, dotted)
        return _format(value, fmt)

    return _PLACEHOLDER_RE.sub(_sub, tpl_text)


def load_theme(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))
