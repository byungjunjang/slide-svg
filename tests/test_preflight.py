"""Tests for the pre-pipeline environment gate."""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / ".claude" / "skills" / "slide" / "scripts"))

import preflight as pf  # noqa: E402


def test_python_deps_present():
    # pptx + PIL are in requirements.txt and installed in the dev venv
    assert pf.check_python_deps() == []


def test_assets_present():
    # full-library Claude Code checkout ships assets/fonts and assets/icons
    assert pf.check_assets() == []


def test_codex_image_reports_when_cli_missing(monkeypatch):
    monkeypatch.setattr(pf.shutil, "which", lambda _: None)
    fails = pf.check_codex_image()
    assert fails and "codex" in fails[0].lower()
