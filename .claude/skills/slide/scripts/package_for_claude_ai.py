#!/usr/bin/env python3
"""
Package the /slide skill into an upload-ready zip for claude.ai.

What this produces:
    output/slide-skill-claude-ai.zip
        SKILL.md
        scripts/...
        templates/...
        references/...
        workflows/...

What it enforces:
    - No nested .zip files inside the bundle (claude.ai rejects zip-in-zip).
    - File count under the claude.ai 200-file upload limit.

Why the icon library is *not* included:
    The full Tabler icon library lives outside the skill folder at
    ${REPO_ROOT}/assets/icons/<lib>/<name>.svg. It is intentionally NOT bundled
    here — embedding 6000+ files would blow past the 200-file limit. The skill
    ships ~20 essentials at templates/icons/tabler-outline/ for claude.ai use,
    and embed_icons.py emits a [WARN] then skips when an icon is unavailable.

Why fonts are *not* bundled by default:
    Bundling .ttf files in a claude.ai skill upload does not install fonts on
    the user's machine — the resulting PPTX still falls back to whatever's
    installed locally. The font files are dead weight in the upload bundle.
    They are still kept under repo-root assets/fonts/ for separate (manual)
    distribution; pass --include-fonts if you want them in the upload anyway.

Usage:
    python3 .claude/skills/slide/scripts/package_for_claude_ai.py
    python3 .claude/skills/slide/scripts/package_for_claude_ai.py --include-fonts
    python3 .claude/skills/slide/scripts/package_for_claude_ai.py --output my.zip
"""

from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path


# Path layout: <repo>/.claude/skills/slide/scripts/package_for_claude_ai.py
#   parents[0] = .../scripts
#   parents[1] = .../slide        (skill root)
#   parents[4] = repo root
SKILL_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[4]

CLAUDE_AI_FILE_LIMIT = 200
DEFAULT_OUTPUT = REPO_ROOT / 'output' / 'slide-skill-claude-ai.zip'


def collect_skill_files() -> list[Path]:
    """All files under the skill folder, excluding compiled artifacts."""
    files: list[Path] = []
    for p in SKILL_ROOT.rglob('*'):
        if not p.is_file():
            continue
        # Skip Python compiled cruft.
        if '__pycache__' in p.parts or p.suffix in {'.pyc', '.pyo'}:
            continue
        files.append(p)
    return files


def collect_font_files() -> list[Path]:
    fonts_dir = REPO_ROOT / 'assets' / 'fonts'
    if not fonts_dir.exists():
        return []
    return [p for p in fonts_dir.rglob('*') if p.is_file()]


def validate(skill_files: list[Path], font_files: list[Path]) -> list[str]:
    errors: list[str] = []

    # Reject any nested zip files in the skill payload.
    nested_zips = [p for p in skill_files if p.suffix == '.zip']
    if nested_zips:
        errors.append(
            f"Skill contains {len(nested_zips)} nested .zip file(s) — claude.ai rejects these:\n"
            + "\n".join(f"    {p.relative_to(SKILL_ROOT)}" for p in nested_zips)
        )

    total = len(skill_files) + len(font_files)
    if total > CLAUDE_AI_FILE_LIMIT:
        errors.append(
            f"Bundle has {total} files (skill {len(skill_files)} + fonts {len(font_files)}); "
            f"claude.ai limit is {CLAUDE_AI_FILE_LIMIT}."
        )

    return errors


def build_zip(output: Path, skill_files: list[Path], font_files: list[Path]) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as zf:
        for p in skill_files:
            arcname = p.relative_to(SKILL_ROOT).as_posix()
            zf.write(p, arcname=arcname)
        for p in font_files:
            arcname = ('assets/fonts/' + p.relative_to(REPO_ROOT / 'assets' / 'fonts').as_posix())
            zf.write(p, arcname=arcname)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--output', type=Path, default=DEFAULT_OUTPUT,
                        help=f'Output zip path (default: {DEFAULT_OUTPUT})')
    parser.add_argument('--include-fonts', action='store_true',
                        help='Bundle assets/fonts/ into the upload. Off by default — font files do '
                             'not install on the recipient via a claude.ai upload, so they are dead '
                             'weight in the bundle. Useful only if you intend to distribute the zip '
                             'manually to someone who will install the fonts.')
    args = parser.parse_args()

    skill_files = collect_skill_files()
    font_files = collect_font_files() if args.include_fonts else []

    print(f"[SCAN] skill files:  {len(skill_files)}  (under {SKILL_ROOT})")
    print(f"[SCAN] font files:   {len(font_files)}  ({REPO_ROOT / 'assets' / 'fonts' if args.include_fonts else 'skipped (use --include-fonts to bundle)'})")

    # Warn if the external full icon library is missing — Claude Code mode
    # will silently fall back to the bundled essentials. Not a build error.
    icons_dir = REPO_ROOT / 'assets' / 'icons'
    if not icons_dir.exists():
        print(f"[WARN] {icons_dir} is absent; Claude Code runs will use only the bundled essentials.")

    errors = validate(skill_files, font_files)
    if errors:
        print()
        print("[FAIL] Validation errors:")
        for e in errors:
            print(f"  - {e}")
        return 1

    build_zip(args.output, skill_files, font_files)
    size_mb = args.output.stat().st_size / 1024 / 1024
    print()
    print(f"[OK] Wrote {args.output}  ({size_mb:.2f} MB, {len(skill_files) + len(font_files)} files)")
    print(f"     Drop this into claude.ai's skill uploader.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
