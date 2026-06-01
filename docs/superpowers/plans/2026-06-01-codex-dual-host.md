# Codex Dual-Host Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `slide-svg` runnable on both Claude Code and Codex (cloud/web) at equal quality, without touching the canonical `.claude/skills` content, by adding a generated `.codex/skills` mirror, an `AGENTS.md` execution-discipline enforcer, and hard-fail quality gates.

**Architecture:** `.claude/skills` stays the single source of truth. `sync_codex_mirror.py` regenerates `.codex/skills` from it (rewriting only the literal `.claude/skills` path token to `.codex/skills` inside text files); a `--check` mode hard-fails when the mirror is stale. `AGENTS.md` (root) forces Codex to execute `SKILL.md` step-by-step instead of improvising. `verify_deck.py` + `preflight.py` enforce the pipeline's signature artifacts so shortcuts fail loudly. All scripts resolve paths from `__file__`, so they run identically from either host folder.

**Tech Stack:** Python 3 (stdlib + Pillow/numpy already in `requirements.txt`), pytest, bash (`_py.sh`), git.

**Cross-cutting rule (read once):** Tasks 1, 4, 5 edit files under `.claude/skills/`. The `.codex/skills` mirror is generated, so **every time you edit `.claude/skills`, you must re-run `sync_codex_mirror.py` and `git add .codex/skills` before committing.** The in-sync regression test (Task 2) and the mirror-freshness gate will fail otherwise — that is the drift guard working as designed.

**Path-depth invariant:** `.claude` and `.codex` are both direct children of the repo root, so every `Path(__file__).resolve().parents[N]` walk-up resolves identically from either tree. Do not change directory depths.

---

### Task 1: `sync_codex_mirror.py` — generator + drift-check

**Files:**
- Create: `.claude/skills/slide/scripts/dev/sync_codex_mirror.py`
- Test: `tests/test_codex_mirror.py`

- [ ] **Step 1: Write failing tests for the pure transform helpers**

Create `tests/test_codex_mirror.py`:

```python
"""Tests for the generated .codex/skills mirror and its drift guard."""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / ".claude" / "skills" / "slide" / "scripts" / "dev"))

import sync_codex_mirror as scm  # noqa: E402


class TestTransform:
    def test_rewrites_path_token_in_text_file(self):
        out = scm._transform_bytes(Path("x.md"), b"run .claude/skills/slide/x")
        assert out == b"run .codex/skills/slide/x"

    def test_leaves_binary_untouched(self):
        raw = b"\x89PNG.claude/skills"
        assert scm._transform_bytes(Path("logo.png"), raw) == raw

    def test_leaves_unrelated_text_unchanged(self):
        out = scm._transform_bytes(Path("x.py"), b"# the .claude dir")
        assert out == b"# the .claude dir"  # only the combined token is rewritten
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest tests/test_codex_mirror.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'sync_codex_mirror'`

- [ ] **Step 3: Implement `sync_codex_mirror.py`**

Create `.claude/skills/slide/scripts/dev/sync_codex_mirror.py`:

```python
#!/usr/bin/env python3
"""Generate the .codex/skills mirror from the canonical .claude/skills tree.

.claude/skills is the single source of truth. .codex/skills is a generated
artifact: a byte-for-byte copy, except the literal path token ".claude/skills"
is rewritten to ".codex/skills" inside text files so Codex copies host-correct
invocation commands. Re-run after editing anything under .claude/skills.

Usage:
    python3 .claude/skills/slide/scripts/dev/sync_codex_mirror.py          # regenerate
    python3 .claude/skills/slide/scripts/dev/sync_codex_mirror.py --check  # exit 1 if stale
"""
from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from pathlib import Path

# dev/sync_codex_mirror.py: parents[0]=dev [1]=scripts [2]=slide [3]=skills [4]=.claude [5]=repo
REPO_ROOT = Path(__file__).resolve().parents[5]
SRC = REPO_ROOT / ".claude" / "skills"
DST = REPO_ROOT / ".codex" / "skills"

TEXT_SUFFIXES = {".md", ".py", ".sh", ".json", ".txt", ".svg", ".cfg",
                 ".toml", ".yml", ".yaml", ".ini"}
EXCLUDE_NAMES = {"__pycache__", ".DS_Store"}
OLD_TOKEN = ".claude/skills"
NEW_TOKEN = ".codex/skills"


def _iter_files(root: Path):
    if not root.exists():
        return
    for p in sorted(root.rglob("*")):
        rel = p.relative_to(root)
        if any(part in EXCLUDE_NAMES for part in rel.parts):
            continue
        if p.suffix == ".pyc":
            continue
        if p.is_file():
            yield p


def _transform_bytes(path: Path, data: bytes) -> bytes:
    if path.suffix.lower() in TEXT_SUFFIXES:
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            return data
        return text.replace(OLD_TOKEN, NEW_TOKEN).encode("utf-8")
    return data


def build_mirror(dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    for src_file in _iter_files(SRC):
        rel = src_file.relative_to(SRC)
        out = dst / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(_transform_bytes(src_file, src_file.read_bytes()))


def _stale_files(mirror: Path, fresh: Path) -> list[str]:
    a = {p.relative_to(mirror) for p in _iter_files(mirror)}
    b = {p.relative_to(fresh) for p in _iter_files(fresh)}
    out = []
    for rel in sorted(a | b):
        fa, fb = mirror / rel, fresh / rel
        if not fa.exists() or not fb.exists() or fa.read_bytes() != fb.read_bytes():
            out.append(str(rel))
    return out


def check() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        fresh = Path(tmp) / "skills"
        build_mirror(fresh)
        stale = _stale_files(DST, fresh)
    if stale:
        sys.stderr.write("[sync_codex_mirror] .codex/skills is STALE:\n")
        for rel in stale[:40]:
            sys.stderr.write(f"  - {rel}\n")
        if len(stale) > 40:
            sys.stderr.write(f"  ... and {len(stale) - 40} more\n")
        sys.stderr.write("  Fix: python3 .claude/skills/slide/scripts/dev/sync_codex_mirror.py\n")
        return 1
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate/verify the .codex/skills mirror.")
    ap.add_argument("--check", action="store_true",
                    help="Exit 1 if the mirror is stale; do not write.")
    args = ap.parse_args()
    if args.check:
        return check()
    build_mirror(DST)
    print(f"[sync_codex_mirror] regenerated {DST} from {SRC}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python -m pytest tests/test_codex_mirror.py -v`
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/slide/scripts/dev/sync_codex_mirror.py tests/test_codex_mirror.py
git commit -m "feat(codex): add .codex/skills mirror generator + drift-check"
```

---

### Task 2: Generate and commit the `.codex/skills` mirror + in-sync regression test

**Files:**
- Create: `.codex/skills/**` (generated artifact, committed)
- Modify: `tests/test_codex_mirror.py`

- [ ] **Step 1: Add the in-sync regression test**

Append to `tests/test_codex_mirror.py`:

```python
class TestMirrorInSync:
    def test_codex_mirror_is_current(self):
        """The committed .codex/skills must match a fresh regeneration.
        Fails if someone edited .claude/skills without re-running sync."""
        assert scm.check() == 0, (
            "Run: python3 .claude/skills/slide/scripts/dev/sync_codex_mirror.py"
        )

    def test_mirror_root_exists(self):
        assert (REPO_ROOT / ".codex" / "skills" / "slide" / "SKILL.md").is_file()
```

- [ ] **Step 2: Run the new test to verify it fails (no mirror yet)**

Run: `python -m pytest tests/test_codex_mirror.py::TestMirrorInSync -v`
Expected: FAIL (`.codex/skills` does not exist yet → stale)

- [ ] **Step 3: Generate the mirror**

Run: `.claude/skills/slide/scripts/_py.sh .claude/skills/slide/scripts/dev/sync_codex_mirror.py`
Expected: prints `regenerated .../.codex/skills from .../.claude/skills`

- [ ] **Step 4: Run the test to verify it passes**

Run: `python -m pytest tests/test_codex_mirror.py -v`
Expected: PASS (all)

- [ ] **Step 5: Commit the generated mirror**

```bash
git add .codex/skills tests/test_codex_mirror.py
git commit -m "feat(codex): generate committed .codex/skills mirror"
```

---

### Task 3: Root `AGENTS.md` — Codex execution-discipline enforcer

**Files:**
- Create: `AGENTS.md`
- Modify: `tests/test_codex_mirror.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_codex_mirror.py`:

```python
class TestAgentsMd:
    def test_agents_md_exists_and_points_to_mirror_skill(self):
        agents = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
        assert ".codex/skills/slide/SKILL.md" in agents
        # the path it points at must actually exist in the mirror
        assert (REPO_ROOT / ".codex" / "skills" / "slide" / "SKILL.md").is_file()

    def test_agents_md_enforces_key_gates(self):
        agents = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
        for needle in ("slide-plan", "verify_deck.py", "HALT", "preflight.py"):
            assert needle in agents, f"AGENTS.md missing enforcement of: {needle}"
```

- [ ] **Step 2: Run to verify it fails**

Run: `python -m pytest tests/test_codex_mirror.py::TestAgentsMd -v`
Expected: FAIL (`FileNotFoundError: AGENTS.md`)

- [ ] **Step 3: Create `AGENTS.md`**

Create `AGENTS.md` at the repo root:

```markdown
# AGENTS.md — Codex execution rules for slide-svg

This repo is **dual-host**: Claude Code and Codex (cloud/web). Claude Code loads
`.claude/skills/` through its Skill runtime. Codex has no skill runtime, so this
file makes Codex execute the same procedures instead of improvising.

`CLAUDE.md` is the project SSOT for design constraints (1280×720, single accent
`#4633E3`, `.gm` line on every content slide, no emoji, native DrawingML
pipeline). Read it. These rules add Codex-side enforcement on top.

## Skill source (generated mirror)

- **`.claude/skills/` is canonical. `.codex/skills/` is a generated mirror** —
  byte-identical except `.claude/skills` paths are rewritten to `.codex/skills`.
- **Never hand-edit `.codex/skills/`.** Edit `.claude/skills/`, then run
  `python3 .claude/skills/slide/scripts/dev/sync_codex_mirror.py`.

## Slide requests — MANDATORY procedure

When the user asks for slides ("슬라이드", "프레젠테이션", "생성PPT",
"make slides", "/slide"):

1. **Run preflight first:**
   `.codex/skills/slide/scripts/_py.sh .codex/skills/slide/scripts/preflight.py`
   (add `--needs-images` if the deck needs generated images). If it fails, STOP
   and fix the environment. Do not proceed with a broken toolchain.
2. **Execute `.codex/skills/slide/SKILL.md` step by step.** Do NOT summarize it
   and improvise. **Forbidden:** reimplementing the pipeline yourself (hand-built
   PPTX, ad-hoc React/HTML, placeholder images). If a step's tool is unavailable,
   HALT and report — never silently fall back.
3. **Plan auto-entry:** if the deck is **≥ 8 slides** OR a lecture / executive
   report / sales / multi-source / explicit-quality deck, run
   `.codex/skills/slide-plan/SKILL.md` first and produce
   `output/<project>/slide_plan.json`. Only the bypass words (`간단히`, `빠르게`,
   `quick`, `simple로`, `plan 없이`) skip this — and then create
   `output/<project>/.standalone` to record the choice.
4. **Serial pipeline, no shortcuts:** strategist → [image_generator] → executor →
   post-processing → export. No cross-merge. Main agent writes SVG itself
   (no sub-agent delegation for Executor Step 6). Generate pages one at a time.
5. **Images:** if a slot needs a generated image, codex-image / image generation
   must be available and logged in (`codex login status`). If not, **HALT** —
   no PIL/solid-color/placeholder fallback.
6. **Post-processing discipline:** run, as three separate calls,
   `total_md_split.py` → `finalize_svg.py` → `svg_to_pptx.py <project> -s final`.
   Never `cp`. Never add undocumented flags. `-s final` is required.
7. **Completion gate:** before saying the deck is done, run
   `.codex/skills/slide/scripts/_py.sh .codex/skills/slide/scripts/verify_deck.py output/<project>`
   It must exit 0. If it fails, fix the deck — do not declare completion.

## Non-negotiables (mirror of CLAUDE.md)

1280×720 only · single accent only · `.gm` on every content slide · no emoji ·
native editable shapes (no image-flatten) · serial execution.
```

- [ ] **Step 4: Re-sync the mirror is NOT needed** (AGENTS.md is at repo root, outside `.claude/skills`)

Run: `python -m pytest tests/test_codex_mirror.py::TestAgentsMd -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add AGENTS.md tests/test_codex_mirror.py
git commit -m "feat(codex): add AGENTS.md execution-discipline enforcer"
```

---

### Task 4: `verify_deck.py` — hard-fail completion gate

**Files:**
- Create: `.claude/skills/slide/scripts/verify_deck.py`
- Test: `tests/test_verify_deck.py`

- [ ] **Step 1: Write failing tests for the pure helpers**

Create `tests/test_verify_deck.py`:

```python
"""Tests for the hard-fail deck verification gate (pure helpers + orchestrator)."""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / ".claude" / "skills" / "slide" / "scripts"))

import verify_deck as vd  # noqa: E402

GM_TEXT = '<text x="640" y="680" text-anchor="middle" fill="#6B7280">so-what</text>'
CANVAS = '<svg viewBox="0 0 1280 720">'


class TestGm:
    def test_detects_gm_line(self):
        assert vd.svg_has_gm(CANVAS + GM_TEXT + "</svg>") is True

    def test_no_gm_when_text_is_not_bottom_centered(self):
        body = '<text x="100" y="120" text-anchor="start">title</text>'
        assert vd.svg_has_gm(CANVAS + body + "</svg>") is False


class TestCanvas:
    def test_viewbox_ok(self):
        assert vd.svg_canvas_ok('<svg viewBox="0 0 1280 720"></svg>') is True

    def test_wrong_size_flagged(self):
        assert vd.svg_canvas_ok('<svg viewBox="0 0 1920 1080"></svg>') is False


class TestPlanRequirement:
    def test_eight_pages_needs_plan(self, tmp_path):
        out = tmp_path / "svg_output"
        out.mkdir()
        for i in range(8):
            (out / f"{i:02d}.svg").write_text(CANVAS + "</svg>", encoding="utf-8")
        assert vd.deck_needs_plan(tmp_path) is True

    def test_standalone_marker_overrides(self, tmp_path):
        out = tmp_path / "svg_output"
        out.mkdir()
        for i in range(8):
            (out / f"{i:02d}.svg").write_text(CANVAS + "</svg>", encoding="utf-8")
        (tmp_path / ".standalone").write_text("", encoding="utf-8")
        assert vd.deck_needs_plan(tmp_path) is False


class TestOrchestrator:
    def _good_deck(self, root: Path, n: int = 4) -> Path:
        proj = root / "deck"
        for sub in ("svg_output", "svg_final", "images"):
            (proj / sub).mkdir(parents=True)
        for i in range(n):
            (proj / "svg_output" / f"{i:02d}.svg").write_text(
                CANVAS + GM_TEXT + "</svg>", encoding="utf-8")
            (proj / "svg_final" / f"{i:02d}.svg").write_text(
                CANVAS + GM_TEXT + "</svg>", encoding="utf-8")
        (proj / "deck.pptx").write_bytes(b"PK\x03\x04stub")
        return proj

    def test_good_small_deck_passes_core_checks(self, tmp_path, monkeypatch):
        proj = self._good_deck(tmp_path)
        # isolate from external tools / mirror state in unit context
        monkeypatch.setattr(vd, "_run_quality_checker", lambda d: 0)
        monkeypatch.setattr(vd, "_sync_check", lambda: 0)
        failures = vd.run_checks(proj)
        assert failures == [], failures

    def test_missing_gm_fails(self, tmp_path, monkeypatch):
        proj = self._good_deck(tmp_path)
        for p in (proj / "svg_output").glob("*.svg"):
            p.write_text(CANVAS + "</svg>", encoding="utf-8")  # strip gm
        monkeypatch.setattr(vd, "_run_quality_checker", lambda d: 0)
        monkeypatch.setattr(vd, "_sync_check", lambda: 0)
        failures = vd.run_checks(proj)
        assert any("governing-message" in f for f in failures)

    def test_stage_parity_mismatch_fails(self, tmp_path, monkeypatch):
        proj = self._good_deck(tmp_path)
        next(iter((proj / "svg_final").glob("*.svg"))).unlink()  # drop one final page
        monkeypatch.setattr(vd, "_run_quality_checker", lambda d: 0)
        monkeypatch.setattr(vd, "_sync_check", lambda: 0)
        failures = vd.run_checks(proj)
        assert any("svg_final" in f for f in failures)
```

- [ ] **Step 2: Run to verify it fails**

Run: `python -m pytest tests/test_verify_deck.py -v`
Expected: FAIL (`ModuleNotFoundError: No module named 'verify_deck'`)

- [ ] **Step 3: Implement `verify_deck.py`**

Create `.claude/skills/slide/scripts/verify_deck.py`:

```python
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
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python -m pytest tests/test_verify_deck.py -v`
Expected: PASS (all)

- [ ] **Step 5: Re-sync the mirror (you edited `.claude/skills`)**

Run: `.claude/skills/slide/scripts/_py.sh .claude/skills/slide/scripts/dev/sync_codex_mirror.py`
Then: `python -m pytest tests/test_codex_mirror.py::TestMirrorInSync -v`
Expected: PASS (mirror current again)

- [ ] **Step 6: Commit**

```bash
git add .claude/skills/slide/scripts/verify_deck.py tests/test_verify_deck.py .codex/skills
git commit -m "feat(codex): add hard-fail verify_deck completion gate"
```

---

### Task 5: `preflight.py` — pre-pipeline environment gate

**Files:**
- Create: `.claude/skills/slide/scripts/preflight.py`
- Test: `tests/test_preflight.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_preflight.py`:

```python
"""Tests for the pre-pipeline environment gate."""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / ".claude" / "skills" / "slide" / "scripts"))

import preflight as pf  # noqa: E402


def test_python_deps_present():
    # pptx + PIL are in requirements.txt and installed in the dev venv
    assert pf.check_python_deps() == []


def test_assets_present():
    # full-library Claude Code checkout ships assets/fonts and assets/icons
    assert pf.check_assets() == []


def test_codex_image_reports_when_cli_missing(monkeypatch):
    monkeypatch.setattr(pf.shutil, "which", lambda _: None)
    fails = pf.check_codex_image()
    assert fails and "codex" in fails[0].lower()
```

- [ ] **Step 2: Run to verify it fails**

Run: `python -m pytest tests/test_preflight.py -v`
Expected: FAIL (`ModuleNotFoundError: No module named 'preflight'`)

- [ ] **Step 3: Implement `preflight.py`**

Create `.claude/skills/slide/scripts/preflight.py`:

```python
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
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python -m pytest tests/test_preflight.py -v`
Expected: PASS (3 passed)

- [ ] **Step 5: Re-sync the mirror and confirm**

Run: `.claude/skills/slide/scripts/_py.sh .claude/skills/slide/scripts/dev/sync_codex_mirror.py`
Then: `python -m pytest tests/test_codex_mirror.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add .claude/skills/slide/scripts/preflight.py tests/test_preflight.py .codex/skills
git commit -m "feat(codex): add preflight environment gate"
```

---

### Task 6: Documentation — README, CLAUDE.md, dual-host guide

**Files:**
- Modify: `README.md`
- Modify: `CLAUDE.md`
- Create: `docs/dual-host.md`

- [ ] **Step 1: Add a dual-host section to `README.md`**

Append this section to `README.md` (place it after the existing intro/usage section):

```markdown
## Dual-host: Claude Code · Codex

This repo runs on both Claude Code and Codex (cloud/web).

- **Claude Code** loads `.claude/skills/` via its Skill runtime (canonical, unchanged).
- **Codex** reads root `AGENTS.md`, which routes slide requests through the
  generated `.codex/skills/` mirror and enforces the same pipeline + gates.

`.claude/skills/` is the single source of truth. `.codex/skills/` is generated —
**never hand-edit it.** After editing any skill, regenerate the mirror:

```bash
.claude/skills/slide/scripts/_py.sh .claude/skills/slide/scripts/dev/sync_codex_mirror.py
```

Quality gates (run on either host):

```bash
# before starting a deck
.claude/skills/slide/scripts/_py.sh .claude/skills/slide/scripts/preflight.py --needs-images
# before declaring a deck done
.claude/skills/slide/scripts/_py.sh .claude/skills/slide/scripts/verify_deck.py output/<project>
```
```

- [ ] **Step 2: Add the sync reminder to `CLAUDE.md`**

In `CLAUDE.md`, under the `## 자주 쓰는 명령` section, add this block after the `package_for_claude_ai.py` (6b) entry:

```markdown
# 6c. Codex 미러 재생성 (.claude/skills 수정 후 필수)
.claude/skills/slide/scripts/_py.sh .claude/skills/slide/scripts/dev/sync_codex_mirror.py
# 6d. dual-host 품질 게이트
.claude/skills/slide/scripts/_py.sh .claude/skills/slide/scripts/preflight.py --needs-images
.claude/skills/slide/scripts/_py.sh .claude/skills/slide/scripts/verify_deck.py output/<project>
```

Also add this line to the `## 개요` section's dual-mode paragraph (after the existing "듀얼 모드" sentence):

```markdown
**듀얼 호스트 (Claude Code · Codex)**: Codex(클라우드/웹)는 루트 `AGENTS.md`를 읽어 생성형 `.codex/skills` 미러로 같은 파이프라인을 실행한다. `.claude/skills`가 정본이고 `.codex/skills`는 `sync_codex_mirror.py` 생성물이므로 손으로 편집하지 말 것. 설계: `docs/superpowers/specs/2026-06-01-codex-dual-host-design.md`.
```

- [ ] **Step 3: Create `docs/dual-host.md`**

Create `docs/dual-host.md`:

```markdown
# Dual-host operations (Claude Code · Codex)

## Why this exists

Running the same repo on Codex produced markedly lower quality than Claude Code.
Root cause was **not** path hardcoding (the Python pipeline already resolves
paths from `__file__`). It was that Codex *read* `SKILL.md` as docs and
improvised — skipping slide-plan, falling back to placeholder images, skipping
verification. The fix enforces execution discipline, it does not rewrite the
pipeline.

## The three pillars

1. **Generated mirror.** `.claude/skills` is canonical; `.codex/skills` is
   regenerated by `sync_codex_mirror.py` (only the `.claude/skills` path token is
   rewritten). A `--check` mode + the `test_codex_mirror.py` regression test +
   the `verify_deck`/`preflight` freshness checks hard-fail on drift. Never
   hand-edit `.codex/skills`.
2. **AGENTS.md.** Root entry file Codex reads. Routes slide requests to
   `SKILL.md`, forbids improvised fallback, forces slide-plan auto-entry,
   image-login-or-HALT, and "verify before done".
3. **Hard-fail gates.** `preflight.py` (env/login/assets/mirror) and
   `verify_deck.py` (plan presence, stage parity, native PPTX, image
   authenticity, `.gm`, canvas, mirror freshness). Shortcuts become non-viable.

## Editing workflow

1. Edit `.claude/skills/...` (canonical).
2. `python3 .claude/skills/slide/scripts/dev/sync_codex_mirror.py`
3. `git add .claude/skills .codex/skills` and commit together.
4. `pytest tests/` — `test_codex_mirror.py` proves the mirror is current.

## Porting to slide-html / slide-pencil

Same four principles; only the "golden artifacts" each gate checks differ.
See the spec's Appendix A:
`docs/superpowers/specs/2026-06-01-codex-dual-host-design.md`.
```

- [ ] **Step 4: Commit** (docs are outside `.claude/skills`, no re-sync needed)

```bash
git add README.md CLAUDE.md docs/dual-host.md
git commit -m "docs(codex): document dual-host workflow and gates"
```

---

### Task 7: Path audit + full regression + Codex-tree smoke check

**Files:**
- Modify (only if a functional hardcode is found): scripts under `.claude/skills/slide/scripts/`
- Test: `tests/test_codex_mirror.py`

- [ ] **Step 1: Audit `.claude` literals for functional hardcodes**

Run: `grep -rn "\.claude/skills" .claude/skills/slide/scripts --include=*.py`
Inspect each hit. Expected: all are inside docstrings/comments/help-text (not used
to build a runtime path). The path-building code uses `Path(__file__)...parents[N]`.
If any hit is a real runtime path literal, replace it with a `__file__`-relative
resolution and note it in the commit. (Audit confirmed during design: none expected.)

- [ ] **Step 2: Add a smoke test that the mirror is import-safe at the Codex depth**

Append to `tests/test_codex_mirror.py`:

```python
class TestCodexTreeSmoke:
    def test_mirror_scripts_have_same_depth(self):
        c = REPO_ROOT / ".claude" / "skills" / "slide" / "scripts" / "verify_deck.py"
        x = REPO_ROOT / ".codex" / "skills" / "slide" / "scripts" / "verify_deck.py"
        assert c.is_file() and x.is_file()
        # repo root is parents[4] from either copy → identical walk-up
        assert c.resolve().parents[4] == x.resolve().parents[4] == REPO_ROOT

    def test_mirror_rewrote_invocation_paths(self):
        skill = (REPO_ROOT / ".codex" / "skills" / "slide" / "SKILL.md").read_text(encoding="utf-8")
        assert ".codex/skills/slide" in skill
        assert ".claude/skills/slide" not in skill
```

- [ ] **Step 3: Run the full test suite**

Run: `python -m pytest tests/ -v`
Expected: PASS (all existing theme/chart tests + the new codex/verify/preflight tests)

- [ ] **Step 4: Run all gates end-to-end as a self-check**

Run:
```bash
.claude/skills/slide/scripts/_py.sh .claude/skills/slide/scripts/dev/sync_codex_mirror.py --check
.claude/skills/slide/scripts/_py.sh .claude/skills/slide/scripts/preflight.py
```
Expected: `--check` prints nothing and exits 0; preflight prints `[preflight] PASS`
(omit `--needs-images` here unless codex is logged in).

- [ ] **Step 5: Re-sync if Step 1 changed anything, then commit**

```bash
.claude/skills/slide/scripts/_py.sh .claude/skills/slide/scripts/dev/sync_codex_mirror.py
git add .codex/skills tests/test_codex_mirror.py .claude/skills
git commit -m "test(codex): mirror depth + invocation-path rewrite smoke checks"
```

---

## Self-Review

**Spec coverage** (against `2026-06-01-codex-dual-host-design.md`):
- 기둥 1 (생성형 미러 + drift-check) → Task 1, 2 ✓
- 기둥 2 (AGENTS.md) → Task 3 ✓
- 기둥 3 (verify + preflight 하드 페일) → Task 4, 5 ✓
- 기둥 4 (경로/호스트 감사) → Task 7 ✓
- 기둥 5 (문서 + 회귀 테스트) → Task 6 + tests across 1–7 ✓
- 부록 A (이식 패턴) → captured in `docs/dual-host.md` + spec, no code task needed ✓

**Placeholder scan:** no TBD/TODO; every code step has complete, runnable code.

**Type/name consistency:** helper names (`_transform_bytes`, `build_mirror`,
`check`, `svg_has_gm`, `svg_canvas_ok`, `image_is_placeholder`, `deck_needs_plan`,
`run_checks`, `_run_quality_checker`, `_sync_check`, `check_python_deps`,
`check_assets`, `check_codex_image`, `check_mirror`) are referenced identically in
the tests that monkeypatch them. Mirror token constants (`OLD_TOKEN`/`NEW_TOKEN`)
match the transform tests.

**Known intentional choices (not gaps):**
- gm gate uses a positional floor (`>= pages//2`) rather than per-page page-type
  detection, to catch total absence without false-failing legitimate decks whose
  page-type info lives only in the plan.
- `.codex/skills` mirrors the whole `.claude/skills` (incl. `dev/`, `theme-init`);
  Codex never invokes the Claude-local tools, and a faithful full mirror keeps the
  drift-check simple.
```
