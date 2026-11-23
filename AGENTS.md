# AGENTS.md — Codex execution rules for slide-svg

This repo is **dual-host**: Claude Code and Codex (cloud/web). Claude Code loads
`.claude/skills/` through its Skill runtime. Codex has no skill runtime, so this
file makes Codex execute the same procedures instead of improvising.

`CLAUDE.md` is the project SSOT for design constraints (1280×720, single accent
from the active theme's `colors.accent`, `.gm` line on every content slide, no emoji, native DrawingML
pipeline). Read it. These rules add Codex-side enforcement on top.

## Skill source (generated mirror)

- **`.claude/skills/` is canonical. `.codex/skills/` is a generated mirror** —
  byte-identical except `.claude/skills` paths are rewritten to `.codex/skills`
  and the mirror root has a generated-marker file.
- **Never hand-edit `.codex/skills/`.** Edit `.claude/skills/`, then run
  `.claude/skills/slide/scripts/_py.sh .claude/skills/slide/scripts/dev/sync_codex_mirror.py`.

## Slide requests — MANDATORY procedure

When the user asks for slides ("슬라이드", "프레젠테이션", "생성PPT",
"make slides", "/slide"):

0. **Fresh-build gate for new-deck requests:** "만들어줘", "생성해줘", or
   equivalent wording means a new build unless the user explicitly asks to
   revise, continue, resume, or base the work on an existing deck. Start from a
   new project slug and run the pipeline from preflight and project init.
   Same-topic directories under `output/` are reference-only: do not copy,
   edit, rename, or reuse their plan, design spec, SVGs, notes, images, charts,
   or PPTX. Create `pipeline_status.json` before generation and record
   current-run timestamps, artifacts, and command/result evidence for every
   required stage. Existing files or old timestamps never prove that a stage
   ran for the current request. Do not declare completion or upload until the
   full current-run chain has passed export, `verify_deck.py`, exported-render
   visual inspection, and PPTX archive-integrity verification.

1. **Run preflight first:**
   `.codex/skills/slide/scripts/_py.sh .codex/skills/slide/scripts/preflight.py`
   (add `--needs-images` if the deck needs generated images). If it fails, STOP
   and fix the environment. Do not proceed with a broken toolchain.
   First-time setup: run
   `.claude/skills/slide/scripts/_py.sh -m pip install -r .claude/skills/slide/requirements.txt`.
2. **Execute `.codex/skills/slide/SKILL.md` step by step.** Do NOT summarize it
   and improvise. **Forbidden:** reimplementing the pipeline yourself (hand-built
   PPTX, ad-hoc React/HTML, placeholder images). If a step's tool is unavailable,
   HALT and report — never silently fall back.
3. **Plan auto-entry:** if the deck is **≥ 10 slides** OR the user provided
   source files OR the brief carries a quality keyword OR it is a lecture /
   executive report / sales deck, run
   `.codex/skills/slide-plan/SKILL.md` first and produce
   `output/<project>/slide_plan.json`. Only the bypass words (`간단히`, `빠르게`,
   `quick`, `simple로`, `plan 없이`) skip this — and then create
   `output/<project>/.standalone` to record the choice.
4. **Serial pipeline, no shortcuts:** strategist → [image_generator] → executor →
   post-processing → export. No cross-merge. Main agent writes SVG itself
   (no sub-agent delegation for Executor Step 6). Generate pages one at a time.
   (The skill docs' parallel path needs Claude Code's `fork` sub-agent; Codex
   stays on this sequential path.)
5. **Images:** if a slot needs a generated image, use Codex's default
   `imagegen` skill / built-in `image_gen` tool and save the selected output to
   the requested `images/<slot>.png` path. If `imagegen` / `image_gen` is not
   available, **HALT** — no PIL/solid-color/placeholder fallback and no
   `/codex-image` dependency in the Codex package.
5b. **Data charts:** for any chart built from real numbers, follow
   `.codex/skills/slide/references/executor.md` §7 — its order of chart paths
   (default → fallback → static `templates/charts/`) is the SSOT. Never
   hand-draw chart geometry; compute it from the data (script or renderer).
6. **Post-processing discipline:** run, as three separate calls,
   `total_md_split.py` → `finalize_svg.py` → `svg_to_pptx.py <project> -s final`.
   Never `cp`. Never add undocumented flags. `-s final` is required.
7. **Completion gate:** before saying the deck is done, run
   `.codex/skills/slide/scripts/_py.sh .codex/skills/slide/scripts/verify_deck.py output/<project>`
   It must exit 0. If it fails, fix the deck — do not declare completion.

For a revision/continuation request, preserve the named existing project and
mark the run as revision mode in `pipeline_status.json`. Never describe revision
mode as a fresh full-pipeline build.

## Non-negotiables (mirror of CLAUDE.md)

1280×720 only · single accent only · `.gm` on every content slide · no emoji ·
native editable shapes (no image-flatten) · serial execution.
