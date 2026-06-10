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
    6. render_charts.py       — re-render templates/charts/*.svg from the
                                tokenized _source/*.tpl.svg in the active accent
                                (keeps charts on-theme after a swap)
    7. validate_charts.py     — FATAL single-accent gate: rendered charts must
                                use the accent family + neutrals only
    8. reskin_gallery.py      — regenerate colors_and_type.css for HTML gallery
    9. render_design_system.py — regenerate design-system.md
   10. render_anti_slop_theme.py — regenerate anti-slop-theme.md
   11. render_prompts.py      — regenerate strategist.md + executor.md
   12. render_design_md.py    — render DESIGN.md skeleton for slide-plan
                                (skipped if target file already exists; --force
                                 to overwrite hand-authored content)
   13. preview_shells.py      — NON-fatal: build _preview/index.html for the
                                Step 6.5 final-approval gate (4 shells + samples)

Preset catalog (assets/design-systems/):
    Every successful bake also snapshots the validated theme into
    `.codex/skills/slide/assets/design-systems/<name>/theme.json` and
    regenerates the catalog README, so themes accumulate instead of being
    lost on the next swap. `active.json` is the catalog pointer;
    `references/theme-active.json` remains the render working copy that
    every downstream script reads.

Usage:
    # Agent wrote theme-active.json directly; run validate + full render:
    python3 init_theme.py

    # Agent wrote a partial draft to /tmp/draft.json; fill, then render:
    python3 init_theme.py --fill-from /tmp/draft.json

    # Bake + register in the catalog WITHOUT switching the active theme
    # (re-activates the previous preset afterwards — double render):
    python3 init_theme.py --fill-from /tmp/draft.json --no-set-active

    # Fast-switch to a preset already in the catalog (no LLM, deterministic):
    python3 init_theme.py --activate <preset>

    # Register the current theme-active.json into the catalog (no render):
    python3 init_theme.py --register-current

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
import os
import shutil
import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPTS_DIR.parents[1] / "slide"
DEFAULT_THEME = SKILL_ROOT / "references" / "theme-active.json"

sys.path.insert(0, str(SCRIPTS_DIR))
import _catalog  # noqa: E402
from render_presets_readme import render_readme  # noqa: E402

# Steps 4-12: the deterministic render chain. Each script reads
# theme-active.json and writes its output file; shared by the full-bake
# path and --activate. See the step list in the module docstring.
RENDER_CHAIN: list[tuple[str, str, list[str]]] = [
    ("render_layouts",          "render_layouts.py",          []),
    ("validate_shells",         "validate_shells.py",         []),
    ("render_charts",           "render_charts.py",           []),
    ("validate_charts",         "validate_charts.py",         []),
    ("reskin_gallery",          "reskin_gallery.py",          []),
    ("render_design_system",    "render_design_system.py",    []),
    ("render_anti_slop_theme",  "render_anti_slop_theme.py",  []),
    ("render_prompts",          "render_prompts.py",          []),
    ("render_design_md",        "render_design_md.py",        []),
]

# The step scripts print non-ASCII status lines (em-dashes, "→"). On a non-UTF-8
# console (e.g. Windows cp949) those raise UnicodeEncodeError mid-print and abort
# the step — and therefore the whole pipeline. Force UTF-8 for our own streams
# and for every child subprocess so /theme-init runs cleanly regardless of the
# host console code page.
try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    sys.stderr.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except (AttributeError, ValueError):
    pass

_CHILD_ENV = {**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"}


def _run(step: str, argv: list[str]) -> None:
    """Run a subprocess and raise SystemExit on failure."""
    print(f"\n=== {step} ===")
    r = subprocess.run(argv, cwd=SCRIPTS_DIR.parents[2], env=_CHILD_ENV)  # repo root
    if r.returncode != 0:
        print(f"\n[init_theme] step failed: {step} (exit {r.returncode})", file=sys.stderr)
        raise SystemExit(r.returncode)


def _run_render_chain() -> int:
    """Run steps 4-13 (fatal RENDER_CHAIN + non-fatal preview_shells).

    render_design_md is intentionally last: it produces a *skeleton* that
    the calling agent must finish authoring (AGENT-FILL markers). It is
    also the only step that is no-op when its output already exists,
    protecting hand-authored content (e.g., the canonical jangpm DESIGN.md).
    render_layouts is source-aware: it renders the per-theme _shell_src/ (the
    Step 5 composed shells) when present, else the global _source/ baseline.
    validate_shells runs immediately after and is FATAL — a composed shell that
    broke a permanent lock (canvas, font chain, banned feature, content-shell
    light lock, GM line) must abort before downstream files reference it.
    """
    for step, script, extra in RENDER_CHAIN:
        path = SCRIPTS_DIR / script
        if not path.exists():
            print(f"[init_theme] missing script: {path}", file=sys.stderr)
            return 1
        _run(step, [sys.executable, str(path)] + extra)

    # preview_shells is NON-fatal: it builds the single-page HTML approval
    # preview (_preview/index.html). The browser renders the inlined SVG with
    # the real font chain, so there is no rasterizer dependency — never a
    # reason to fail the init.
    preview = SCRIPTS_DIR / "preview_shells.py"
    if preview.exists():
        print(f"\n=== preview_shells (non-fatal) ===")
        subprocess.run([sys.executable, str(preview)], cwd=SCRIPTS_DIR.parents[2], env=_CHILD_ENV)
    return 0


def _save_to_catalog(presets_root: Path, theme: dict, *, set_active: bool) -> None:
    """Snapshot theme into the catalog, optionally move the pointer, regen README."""
    saved = _catalog.save_preset(presets_root, theme)
    print(f"\n=== catalog ===\n  snapshot: {saved}")
    if set_active:
        _catalog.set_active(presets_root, theme["name"])
        print(f"  active.json → {theme['name']}")
    print(f"  catalog README: {render_readme(presets_root)}")


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


def _activate(preset: str, presets_root: Path, theme_path: Path,
              dry_run: bool = False) -> int:
    """Fast-switch to a preset already in the catalog.

    Copies the catalog snapshot over theme-active.json, validates, and re-runs
    the deterministic render chain. Per-theme artifacts of OTHER themes
    (templates/layouts/<name>/ shells, _shell_src/, DESIGN.md) are never
    touched — every render is keyed on the active theme's name.
    """
    src = _catalog.preset_theme_path(presets_root, preset)
    if not src.is_file():
        avail = _catalog.list_presets(presets_root)
        print(f"[init_theme] preset not in catalog: {preset!r}", file=sys.stderr)
        print(f"  available: {', '.join(avail) if avail else '(none — run --register-current first)'}",
              file=sys.stderr)
        return 1

    before = _snapshot_theme(theme_path)
    shutil.copyfile(src, theme_path)
    print(f"[init_theme] activate: {src} → {theme_path}")

    _run("validate_theme",
         [sys.executable, str(SCRIPTS_DIR / "validate_theme.py"), "--theme", str(theme_path)])
    _run("validate_fonts",
         [sys.executable, str(SCRIPTS_DIR / "validate_fonts.py"), "--theme", str(theme_path)])

    after = _snapshot_theme(theme_path)
    if after is None:
        print("post-validation theme read failed; aborting", file=sys.stderr)
        return 1
    _diff_summary(before, after)

    if dry_run:
        print("\n[init_theme] dry run complete — no downstream files touched")
        return 0

    rc = _run_render_chain()
    if rc:
        return rc

    _catalog.set_active(presets_root, preset)
    print(f"\n=== catalog ===\n  active.json → {preset}")
    print(f"  catalog README: {render_readme(presets_root)}")
    print(f"\n=== /theme-init --activate complete ===")
    print(f"active theme: {after.get('display_name')} ({after.get('name')})")
    return 0


def _register_current(presets_root: Path, theme_path: Path) -> int:
    """Snapshot the current theme-active.json into the catalog (no render)."""
    theme = _snapshot_theme(theme_path)
    if theme is None:
        print(f"[init_theme] cannot read {theme_path}; nothing to register", file=sys.stderr)
        return 1
    _run("validate_theme",
         [sys.executable, str(SCRIPTS_DIR / "validate_theme.py"), "--theme", str(theme_path)])
    _save_to_catalog(presets_root, theme, set_active=True)
    print(f"\n=== /theme-init --register-current complete ===")
    print(f"registered: {theme.get('display_name')} ({theme.get('name')})")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--theme", type=Path, default=DEFAULT_THEME,
                    help="path to theme-active.json (input to render, overwritten by --fill-from)")
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--fill-from", type=Path,
                      help="partial theme JSON to fill with safe defaults before validation")
    mode.add_argument("--activate", metavar="PRESET",
                      help="fast-switch to a preset already in the catalog "
                           "(copy snapshot → theme-active.json + re-render; no LLM)")
    mode.add_argument("--register-current", action="store_true",
                      help="snapshot the current theme-active.json into the catalog "
                           "and point active.json at it (no render)")
    ap.add_argument("--set-active", action=argparse.BooleanOptionalAction, default=True,
                    help="after a bake, mark the new theme active in the catalog pointer "
                         "(default: on). --no-set-active registers it in the catalog but "
                         "re-activates the previous preset afterwards (double render).")
    ap.add_argument("--presets-root", type=Path, default=_catalog.DEFAULT_PRESETS_ROOT,
                    help="catalog root (default: slide skill assets/design-systems; for tests)")
    ap.add_argument("--dry-run", action="store_true",
                    help="fill + validate only; skip render steps")
    ap.add_argument("--confirm", action="store_true",
                    help="after diff summary, prompt y/n before running the render chain")
    args = ap.parse_args()

    if args.activate:
        return _activate(args.activate, args.presets_root, args.theme, dry_run=args.dry_run)
    if args.register_current:
        return _register_current(args.presets_root, args.theme)

    # --no-set-active preflight — BEFORE any write (fill / render), so a
    # failure leaves the working tree untouched. The restore target must
    # already be in the catalog.
    restore_preset: str | None = None
    if not args.set_active:
        try:
            restore_preset = _catalog.check_no_set_active_preflight(args.presets_root)
        except ValueError as e:
            print(f"[init_theme] {e}", file=sys.stderr)
            return 1

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

    # Pristine snapshot for the catalog — taken BEFORE validate_fonts, which
    # may inject a host-specific Arial fallback into the working copy. The
    # portable catalog snapshot must not bake in this machine's font gaps.
    pristine = _snapshot_theme(args.theme)

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

    # Steps 4-13. Render chain (shared with --activate). Any failure aborts.
    rc = _run_render_chain()
    if rc:
        return rc

    # Catalog registration: snapshot the pristine theme so it can be
    # re-activated later without re-extracting from a design guide.
    _save_to_catalog(args.presets_root, pristine or after, set_active=args.set_active)

    if restore_preset is not None and restore_preset != after.get("name"):
        # --no-set-active: the new theme is registered (and its
        # templates/layouts/<new>/ artifacts, incl. _preview/, stay rendered),
        # but the global reference docs must be restored to the previous
        # active preset — same deterministic chain, one more run.
        print(f"\n[init_theme] --no-set-active: restoring previous active preset "
              f"'{restore_preset}' (global docs re-render)")
        rc = _activate(restore_preset, args.presets_root, args.theme)
        if rc:
            return rc
        print(f"\n=== /theme-init complete (baked without switching) ===")
        print(f"baked + registered: {after.get('display_name')} ({after.get('name')})")
        print(f"active theme restored: {restore_preset}")
        print(f"to switch later: python3 .codex/skills/theme-init/scripts/init_theme.py "
              f"--activate {after.get('name')}")
        print(f"new theme preview: templates/layouts/{after.get('name')}/_preview/index.html")
        return 0

    print(f"\n=== /theme-init complete ===")
    print(f"active theme: {after.get('display_name')} ({after.get('name')})")
    print(f"BLOCKING — Step 6.5 final approval:")
    print(f"  - open templates/layouts/{after.get('name')}/_preview/index.html")
    print(f"    (python3 -m http.server -d templates/layouts/{after.get('name')}/_preview 8000)")
    print(f"  - present it to the user; wait for approval or feedback before done")
    print(f"further checks:")
    print(f"  - generate a sample deck via /slide and confirm 5-page smoke build")
    return 0


if __name__ == "__main__":
    sys.exit(main())
