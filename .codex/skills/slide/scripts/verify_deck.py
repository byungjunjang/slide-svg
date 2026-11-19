#!/usr/bin/env python3
"""Hard-fail quality gate for a finished slide-svg deck.

Run before declaring a deck 'done'. Any failed check exits non-zero with a
remediation message, so neither host can ship a deck that skipped the pipeline
(missing plan, placeholder images, no governing message, stale mirror, ...).

Usage:
    python3 .codex/skills/slide/scripts/verify_deck.py output/<project>
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent          # .../slide/scripts
SKILLS_DIR = HERE.parents[1]                     # .../skills (slide-plan lives beside slide)

SYSTEMATIC_MIN_PAGES = 10  # /slide Step 4.0 auto-entry threshold (executor-steps-4-6.md)
GM_Y_RANGE = (655, 705)
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}
NATIVE_SHAPE_TAGS = ("sp", "grpSp", "cxnSp", "graphicFrame")
NON_CONTENT_SLIDE_RE = re.compile(
    r"(^|[_\-\s])(cover|title|chapter|section|ending|closing|close|thanks|thank_you|appendix"
    r"|표지|간지|챕터|섹션|마무리|엔딩|감사|부록)([_\-\s]|$)",
    re.IGNORECASE,
)
DENSITY_MIN_ELEMENTS = 30  # content-page floor; the 2026-11-19 bench decks' body pages held 46+


# ---- pure helpers -------------------------------------------------------

def _svgs(d: Path) -> list[Path]:
    return sorted(d.glob("*.svg")) if d.is_dir() else []


def page_count(project: Path, sub: str) -> int:
    return len(_svgs(project / sub))


def plan_page_families(project: Path) -> dict[int, str]:
    """slide_number -> page_family (title / chapter / body / end) from
    slide_plan.json; empty without a readable plan."""
    try:
        plan = json.loads((project / "slide_plan.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return {s["slide_number"]: s["page_family"] for s in plan.get("slides") or []
            if isinstance(s, dict) and isinstance(s.get("slide_number"), int)
            and isinstance(s.get("page_family"), str)}


def is_content_slide(svg_path: Path, families: dict[int, str] | None = None) -> bool:
    """Whether a slide is content-bearing (needs a .gm, meets the density floor).

    The plan's page_family decides when the page number is in the plan; else
    the filename — a role word in the stem, English or Korean (01_cover.svg,
    01_표지.svg, 04_간지_구조.svg) marks a cover / chapter / ending page.
    """
    m = re.match(r"\d+", svg_path.stem)
    if families and m and int(m.group()) in families:
        return families[int(m.group())] == "body"
    return NON_CONTENT_SLIDE_RE.search(svg_path.stem) is None


def density_failures(project: Path) -> list[str]:
    """Content pages under DENSITY_MIN_ELEMENTS SVG elements (B-density). Counts
    elements, not lines, so the verdict does not depend on markup style."""
    families = plan_page_families(project)
    out = []
    for svg in _svgs(project / "svg_output"):
        if not is_content_slide(svg, families):
            continue
        n = len(re.findall(r"<[A-Za-z]", svg.read_text(encoding="utf-8", errors="replace")))
        if n < DENSITY_MIN_ELEMENTS:
            out.append(f"{svg.name}: {n} elements < {DENSITY_MIN_ELEMENTS}")
    return out


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


# ---- figures: numbers on a page vs its slide_plan figures (WARN only) ----

_NUM_RE = re.compile(r"\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?")
_URL_RE = re.compile(r"https?://\S+|www\.\S+")
_DATE_RE = re.compile(  # 2026-07-15 / 2025.09 / 2월 15일
    r"(?<![\d.,])(?:19|20)\d\d[.\-/](?:0?[1-9]|1[0-2])(?:[.\-/](?:0?[1-9]|[12]\d|3[01]))?(?!\d)"
    r"|(?<!\d)\d{1,2}\s?월\s?\d{1,2}\s?일")
_COUNTER_RE = re.compile(r"\s?(?:분기|반기|년차|월|위|차|번째|단계|단|세대|종|유형|가지|쪽|페이지|장)|부(?![가-힣])")  # 1부
_CHAIN_RE = re.compile(r"\s?[·~∼–\-/]\s?\d+(?:\.\d+)?")  # '4–6장', '1~12월': one counter for all
_WORD_PREFIX_RE = re.compile(r"(?<![A-Za-z])(?!vs\b)[A-Za-z]{2,}\.?\s$")  # 'Phase 1'
_LETTER_UNIT_RE = re.compile(r"(?:x|pp|bp)(?![A-Za-z])")                 # 3.4x, 25pp
_KO_LABEL_RE = re.compile(r"(?:과제|문제|연습|질문|사례|예시|예제|실습|단계|파트)\s?$")  # '과제 1'
_BARE_RE = re.compile(r"[+\-−]?(\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?)\s?(?:%|조|억|만|원|배|x)?")
_PAGE_NO_RE = re.compile(r"(?:p\.?\s?|page\s)?0*(\d{1,3})(?:\s?/\s?\d{1,3})?", re.IGNORECASE)
_INTERNAL_RE = re.compile(  # analysis/x.json, sources/a.md, src_01, web_03
    r"(?<![\w.])(?:analysis|sources|svg_output|notes|images|exports)[/\\]"
    r"|(?<![\w])(?:src|web)_\d+")
FIGURE_TAGS = {"calc": "계산", "forecast": "전망", "assumption": "가정", "web": "보강"}


def figure_numbers(text: str) -> list[tuple[str, float]]:
    """`(raw, value)` for each number in a line that needs a figure. Years,
    dates, counters ('4분기', '3단계') and identifiers ('HBM4', '1Q25',
    'Phase 1') need none."""
    text = _DATE_RE.sub(" ", _URL_RE.sub(" ", text))
    out = []
    for m in _NUM_RE.finditer(text):
        raw, before, after = m.group(), text[:m.start()], text[m.end():]
        if before[-1:] in (".", ",") and before[-2:-1].isdigit():
            continue  # tail of a dotted run such as 1.2.3
        value = float(raw.replace(",", ""))
        plain = "," not in raw and "." not in raw
        chain = _CHAIN_RE.match(after)
        if (re.search(r"[A-Za-z]$", before)
                or (re.match(r"[A-Za-z]", after) and not _LETTER_UNIT_RE.match(after))
                or (plain and len(raw) == 4 and 1900 <= value <= 2100)
                or (value <= 20 and (_WORD_PREFIX_RE.search(before) or (plain and _KO_LABEL_RE.search(before))))
                or (plain and len(raw) == 2 and raw[0] == "0")  # 02: a chapter or step number
                or _COUNTER_RE.match(after)
                or (chain and _COUNTER_RE.match(after[chain.end():]))):
            continue
        out.append((raw, value))
    return out


def _tick_texts(elements: list) -> set[int]:
    """Indexes of axis-tick / list-marker labels: 3+ bare-number labels on one
    x (or one y) whose values step evenly in position order — or just two
    there when both are round tens (a short axis: '10조', '20조')."""
    labels = []
    for i, (x, y, _fs, _fw, _a, text, _r, _p) in enumerate(elements):
        m = _BARE_RE.fullmatch(text)
        if m:
            labels.append((i, x, y, float(m.group(1).replace(",", ""))))
    ticks: set[int] = set()
    for axis in (1, 2):  # 1: shared x (a column), 2: shared y (a row)
        runs: dict[int, list] = {}
        for lab in labels:
            runs.setdefault(round(lab[axis]), []).append(lab)
        for run in runs.values():
            run.sort(key=lambda lab: lab[3 - axis])
            steps = [b[3] - a[3] for a, b in zip(run, run[1:])]
            even = bool(steps) and steps[0] != 0 and all(abs(s - steps[0]) < 1e-9 for s in steps)
            if even and (len(run) >= 3 or all(lab[3] % 10 == 0 for lab in run)):
                ticks.update(lab[0] for lab in run)
    return ticks


def figure_warnings(project: Path) -> list[str]:
    """Plan decks only: numbers a page shows that its slide_plan figures do
    not list; calc / forecast / assumption / web figures with no tag word on the
    page; lines that name an internal file or plan id instead of a source."""
    plan_path = project / "slide_plan.json"
    if not plan_path.exists():
        return []
    try:
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    slides = [s for s in plan.get("slides") or [] if isinstance(s, dict)]
    # '보강' marks a web number only against given source files; a brief-only deck's facts all come from the web
    given = any(isinstance(i, dict) and i.get("source_type") == "file"
                for i in plan.get("content_inventory") or [])
    if not any("figures" in s for s in slides):
        return []  # a plan written before figures[] existed
    figures = {s.get("slide_number"): s.get("figures") or [] for s in slides}
    from svg_quality_checker import parse_text_elements
    out = []
    for svg in _svgs(project / "svg_output"):
        m = re.match(r"\d+", svg.stem)
        if not m or int(m.group()) not in figures:
            continue
        page = int(m.group())
        figs = [f for f in figures[page] if isinstance(f, dict)]
        listed = {value for f in figs for _raw, value in figure_numbers(str(f.get("text", "")))}
        elements = parse_text_elements(svg.read_text(encoding="utf-8", errors="replace"))
        ticks = _tick_texts(elements)
        texts = [e[5] for e in elements]
        missing = []
        for i, text in enumerate(texts):
            page_no = _PAGE_NO_RE.fullmatch(text)
            if i in ticks or (page_no and int(page_no.group(1)) == page):
                continue
            missing += [raw for raw, value in figure_numbers(text) if value not in listed]
        label = svg.stem.split("_")[0]
        if missing:
            out.append(f"figures: page {label} shows {', '.join(dict.fromkeys(missing))} not listed "
                       "in its slide_plan figures — add a figure (kind + basis) or drop the number")
        page_text = " ".join(texts)
        for kind, word in FIGURE_TAGS.items():
            if kind == "web" and not given:
                continue
            tagged = [str(f.get("text")) for f in figs if f.get("kind") == kind]
            if tagged and word not in page_text:
                out.append(f"figures: page {label} shows {kind} figures ({', '.join(tagged)}) "
                           f"but no '{word}' tag or note on the page")
        leaks = [t for t in texts if _INTERNAL_RE.search(t)]
        if leaks:
            out.append(f"figures: page {label} names an internal file or id ('{leaks[0][:40]}') "
                       "— cite a readable source instead")
    return out


def pipeline_status_warnings(project: Path) -> list[str]:
    """Non-blocking check for the current-run stage log (SKILL.md Fresh-Build Entry Gate #7)."""
    status = project / "pipeline_status.json"
    if not status.exists():
        return ["pipeline_status.json missing — current-run stage evidence was not recorded"]
    try:
        json.loads(status.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return ["pipeline_status.json is not readable JSON — stage evidence cannot be checked"]
    return []


# ---- external tool wrappers (monkeypatched in tests) --------------------

def _run_validator(plan_path: Path) -> int:
    vp = SKILLS_DIR / "slide-plan" / "scripts" / "validate_plan.py"
    if not vp.exists():
        return 0
    return subprocess.run([sys.executable, str(vp), str(plan_path)]).returncode


def _run_quality_checker(svg_dir: Path) -> int:
    """Strict mode: off-theme hex colors are gate failures, not advisories.
    svg_output is the SSOT for authored colors (svg_final embeds base64 assets
    whose bytes can false-positive the hex scan)."""
    qc = HERE / "svg_quality_checker.py"
    if not qc.exists() or not svg_dir.is_dir():
        return 0
    return subprocess.run(
        [sys.executable, str(qc), "--strict-theme", str(svg_dir)]).returncode


def _sync_check() -> int:
    sync = HERE / "dev" / "sync_codex_mirror.py"
    if not sync.exists():
        return 0
    return subprocess.run([sys.executable, str(sync), "--check"]).returncode


def _officecli_bin() -> str | None:
    # OFFICECLI_BIN overrides discovery: a path forces that binary, an empty
    # string disables the layer (hermetic tests / opting out).
    env = os.environ.get("OFFICECLI_BIN")
    if env is not None:
        return env or None
    found = shutil.which("officecli")
    if found:
        return found
    for cand in ("/opt/homebrew/bin/officecli", "/usr/local/bin/officecli"):
        if Path(cand).exists():
            return cand
    return None


def _run_officecli(args: list[str], timeout: int) -> subprocess.CompletedProcess | None:
    try:
        return subprocess.run(args, capture_output=True, text=True, timeout=timeout)
    except (subprocess.TimeoutExpired, OSError):
        return None


def officecli_checks(project: Path) -> tuple[list[str], list[str]]:
    """OpenXML validation + converted-PPTX contact sheet via officecli.

    Returns (failures, warnings). Skipped entirely when officecli is absent so
    hosts without it (claude.ai, public users) see no behavior change.
    Verdict policy (probed against officecli 1.0.135):
      - `error` object -> file cannot be opened (corrupt): FAILURE
      - success:false with only `warnings` -> schema strictness: WARNING
      - unparseable output / timeout, twice in a row -> tool problem, not deck
        evidence: WARNING
    """
    binary = _officecli_bin()
    if binary is None:
        return [], []
    natives = _native_pptx_files(project)
    if not natives:
        return [], []
    pptx = max(natives, key=lambda p: p.stat().st_mtime)  # newest export
    failures: list[str] = []
    warnings: list[str] = []

    # The first call right after an OfficeCLI auto-update can crash, so retry
    # once; two crashes are a tool problem, not evidence about the deck.
    verdict = None
    for _ in range(2):
        rc = _run_officecli([binary, "validate", str(pptx), "--json"], timeout=120)
        try:
            verdict = json.loads(rc.stdout) if rc is not None else None
        except ValueError:
            verdict = None
        if verdict is not None:
            break
    if verdict is None:
        warnings.append("officecli validate: tool error, not a deck defect — no "
                        f"verdict after 2 attempts ({_officecli_error(rc)}) — non-blocking")
    elif verdict.get("error"):
        failures.append(f"officecli validate: {pptx.name} unopenable — "
                        f"{verdict['error']}")
    elif not verdict.get("success"):
        warns = verdict.get("warnings") or []
        head = warns[0].get("message", "") if warns else ""
        warnings.append(f"officecli validate schema warnings on {pptx.name} "
                        f"({len(warns)} line(s), non-blocking): {head[:200]}")

    if not failures:
        out = project / "_pptx_render" / f"{pptx.stem}-grid.png"
        out.parent.mkdir(parents=True, exist_ok=True)
        base = [binary, "view", str(pptx), "screenshot", "--grid",
                "--out", str(out), "--json"]
        # On Windows the default render path drives PowerPoint over COM, which
        # can throw on a cold start. Retry it once, then fall back to the
        # PowerPoint-free HTML renderer so the contact sheet still lands.
        attempts = [("native", base), ("native retry", base),
                    ("html", base + ["--render", "html"])]
        errors: list[str] = []
        rendered = None
        for label, args in attempts:
            out.unlink(missing_ok=True)  # a stale sheet must not pass as fresh
            rs = _run_officecli(args, timeout=180)
            if rs is not None and rs.returncode == 0 and out.exists():
                rendered = label
                break
            errors.append(f"{label}: {_officecli_error(rs)}")
        if rendered:
            note = ""
            if rendered == "html":
                note = (" (HTML renderer fallback — PowerPoint render failed: "
                        f"{errors[0]})")
            print(f"[verify_deck] pptx render: {out}{note} — Read it to eyeball "
                  f"overflow/collision issues in the exported deck")
        else:
            warnings.append("officecli screenshot failed (non-blocking): "
                            + " | ".join(errors))
    # `view` leaves a `__resident-serve__` process holding the PPTX open; stop it.
    _run_officecli([binary, "close", str(pptx)], timeout=60)
    return failures, warnings


def _officecli_error(rs: subprocess.CompletedProcess | None) -> str:
    """The cause line of a failed officecli call. A .NET stack trace follows the
    message, so keep the head of the output and drop the `at ...` frames."""
    if rs is None:
        return "timeout or launch error"
    text = (rs.stderr or rs.stdout or "").strip()
    lines = [ln.strip() for ln in text.splitlines()
             if ln.strip() and not ln.strip().startswith("at ")]
    return (" ".join(lines) or f"exit {rs.returncode}, no output")[:300]


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
        pptx = max(native_pptx_files, key=lambda p: p.stat().st_mtime_ns)
        errs = validate_native_pptx(pptx)
        if errs:
            failures.append(f"native .pptx validation failed — {pptx.name}: " + "; ".join(errs))
    if _run_quality_checker(out) != 0:
        failures.append(
            "svg_quality_checker (--strict-theme) reported errors on svg_output — "
            "fix off-theme colors or whitelist brand exceptions in "
            "<project>/.theme-color-allow")

    # 4. image authenticity
    imgs_dir = project / "images"
    bad_imgs = [p.name for p in (imgs_dir.glob("*") if imgs_dir.is_dir() else [])
                if p.suffix.lower() in IMAGE_SUFFIXES and image_is_placeholder(p)]
    if bad_imgs:
        failures.append("placeholder/degenerate images: " + ", ".join(bad_imgs)
                        + " — real generation required, no fallback")

    # 5. governing-message discipline (svg_output, pre-flatten)
    if pages:
        families = plan_page_families(project)
        content_pages = [p for p in pages if is_content_slide(p, families)]
        gm = sum(1 for p in content_pages
                 if svg_has_gm(p.read_text(encoding="utf-8", errors="replace")))
        floor = len(content_pages)
        if gm < floor:
            failures.append(f"governing-message lines missing: {gm}/{floor} "
                            f"content pages carry a .gm (need {floor}/{floor})")

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
    cli_failures, cli_warnings = officecli_checks(project)
    failures.extend(cli_failures)
    for w in pipeline_status_warnings(project) + cli_warnings + figure_warnings(project):
        sys.stderr.write(f"  ! WARN {w}\n")
    if failures:
        sys.stderr.write(f"[verify_deck] FAIL ({len(failures)} issue(s)):\n")
        for f in failures:
            sys.stderr.write(f"  ✗ {f}\n")
        return 1
    print(f"[verify_deck] PASS — {project.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
