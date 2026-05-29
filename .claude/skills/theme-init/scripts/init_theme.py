#!/usr/bin/env python3
"""Orchestrate the /theme-init render pipeline.

The calling Claude agent produces theme-active.json from the user's design
guide before invoking this script — there is no internal LLM call. If the
agent emits a partial draft with nulls / missing tokens, pass it via
`--fill-from` and this script will populate safe defaults before validating.

Steps:
    0. (optional) fill_theme_defaults.py — partial draft → complete theme
    1. validate_theme.py      — schema check against token-contract v1
    2. validate_fonts.py      — primary-font availability under assets/fonts/;
                                injects "Arial" into the chain if missing
    3. diff vs. prior theme   — human-readable summary of what changed
    4. render_layouts.py      — theme-parametric SVG layouts (source-aware:
                                per-theme _shell_src/ if composed, else _source/)
    5. validate_shells.py     — FATAL lock check on the rendered shells
    6. reskin_gallery.py      — regenerate colors_and_type.css for HTML gallery
    7. render_design_system.py — regenerate design-system.md
    8. render_anti_slop_theme.py — regenerate anti-slop-theme.md
    9. render_prompts.py      — regenerate strategist.md + executor.md
   10. render_design_md.py    — render DESIGN.md skeleton for slide-plan
                                (skipped if target file already exists; --force
                                 to overwrite hand-authored content)
   11. preview_shells.py      — NON-fatal: rasterize shells for Step 5 review

Usage:
    # Agent wrote theme-active.json directly; run validate + full render:
    python3 init_theme.py

    # Agent wrote a partial draft to /tmp/draft.json; fill, then render:
    python3 init_theme.py --fill-from /tmp/draft.json

    # Dry run (fill + validate, no render writes):
    python3 init_theme.py --fill-from /tmp/draft.json --dry-run

    # Interactive: pause after diff summary for y/n confirmation before render:
    python3 init_theme.py --fill-from /tmp/draft.json --confirm

All sub-scripts are invoked as separate processes so a failure in any
step surfaces cleanly with its own exit code. A non-zero step aborts the
pipeline immediately — no partial renders are left behind.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPTS_DIR.parents[1] / "slide"
DEFAULT_THEME = SKILL_ROOT / "references" / "theme-active.json"


def _run(step: str, argv: list[str]) -> None:
    """Run a subprocess and raise SystemExit on failure."""
    print(f"\n=== {step} ===")
    r = subprocess.run(argv, cwd=SCRIPTS_DIR.parents[2])  # repo root
    if r.returncode != 0:
        print(f"\n[init_theme] step failed: {step} (exit {r.returncode})", file=sys.stderr)
        raise SystemExit(r.returncode)


def _snapshot_theme(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def _diff_summary(before: dict | None, after: dict) -> None:
    print("\n=== theme diff ===")
    if before is None:
        print(f"  (new theme) → {after.get('display_name', after.get('name'))}")
        return
    if before.get("name") != after.get("name"):
        print(f"  name: {before.get('name')} → {after.get('name')}")
    # Top-level key-level diff for colors, typography, voice — the three
    # most visible token groups. We don't pretty-print every leaf; the
    # operator can read the file directly if they want chapter-and-verse.
    for group in ("colors", "typography", "voice"):
        b = before.get(group, {})
        a = after.get(group, {})
        changed = [k for k in set(b) | set(a) if b.get(k) != a.get(k)]
        if changed:
            print(f"  {group}: {len(changed)} key(s) changed — {', '.join(sorted(changed)[:5])}"
                  + ("..." if len(changed) > 5 else ""))
    if before == after:
        print("  (no changes — theme identical)")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--theme", type=Path, default=DEFAULT_THEME,
                    help="path to theme-active.json (input to render, overwritten by --fill-from)")
    ap.add_argument("--fill-from", type=Path,
                    help="partial theme JSON to fill with safe defaults before validation")
    ap.add_argument("--dry-run", action="store_true",
                    help="fill + validate only; skip render steps")
    ap.add_argument("--confirm", action="store_true",
                    help="after diff summary, prompt y/n before running the render chain")
    args = ap.parse_args()

    before = _snapshot_theme(args.theme)

    # 0. Optional fill from a partial agent draft
    if args.fill_from:
        _run("fill_theme_defaults",
             [sys.executable, str(SCRIPTS_DIR / "fill_theme_defaults.py"),
              "--input", str(args.fill_from), "--out", str(args.theme)])

    # 1. Validate
    _run("validate_theme",
         [sys.executable, str(SCRIPTS_DIR / "validate_theme.py"),
          "--theme", str(args.theme)])

    # 2. Font availability check (warns + injects Arial fallback if needed).
    #    Mutates theme-active.json when the primary font has no on-disk files
    #    AND Arial is not already in the chain — so the diff snapshot below
    #    reflects the post-injection state.
    _run("validate_fonts",
         [sys.executable, str(SCRIPTS_DIR / "validate_fonts.py"),
          "--theme", str(args.theme)])

    # 3. Diff summary (always runs after validate succeeds)
    after = _snapshot_theme(args.theme)
    if after is None:
        print("post-validation theme read failed; aborting", file=sys.stderr)
        return 1
    _diff_summary(before, after)

    if args.dry_run:
        print("\n[init_theme] dry run complete — no downstream files touched")
        return 0

    if args.confirm:
        if not sys.stdin.isatty():
            print("[init_theme] --confirm given but stdin is not a tty; aborting to avoid an undetected auto-skip",
                  file=sys.stderr)
            return 2
        try:
            reply = input("\nProceed with render chain? [y/N] ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\n[init_theme] aborted — no render writes", file=sys.stderr)
            return 1
        if reply not in ("y", "yes"):
            print("[init_theme] aborted — no render writes")
            return 0

    # 4-9. Render chain. Each script reads theme-active.json and writes its
    # output file. Any failure aborts the pipeline.
    #
    # render_design_md is intentionally last: it produces a *skeleton* that
    # the calling agent must finish authoring (AGENT-FILL markers). It is
    # also the only step that is no-op when its output already exists,
    # protecting hand-authored content (e.g., the canonical jangpm DESIGN.md).
    # render_layouts is source-aware: it renders the per-theme _shell_src/ (the
    # Step 5 composed shells) when present, else the global _source/ baseline.
    # validate_shells runs immediately after and is FATAL — a composed shell that
    # broke a permanent lock (canvas, font chain, banned feature, content-shell
    # light lock, GM line) must abort before downstream files reference it.
    for step, script, extra in [
        ("render_layouts",          "render_layouts.py",          []),
        ("validate_shells",         "validate_shells.py",         []),
        ("reskin_gallery",          "reskin_gallery.py",          []),
        ("render_design_system",    "render_design_system.py",    []),
        ("render_anti_slop_theme",  "render_anti_slop_theme.py",  []),
        ("render_prompts",          "render_prompts.py",          []),
        ("render_design_md",        "render_design_md.py",        []),
    ]:
        path = SCRIPTS_DIR / script
        if not path.exists():
            print(f"[init_theme] missing script: {path}", file=sys.stderr)
            return 1
        _run(step, [sys.executable, str(path)] + extra)

    # preview_shells is NON-fatal: it rasterizes the rendered shells for the
    # Step 5 review checkpoint. Missing rasterizer (cairosvg/svglib) just yields
    # filled SVGs to open in a browser — never a reason to fail the init.
    preview = SCRIPTS_DIR / "preview_shells.py"
    if preview.exists():
        print(f"\n=== preview_shells (non-fatal) ===")
        subprocess.run([sys.executable, str(preview)], cwd=SCRIPTS_DIR.parents[2])

    print(f"\n=== /theme-init complete ===")
    print(f"active theme: {after.get('display_name')} ({after.get('name')})")
    print(f"tests to verify:")
    print(f"  - python3 -m http.server -d .claude/skills/slide/references/jangpm-patterns 8000")
    print(f"  - generate a sample deck via /slide and confirm 5-page smoke build")
    return 0


if __name__ == "__main__":
    sys.exit(main())
