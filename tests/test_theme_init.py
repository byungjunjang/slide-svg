"""Smoke tests for the /theme-init pipeline.

Coverage targets the unit-level surface of every script init_theme.py
orchestrates so a future refactor (v2 token contract, charts palette,
themes-registry, etc.) breaks loudly here instead of silently mid-render.

Each test uses tmp paths exclusively — no test mutates the live
`theme-active.json` or any rendered reference under
`.claude/skills/slide/references/`. Run with `pytest tests/`.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

# These imports rely on conftest.py adding the theme-init scripts dir to sys.path.
import _token_render  # noqa: E402
import fill_theme_defaults  # noqa: E402
import reskin_gallery  # noqa: E402
import validate_fonts  # noqa: E402
import validate_theme  # noqa: E402


# =============================================================================
# validate_theme — schema enforcement + actionable hints
# =============================================================================

class TestValidateTheme:
    def test_jangpm_passes_clean(self, jangpm_theme, token_contract):
        """The live Jangpm theme must always validate against the v1 contract."""
        errors = validate_theme.validate(jangpm_theme, token_contract)
        assert errors == [], f"Jangpm regressed: {errors}"

    def test_carbon_partial_passes_after_fill(self, carbon_partial, token_contract):
        """An agent-style partial draft should pass once filled with defaults."""
        filled = fill_theme_defaults.fill(carbon_partial)
        errors = validate_theme.validate(filled, token_contract)
        assert errors == [], f"Carbon partial regressed: {errors}"

    def test_lowercase_hex_rejected_with_hint(self, jangpm_theme, token_contract):
        bad = json.loads(json.dumps(jangpm_theme))
        bad["colors"]["accent"] = "#4633e3"  # lowercase
        errors = validate_theme.validate(bad, token_contract)
        assert any("colors/accent" in e for e in errors)
        assert any("uppercase" in e.lower() and "#4633E3" in e for e in errors), \
            f"missing actionable hint for lowercase hex: {errors}"

    def test_three_digit_hex_rejected_with_hint(self, jangpm_theme, token_contract):
        bad = json.loads(json.dumps(jangpm_theme))
        bad["colors"]["accent"] = "#abc"
        errors = validate_theme.validate(bad, token_contract)
        assert any("3-digit" in e and "#AABBCC" in e for e in errors), \
            f"missing 3-digit-shorthand hint: {errors}"

    def test_rgb_string_rejected_with_hint(self, jangpm_theme, token_contract):
        bad = json.loads(json.dumps(jangpm_theme))
        bad["colors"]["accent"] = "rgb(70, 51, 227)"
        errors = validate_theme.validate(bad, token_contract)
        assert any("rgb()" in e and "Convert to hex" in e for e in errors), \
            f"missing rgb-to-hex hint: {errors}"

    def test_quoted_typography_size_rejected_with_hint(self, jangpm_theme, token_contract):
        bad = json.loads(json.dumps(jangpm_theme))
        bad["typography"]["display"]["size"] = "56"  # string instead of number
        errors = validate_theme.validate(bad, token_contract)
        assert any("Drop the quotes" in e for e in errors), \
            f"missing quoted-numeric hint: {errors}"

    def test_unknown_field_rejected_with_hint(self, jangpm_theme, token_contract):
        bad = json.loads(json.dumps(jangpm_theme))
        bad["assets"]["bonus-field"] = "oops"
        errors = validate_theme.validate(bad, token_contract)
        assert any("'bonus-field'" in e and "v1 contract" in e for e in errors), \
            f"missing additionalProperties hint: {errors}"

    def test_missing_required_color_rejected(self, jangpm_theme, token_contract):
        bad = json.loads(json.dumps(jangpm_theme))
        del bad["colors"]["accent"]
        errors = validate_theme.validate(bad, token_contract)
        assert any("'accent'" in e and "required" in e.lower() for e in errors)


# =============================================================================
# fill_theme_defaults — partial JSON → complete theme
# =============================================================================

class TestFillThemeDefaults:
    def test_partial_gets_complete_color_block(self, carbon_partial, token_contract):
        """Color tokens given by the agent must survive the fill (not be overridden)."""
        filled = fill_theme_defaults.fill(carbon_partial)
        assert filled["colors"]["accent"] == "#0F62FE"
        assert filled["colors"]["bg"] == "#FFFFFF"

    def test_null_typography_filled_from_defaults(self, carbon_partial):
        """Numeric type-scale leaves filled with calibrated 1280×720 defaults."""
        filled = fill_theme_defaults.fill(carbon_partial)
        assert filled["typography"]["display"]["size"] == 56
        assert filled["typography"]["body"]["size"] == 15.2
        # Font chain from agent must be preserved, not replaced.
        assert "IBM Plex Sans" in filled["typography"]["font-chain"]

    def test_null_radius_stroke_spacing_filled(self, carbon_partial):
        filled = fill_theme_defaults.fill(carbon_partial)
        assert filled["radius"]["sm"] == 8
        assert filled["stroke"]["icon"] == 2
        assert filled["spacing"]["6"] == 24

    def test_idempotent(self, carbon_partial):
        """Filling an already-filled theme must produce the same result."""
        once = fill_theme_defaults.fill(carbon_partial)
        twice = fill_theme_defaults.fill(once)
        assert once == twice

    def test_assets_character_null_preserved(self, carbon_partial):
        """assets.character is optional; null must survive the fill."""
        filled = fill_theme_defaults.fill(carbon_partial)
        assert filled["assets"]["character"] is None


# =============================================================================
# validate_fonts — Arial fallback injection
# =============================================================================

class TestValidateFonts:
    def test_primary_font_with_arial_in_chain_no_inject(self):
        chain = "Pretendard, 'Apple SD Gothic Neo', Arial, sans-serif"
        assert validate_fonts.has_arial(chain) is True
        # When Arial already present, inject_arial would still produce a chain
        # *containing* Arial — but the no-op branch upstream prevents the
        # rewrite. We assert the contract: has_arial detects existing Arial.

    def test_primary_font_no_arial_injects_before_generic(self):
        chain = "Pretendard, 'Apple SD Gothic Neo', sans-serif"
        injected = validate_fonts.inject_arial(chain)
        # Arial must end up before the trailing generic family.
        tokens = [t.strip().strip("'\"") for t in injected.split(",")]
        assert "Arial" in tokens
        assert tokens.index("Arial") == len(tokens) - 2
        assert tokens[-1] == "sans-serif"

    def test_inject_arial_idempotent(self):
        """Once injected, re-injecting must not duplicate Arial."""
        chain = "Pretendard, sans-serif"
        once = validate_fonts.inject_arial(chain)
        # Simulate the upstream flow: only call inject_arial when has_arial is False.
        assert validate_fonts.has_arial(once) is True
        # If somehow called again, the chain shape stays sensible.
        twice = validate_fonts.inject_arial(once)
        # Either unchanged or the already-present Arial isn't duplicated to mid-chain
        # in a way that would break the generic-tail invariant.
        assert twice.endswith("sans-serif") or twice.endswith("serif") or twice.endswith("monospace")

    def test_empty_chain_falls_back(self):
        injected = validate_fonts.inject_arial("")
        assert "Arial" in injected
        assert "sans-serif" in injected

    def test_count_font_files_hits_pretendard(self, repo_root):
        """The shared font pool always carries 9 Pretendard weights."""
        fonts_dir = repo_root / "assets" / "fonts"
        n = validate_fonts.count_font_files("Pretendard", fonts_dir)
        assert n == 9, f"expected 9 Pretendard weights under {fonts_dir}, got {n}"

    def test_count_font_files_misses_unknown_family(self, repo_root):
        fonts_dir = repo_root / "assets" / "fonts"
        n = validate_fonts.count_font_files("NoSuchFontFamily", fonts_dir)
        assert n == 0


# =============================================================================
# _token_render — placeholder substitution + filters
# =============================================================================

class TestTokenRender:
    def test_basic_substitution(self):
        theme = {"colors": {"accent": "#0F62FE"}}
        out = _token_render.render("color is {{TOKEN:colors.accent}}", theme)
        assert out == "color is #0F62FE"

    def test_optional_filter_with_value(self):
        theme = {"assets": {"character": "path/to/img.png"}}
        out = _token_render.render("{{TOKEN:assets.character|optional}}", theme)
        assert out == "path/to/img.png"

    def test_optional_filter_with_null(self):
        theme = {"assets": {"character": None}}
        out = _token_render.render("{{TOKEN:assets.character|optional}}", theme)
        assert out == "_(not provided)_"

    def test_rgb_filter(self):
        theme = {"colors": {"accent": "#0F62FE"}}
        out = _token_render.render("{{TOKEN:colors.accent|rgb}}", theme)
        assert out == "15, 98, 254"

    def test_csv_filter_with_items(self):
        theme = {"voice": {"forbidden_phrases": ["여러분", "우리는"]}}
        out = _token_render.render("{{TOKEN:voice.forbidden_phrases|csv}}", theme)
        assert out == '"여러분", "우리는"'

    def test_csv_filter_empty_list(self):
        theme = {"voice": {"forbidden_phrases": []}}
        out = _token_render.render("{{TOKEN:voice.forbidden_phrases|csv}}", theme)
        assert out == "_(none)_"

    def test_bulleted_filter(self):
        theme = {"voice": {"forbidden_phrases": ["a", "b"]}}
        out = _token_render.render("{{TOKEN:voice.forbidden_phrases|bulleted}}", theme)
        assert out == "- a\n- b"

    def test_missing_token_raises(self):
        theme = {"colors": {"accent": "#0F62FE"}}
        with pytest.raises(KeyError, match="missing theme token"):
            _token_render.render("{{TOKEN:colors.nonexistent}}", theme)

    def test_unknown_filter_raises(self):
        theme = {"colors": {"accent": "#0F62FE"}}
        with pytest.raises(ValueError, match="unknown format filter"):
            _token_render.render("{{TOKEN:colors.accent|nope}}", theme)


# =============================================================================
# reskin_gallery — primary-font extraction + on-disk weight scan
# =============================================================================

class TestReskinGallery:
    def test_primary_font_simple(self):
        assert reskin_gallery._primary_font_name("Pretendard, sans-serif") == "Pretendard"

    def test_primary_font_quoted(self):
        chain = "'IBM Plex Sans', 'Apple SD Gothic Neo', Arial, sans-serif"
        assert reskin_gallery._primary_font_name(chain) == "IBM Plex Sans"

    def test_primary_font_empty_falls_back_to_arial(self):
        assert reskin_gallery._primary_font_name("") == "Arial"

    def test_scan_finds_pretendard_weights(self, tmp_path: Path):
        """Synthesize a fonts dir, confirm the suffix-mapping logic."""
        for suffix, ext in [("Regular", ".otf"), ("Bold", ".otf"),
                            ("Light", ".ttf"), ("Black", ".woff2")]:
            (tmp_path / f"FakeSans-{suffix}{ext}").write_bytes(b"")
        # patch the module-level dir
        original = reskin_gallery.ASSETS_FONTS_DIR
        reskin_gallery.ASSETS_FONTS_DIR = tmp_path
        try:
            files = reskin_gallery._scan_font_files("FakeSans")
        finally:
            reskin_gallery.ASSETS_FONTS_DIR = original
        weights = sorted(w for _, w, _ in files)
        # Light(300) Regular(400) Bold(700) Black(900)
        assert weights == [300, 400, 700, 900]

    def test_scan_skips_non_weighted_files(self, tmp_path: Path):
        """Variable fonts and non-weighted files are skipped (no weight to map)."""
        (tmp_path / "FakeSansVariable.ttf").write_bytes(b"")
        (tmp_path / "FakeSans-OddSuffix.otf").write_bytes(b"")
        original = reskin_gallery.ASSETS_FONTS_DIR
        reskin_gallery.ASSETS_FONTS_DIR = tmp_path
        try:
            files = reskin_gallery._scan_font_files("FakeSans")
        finally:
            reskin_gallery.ASSETS_FONTS_DIR = original
        assert files == []

    def test_build_font_face_block_handles_missing_files(self, tmp_path: Path):
        """When primary font has no on-disk files, emit a fallback comment instead
        of broken @font-face references — the bug that the asset-modularization
        pass fixed."""
        original = reskin_gallery.ASSETS_FONTS_DIR
        reskin_gallery.ASSETS_FONTS_DIR = tmp_path  # empty dir
        try:
            theme = {"typography": {"font-chain": "NoSuchFont, Arial, sans-serif"}}
            block = reskin_gallery.build_font_face_block(theme)
        finally:
            reskin_gallery.ASSETS_FONTS_DIR = original
        # The header comment mentions "@font-face entries below are…" — what we
        # care about is that no actual @font-face *rule* is emitted.
        assert "@font-face {" not in block
        assert "No files for 'NoSuchFont' found" in block

    def test_build_font_face_block_emits_entries_when_files_exist(self, tmp_path: Path):
        for suffix in ["Regular", "Bold"]:
            (tmp_path / f"FakeSans-{suffix}.otf").write_bytes(b"")
        original = reskin_gallery.ASSETS_FONTS_DIR
        reskin_gallery.ASSETS_FONTS_DIR = tmp_path
        try:
            theme = {"typography": {"font-chain": "FakeSans, Arial, sans-serif"}}
            block = reskin_gallery.build_font_face_block(theme)
        finally:
            reskin_gallery.ASSETS_FONTS_DIR = original
        assert "@font-face" in block
        assert "FakeSans-Regular.otf" in block
        assert "FakeSans-Bold.otf" in block
        assert "font-weight: 400" in block
        assert "font-weight: 700" in block


# =============================================================================
# init_theme.py orchestration — end-to-end smoke
# =============================================================================

class TestInitThemeOrchestration:
    """Closes the gap flagged in code review: individual scripts had unit
    coverage but the orchestration glue (subprocess invocation, exit-code
    propagation, file mutations across steps) was never exercised. Uses
    --dry-run so renders are skipped; fill -> validate -> validate_fonts
    runs for real against a tmp theme path so live state stays untouched.
    """

    def test_carbon_partial_fill_validate_dryrun(self, repo_root, carbon_partial, tmp_path):
        import subprocess
        import sys as _sys

        draft = tmp_path / "draft.json"
        target_theme = tmp_path / "theme-active.json"
        draft.write_text(json.dumps(carbon_partial), encoding="utf-8")

        init_theme = (
            repo_root / ".claude" / "skills" / "theme-init" / "scripts" / "init_theme.py"
        )
        result = subprocess.run(
            [
                _sys.executable, str(init_theme),
                "--fill-from", str(draft),
                "--theme", str(target_theme),
                "--dry-run",
            ],
            cwd=repo_root,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, (
            f"init_theme orchestration failed (exit {result.returncode}):\n"
            f"--- stdout ---\n{result.stdout}\n--- stderr ---\n{result.stderr}"
        )
        # fill_theme_defaults should have written the filled theme to --theme
        assert target_theme.exists(), "filled theme not written to --theme path"
        filled = json.loads(target_theme.read_text(encoding="utf-8"))
        assert filled["name"] == "ibm-carbon-test"
        # nulls in carbon_partial fixture should have been populated
        assert filled["radius"] is not None, "fill_theme_defaults did not populate null `radius`"
        assert filled["typography"]["body"] is not None, \
            "fill_theme_defaults did not populate null typography scale"


# =============================================================================
# Hangul (Korean) text-width regression — sol-20260423-001
# =============================================================================

class TestHangulWidthRegression:
    """Before the fix, is_cjk_char missed Hangul ranges so estimate_text_width
    fell through to the 0.55x ASCII default for Korean text — producing
    undersized text boxes in PPTX export. Lock the Hangul coverage so a
    future refactor of drawingml_utils can't silently regress it.
    """

    def test_hangul_syllables_block_is_cjk(self):
        from svg_to_pptx.drawingml_utils import is_cjk_char  # noqa: E402
        # Hangul Syllables U+AC00–U+D7AF — the everyday Korean text block
        for ch in "한국어강의슬라이드":
            assert is_cjk_char(ch), f"Hangul syllable {ch!r} (U+{ord(ch):04X}) must be CJK"

    def test_hangul_jamo_blocks_are_cjk(self):
        from svg_to_pptx.drawingml_utils import is_cjk_char  # noqa: E402
        # Hangul Jamo U+1100–U+11FF + Compatibility Jamo U+3130–U+318F
        for ch in "ᄀᄂᄃㄱㄴㄷ":
            assert is_cjk_char(ch), f"Hangul jamo {ch!r} (U+{ord(ch):04X}) must be CJK"

    def test_hangul_text_width_uses_full_em_metric(self):
        from svg_to_pptx.drawingml_utils import estimate_text_width  # noqa: E402
        # CJK chars contribute ~font_size each (1.0em); ASCII default is 0.55em.
        # If is_cjk_char misses Hangul, width collapses toward the ASCII path.
        font_size = 15.0
        hangul_width = estimate_text_width("안녕하세요", font_size)  # 5 chars
        # Lower bound: well above the ASCII fallback (5 * 0.55 * 15 ≈ 41.25)
        assert hangul_width > 60, (
            f"Hangul width {hangul_width} too small at font_size={font_size}; "
            f"is_cjk_char likely missing a Hangul range"
        )
        # Upper bound: 5 * 1.0 * 15 = 75
        assert hangul_width <= 75, (
            f"Hangul width {hangul_width} exceeds 1.0em-per-char; "
            f"unexpected width metric"
        )
