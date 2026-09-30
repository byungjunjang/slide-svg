# /slide 파이프라인 — Step 4–6 상세 절차

> 이 파일은 `/slide` 파이프라인의 Step 4 (Strategist) · Step 5 (Image_Generator) · Step 6 (Executor) 상세 절차 본문이다.
> SKILL.md는 해당 스텝 진입 시 이 파일의 해당 섹션을 반드시 먼저 로드한다.

---

### Step 4: Strategist Phase — Dual-Mode

🚧 **GATE**: Step 3 complete; active-theme template pack copied.

#### Step 4.0: Mode Detection (run first)

Check whether `/slide-plan` has already produced a plan:

```bash
test -f <project_path>/slide_plan.json && echo "PLAN_EXISTS" || echo "NO_PLAN"
```

| Result | Mode | Behavior |
|---|---|---|
| `PLAN_EXISTS` | **Plan-Consuming** | The plan is the SSOT for content / structure. Strategist's job is to *transcribe* the plan + active-theme tokens into `design_spec.md`. Skip Eight Confirmations except for a one-screen active-theme lock confirmation. |
| `NO_PLAN` | **Standalone** | Run the Eight Confirmations flow documented below. |

**Auto-trigger — if `NO_PLAN` BUT any of the following holds, switch to Plan-Consuming by invoking `/slide-plan` first:**

1. User specified slide count and it is **≥ 10**
2. User provided source files (xlsx / md / pdf / docx / pptx) anywhere in the project's `inputs/` or in conversation
3. User brief contains an **attitude/expectation keyword** — `계획` / `철저` / `상세` / `꼼꼼` / `체계` / `완벽` / `정성` / `신중` / `제대로` / `완성도` / `퀄리티` / `고품질` / `thorough` / `detailed` / `comprehensive` / `polished` / `careful` / `deep`
4. The deck is a **lecture, executive report, or sales deck** (`강의` / `수업` / `임원 보고` / `경영진 보고` / `보고서` / `세일즈` / `제품 소개` / `lecture` / `executive` / `sales pitch`)

When auto-triggered, announce in one line and invoke `/slide-plan` before resuming Step 4. Explicit bypass keywords (`simple로`, `plan 없이`, `빠르게`, `간단히`, `quick`) suppress the trigger and force Standalone (record the choice with `<project_path>/.standalone`). This list is the single SSOT for plan auto-entry; `CLAUDE.md`, `AGENTS.md`, `slide/SKILL.md`, and `slide-plan/SKILL.md` restate it.

> **Why dual-mode?** Quick decks (< 10 slides, no source files, no quality keyword, not a lecture / executive / sales deck) work fine with Standalone. Systematic decks benefit from `/slide-plan` running first. `verify_deck.py` enforces the same 10-slide floor: a deck of ≥ 10 pages without `slide_plan.json` fails unless `.standalone` exists.

#### Step 4.1: Plan-Consuming Mode

If a plan exists:

1. **Validate the plan first.** Re-run the plan validator to catch any post-edit drift:
   ```bash
   .claude/skills/slide/scripts/_py.sh .claude/skills/slide-plan/scripts/validate_plan.py <project_path>/slide_plan.json
   ```
   Hard errors abort `/slide`; the user must fix them via `/slide-plan` before proceeding.

2. **Read the plan + active-theme references**:
   ```
   Read <project_path>/slide_plan.json
   Read references/strategist.md          (active-theme lock — palette / type / icon / voice)
   Read templates/layouts/<theme>/DESIGN.md (preset's layout-family vocabulary)
   ```

   **Plan fingerprint** — after reading the plan, print each slide's fingerprint in the format below; this is the checklist that B-plan-fidelity later checks against:
   ```
   slide #N:
     family   = <recommended_layout_family>
     role     = <slide_role>
     core     = <core_message>
     why_here = <why_here>
     chart    = <chart_strategy>: <chart_takeaway>  (if any)
     table    = <table_strategy>: <table_takeaway>  (if any)
     evidence = <evidence_sources or content_constraints.evidence_to_use>
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

If no plan exists, run the Eight Confirmations flow:

First, read the role definition:
```
Read references/strategist.md
```

> ⚠️ **Mandatory gate in `strategist.md`**: Before writing `design_spec.md`, Strategist MUST Read `templates/design_spec_reference.md` and produce the spec following its full I–XI section structure. See `strategist.md` Section 1 for the explicit gate rule.

**Must complete the Eight Confirmations** (full template structure in `templates/design_spec_reference.md`):

⛔ **BLOCKING**: The Eight Confirmations MUST be presented to the user as a bundled set of recommendations, and you MUST **wait for the user to confirm or modify** before outputting the Design Specification & Content Outline. This is the only BLOCKING confirmation in Standalone mode. Once confirmed, all subsequent script execution and slide generation should proceed fully automatically.

1. Canvas format
2. Page count range
3. Target audience
4. Style objective
5. Color scheme
6. Icon usage approach
7. Typography plan
8. Image usage approach

If the user has provided images, run the analysis script **before outputting the design spec**; it writes `<project_path>/image_analysis.csv`:
```bash
${SKILL_DIR}/scripts/_py.sh ${SKILL_DIR}/scripts/analyze_images.py <project_path>/images
```

> **Image handling rule**: Layout facts (pixel size, aspect ratio, placement math) come from `image_analysis.csv` or the Design Specification's Image Resource List — not from eyeballing the files. Open an image with Read to check its **content**: when what it shows decides the layout, when verifying each generated image in Step 5 (as `/codex-image` Step 6 does), and when reviewing rendered output in Step 7.

**Output**: `<project_path>/design_spec.md`

#### Step 4.5: Quality Floor Verification (both modes)

Before leaving Step 4, perform a self-check against Layer 1 quality rules. This is the "common quality floor" both modes must meet:

| Rule | Self-check |
|---|---|
| **R2** (chart/table needs takeaway) | Every chart slide in design_spec.md §IX has a takeaway sentence next to the chart spec. Every table slide has a verdict / takeaway row. |
| **R3** (length pressure) | If slide count > 20, document split / merge / defer candidates in §IX or in `slide_plan.json` `ordering_notes`. |
| **R4** (no lazy repetition) | No 3+ consecutive slides use the same layout family without a written justification. Min 3 distinct layout families in the deck. |
| **R6 density** | Every content slide in §IX carries a dominant visual as evidence plus its supporting context and takeaway (`anti-slop-core.md` Rule 21 — density means a dominant visual, not dense text or stacked cards). The B-density script below checks a floor after Step 6. |

If any check fails, fix `design_spec.md` (Standalone) or roll back to `/slide-plan` (Plan-Consuming) and re-validate. **Plan-Consuming mode users:** `validate_plan.py` already enforced this — re-running it after any post-plan hand edit is recommended:
```bash
.claude/skills/slide/scripts/_py.sh .claude/skills/slide-plan/scripts/validate_plan.py <project_path>/slide_plan.json
```

**B-density verification (both modes; run after Step 6 SVGs exist):**
```bash
${SKILL_DIR}/scripts/_py.sh - "<project_path>" <<'PY'
import re,glob,json,sys
from pathlib import Path
project = Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
plan_files = list(project.glob('slide_plan.json'))
plan = {}
if plan_files:
    data = json.loads(plan_files[0].read_text())
    plan = {s.get('slide_number'): s for s in data.get('slides', [])}
fails = []
for f in sorted(project.glob('svg_output/*.svg')):
    txt = f.read_text(); lines = txt.count('\n') + 1
    m = re.search(r'(\d+)', f.stem); n = int(m.group(1)) if m else None
    if n and n in plan and isinstance(plan[n].get('min_lines_estimate'), (int, float)):
        thr = int(plan[n]['min_lines_estimate']); src = 'plan'
    elif re.search(r'<(line|polyline|circle|rect)[^>]*data-(role|series)|<g[^>]*chart|<text[^>]*tbl-', txt):
        thr = 120; src = 'simple-chart/dense'
    elif re.search(r'(cover|section|closing)', f.stem, re.I):
        thr = 40; src = 'simple-section/cover/closing'
    else:
        thr = 80; src = 'simple-general'
    if lines < thr:
        fails.append(f'{f.name}:lines={lines}<{thr}({src})')
print('B-density FAIL:', fails) if fails else print('B-density: PASS')
PY
```

The line count is a floor that flags a thin page, not a target. A FAIL means the page is missing its dominant visual or supporting context — add that block; do not split elements or pad markup to raise the count.

**B-r2-simple + B-gm-simple + B-family-diversity-simple (Standalone mode hardening — plan 부재 시에도 활성):**
```bash
${SKILL_DIR}/scripts/_py.sh - "<project_path>" <<'PY'
import re,glob,json,sys
from pathlib import Path
project = Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
plan_files = list(project.glob('slide_plan.json'))
if plan_files:
    print('B-r2-simple: SKIP (plan-mode 활성)')
    print('B-gm-simple: SKIP (plan-mode 활성)')
    print('B-family-diversity-simple: SKIP (plan-mode 활성)')
else:
    svgs = sorted(project.glob('svg_output/*.svg'))
    # B-r2-simple: chart/dense visual 가진 SVG 옆에 takeaway 텍스트 (≥30자 텍스트 노드) 있어야 함
    r2_fails = []
    for f in svgs:
        txt = f.read_text()
        has_visual = bool(re.search(r'<polyline|<line[^>]*data-(role|series)|<g[^>]*chart|<text[^>]*tbl-', txt))
        text_nodes = re.findall(r'<text[^>]*>([^<]+)</text>', txt)
        has_takeaway = any(len(t.strip()) >= 30 for t in text_nodes)
        if has_visual and not has_takeaway:
            r2_fails.append(f'{f.name}: visual but no takeaway text (≥30 chars)')
    print('B-r2-simple FAIL:', r2_fails) if r2_fails else print('B-r2-simple: PASS')
    # B-gm-simple: 콘텐츠 SVG (cover/section/closing 제외)에 .gm 클래스 또는 governing message 텍스트 존재
    gm_fails = []
    for f in svgs:
        stem = f.stem.lower()
        if any(k in stem for k in ('cover', 'section', 'closing')):
            continue
        txt = f.read_text()
        if not re.search(r'class="[^"]*gm[^"]*"|data-role="gm"', txt):
            gm_fails.append(f'{f.name}: missing .gm marker')
    print('B-gm-simple FAIL:', gm_fails) if gm_fails else print('B-gm-simple: PASS')
    # B-family-diversity-simple: ≥6 SVG 데크는 distinct filename slug ≥ 3
    if len(svgs) >= 6:
        slugs = set()
        for f in svgs:
            m = re.match(r'\d+[-_]([a-z-]+)', f.stem)
            if m: slugs.add(m.group(1))
        if len(slugs) < 3:
            print(f'B-family-diversity-simple FAIL: only {len(slugs)} distinct SVG slugs in {len(svgs)} files — possible lazy repetition')
        else:
            print(f'B-family-diversity-simple: PASS ({len(slugs)} distinct slugs)')
    else:
        print('B-family-diversity-simple: SKIP (< 6 slides)')
PY
```

**B-plan-count + B-plan-fidelity (plan-consuming mode only; auto-SKIPs in Standalone):**
```bash
${SKILL_DIR}/scripts/_py.sh - "<project_path>" <<'PY'
import re,glob,json,sys
from pathlib import Path
project = Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
plan_files = list(project.glob('slide_plan.json'))
if not plan_files:
    print('B-plan-count: SKIP (standalone mode)')
    print('B-plan-fidelity: SKIP (standalone mode)')
else:
    data = json.loads(plan_files[0].read_text())
    plan_slides = data.get('slides', [])
    svg_files = sorted(project.glob('svg_output/*.svg'))
    # B-plan-count: 슬라이드 수 일치
    if len(plan_slides) != len(svg_files):
        print(f'B-plan-count FAIL: plan={len(plan_slides)} vs SVG={len(svg_files)}')
    else:
        print(f'B-plan-count: PASS ({len(plan_slides)})')
    # B-plan-fidelity: 슬라이드별 core_message 키워드가 SVG <text> 안에 존재 (heuristic)
    fails = []
    stopwords = {'있다','없다','한다','하는','되는','된다','대한','위한','수','것','이','그','저','등','및','또는',
                 'that','this','with','from','have','will','they','your','their','about'}
    for s in plan_slides:
        n = s.get('slide_number')
        matching = [f for f in svg_files if re.search(rf'(^|[^0-9])0*{n}([^0-9]|$)', f.stem)]
        if not matching:
            fails.append(f'slide #{n}: no matching SVG'); continue
        svg = matching[0].read_text()
        # Extract <text> content for keyword check
        text_content = ' '.join(re.findall(r'<text[^>]*>(.*?)</text>', svg, re.DOTALL))
        core = s.get('core_message', '')
        keywords = set(re.findall(r'[가-힣]{2,}|[A-Za-z]{4,}', core)) - stopwords
        if not keywords:
            continue
        if not any(k in text_content for k in keywords):
            fails.append(f'slide #{n}: core_message keywords {sorted(keywords)[:5]} NOT in SVG text')
    print('B-plan-fidelity FAIL:', fails) if fails else print('B-plan-fidelity: PASS')
PY
```

**✅ Checkpoint** — confirmation done, `design_spec.md` written, quality floor verified → auto-proceed to Image_Generator (if AI images are pending) or Executor.

---

### Step 5: Image_Generator Phase (Conditional)

🚧 **GATE**: Step 4 complete; Design Specification & Content Outline generated and user confirmed.

> **Trigger condition**: Image approach includes "AI generation". If not triggered, skip directly to Step 6 (Step 6 GATE must still be satisfied).

Read `references/image-generator.md`

> 🔒 **Host backend lock**: AI images are generated only through the sanctioned backend for the current host. Claude Code uses the vendored `/codex-image` skill. Codex uses its built-in `imagegen` skill / built-in `image_gen` tool. Never use nanobanana2, Gemini, DALL·E, Midjourney, Stable Diffusion, FLUX, Imagen, Qwen, Zhipu, or any unrelated MCP image tool. If the sanctioned backend is unavailable, halt — do NOT substitute another generator.

1. Extract all images with status "pending generation" from the design spec
2. Generate prompt document → `<project_path>/images/image_prompts.md`. Every prompt MUST embed the active theme's Deck Style Anchor (§🔒 of `image-generator.md`) as prefix, and the negative list as `Avoid: ...` suffix in the prompt body.
3. Generate images one slot at a time — serial; before the next slot, confirm the file exists and open it with Read to check it against the prompt. To rerun a slot that shows a painted checkerboard or misses the prompt, delete the rejected PNG first — `/codex-image` never overwrites an existing file:

   - **Claude Code host**: invoke `/codex-image --out <project_path>/images --filename <slot_name>` with the slot prompt, so it writes `<project_path>/images/<slot_name>.png`.
   - **Codex host**: use the default `imagegen` skill, call the built-in `image_gen` tool for the slot prompt, then move/copy the selected generated file from Codex's default generated-images location into `<project_path>/images/<slot_name>.png`. Do not assume `/codex-image` CLI flags such as `--size`, `--quality`, `--out`, or `--filename` exist in Codex.

   Size guidance:
   - Hero / full-bleed 16:9 slot → request a wide landscape image; SVG `preserveAspectRatio="xMidYMid slice"` may crop to 1280×720.
   - Inline card 1:1 → request a square image.
   - Portrait card 3:4 → request a portrait image.

   See `references/image-generator.md` for the full host-specific recipe. If the sanctioned backend fails or is unavailable, keep `images/image_prompts.md`, halt, and report the exact blocker. Do not silently skip slots.

**✅ Checkpoint** — `images/image_prompts.md` exists and every pending slot has its `images/<slot_name>.png` → proceed to Step 6.

---

### Step 6: Executor Phase

🚧 **GATE**: Step 4 (and Step 5 if triggered) complete; Step 4.5 quality floor verified; all prerequisite deliverables are ready.

Read the single executor role definition:
```
Read references/executor.md
```

> The active theme is a single visual language — there is only one executor.

**Plan-Consuming mode reminder** — if `slide_plan.json` exists at `<project_path>/slide_plan.json`, Executor MUST treat it as the per-slide source of truth: each slide's `recommended_layout_family`, `chart_strategy`, `content_blocks[]`, and `evidence_to_use` drive page construction. `design_spec.md` §IX is the formatted transcription; `slide_plan.json` is the SSOT. If the two disagree (e.g., user hand-edited only one), trust `slide_plan.json` and surface the inconsistency to the user before continuing. In Standalone mode (no plan), `design_spec.md` §IX is itself the SSOT.

**Design Parameter Confirmation (Mandatory)**: Before generating the first SVG, the Executor MUST review and output key design parameters from the Design Specification (canvas 1280×720 — permanently locked — plus the active theme's accent, font chain, and body baseline; the rendered values live in `executor.md` §2 / `design-system.md`) to ensure active-theme lock adherence. See `executor.md` §2 for the exact confirmation block.

> ⚠️ **Main-agent only rule**: SVG generation in Step 6 MUST remain with the current main agent because page design depends on full upstream context (source content, design spec, template mapping, image decisions, and cross-page consistency). Do NOT delegate any slide SVG generation to sub-agents.
> ⚠️ **Generation rhythm rule**: After confirming the global design parameters, the Executor MUST generate pages sequentially, one page at a time, while staying in the same continuous main-agent context. Do NOT split Step 6 into grouped page batches such as 5 pages per batch.

**Visual Construction Phase**:
- Generate SVG pages sequentially, one page at a time, in one continuous pass → `<project_path>/svg_output/`

**Logic Construction Phase**:
- Generate speaker notes → `<project_path>/notes/total.md`

**✅ Checkpoint** — all SVGs are in `svg_output/` and `notes/total.md` is written → proceed directly to Step 7 post-processing.

