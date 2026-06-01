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
