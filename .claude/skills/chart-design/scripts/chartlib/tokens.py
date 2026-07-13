"""Token resolver — maps slide-svg design tokens onto the chart style contract.

Reads the ACTIVE theme's render copy (`slide/references/theme-active.json`),
the same file every other slide-svg reference is rendered from. When slide-svg's
design system changes (theme-init --activate), charts follow automatically on
the next render — nothing in chart-design stores color or type values.

Hard-fail policy: if the theme file is missing or violates the token contract,
raise TokenResolutionError. Never fall back to invented defaults — a chart
rendered with wrong tokens silently poisons a whole deck.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

# chart-design/scripts/chartlib/tokens.py → .claude/skills
_SKILLS_DIR = Path(__file__).resolve().parents[3]
THEME_ACTIVE_PATH = _SKILLS_DIR / "slide" / "references" / "theme-active.json"

# T4 single-accent opacity ladder (anti-slop-theme.md Rule T4).
# Position in the ladder = series index. >4 series is a judgment error upstream.
SERIES_ALPHA_LADDER = (0.85, 0.60, 0.40, 0.25)
MAX_SERIES = len(SERIES_ALPHA_LADDER)

_HEX_RE = re.compile(r"^#([0-9A-Fa-f]{6})([0-9A-Fa-f]{2})?$")

# Token names chartlib depends on. Checked eagerly so a contract drift fails
# loudly at resolve time, not deep inside a renderer.
_REQUIRED_COLORS = (
    "bg", "surface", "surface-alt", "text", "text-secondary", "text-tertiary",
    "border", "border-strong", "accent", "accent-soft", "accent-ink",
    "positive", "positive-soft", "negative", "negative-soft",
    "warning", "warning-soft",
)
_REQUIRED_TYPE_ROLES = ("display-sm", "headline", "title", "body", "caption", "label")
_REQUIRED_STROKES = ("icon", "divider", "emphasis")
_REQUIRED_RADII = ("xs", "sm", "md")


class TokenResolutionError(RuntimeError):
    """Raised when slide-svg theme tokens cannot be resolved. Never swallowed."""


def _parse_hex(value: str, token_name: str) -> tuple[int, int, int]:
    m = _HEX_RE.match(value or "")
    if not m:
        raise TokenResolutionError(
            f"Theme token colors.{token_name} is not a hex color: {value!r} "
            f"(file: {THEME_ACTIVE_PATH})"
        )
    rgb = m.group(1)
    return int(rgb[0:2], 16), int(rgb[2:4], 16), int(rgb[4:6], 16)


def _to_hex(rgb: tuple[int, int, int]) -> str:
    return "#{:02X}{:02X}{:02X}".format(*rgb)


def blend_over(fg_hex: str, bg_hex: str, alpha: float) -> str:
    """Alpha-blend fg over bg, returning a solid hex.

    Solid fills survive every SVG→DrawingML converter identically, unlike
    rgba()/fill-opacity which some paths flatten differently. Charts sit on
    the slide background, so blending over colors.bg reproduces the T4
    opacity-ladder appearance exactly.
    """
    fr, fg_, fb = _parse_hex(fg_hex, "blend.fg")
    br, bg_, bb = _parse_hex(bg_hex, "blend.bg")
    a = max(0.0, min(1.0, alpha))
    return _to_hex((
        round(fr * a + br * (1 - a)),
        round(fg_ * a + bg_ * (1 - a)),
        round(fb * a + bb * (1 - a)),
    ))


def relative_luminance(hex_color: str) -> float:
    r, g, b = (c / 255.0 for c in _parse_hex(hex_color, "luminance"))
    def lin(c: float) -> float:
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


class TypeScale:
    __slots__ = ("size", "weight", "line_height", "letter_spacing", "transform")

    def __init__(self, raw: dict[str, Any], role: str):
        try:
            self.size = float(raw["size"])
            self.weight = int(raw["weight"])
            self.line_height = float(raw["line-height"])
        except (KeyError, TypeError, ValueError) as exc:
            raise TokenResolutionError(
                f"Theme typography.{role} is missing size/weight/line-height "
                f"(file: {THEME_ACTIVE_PATH})"
            ) from exc
        self.letter_spacing = float(raw.get("letter-spacing", 0.0))
        self.transform = raw.get("transform", "none")


class ChartStyle:
    """The style contract every renderer consumes. Built only from tokens."""

    def __init__(self, theme: dict[str, Any], source_path: Path):
        self.source_path = source_path
        self.theme_name = theme.get("name", "?")

        colors = theme.get("colors")
        if not isinstance(colors, dict):
            raise TokenResolutionError(
                f"Theme has no colors object (file: {source_path})")
        missing = [k for k in _REQUIRED_COLORS if not colors.get(k)]
        if missing:
            raise TokenResolutionError(
                f"Theme colors missing required tokens {missing} (file: {source_path}). "
                "Run theme-init to regenerate a contract-valid theme; chart-design "
                "does not substitute defaults.")
        for k in _REQUIRED_COLORS:
            _parse_hex(colors[k], k)  # validate eagerly
        self.color: dict[str, str] = {k: colors[k] for k in colors if isinstance(colors[k], str)}

        typo = theme.get("typography")
        if not isinstance(typo, dict) or not typo.get("font-chain"):
            raise TokenResolutionError(
                f"Theme typography.font-chain missing (file: {source_path})")
        self.font_chain: str = typo["font-chain"]
        self.type: dict[str, TypeScale] = {}
        for role in _REQUIRED_TYPE_ROLES:
            if role not in typo:
                raise TokenResolutionError(
                    f"Theme typography.{role} missing (file: {source_path})")
            self.type[role] = TypeScale(typo[role], role)

        stroke = theme.get("stroke") or {}
        for k in _REQUIRED_STROKES:
            if not isinstance(stroke.get(k), (int, float)):
                raise TokenResolutionError(
                    f"Theme stroke.{k} missing (file: {source_path})")
        self.stroke: dict[str, float] = {k: float(stroke[k]) for k in _REQUIRED_STROKES}

        radius = theme.get("radius") or {}
        for k in _REQUIRED_RADII:
            if not isinstance(radius.get(k), (int, float)):
                raise TokenResolutionError(
                    f"Theme radius.{k} missing (file: {source_path})")
        self.radius: dict[str, float] = {
            k: float(v) for k, v in radius.items() if isinstance(v, (int, float))}

        spacing = theme.get("spacing") or {}
        if not spacing:
            raise TokenResolutionError(f"Theme spacing missing (file: {source_path})")
        self.spacing: dict[str, float] = {
            k: float(v) for k, v in spacing.items() if isinstance(v, (int, float))}

        self.palette_mode: str = theme.get("palette_mode", "chromatic")
        self.card_style: str = (theme.get("surface") or {}).get("card_style", "hairline")

        # Pre-derived roles used across renderers.
        self.muted_fill = blend_over(self.color["text-secondary"], self.color["bg"], 0.30)
        self.grid_stroke = self.color["border"]
        self.axis_stroke = self.color["border-strong"]

    # -- palette derivation (the ONLY sources of series color) ----------------

    def series_paints(self, n: int) -> list[tuple[str, float]]:
        """T4 single-accent opacity ladder as (token_hex, opacity) paints.

        Multi-hue palettes are forbidden by slide-svg's anti-slop discipline;
        series are distinguished by opacity steps of the one accent token.
        Emitting the literal accent hex + fill-opacity keeps every color in the
        SVG a theme-palette hex, so svg_quality_checker's off-theme scan passes.
        """
        if n < 1:
            raise ValueError("series count must be >= 1")
        if n > MAX_SERIES:
            raise TokenResolutionError(
                f"{n} series requested but the single-accent ladder supports at "
                f"most {MAX_SERIES} (anti-slop Rule T4). Aggregate minor series "
                "(e.g. top-3 + '기타') or split the chart.")
        base = self.color["accent"]
        return [(base, a) for a in SERIES_ALPHA_LADDER[:n]]

    def series_palette(self, n: int) -> list[str]:
        """Ladder flattened to solid hex over bg — for contrast math and docs."""
        return [blend_over(hex_, self.color["bg"], a)
                for hex_, a in self.series_paints(n)]

    def paint_solid(self, paint: tuple[str, float]) -> str:
        """Visual result of a paint on the slide background (for contrast)."""
        return blend_over(paint[0], self.color["bg"], paint[1])

    @property
    def muted_paint(self) -> tuple[str, float]:
        """Non-focus fill per the rhetorical styling lock (text-secondary tint)."""
        return (self.color["text-secondary"], 0.30)

    def sequential_fill(self, t: float) -> str:
        """Intensity fill for heatmaps: accent alpha scaled by normalized t∈[0,1]."""
        a = 0.06 + max(0.0, min(1.0, t)) * 0.84
        return blend_over(self.color["accent"], self.color["bg"], a)

    def sequential_alpha(self, t: float) -> float:
        return 0.06 + max(0.0, min(1.0, t)) * 0.84

    def semantic(self, kind: str) -> str:
        """positive/negative/warning — only when color encodes data meaning."""
        if kind not in ("positive", "negative", "warning"):
            raise ValueError(f"unknown semantic color: {kind}")
        return self.color[kind]

    def contrast_text(self, fill_hex: str) -> str:
        """Pick readable text color (text vs surface) for a given fill."""
        return (self.color["surface"] if relative_luminance(fill_hex) < 0.35
                else self.color["text"])


def resolve_style(theme_path: str | Path | None = None) -> ChartStyle:
    """Load the active slide-svg theme and build the chart style contract.

    theme_path overrides the default only for testing; production callers use
    the active-theme render copy so charts always match the deck.
    """
    path = Path(theme_path) if theme_path else THEME_ACTIVE_PATH
    if not path.is_file():
        raise TokenResolutionError(
            f"slide-svg theme tokens not found: {path}\n"
            "chart-design inherits ALL style from the active slide-svg theme and "
            "has no built-in defaults. Fix: run theme-init "
            "(python3 .claude/skills/theme-init/scripts/init_theme.py --activate <preset>) "
            "so slide/references/theme-active.json exists, or pass --theme <path>.")
    try:
        theme = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise TokenResolutionError(
            f"Failed to parse theme tokens at {path}: {exc}") from exc
    if not isinstance(theme, dict):
        raise TokenResolutionError(f"Theme root is not an object (file: {path})")
    return ChartStyle(theme, path)
