"""Tests for the generated .codex/skills mirror and its drift guard."""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / ".claude" / "skills" / "slide" / "scripts" / "dev"))

import sync_codex_mirror as scm  # noqa: E402


class TestTransform:
    def test_rewrites_path_token_in_text_file(self):
        out = scm._transform_bytes(Path("x.md"), b"run .claude/skills/slide/x")
        assert out == b"run .codex/skills/slide/x"

    def test_leaves_binary_untouched(self):
        raw = b"\x89PNG.claude/skills"
        assert scm._transform_bytes(Path("logo.png"), raw) == raw

    def test_leaves_unrelated_text_unchanged(self):
        out = scm._transform_bytes(Path("x.py"), b"# the .claude dir")
        assert out == b"# the .claude dir"  # only the combined token is rewritten

    def test_unicode_decode_error_falls_back_to_raw(self):
        raw = b"\xff\xfe.claude/skills"  # invalid UTF-8
        assert scm._transform_bytes(Path("x.md"), raw) == raw


class TestMirrorInSync:
    def test_codex_mirror_is_current(self):
        """The committed .codex/skills must match a fresh regeneration.
        Fails if someone edited .claude/skills without re-running sync."""
        assert scm.check() == 0, (
            "Run: python3 .claude/skills/slide/scripts/dev/sync_codex_mirror.py"
        )

    def test_mirror_root_exists(self):
        assert (REPO_ROOT / ".codex" / "skills" / "slide" / "SKILL.md").is_file()
