#!/usr/bin/env python3
"""Pre-pipeline environment gate. Fails loudly so a host cannot start a deck
with a broken toolchain (which is what leads to silent fallbacks).

Usage:
    python3 .claude/skills/slide/scripts/preflight.py [--needs-images]
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent     # .../slide/scripts
REPO_ROOT = HERE.parents[3]                 # scripts->slide->skills->.claude->repo
REQUIREMENTS = HERE.parent / "requirements.txt"


def check_python_deps() -> list[str]:
    fails = []
    for mod in ("pptx", "PIL"):
        try:
            __import__(mod)
        except Exception:
            fails.append(f"missing Python dep '{mod}' — pip install -r {REQUIREMENTS}")
    return fails


def check_assets() -> list[str]:
    fails = []
    if not (REPO_ROOT / "assets" / "fonts").is_dir():
        fails.append("assets/fonts missing")
    if not (REPO_ROOT / "assets" / "icons").is_dir():
        fails.append("assets/icons missing (Claude Code full-library mode)")
    return fails


def check_codex_image() -> list[str]:
    """codex CLI login status. Failure halts image-bearing decks rather than
    silently producing placeholder art."""
    exe = shutil.which("codex")
    if not exe:
        return ["codex CLI not found — image generation unavailable "
                "(install @openai/codex, then `codex login`)"]
    try:
        r = subprocess.run([exe, "login", "status"], capture_output=True,
                           text=True, timeout=30)
    except Exception as e:  # noqa: BLE001
        return [f"`codex login status` failed to run: {e}"]
    blob = (r.stdout + r.stderr).lower()
    if r.returncode != 0 or "logged in" not in blob:
        return ["codex not logged in — run `codex login` (no placeholder fallback allowed)"]
    return []


def check_mirror() -> list[str]:
    sync = HERE / "dev" / "sync_codex_mirror.py"
    if sync.exists() and subprocess.run([sys.executable, str(sync), "--check"]).returncode != 0:
        return [".codex/skills mirror stale — run sync_codex_mirror.py"]
    return []


def main() -> int:
    ap = argparse.ArgumentParser(description="Pre-pipeline environment gate.")
    ap.add_argument("--needs-images", action="store_true",
                    help="Also require codex-image login.")
    args = ap.parse_args()
    fails = check_python_deps() + check_assets() + check_mirror()
    if args.needs_images:
        fails += check_codex_image()
    if fails:
        sys.stderr.write("[preflight] FAIL:\n")
        for f in fails:
            sys.stderr.write(f"  ✗ {f}\n")
        return 1
    print("[preflight] PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
