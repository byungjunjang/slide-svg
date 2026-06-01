#!/usr/bin/env python3
"""Hard-fail quality gate for a finished slide-svg deck.

Run before declaring a deck 'done'. Any failed check exits non-zero with a
remediation message, so neither host can ship a deck that skipped the pipeline
(missing plan, placeholder images, no governing message, stale mirror, ...).

Usage:
    python3 .claude/skills/slide/scripts/verify_deck.py output/<project>
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent          # .../slide/scripts
SKILLS_DIR = HERE.parents[1]                     # .../skills (slide-plan lives beside slide)

SYSTEMATIC_MIN_PAGES = 8
GM_Y_RANGE = (655, 705)
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}


# ---- pure helpers -------------------------------------------------------

def _svgs(d: Path) -> list[Path]:
    return sorted(d.glob("*.svg")) if d.is_dir() else []


def page_count(project: Path, sub: str) -> int:
    return len(_svgs(project / sub))


def svg_has_gm(svg_text: str) -> bool:
    """A governing-message line: a <text> anchored middle in the bottom band.
    Check svg_output (pre-flatten); finalize_svg turns text into paths."""
    for m in re.finditer(r"<text\b[^>]*>", svg_text):
        tag = m.group(0)
        if 'text-anchor="middle"' not in tag:
            continue
        ym = re.search(r'\by="([\d.]+)"', tag)
        if ym and GM_Y_RANGE[0] <= float(ym.group(1)) <= GM_Y_RANGE[1]:
            return True
    return False


def svg_canvas_ok(svg_text: str) -> bool:
    if re.search(r'viewBox="0\s+0\s+1280\s+720"', svg_text):
        return True
    return bool(re.search(r'\bwidth="1280"', svg_text)
                and re.search(r'\bheight="720"', svg_text))


def image_is_placeholder(path: Path, min_bytes: int = 12_000, min_std: float = 6.0) -> bool:
    """Tiny OR near-uniform image ⇒ placeholder/degenerate."""
    try:
        if path.stat().st_size < min_bytes:
            return True
        from PIL import Image
        import numpy as np
        with Image.open(path) as im:
            arr = np.asarray(im.convert("RGB"), dtype="float32")
        return float(arr.std()) < min_std
    except Exception:
        return True  # unreadable image is itself a failure


def deck_needs_plan(project: Path) -> bool:
    if (project / ".standalone").exists():
        return False
    return page_count(project, "svg_output") >= SYSTEMATIC_MIN_PAGES


# ---- external tool wrappers (monkeypatched in tests) --------------------

def _run_validator(plan_path: Path) -> int:
    vp = SKILLS_DIR / "slide-plan" / "scripts" / "validate_plan.py"
    if not vp.exists():
        return 0
    return subprocess.run([sys.executable, str(vp), str(plan_path)]).returncode


def _run_quality_checker(svg_dir: Path) -> int:
    qc = HERE / "svg_quality_checker.py"
    if not qc.exists() or not svg_dir.is_dir():
        return 0
    return subprocess.run([sys.executable, str(qc), str(svg_dir)]).returncode


def _sync_check() -> int:
    sync = HERE / "dev" / "sync_codex_mirror.py"
    if not sync.exists():
        return 0
    return subprocess.run([sys.executable, str(sync), "--check"]).returncode


# ---- orchestrator -------------------------------------------------------

def run_checks(project: Path) -> list[str]:
    failures: list[str] = []
    out, fin = project / "svg_output", project / "svg_final"

    # 1. plan required for systematic decks
    if deck_needs_plan(project) and not (project / "slide_plan.json").exists():
        failures.append(
            f"systematic deck ({page_count(project, 'svg_output')} pages >= "
            f"{SYSTEMATIC_MIN_PAGES}) has no slide_plan.json — run slide-plan, "
            f"or `touch {project}/.standalone` to override.")
    if (project / "slide_plan.json").exists() and _run_validator(project / "slide_plan.json") != 0:
        failures.append("slide_plan.json failed validate_plan.py")

    # 2. stage parity
    n_out, n_fin = page_count(project, "svg_output"), page_count(project, "svg_final")
    if n_out == 0:
        failures.append("svg_output/ has no SVG pages — executor stage did not run")
    elif n_fin != n_out:
        failures.append(f"svg_final/ ({n_fin}) != svg_output/ ({n_out}) — finalize incomplete")

    # 3. native pptx + SVG quality
    if not sorted(project.glob("*.pptx")):
        failures.append("no .pptx export — run svg_to_pptx.py <project> -s final")
    if _run_quality_checker(out) != 0:
        failures.append("svg_quality_checker reported errors on svg_output")

    # 4. image authenticity
    bad_imgs = [p.name for p in (project / "images").glob("*")
                if p.suffix.lower() in IMAGE_SUFFIXES and image_is_placeholder(p)]
    if bad_imgs:
        failures.append("placeholder/degenerate images: " + ", ".join(bad_imgs)
                        + " — real generation required, no fallback")

    # 5. governing-message discipline (svg_output, pre-flatten)
    pages = _svgs(out)
    if pages:
        gm = sum(1 for p in pages
                 if svg_has_gm(p.read_text(encoding="utf-8", errors="replace")))
        floor = max(1, len(pages) // 2)
        if gm < floor:
            failures.append(f"governing-message lines missing: {gm}/{len(pages)} "
                            f"pages carry a .gm (need >= {floor})")

    # 6. canvas
    bad_canvas = [p.name for p in pages
                  if not svg_canvas_ok(p.read_text(encoding="utf-8", errors="replace"))]
    if bad_canvas:
        failures.append("non-1280x720 pages: " + ", ".join(bad_canvas))

    # 7. mirror freshness
    if _sync_check() != 0:
        failures.append(".codex/skills mirror is stale — run sync_codex_mirror.py")

    return failures


def main() -> int:
    ap = argparse.ArgumentParser(description="Hard-fail quality gate for a finished deck.")
    ap.add_argument("project", help="path to output/<project>")
    args = ap.parse_args()
    project = Path(args.project).resolve()
    if not project.is_dir():
        sys.stderr.write(f"[verify_deck] not a directory: {project}\n")
        return 2
    failures = run_checks(project)
    if failures:
        sys.stderr.write(f"[verify_deck] FAIL ({len(failures)} issue(s)):\n")
        for f in failures:
            sys.stderr.write(f"  ✗ {f}\n")
        return 1
    print(f"[verify_deck] PASS — {project.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
