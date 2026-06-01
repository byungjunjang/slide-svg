"""Tests for the pre-pipeline environment gate."""
from __future__ import annotations

import subprocess
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


def test_codex_image_passes_when_logged_in(monkeypatch):
    monkeypatch.setattr(pf.shutil, "which", lambda _: "/usr/bin/codex")
    result = subprocess.CompletedProcess([], 0, stdout="", stderr="Logged in using ChatGPT\n")
    monkeypatch.setattr(pf.subprocess, "run", lambda *a, **kw: result)
    assert pf.check_codex_image() == []


def test_codex_image_fails_when_not_logged_in(monkeypatch):
    monkeypatch.setattr(pf.shutil, "which", lambda _: "/usr/bin/codex")
    result = subprocess.CompletedProcess([], 1, stdout="", stderr="Not logged in.\n")
    monkeypatch.setattr(pf.subprocess, "run", lambda *a, **kw: result)
    fails = pf.check_codex_image()
    assert fails and "codex login" in fails[0]


def test_codex_image_fails_when_rc0_but_no_auth_phrase(monkeypatch):
    monkeypatch.setattr(pf.shutil, "which", lambda _: "/usr/bin/codex")
    result = subprocess.CompletedProcess([], 0, stdout="Session active.", stderr="")
    monkeypatch.setattr(pf.subprocess, "run", lambda *a, **kw: result)
    fails = pf.check_codex_image()
    assert fails  # rc=0 but no recognized auth phrase
