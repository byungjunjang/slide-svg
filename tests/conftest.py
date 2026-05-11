"""Shared pytest fixtures and path setup for theme-init smoke tests.

The tests import the theme-init scripts as modules (no subprocess) so they
run quickly and surface real Python errors. The scripts live outside any
package, so we add their directory to sys.path here.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
THEME_INIT_SCRIPTS = REPO_ROOT / ".claude" / "skills" / "theme-init" / "scripts"
THEME_INIT_REFS = REPO_ROOT / ".claude" / "skills" / "theme-init" / "references"
SLIDE_SCRIPTS = REPO_ROOT / ".claude" / "skills" / "slide" / "scripts"
SLIDE_REFS = REPO_ROOT / ".claude" / "skills" / "slide" / "references"

sys.path.insert(0, str(THEME_INIT_SCRIPTS))
sys.path.insert(0, str(SLIDE_SCRIPTS))


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture(scope="session")
def jangpm_theme() -> dict:
    """The live Jangpm theme — used as a known-good baseline."""
    return json.loads((SLIDE_REFS / "theme-active.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def token_contract() -> dict:
    return json.loads((THEME_INIT_REFS / "token-contract.json").read_text(encoding="utf-8"))


@pytest.fixture
def carbon_partial() -> dict:
    """A minimal IBM-Carbon-like partial draft — exercises the agent's typical
    extraction shape (theme identity + colors + font-chain + voice; numeric
    scales left null for fill_theme_defaults to populate).
    """
    return {
        "version": "1.0",
        "name": "ibm-carbon-test",
        "display_name": "IBM Carbon (test)",
        "description": "Carbon white theme — fixture",
        "colors": {
            "bg":             "#FFFFFF",
            "surface":        "#FFFFFF",
            "surface-alt":    "#F4F4F4",
            "text":           "#161616",
            "text-secondary": "#525252",
            "text-tertiary":  "#8D8D8D",
            "border":         "#E0E0E0",
            "border-strong":  "#C6C6C6",
            "accent":         "#0F62FE",
            "accent-soft":    "#EDF5FF",
            "accent-ink":     "#0043CE",
            "positive":       "#24A148",
            "positive-soft":  "#DEFBE6",
            "negative":       "#DA1E28",
            "negative-soft":  "#FFF1F1",
            "warning":        "#F1C21B",
            "warning-soft":   "#FCF4D6",
        },
        "typography": {
            "font-chain": "'IBM Plex Sans', Arial, sans-serif",
            "display": None, "display-sm": None, "headline": None,
            "title": None, "body": None, "caption": None, "label": None,
        },
        "radius": None, "stroke": None, "spacing": None,
        "assets": {
            "icon-pack-default":  "tabler-outline",
            "icon-pack-fallback": "tabler-filled",
            "character": None,
        },
        "voice": {
            "tone": "technical, declarative",
            "pov": "third-person engineering",
            "register": "Korean technical lecture",
            "forbidden_phrases": [],
            "gm_style_hint": "One declarative engineering takeaway."
        },
    }
