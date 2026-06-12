---
name: slide
description: >
  Korean-first lecture deck generator. Converts source documents (PDF/DOCX/URL/Markdown)
  or a prompt brief into active-theme-branded SVG pages and exports to native DrawingML PPTX
  through a strict serial pipeline (Strategist → [Image_Generator] → Executor →
  Post-processing → Export). Locks the canvas to 1280×720 and the visual language to the
  active theme's single accent + typography (default: Jangpm — monochrome, `#4633E3` indigo,
  Pretendard). Use when user asks to "make slides",
  "슬라이드 만들어", "강의 슬라이드", "프레젠테이션", "생성PPT", or invokes "/slide".
---

# /slide — Active-Theme Lecture Deck Skill

> Korean-first lecture deck generator. Converts source documents or prompt briefs into active-theme-branded SVG pages and exports to native DrawingML PPTX through a strict serial pipeline.

**Core Pipeline**: `Source Document → Create Project → Strategist → [Image_Generator] → Executor → Post-processing → Export`

> [!NOTE]
> The active theme (read from `references/theme-active.json`) is the single visual language for this skill. **1280×720 is permanently locked**; the accent, typography, and palette come from the active theme (default: Jangpm — monochrome, single `#4633E3` indigo accent, Pretendard, editorial report tone). See `references/design-system.md`, `references/anti-slop-core.md` (structural), and `references/anti-slop-theme.md` (theme-literal enforcement). The active theme's `templates/layouts/<theme>/` pack (currently `jangpm/`) is the only layout pack.

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
| `${SKILL_DIR}/scripts/analyze_images.py` | Image analysis (size / aspect inspection only — AI generation is host-specific: Claude Code uses `/codex-image`; Codex uses built-in `imagegen`) |
| `${SKILL_DIR}/scripts/svg_quality_checker.py` | SVG quality check |
| `${SKILL_DIR}/scripts/total_md_split.py` | Speaker notes splitting |
| `${SKILL_DIR}/scripts/finalize_svg.py` | SVG post-processing (unified entry) |
| `${SKILL_DIR}/scripts/svg_to_pptx.py` | Export to PPTX |

For complete tool documentation, see `${SKILL_DIR}/scripts/README.md`.

## Template Index

| Index | Path | Purpose |
|-------|------|---------|
| Layout template (active theme) | `${SKILL_DIR}/templates/layouts/<active-theme>/` (currently `jangpm/`) | The active theme's layout pack: `01_cover.svg`, `02_chapter.svg`, `03_content.svg`, `04_ending.svg`, `design_spec.md`. `/theme-init` renames this directory on a swap |
| Visualization templates | `${SKILL_DIR}/templates/charts/charts_index.json` | Chart / infographic / diagram SVG templates. **Under the active-theme lock**: Executor overrides fills to the active accent's opacity ladder regardless of template's native palette |
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
python3 .claude/skills/slide/scripts/announce_theme.py
```

The script also performs catalog-drift detection: if the preset catalog pointer (`assets/design-systems/active.json`) disagrees with `theme-active.json`'s name, it prints a `[WARN] theme drift` line with the fix (`init_theme.py --activate <pointer>` to follow the catalog, or `--register-current` to adopt the working copy). A drift warning means a previous activate/bake was interrupted — resolve it before generating slides. A missing catalog (claude.ai essentials bundle) is silent and fine.

**If `theme-active.json` is missing or fails to load**: stop. The user must run `/theme-init` first (see `.claude/skills/theme-init/SKILL.md`). Do NOT fall back to hard-coded Jangpm values — that would mask the configuration error and produce decks in an unintended language.

**If the active theme is not what the user expects**: stop and redirect them. If the wanted theme is already in the catalog (`assets/design-systems/README.md`), `python3 .claude/skills/theme-init/scripts/init_theme.py --activate <preset>` switches in seconds; otherwise `/theme-init <design-guide.md>` bakes it first. Do NOT hand-patch literals in Strategist/Executor output to match a different theme — the render chain is the only supported way to change the active theme.

This step is **read-only** — it never writes files. Subsequent steps inherit the active theme by reading the already-rendered `references/strategist.md`, `references/executor.md`, `references/design-system.md`, and `references/anti-slop-*.md`.

---

### Step 1: Source Content Processing

🚧 **GATE**: User has provided source material (PDF / DOCX / EPUB / URL / Markdown file / text description / conversation content — any form is acceptable).

When the user provides non-Markdown content, convert immediately:

| User Provides | Command |
|---------------|---------|
| PDF file | `${SKILL_DIR}/scripts/_py.sh ${SKILL_DIR}/scripts/source_to_md/pdf_to_md.py <file>` |
| DOCX / Word / Office document | `${SKILL_DIR}/scripts/_py.sh ${SKILL_DIR}/scripts/source_to_md/doc_to_md.py <file>` |
| PPTX / PowerPoint deck | `${SKILL_DIR}/scripts/_py.sh ${SKILL_DIR}/scripts/source_to_md/ppt_to_md.py <file>` |
| EPUB / HTML / LaTeX / RST / other | `${SKILL_DIR}/scripts/_py.sh ${SKILL_DIR}/scripts/source_to_md/doc_to_md.py <file>` |
| Web link | `${SKILL_DIR}/scripts/_py.sh ${SKILL_DIR}/scripts/source_to_md/web_to_md.py <URL>` |
| WeChat / high-security site | `${SKILL_DIR}/scripts/_py.sh ${SKILL_DIR}/scripts/source_to_md/web_to_md.py <URL>` (requires `curl_cffi`; falls back to `node web_to_md.cjs <URL>` only if that package is unavailable) |
| Markdown | Read directly |

**✅ Checkpoint — Confirm source content is ready, proceed to Step 2.**

---

### Step 2: Project Initialization

🚧 **GATE**: Step 1 complete; source content is ready (Markdown file, user-provided text, or requirements described in conversation are all valid).

```bash
${SKILL_DIR}/scripts/_py.sh ${SKILL_DIR}/scripts/project_manager.py init <project_name> --format ppt169
```

**Under this skill, always use `--format ppt169` (1280×720).** Other format flags exist for CLI compatibility but the active theme is calibrated to 1280×720 only (a permanent lock across themes). See `references/canvas-formats.md`.

Import source content (choose based on the situation):

| Situation | Action |
|-----------|--------|
| Has source files (PDF/MD/etc.) | `${SKILL_DIR}/scripts/_py.sh ${SKILL_DIR}/scripts/project_manager.py import-sources <project_path> <source_files...> --move` |
| User provided text directly in conversation | No import needed — content is already in conversation context; subsequent steps can reference it directly |

> ⚠️ **MUST use `--move`**: All source files (original PDF / MD / images) MUST be **moved** (not copied) into `sources/` for archiving.
> - Markdown files generated in Step 1, original PDFs, original MDs — **all** must be moved into the project via `import-sources --move`
> - Intermediate artifacts (e.g., `_files/` directories) are handled automatically by `import-sources`
> - After execution, source files no longer exist at their original location

**✅ Checkpoint — Confirm project structure created successfully, `sources/` contains all source files, converted materials are ready. Proceed to Step 3.**

---

### Step 3: Template Copy (active theme — automatic, non-blocking)

🚧 **GATE**: Step 2 complete; project directory structure is ready.

This skill uses a single layout pack — the **active theme**'s (default: Jangpm). There is no branching prompt at this step. The pack lives at `templates/layouts/<active-theme>/`, where `<active-theme>` is `theme-active.json`'s `name` (`/theme-init` renames this directory on a swap). Resolve it, then copy automatically:

```bash
THEME=$(python3 -c "import json; print(json.load(open('${SKILL_DIR}/references/theme-active.json'))['name'])")
cp ${SKILL_DIR}/templates/layouts/$THEME/*.svg <project_path>/templates/
cp ${SKILL_DIR}/templates/layouts/$THEME/design_spec.md <project_path>/templates/
```

**No user prompt for template selection.** The active theme is the skill's defining decision. If the user needs a different visual style, run `/theme-init` to replace the active theme — this skill only renders decks in whatever theme is currently active.

> To author an alternate template pack under the active-theme lock (unusual — e.g., for a sub-brand), see `workflows/create-template.md`.

**✅ Checkpoint — active-theme template pack copied to `<project_path>/templates/`. Proceed to Step 4.**

---

### Step 4: Strategist Phase — Dual-Mode

**이 스텝을 실행하기 전에 `references/executor-steps-4-6.md`의 해당 섹션을 반드시 먼저 읽어라.**

- 🚧 GATE: Step 3 완료 — active-theme 템플릿 팩이 `<project_path>/templates/`에 복사됨.
- 목적: 소스 콘텐츠를 `design_spec.md`로 변환. Step 4.0 모드 감지로 `slide_plan.json` 존재 시 **Plan-Consuming**, 부재 시 **Standalone** (Eight Confirmations) 자동 분기 — auto-trigger 조건(슬라이드 ≥ 10, 소스 파일, 품질 키워드) 충족 시 `/slide-plan`을 먼저 호출.
- 입력: 소스 콘텐츠, `references/strategist.md`, (plan 모드) `slide_plan.json` + `templates/layouts/<theme>/DESIGN.md` · 출력: `<project_path>/design_spec.md`.
- ⛔ **BLOCKING (사용자 확인 필수)**: Plan-Consuming은 active-theme lock 1화면 확인, Standalone은 Eight Confirmations 일괄 제시 — 명시적 사용자 확인 전 진행 금지.
- Plan-Consuming 필수 절차: `validate_plan.py` 재검증 → plan fingerprint dump (생략 시 plan-drift 회귀 #1 원인).
- 이미지가 제공된 경우 `analyze_images.py` 스크립트 출력만 사용 — 이미지 파일 직접 열람 금지.
- Step 4.5 Quality Floor (R2/R3/R4/R6 self-check + B-density / B-r2-simple / B-gm-simple / B-family-diversity / B-plan-count / B-plan-fidelity 검증 스크립트) 통과 후에만 다음 스텝 진행.

---

### Step 5: Image_Generator Phase (Conditional)

**이 스텝을 실행하기 전에 `references/executor-steps-4-6.md`의 해당 섹션을 반드시 먼저 읽어라.**

- 🚧 GATE: Step 4 완료 — design spec 생성 + 사용자 확인. 트리거: 이미지 접근법에 "AI generation" 포함 — 미트리거 시 Step 6으로 스킵 (Step 6 GATE는 여전히 충족 필요).
- 목적: design spec의 "pending generation" 이미지 슬롯을 활성 테마 Style Lock(Deck Style Anchor prefix + `Avoid:` negative suffix) 프롬프트로 생성.
- 입력: design_spec.md 이미지 목록 + `references/image-generator.md` · 출력: `<project_path>/images/image_prompts.md` + `images/<slot_name>.png`.
- 🔒 **호스트 백엔드 락**: Claude Code는 vendored `/codex-image`, Codex는 내장 `imagegen` 스킬 / `image_gen` 도구만. 다른 생성기(Gemini, DALL·E, Midjourney 등) 대체 금지 — 백엔드 실패/불가 시 `image_prompts.md`를 보존하고 halt, 정확한 블로커 보고. 슬롯 silent skip 금지.
- 슬롯당 1장, 직렬 생성 — 파일 존재 확인 후 다음 슬롯. 사이즈 매핑(16:9 wide / 1:1 square / 3:4 portrait)은 상세 절차 참조.

---

### Step 6: Executor Phase

**이 스텝을 실행하기 전에 `references/executor-steps-4-6.md`의 해당 섹션을 반드시 먼저 읽어라.**

- 🚧 GATE: Step 4 (트리거 시 Step 5 포함) 완료 + Step 4.5 quality floor 통과.
- 목적: `references/executor.md`(단일 executor)를 읽고 SVG 페이지와 스피커 노트를 생성.
- 입력 SSOT: Plan-Consuming은 `slide_plan.json` (design_spec.md §IX와 불일치 시 plan 우선, 사용자에게 보고), Standalone은 `design_spec.md` §IX · 출력: `<project_path>/svg_output/*.svg` + `notes/total.md`.
- 첫 SVG 생성 전 **Design Parameter Confirmation 필수** — `executor.md` §2의 확인 블록 출력 (canvas 1280×720 영구 락 + 활성 테마 accent/font/baseline).
- ⚠️ **메인 에이전트 단독 실행** — SVG 생성을 sub-agent에 위임 금지 (Global Execution Discipline #6).
- ⚠️ **순차 페이지 생성** — 글로벌 디자인 컨텍스트 확정 후 한 번에 한 페이지씩 연속 생성. 그룹 배치(예: 5장씩) 금지 (#7).

---

### Step 7: Post-processing & Export

🚧 **GATE**: Step 6 complete; all SVGs generated to `svg_output/`; speaker notes `notes/total.md` generated.

> ⚠️ The following four sub-steps MUST be **executed individually one at a time**. Each command must complete and be confirmed successful before running the next.
> ❌ **NEVER** put all four commands in a single code block or single shell invocation.

**Step 7.1** — Split speaker notes:
```bash
${SKILL_DIR}/scripts/_py.sh ${SKILL_DIR}/scripts/total_md_split.py <project_path>
```

**Step 7.2** — SVG post-processing (icon embedding / image crop & embed / text flattening / rounded rect to path):
```bash
${SKILL_DIR}/scripts/_py.sh ${SKILL_DIR}/scripts/finalize_svg.py <project_path>
```

**Step 7.3** — Export PPTX (embeds speaker notes by default):
```bash
${SKILL_DIR}/scripts/_py.sh ${SKILL_DIR}/scripts/svg_to_pptx.py <project_path> -s final
# Output: exports/<project_name>_<timestamp>.pptx + exports/<project_name>_<timestamp>_svg.pptx
# Use --only native  to skip SVG reference version
# Use --only legacy  to only generate SVG image version
```

**Step 7.4** — Verify the deck (hard-fail quality gate):
```bash
${SKILL_DIR}/scripts/_py.sh ${SKILL_DIR}/scripts/verify_deck.py <project_path>
```
- Runs the full gate: plan validation, stage parity, native PPTX integrity, **theme-palette compliance** (`svg_quality_checker.py --strict-theme` on `svg_output/`), image authenticity, governing-message discipline, canvas lock, mirror freshness.
- Off-theme colors fail the gate. Legitimate exceptions (e.g., partner brand colors) go in `<project_path>/.theme-color-allow` — one `#RRGGBB` per line.
- The deck is **not done** until this step exits 0.

> ❌ **NEVER** use `cp` as a substitute for `finalize_svg.py` — it performs multiple critical processing steps
> ❌ **NEVER** export directly from `svg_output/` — MUST use `-s final` to export from `svg_final/`
> ❌ **NEVER** add undocumented flags — only the documented `--only native` / `--only legacy` (shown above) are permitted
> ❌ **NEVER** declare the deck complete while Step 7.4 fails — fix the reported issues, don't skip the gate

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
| Diagram type grammar (14 types, native SVG) | `references/diagram-types.md` |
| HTML skeleton (for preview mode) | `references/skeleton.md` |
| Library usage (Reveal.js, Chart.js, Mermaid, Lucide) | `references/libraries.md` |
| Visual assets (illustration style) | `references/visual-assets.md` |
| Target reference text (theme-owned via `assets.reference-text`; skip if null) | `references/reference-2-text.txt` |
| Visual reference gallery (theme-owned via `assets.gallery`; CSS reskinned on /theme-init) | `references/jangpm-patterns/` |

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

- Do NOT add undocumented flags to the post-processing commands — run them as-is, except for the documented `--only native` / `--only legacy` on the export step
- Local preview: `python3 -m http.server -d <project_path>/svg_final 8000`
- **Troubleshooting**: If the user encounters issues during generation (layout overflow, export errors, blank images, etc.), recommend checking the project's known-issues tracker (GitHub Issues) — it collects fixes from real user reports
