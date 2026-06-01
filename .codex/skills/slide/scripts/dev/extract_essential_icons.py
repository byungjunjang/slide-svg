#!/usr/bin/env python3
"""
Sync the bundled "essentials" icon subset into the skill folder.

Why this exists:
    The full Tabler library lives outside the skill folder at
    ${REPO_ROOT}/assets/icons/<lib>/<name>.svg. That tree is too big to ship
    inside a claude.ai skill upload (>200 files, and the recent claude.ai
    upload validation also rejects nested zips). This script copies a small
    curated subset into ${SKILL_DIR}/templates/icons/<lib>/<name>.svg so the
    skill stays usable even when the external library is absent — i.e. when
    the skill has been uploaded to claude.ai by itself.

Usage:
    python3 .codex/skills/slide/scripts/dev/extract_essential_icons.py

Idempotent. Safe to re-run after editing the whitelist below.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path


# Path layout: <repo>/.codex/skills/slide/scripts/dev/extract_essential_icons.py
#   parents[0] = .../scripts/dev
#   parents[2] = .../slide          (skill root)
#   parents[5] = repo root
SKILL_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = Path(__file__).resolve().parents[5]

SOURCE_ROOT = REPO_ROOT / 'assets' / 'icons'
DEST_ROOT = SKILL_ROOT / 'templates' / 'icons'


# Essentials whitelist. Pick the smallest set that lets a typical Jangpm deck
# render readable icons in claude.ai mode. Edit and re-run to sync.
ESSENTIALS: dict[str, list[str]] = {
    'tabler-outline': [
        'arrow-right',
        'arrow-left',
        'check',
        'x',
        'plus',
        'minus',
        'chevron-right',
        'chevron-down',
        'bulb',
        'target',
        'chart-bar',
        'chart-line',
        'message-circle',
        'mail',
        'calendar',
        'clock',
        'user',
        'users',
        'search',
        'info-circle',
    ],
}


def sync_library(lib: str, names: list[str]) -> tuple[int, int]:
    """Copy each whitelisted SVG from SOURCE_ROOT/lib/ into DEST_ROOT/lib/.

    Returns (copied, missing). Missing means the source SVG was not found —
    indicates the whitelist drifted from the upstream library and should be
    fixed.
    """
    src_dir = SOURCE_ROOT / lib
    dst_dir = DEST_ROOT / lib
    if not src_dir.exists():
        print(f"[ERROR] Source library not found: {src_dir}")
        print(f"        Run the icon migration first (assets/icons/ must contain the full library).")
        return 0, len(names)

    dst_dir.mkdir(parents=True, exist_ok=True)

    copied = 0
    missing = 0
    for name in names:
        src = src_dir / f'{name}.svg'
        if not src.exists():
            print(f"[MISS] {lib}/{name} — not in source library")
            missing += 1
            continue
        dst = dst_dir / f'{name}.svg'
        shutil.copy2(src, dst)
        copied += 1

    return copied, missing


def main() -> int:
    print(f"[SRC] {SOURCE_ROOT}")
    print(f"[DST] {DEST_ROOT}")
    print()

    total_copied = 0
    total_missing = 0
    for lib, names in ESSENTIALS.items():
        copied, missing = sync_library(lib, names)
        print(f"  {lib}: {copied} copied, {missing} missing")
        total_copied += copied
        total_missing += missing

    print()
    print(f"[Summary] {total_copied} icon(s) synced to skill, {total_missing} missing")
    return 1 if total_missing else 0


if __name__ == '__main__':
    sys.exit(main())
