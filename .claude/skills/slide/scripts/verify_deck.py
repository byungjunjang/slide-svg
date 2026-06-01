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
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent          # .../slide/scripts
SKILLS_DIR = HERE.parents[1]                     # .../skills (slide-plan lives beside slide)

SYSTEMATIC_MIN_PAGES = 8
GM_Y_RANGE = (655, 705)
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}
NATIVE_SHAPE_TAGS = ("sp", "grpSp", "cxnSp", "graphicFrame")


# ---- pure helpers -------------------------------------------------------

def _svgs(d: Path) -> list[Path]:
    return sorted(d.glob("*.svg")) if d.is_dir() else []


def page_count(project: Path, sub: str) -> int:
    return len(_svgs(project / sub))


def _pptx_files(project: Path) -> list[Path]:
    """Find PPTX exports in the legacy root location and the current exports/ dir."""
    paths = list(project.glob("*.pptx"))
    exports_dir = project / "exports"
    if exports_dir.is_dir():
        paths.extend(exports_dir.glob("*.pptx"))
    return sorted(set(paths))


def _native_pptx_files(project: Path) -> list[Path]:
    return [p for p in _pptx_files(project) if not p.stem.endswith("_svg")]


def _tag_count(xml: str, local_name: str) -> int:
    return len(re.findall(rf"<(?:\w+:)?{re.escape(local_name)}\b", xml))


def validate_native_pptx(path: Path) -> list[str]:
    """Validate a PPTX is readable and contains editable DrawingML per slide.

    The exporter writes two decks by default: the primary native deck and a
    *_svg reference deck. This check is intentionally focused on the native deck:
    every slide must contain at least one editable DrawingML shape/table/group,
    not only <p:pic> image nodes.
    """
    failures: list[str] = []
    try:
        with zipfile.ZipFile(path) as zf:
            bad_member = zf.testzip()
            if bad_member:
                return [f"corrupt zip member: {bad_member}"]
            slide_names = sorted(
                n for n in zf.namelist()
                if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)
            )
            if not slide_names:
                return ["no ppt/slides/slide*.xml entries"]
            flattened: list[str] = []
            for name in slide_names:
                xml = zf.read(name).decode("utf-8", errors="replace")
                native_count = sum(_tag_count(xml, tag) for tag in NATIVE_SHAPE_TAGS)
                if native_count == 0:
                    pic_count = _tag_count(xml, "pic")
                    suffix = " (image-only)" if pic_count else ""
                    flattened.append(f"{Path(name).name}{suffix}")
            if flattened:
                failures.append("slides lack editable DrawingML: " + ", ".join(flattened))
    except zipfile.BadZipFile:
        failures.append("not a valid PPTX zip")
    except OSError as e:
        failures.append(f"unreadable PPTX: {e}")
    return failures


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
    """Tiny OR near-uniform image ⇒ placeholder/degenerate.

    A missing image-processing library is an environment problem. Treat it as a
    verification failure rather than allowing placeholder art to pass silently.
    """
    try:
        if path.stat().st_size < min_bytes:
            return True
    except OSError:
        return True  # missing/unreadable file is itself a failure
    try:
        from PIL import Image
        import numpy as np
    except ImportError:
        return True
    try:
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
    pages = _svgs(out)
    n_out, n_fin = len(pages), page_count(project, "svg_final")
    if n_out == 0:
        failures.append("svg_output/ has no SVG pages — executor stage did not run")
    elif n_fin != n_out:
        failures.append(f"svg_final/ ({n_fin}) != svg_output/ ({n_out}) — finalize incomplete")

    # 3. native pptx + SVG quality
    pptx_files = _pptx_files(project)
    native_pptx_files = _native_pptx_files(project)
    if not pptx_files:
        failures.append("no .pptx export — run svg_to_pptx.py <project> -s final")
    elif not native_pptx_files:
        failures.append("no native .pptx export — *_svg.pptx reference decks are not enough")
    else:
        pptx_errors = []
        for pptx in native_pptx_files:
            errs = validate_native_pptx(pptx)
            if not errs:
                break
            try:
                label = str(pptx.relative_to(project))
            except ValueError:
                label = str(pptx)
            pptx_errors.append(f"{label}: {', '.join(errs)}")
        else:
            failures.append("native .pptx validation failed — " + "; ".join(pptx_errors))
    if _run_quality_checker(out) != 0:
        failures.append("svg_quality_checker reported errors on svg_output")

    # 4. image authenticity
    imgs_dir = project / "images"
    bad_imgs = [p.name for p in (imgs_dir.glob("*") if imgs_dir.is_dir() else [])
                if p.suffix.lower() in IMAGE_SUFFIXES and image_is_placeholder(p)]
    if bad_imgs:
        failures.append("placeholder/degenerate images: " + ", ".join(bad_imgs)
                        + " — real generation required, no fallback")

    # 5. governing-message discipline (svg_output, pre-flatten)
    if pages:
        gm = sum(1 for p in pages
                 if svg_has_gm(p.read_text(encoding="utf-8", errors="replace")))
        floor = len(pages)
        if gm < floor:
            failures.append(f"governing-message lines missing: {gm}/{len(pages)} "
                            f"pages carry a .gm (need {floor}/{len(pages)})")

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
