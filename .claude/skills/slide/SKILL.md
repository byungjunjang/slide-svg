---
name: slide
description: >
  Korean-first lecture deck generator. Converts source documents (PDF/DOCX/URL/Markdown)
  or a prompt brief into Jangpm-branded SVG pages and exports to native DrawingML PPTX
  through a strict serial pipeline (Strategist → [Image_Generator] → Executor →
  Post-processing → Export). Locks visual language to monochrome + single `#4633E3`
  indigo accent, Pretendard typography, 1280×720. Use when user asks to "make slides",
  "슬라이드 만들어", "강의 슬라이드", "프레젠테이션", "생성PPT", or invokes "/slide".
---

# /slide — Active-Theme Lecture Deck Skill

> Korean-first lecture deck generator. Converts source documents or prompt briefs into Jangpm-branded SVG pages and exports to native DrawingML PPTX through a strict serial pipeline.

**Core Pipeline**: `Source Document → Create Project → Strategist → [Image_Generator] → Executor → Post-processing → Export`

> [!NOTE]
> The Jangpm Slide Design System is the single visual language for this skill. Monochrome + single `#4633E3` accent, Pretendard, 1280×720, editorial report tone. See `references/design-system.md`, `references/anti-slop-core.md` (structural), and `references/anti-slop-theme.md` (theme-literal enforcement). The `templates/layouts/jangpm/` pack is the only layout pack.

> [!CAUTION]
> ## 🚨 Global Execution Discipline (MANDATORY)
>
> **This workflow is a strict serial pipeline. The following rules have the highest priority — violating any one of them constitutes execution failure:**
>
> 1. **SERIAL EXECUTION** — Steps MUST be executed in order; the output of each step is the input for the next. Non-BLOCKING adjacent steps may proceed continuously once prerequisites are met, without waiting for the user to say "continue"
> 2. **BLOCKING = HARD STOP** — Steps marked ⛔ BLOCKING require a full stop; the AI MUST wait for an explicit user response before proceeding and MUST NOT make any decisions on behalf of the user
> 3. **NO CROSS-PHASE BUNDLING** — Cross-phase bundling is FORBIDDEN. (Note: the Eight Confirmations in Step 4 are ⛔ BLOCKING — the AI MUST present recommendations and wait for explicit user confirmation before proceeding. Once the user confirms, all subsequent non-BLOCKING steps — design spec output, SVG generation, speaker notes, and post-processing — may proceed automatically without further user confirmation)
> 4. **GATE BEFORE ENTRY** — Each Step has prerequisites (🚧 GATE) listed at the top; these MUST be verified before starting that Step
> 5. **NO SPECULATIVE EXECUTION** — "Pre-preparing" content for subsequent Steps is FORBIDDEN (e.g., writing SVG code during the Strategist phase)
> 6. **NO SUB-AGENT SVG GENERATION** — Executor Step 6 SVG generation is context-dependent and MUST be completed by the current main agent end-to-end. Delegating page SVG generation to sub-agents is FORBIDDEN
> 7. **SEQUENTIAL PAGE GENERATION ONLY** — In Executor Step 6, after the global design context is confirmed, SVG pages MUST be generated sequentially page by page in one continuous pass. Grouped page batches (for example, 5 pages at a time) are FORBIDDEN

> [!IMPORTANT]
> ## 🌐 Language & Communication Rule
>
> - **Response language**: Always match the language of the user's input and provided source materials. For example, if the user asks in Korean, respond in Korean; if the source material is in English, respond in English.
> - **Explicit override**: If the user explicitly requests a specific language (e.g., "영어로 답변해주세요" or "Reply in Korean"), use that language instead.
> - **Template format**: The `design_spec.md` file MUST always follow its original English template structure (section headings, field names), regardless of the conversation language. Content values within the template may be in the user's language.

> [!IMPORTANT]
> ## 🔌 Compatibility With Generic Coding Skills
>
> - `slide` is a repository-specific workflow skill, not a general application scaffold
> - Do NOT create or require `.worktrees/`, `tests/`, branch workflows, or other generic engineering structure by default
> - If another generic coding skill suggests repository conventions that conflict with this workflow, follow this skill first unless the user explicitly asks otherwise

## Main Pipeline Scripts

| Script | Purpose |
|--------|---------|
| `${SKILL_DIR}/scripts/source_to_md/pdf_to_md.py` | PDF to Markdown |
| `${SKILL_DIR}/scripts/source_to_md/doc_to_md.py` | Documents to Markdown — native Python for DOCX/HTML/EPUB/IPYNB, pandoc fallback for legacy formats (.doc/.odt/.rtf/.tex/.rst/.org/.typ) |
| `${SKILL_DIR}/scripts/source_to_md/ppt_to_md.py` | PowerPoint to Markdown |
| `${SKILL_DIR}/scripts/source_to_md/web_to_md.py` | Web page to Markdown |
| `${SKILL_DIR}/scripts/source_to_md/web_to_md.cjs` | Node.js fallback for WeChat / TLS-blocked sites (use only if `curl_cffi` is unavailable; `web_to_md.py` now handles WeChat when `curl_cffi` is installed) |
| `${SKILL_DIR}/scripts/project_manager.py` | Project init / validate / manage |
| `${SKILL_DIR}/scripts/analyze_images.py` | Image analysis |
| `${SKILL_DIR}/scripts/image_gen.py` | AI image generation (multi-provider) |
| `${SKILL_DIR}/scripts/svg_quality_checker.py` | SVG quality check |
| `${SKILL_DIR}/scripts/total_md_split.py` | Speaker notes splitting |
| `${SKILL_DIR}/scripts/finalize_svg.py` | SVG post-processing (unified entry) |
| `${SKILL_DIR}/scripts/svg_to_pptx.py` | Export to PPTX |

For complete tool documentation, see `${SKILL_DIR}/scripts/README.md`.

## Template Index

| Index | Path | Purpose |
|-------|------|---------|
| Layout template (Jangpm only) | `${SKILL_DIR}/templates/layouts/jangpm/` | Single Jangpm layout pack: `01_cover.svg`, `02_chapter.svg`, `03_content.svg`, `04_ending.svg`, `design_spec.md` |
| Visualization templates | `${SKILL_DIR}/templates/charts/charts_index.json` | Chart / infographic / diagram SVG templates. **Under Jangpm lock**: Executor overrides fills to the `#4633E3` opacity ladder regardless of template's native palette |
| Icon library | `${REPO_ROOT}/assets/icons/tabler-outline/<name>.svg` (Claude Code) · `${SKILL_DIR}/templates/icons/tabler-outline/<name>.svg` (claude.ai essentials) | Lucide-compatible line-art icons (Jangpm-preferred). Fallback library: `tabler-filled/`. `embed_icons.py` resolves `data-icon="tabler-outline/<name>"` against the external repo asset first, then the bundled essentials inside the skill, then warns and skips. Search the full library with `grep <keyword> ${REPO_ROOT}/assets/icons/icons_index.txt`; the bundled essentials are listable via `ls ${SKILL_DIR}/templates/icons/tabler-outline/`. |

## Standalone Workflows

| Workflow | Path | Purpose |
|----------|------|---------|
| `create-template` | `workflows/create-template.md` | Standalone template creation workflow |

---

## Workflow

### Step 0: Active-Theme Load (every session)

Before any user-visible work, read `references/theme-active.json` and announce the active theme in one line. This confirms the visual language you will lock to for the rest of the session.

> The schema this file conforms to (v1 token contract) lives at `.claude/skills/theme-init/references/token-contract.json`. Read that if you need to know which fields are required, what value formats are accepted, or how to validate a hand-edited theme.

```bash
python3 -c "import json; t=json.load(open('.claude/skills/slide/references/theme-active.json')); print(f'[active theme] {t[\"display_name\"]} ({t[\"name\"]}) — accent {t[\"colors\"][\"accent\"]}, font {t[\"typography\"][\"font-chain\"].split(\",\")[0]}')"
```

**If `theme-active.json` is missing or fails to load**: stop. The user must run `/theme-init` first (see `.claude/skills/theme-init/SKILL.md`). Do NOT fall back to hard-coded Jangpm values — that would mask the configuration error and produce decks in an unintended language.

**If the active theme is not what the user expects**: stop and redirect them to `/theme-init <design-guide.md>` with their target guide. Do NOT hand-patch literals in Strategist/Executor output to match a different theme — the render chain is the only supported way to change the active theme.

This step is **read-only** — it never writes files. Subsequent steps inherit the active theme by reading the already-rendered `references/strategist.md`, `references/executor.md`, `references/design-system.md`, and `references/anti-slop-*.md`.

---

### Step 1: Source Content Processing

🚧 **GATE**: User has provided source material (PDF / DOCX / EPUB / URL / Markdown file / text description / conversation content — any form is acceptable).

When the user provides non-Markdown content, convert immediately:

| User Provides | Command |
|---------------|---------|
| PDF file | `python3 ${SKILL_DIR}/scripts/source_to_md/pdf_to_md.py <file>` |
| DOCX / Word / Office document | `python3 ${SKILL_DIR}/scripts/source_to_md/doc_to_md.py <file>` |
| PPTX / PowerPoint deck | `python3 ${SKILL_DIR}/scripts/source_to_md/ppt_to_md.py <file>` |
| EPUB / HTML / LaTeX / RST / other | `python3 ${SKILL_DIR}/scripts/source_to_md/doc_to_md.py <file>` |
| Web link | `python3 ${SKILL_DIR}/scripts/source_to_md/web_to_md.py <URL>` |
| WeChat / high-security site | `python3 ${SKILL_DIR}/scripts/source_to_md/web_to_md.py <URL>` (requires `curl_cffi`; falls back to `node web_to_md.cjs <URL>` only if that package is unavailable) |
| Markdown | Read directly |

**✅ Checkpoint — Confirm source content is ready, proceed to Step 2.**

---

### Step 2: Project Initialization

🚧 **GATE**: Step 1 complete; source content is ready (Markdown file, user-provided text, or requirements described in conversation are all valid).

```bash
python3 ${SKILL_DIR}/scripts/project_manager.py init <project_name> --format ppt169
```

**Under this skill, always use `--format ppt169` (1280×720).** Other format flags exist for CLI compatibility but the Jangpm design language is calibrated to 1280×720 only. See `references/canvas-formats.md`.

Import source content (choose based on the situation):

| Situation | Action |
|-----------|--------|
| Has source files (PDF/MD/etc.) | `python3 ${SKILL_DIR}/scripts/project_manager.py import-sources <project_path> <source_files...> --move` |
| User provided text directly in conversation | No import needed — content is already in conversation context; subsequent steps can reference it directly |

> ⚠️ **MUST use `--move`**: All source files (original PDF / MD / images) MUST be **moved** (not copied) into `sources/` for archiving.
> - Markdown files generated in Step 1, original PDFs, original MDs — **all** must be moved into the project via `import-sources --move`
> - Intermediate artifacts (e.g., `_files/` directories) are handled automatically by `import-sources`
> - After execution, source files no longer exist at their original location

**✅ Checkpoint — Confirm project structure created successfully, `sources/` contains all source files, converted materials are ready. Proceed to Step 3.**

---

### Step 3: Template Copy (Jangpm — automatic, non-blocking)

🚧 **GATE**: Step 2 complete; project directory structure is ready.

This skill uses a single template pack — **Jangpm**. There is no branching prompt at this step. Copy the Jangpm pack automatically:

```bash
cp ${SKILL_DIR}/templates/layouts/jangpm/*.svg <project_path>/templates/
cp ${SKILL_DIR}/templates/layouts/jangpm/design_spec.md <project_path>/templates/
```

**No user prompt for template selection.** The Jangpm design language is the skill's defining decision. If the user needs a different visual style, run `/theme-init` to replace the active theme — this skill only renders decks in whatever theme is currently active.

> To author an alternate template pack under the Jangpm lock (unusual — e.g., for a sub-brand), see `workflows/create-template.md`.

**✅ Checkpoint — Jangpm template pack copied to `<project_path>/templates/`. Proceed to Step 4.**

---

### Step 4: Strategist Phase — Dual-Mode

🚧 **GATE**: Step 3 complete; user has confirmed template selection.

#### Step 4.0: Mode Detection (run first)

Check whether `/slide-plan` has already produced a plan:

```bash
test -f <project_path>/slide_plan.json && echo "PLAN_EXISTS" || echo "NO_PLAN"
```

| Result | Mode | Behavior |
|---|---|---|
| `PLAN_EXISTS` | **Plan-Consuming** | The plan is the SSOT for content / structure. Strategist's job is to *transcribe* the plan + active-theme tokens into `design_spec.md`. Skip Eight Confirmations except for a one-screen active-theme lock confirmation. |
| `NO_PLAN` | **Standalone** | Run the existing Eight Confirmations flow as documented below. No change to the legacy behavior. |

> **Why dual-mode?** `/slide-plan` is OPTIONAL. Quick decks (< 8 slides, single source) work fine with the Standalone mode. Systematic decks (lectures, executive reports, multi-source) benefit from `/slide-plan` running first. See `.claude/skills/slide-plan/SKILL.md` §"When to invoke this skill" for the boundary.

#### Step 4.1: Plan-Consuming Mode

If a plan exists:

1. **Validate the plan first.** Re-run the plan validator to catch any post-edit drift:
   ```bash
   python3 .claude/skills/slide-plan/scripts/validate_plan.py <project_path>/slide_plan.json
   ```
   Hard errors abort `/slide`; the user must fix them via `/slide-plan` before proceeding.

2. **Read the plan + active-theme references**:
   ```
   Read <project_path>/slide_plan.json
   Read references/strategist.md          (active-theme lock — palette / type / icon / voice)
   Read templates/layouts/<theme>/DESIGN.md (preset's layout-family vocabulary)
   ```

3. **Render `design_spec.md` as a transcription** of plan + theme:
   - Section IX (Content Outline) is generated 1:1 from `slide_plan.slides[]`. For each slide write: working_title, recommended_layout_family, content_blocks, chart_strategy + chart_takeaway, evidence_to_use.
   - Sections II–VIII (canvas / palette / type / layout principles / icon / chart references / image list) are auto-filled from `theme-active.json` + plan's `design_dependency`.
   - Sections X–XI (speaker notes + technical constraints) follow the boilerplate.

4. ⛔ **BLOCKING — Active-Theme Confirmation (one screen)**:
   Present a compact lock summary to the user:
   ```markdown
   ## ✅ Active-theme lock — {{display_name}}
   - Canvas: 1280×720 (locked across themes)
   - Palette: monochrome + single accent {{accent}}
   - Font chain: {{font-chain}}
   - Icon library: {{icon-pack-default}}
   - Voice: {{voice.tone}} / {{voice.pov}} / {{voice.register}}
   - Plan slides: {{N}} (deck_type: {{deck_type}})

   이 락 아래에서 plan 그대로 진행할까요? (y/N — 'N'이면 /slide-plan으로 돌아가 plan을 수정)
   ```
   Wait for explicit confirmation. (Eight Confirmations items b, c, h are absorbed by the plan; items a, d, e, f, g are theme-locked and shown as confirmations, not choices.)

5. After confirmation, output `<project_path>/design_spec.md` and proceed to Step 4.5.

#### Step 4.2: Standalone Mode

If no plan exists, run the legacy Eight Confirmations flow (this is the existing /slide behavior — unchanged):

First, read the role definition:
```
Read references/strategist.md
```

> ⚠️ **Mandatory gate in `strategist.md`**: Before writing `design_spec.md`, Strategist MUST `read_file templates/design_spec_reference.md` and produce the spec following its full I–XI section structure. See `strategist.md` Section 1 for the explicit gate rule.

**Must complete the Eight Confirmations** (full template structure in `templates/design_spec_reference.md`):

⛔ **BLOCKING**: The Eight Confirmations MUST be presented to the user as a bundled set of recommendations, and you MUST **wait for the user to confirm or modify** before outputting the Design Specification & Content Outline. This is one of only two core confirmation points in the workflow (the other is template selection). Once confirmed, all subsequent script execution and slide generation should proceed fully automatically.

1. Canvas format
2. Page count range
3. Target audience
4. Style objective
5. Color scheme
6. Icon usage approach
7. Typography plan
8. Image usage approach

If the user has provided images, run the analysis script **before outputting the design spec** (do NOT directly read/open image files — use the script output only):
```bash
python3 ${SKILL_DIR}/scripts/analyze_images.py <project_path>/images
```

> ⚠️ **Image handling rule**: The AI must NEVER directly read, open, or view image files (`.jpg`, `.png`, etc.). All image information must come from the `analyze_images.py` script output or the Design Specification's Image Resource List.

**Output**: `<project_path>/design_spec.md`

#### Step 4.5: Quality Floor Verification (both modes)

Before leaving Step 4, perform a self-check against Layer 1 quality rules. This is the "common quality floor" both modes must meet:

| Rule | Self-check |
|---|---|
| **R2** (chart/table needs takeaway) | Every chart slide in design_spec.md §IX has a takeaway sentence next to the chart spec. Every table slide has a verdict / takeaway row. |
| **R3** (length pressure) | If slide count > 20, document split / merge / defer candidates in §IX or in `slide_plan.json` `ordering_notes`. |
| **R4** (no lazy repetition) | No 3+ consecutive slides use the same layout family without a written justification. Min 3 distinct layout families in the deck. |

If any check fails, fix `design_spec.md` (Standalone) or roll back to `/slide-plan` (Plan-Consuming) and re-validate. **Plan-Consuming mode users:** `validate_plan.py` already enforced this — re-running it after any post-plan hand edit is recommended:
```bash
python3 .claude/skills/slide-plan/scripts/validate_plan.py <project_path>/slide_plan.json
```

**✅ Checkpoint — Phase deliverables complete, auto-proceed to next step**:
```markdown
## ✅ Strategist Phase Complete
- [x] Mode: <Plan-Consuming | Standalone>
- [x] Eight Confirmations completed (Standalone) OR active-theme lock confirmed (Plan-Consuming)
- [x] Design Specification & Content Outline generated
- [x] Layer 1 R2/R3/R4 quality floor verified
- [ ] **Next**: Auto-proceed to [Image_Generator / Executor] phase
```

---

### Step 5: Image_Generator Phase (Conditional)

🚧 **GATE**: Step 4 complete; Design Specification & Content Outline generated and user confirmed.

> **Trigger condition**: Image approach includes "AI generation". If not triggered, skip directly to Step 6 (Step 6 GATE must still be satisfied).

Read `references/image-generator.md`

1. Extract all images with status "pending generation" from the design spec
2. Generate prompt document → `<project_path>/images/image_prompts.md`
3. Generate images (CLI tool recommended):
   ```bash
   python3 ${SKILL_DIR}/scripts/image_gen.py "prompt" --aspect_ratio 16:9 --image_size 1K -o <project_path>/images
   ```

**✅ Checkpoint — Confirm all images are ready, proceed to Step 6**:
```markdown
## ✅ Image_Generator Phase Complete
- [x] Prompt document created
- [x] All images saved to images/
```

---

### Step 6: Executor Phase

🚧 **GATE**: Step 4 (and Step 5 if triggered) complete; Step 4.5 quality floor verified; all prerequisite deliverables are ready.

Read the single executor role definition:
```
Read references/executor.md
```

> Jangpm is a single visual language — there is only one executor. The legacy multi-style split (general / consultant / consultant-top) is removed.

**Plan-Consuming mode reminder** — if `slide_plan.json` exists at `<project_path>/slide_plan.json`, Executor MUST treat it as the per-slide source of truth: each slide's `recommended_layout_family`, `chart_strategy`, `content_blocks[]`, and `evidence_to_use` drive page construction. `design_spec.md` §IX is the formatted transcription; `slide_plan.json` is the SSOT. If the two disagree (e.g., user hand-edited only one), trust `slide_plan.json` and surface the inconsistency to the user before continuing. In Standalone mode (no plan), `design_spec.md` §IX is itself the SSOT — proceed with the existing flow.

**Design Parameter Confirmation (Mandatory)**: Before generating the first SVG, the Executor MUST review and output key design parameters from the Design Specification (canvas 1280×720, monochrome + `#4633E3` accent, Pretendard font chain, body 15.2px baseline) to ensure Jangpm lock adherence. See `executor.md` §2 for the exact confirmation block.

> ⚠️ **Main-agent only rule**: SVG generation in Step 6 MUST remain with the current main agent because page design depends on full upstream context (source content, design spec, template mapping, image decisions, and cross-page consistency). Do NOT delegate any slide SVG generation to sub-agents.
> ⚠️ **Generation rhythm rule**: After confirming the global design parameters, the Executor MUST generate pages sequentially, one page at a time, while staying in the same continuous main-agent context. Do NOT split Step 6 into grouped page batches such as 5 pages per batch.

**Visual Construction Phase**:
- Generate SVG pages sequentially, one page at a time, in one continuous pass → `<project_path>/svg_output/`

**Logic Construction Phase**:
- Generate speaker notes → `<project_path>/notes/total.md`

**✅ Checkpoint — Confirm all SVGs and notes are fully generated. Proceed directly to Step 7 post-processing**:
```markdown
## ✅ Executor Phase Complete
- [x] All SVGs generated to svg_output/
- [x] Speaker notes generated at notes/total.md
```

---

### Step 7: Post-processing & Export

🚧 **GATE**: Step 6 complete; all SVGs generated to `svg_output/`; speaker notes `notes/total.md` generated.

> ⚠️ The following three sub-steps MUST be **executed individually one at a time**. Each command must complete and be confirmed successful before running the next.
> ❌ **NEVER** put all three commands in a single code block or single shell invocation.

**Step 7.1** — Split speaker notes:
```bash
python3 ${SKILL_DIR}/scripts/total_md_split.py <project_path>
```

**Step 7.2** — SVG post-processing (icon embedding / image crop & embed / text flattening / rounded rect to path):
```bash
python3 ${SKILL_DIR}/scripts/finalize_svg.py <project_path>
```

**Step 7.3** — Export PPTX (embeds speaker notes by default):
```bash
python3 ${SKILL_DIR}/scripts/svg_to_pptx.py <project_path> -s final
# Output: exports/<project_name>_<timestamp>.pptx + exports/<project_name>_<timestamp>_svg.pptx
# Use --only native  to skip SVG reference version
# Use --only legacy  to only generate SVG image version
```

> ❌ **NEVER** use `cp` as a substitute for `finalize_svg.py` — it performs multiple critical processing steps
> ❌ **NEVER** export directly from `svg_output/` — MUST use `-s final` to export from `svg_final/`
> ❌ **NEVER** add extra flags like `--only`

---

## Role Switching Protocol

Before switching roles, you **MUST first read** the corresponding reference file — skipping is FORBIDDEN. Output marker:

```markdown
## [Role Switch: <Role Name>]
📖 Reading role definition: references/<filename>.md
📋 Current task: <brief description>
```

---

## Reference Resources

### Jangpm Design Language (read when in doubt)
| Resource | Path |
|----------|------|
| Design system (tokens, spacing, typography) | `references/design-system.md` |
| Anti-slop structural rules (theme-agnostic) | `references/anti-slop-core.md` |
| Anti-slop theme literals (regenerated on /theme-init) | `references/anti-slop-theme.md` |
| Layout pattern registry (30+ patterns) | `references/patterns.md` |
| HTML skeleton (for preview mode) | `references/skeleton.md` |
| Library usage (Reveal.js, Chart.js, Mermaid, Lucide) | `references/libraries.md` |
| Visual assets (illustration style) | `references/visual-assets.md` |
| Target reference text (Jangpm source deck extract) | `references/reference-2-text.txt` |
| Visual reference gallery (25 Jangpm HTMLs) | `references/jangpm-patterns/` |

### Pipeline Technical Reference
| Resource | Path |
|----------|------|
| Shared SVG / PPT technical constraints | `references/shared-standards.md` |
| Canvas format specification | `references/canvas-formats.md` |
| Image layout specification | `references/image-layout-spec.md` |
| SVG image embedding | `references/svg-image-embedding.md` |
| Export pipeline | `references/export.md` |

---

## Notes

- Do NOT add extra flags like `--only` to the post-processing commands — run them as-is
- Local preview: `python3 -m http.server -d <project_path>/svg_final 8000`
- **Troubleshooting**: If the user encounters issues during generation (layout overflow, export errors, blank images, etc.), recommend checking `docs/faq.md` — it contains known solutions sourced from real user reports and is continuously updated
