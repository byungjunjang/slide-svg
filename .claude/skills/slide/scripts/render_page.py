#!/usr/bin/env python3
"""Render one svg_output page to a PNG for the Executor's visual self-review.

A headless Chrome / Chromium / Edge draws the page the way a browser resolves
the font chain, so Hangul uses the installed Pretendard. (svglib + reportlab,
the pure-Python path, draws Hangul as tofu boxes and drops fill opacity, so it
is not used.) Icons are embedded into a copy under <project>/_render/ first —
the same depth as svg_output/, so ../images links still resolve, and
svg_output/ keeps its placeholders. Without a browser (claude.ai, a bare
server) the review is skipped with one line; a failed render never blocks.

Usage: render_page.py <project>/svg_output/<page>.svg [--out <png>] [--width 960]
Env:   CHROME_BIN — a browser binary to use; an empty value disables rendering.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svg_finalize.embed_icons import process_svg_file as embed_icons  # noqa: E402

CANVAS_W, CANVAS_H = 1280, 720


def find_browser() -> str | None:
    env = os.environ.get("CHROME_BIN")
    if env is not None:
        return env or None
    for name in ("chrome", "google-chrome", "chromium", "chromium-browser"):
        if shutil.which(name):
            return shutil.which(name)
    program_files = [os.environ.get(k) for k in ("PROGRAMFILES", "PROGRAMFILES(X86)", "LOCALAPPDATA")]
    candidates = [Path(base) / "Google/Chrome/Application/chrome.exe" for base in program_files if base]
    candidates += [Path(base) / "Microsoft/Edge/Application/msedge.exe" for base in program_files if base]
    candidates.append(Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"))
    return next((str(c) for c in candidates if c.is_file()), None)


def render(svg: Path, out: Path, width: int, browser: str) -> Path:
    stage = svg.resolve().parent.parent / "_render"
    stage.mkdir(exist_ok=True)
    copy = stage / svg.name
    shutil.copyfile(svg, copy)
    embed_icons(copy)
    out.unlink(missing_ok=True)  # a stale PNG must not pass as this render
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as profile:
        subprocess.run(
            [browser, "--headless=new", "--disable-gpu", "--hide-scrollbars",
             f"--user-data-dir={profile}", f"--window-size={CANVAS_W},{CANVAS_H}",
             f"--force-device-scale-factor={width / CANVAS_W:g}",
             f"--screenshot={out}", copy.resolve().as_uri()],
            capture_output=True, timeout=60)
    if not out.is_file():
        raise RuntimeError("the browser wrote no screenshot")
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Render one SVG page to PNG for review.")
    ap.add_argument("svg")
    ap.add_argument("--out", help="PNG path (default <project>/_render/<page>.png)")
    ap.add_argument("--width", type=int, default=960)
    args = ap.parse_args(argv)
    svg = Path(args.svg)
    browser = find_browser()
    if browser is None:
        print("[skip] no Chrome / Chromium / Edge found — page render review skipped")
        return 0
    out = Path(args.out) if args.out else svg.resolve().parent.parent / "_render" / f"{svg.stem}.png"
    started = time.time()
    try:
        render(svg, out, args.width, browser)
    except (OSError, RuntimeError, subprocess.SubprocessError) as exc:
        print(f"[skip] page render failed ({exc}) — review skipped")
        return 0
    print(f"[render] {out} ({time.time() - started:.1f}s) — Read it and fix visible defects")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
