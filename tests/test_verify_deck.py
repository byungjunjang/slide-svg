"""Tests for the hard-fail deck verification gate (pure helpers + orchestrator)."""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / ".claude" / "skills" / "slide" / "scripts"))

import verify_deck as vd  # noqa: E402

GM_TEXT = '<text x="640" y="680" text-anchor="middle" fill="#6B7280">so-what</text>'
CANVAS = '<svg viewBox="0 0 1280 720">'


class TestGm:
    def test_detects_gm_line(self):
        assert vd.svg_has_gm(CANVAS + GM_TEXT + "</svg>") is True

    def test_no_gm_when_text_is_not_bottom_centered(self):
        body = '<text x="100" y="120" text-anchor="start">title</text>'
        assert vd.svg_has_gm(CANVAS + body + "</svg>") is False


class TestCanvas:
    def test_viewbox_ok(self):
        assert vd.svg_canvas_ok('<svg viewBox="0 0 1280 720"></svg>') is True

    def test_wrong_size_flagged(self):
        assert vd.svg_canvas_ok('<svg viewBox="0 0 1920 1080"></svg>') is False


class TestPlanRequirement:
    def test_eight_pages_needs_plan(self, tmp_path):
        out = tmp_path / "svg_output"
        out.mkdir()
        for i in range(8):
            (out / f"{i:02d}.svg").write_text(CANVAS + "</svg>", encoding="utf-8")
        assert vd.deck_needs_plan(tmp_path) is True

    def test_standalone_marker_overrides(self, tmp_path):
        out = tmp_path / "svg_output"
        out.mkdir()
        for i in range(8):
            (out / f"{i:02d}.svg").write_text(CANVAS + "</svg>", encoding="utf-8")
        (tmp_path / ".standalone").write_text("", encoding="utf-8")
        assert vd.deck_needs_plan(tmp_path) is False


class TestOrchestrator:
    def _good_deck(self, root: Path, n: int = 4) -> Path:
        proj = root / "deck"
        for sub in ("svg_output", "svg_final", "images"):
            (proj / sub).mkdir(parents=True)
        for i in range(n):
            (proj / "svg_output" / f"{i:02d}.svg").write_text(
                CANVAS + GM_TEXT + "</svg>", encoding="utf-8")
            (proj / "svg_final" / f"{i:02d}.svg").write_text(
                CANVAS + GM_TEXT + "</svg>", encoding="utf-8")
        (proj / "deck.pptx").write_bytes(b"PK\x03\x04stub")
        return proj

    def test_good_small_deck_passes_core_checks(self, tmp_path, monkeypatch):
        proj = self._good_deck(tmp_path)
        monkeypatch.setattr(vd, "_run_quality_checker", lambda d: 0)
        monkeypatch.setattr(vd, "_sync_check", lambda: 0)
        failures = vd.run_checks(proj)
        assert failures == [], failures

    def test_missing_gm_fails(self, tmp_path, monkeypatch):
        proj = self._good_deck(tmp_path)
        for p in (proj / "svg_output").glob("*.svg"):
            p.write_text(CANVAS + "</svg>", encoding="utf-8")  # strip gm
        monkeypatch.setattr(vd, "_run_quality_checker", lambda d: 0)
        monkeypatch.setattr(vd, "_sync_check", lambda: 0)
        failures = vd.run_checks(proj)
        assert any("governing-message" in f for f in failures)

    def test_stage_parity_mismatch_fails(self, tmp_path, monkeypatch):
        proj = self._good_deck(tmp_path)
        next(iter((proj / "svg_final").glob("*.svg"))).unlink()  # drop one final page
        monkeypatch.setattr(vd, "_run_quality_checker", lambda d: 0)
        monkeypatch.setattr(vd, "_sync_check", lambda: 0)
        failures = vd.run_checks(proj)
        assert any("svg_final" in f for f in failures)
