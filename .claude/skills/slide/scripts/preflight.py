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
REPO_ROOT = HERE.parents[3]                 # HERE=scripts → slide → skills → .claude → repo (4 hops)
REQUIREMENTS = HERE.parent / "requirements.txt"

# Auth-confirmation phrases emitted by `codex login status`. Heuristic on external
# CLI output — extend this tuple if a future codex build changes its wording.
LOGIN_OK_PHRASES = ("logged in", "authenticated", "authorized")
REQUIRED_PYTHON_MODULES = ("pptx", "PIL", "numpy")
CODEX_IMAGEGEN_NOTICE = (
    "Codex built-in imagegen availability is enforced at Image_Generator "
    "execution time"
)


def check_python_deps() -> list[str]:
    fails = []
    for mod in REQUIRED_PYTHON_MODULES:
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


def host_kind() -> str:
    parts = set(HERE.parts)
    if ".codex" in parts:
        return "codex"
    if ".claude" in parts:
        return "claude"
    return "unknown"


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
    if r.returncode != 0 or not any(p in blob for p in LOGIN_OK_PHRASES):
        return ["codex not logged in — run `codex login` (no placeholder fallback allowed)"]
    return []


def check_image_generation() -> list[str]:
    """Host-specific image gate.

    Claude Code uses the vendored /codex-image skill and can preflight the
    Codex CLI login. Codex uses its built-in imagegen skill; this Python script
    cannot introspect that tool, so Step 5 enforces availability when it calls
    imagegen.
    """
    if host_kind() == "codex":
        print(f"[preflight] INFO: {CODEX_IMAGEGEN_NOTICE}")
        return []
    return check_codex_image()


def check_mirror() -> list[str]:
    sync = HERE / "dev" / "sync_codex_mirror.py"
    if not sync.exists():
        return []
    try:
        r = subprocess.run([sys.executable, str(sync), "--check"],
                           capture_output=True, timeout=60)
    except Exception as e:  # noqa: BLE001
        return [f"mirror check failed to run: {e}"]
    if r.returncode != 0:
        return [".codex/skills mirror stale — run sync_codex_mirror.py"]
    return []


def main() -> int:
    ap = argparse.ArgumentParser(description="Pre-pipeline environment gate.")
    ap.add_argument("--needs-images", action="store_true",
                    help="Also require host image-generation readiness.")
    args = ap.parse_args()
    fails = check_python_deps() + check_assets() + check_mirror()
    if args.needs_images:
        fails += check_image_generation()
    if fails:
        sys.stderr.write("[preflight] FAIL:\n")
        for f in fails:
            sys.stderr.write(f"  ✗ {f}\n")
        return 1
    print("[preflight] PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
