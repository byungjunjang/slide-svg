---
name: slide-plan
description: >
  Optional planning layer that runs BEFORE /slide. Detects deck_type
  (educational / report / consulting / sales / internal_update / proposal /
  keynote), selects a narrative arc, and writes a structured slide_plan.json
  with per-slide core_message / why_here / recommended_layout_family /
  chart_strategy / evidence_sources. Use when the user wants a systematic
  deck (lectures, executive reports, sales pitches), or invokes /slide-plan,
  "기획부터", "체계적으로 슬라이드", "narrative 짜줘". For quick decks,
  /slide alone is fine — slide-plan is opt-in.
---

# /slide-plan — Optional Planning Layer for /slide

> **Position in pipeline:** OPTIONAL prerequisite to `/slide`.
> Quick decks: `/slide` alone (existing flow, unchanged).
> Systematic decks: `/slide-plan` → user confirm → `/slide` consumes `slide_plan.json`.

```
사용자: 체계적으로 슬라이드 만들어줘
        ↓
/slide-plan
  → deck_type 감지
  → narrative arc 선택
  → 슬라이드별 plan 작성
  → slide_plan.json 출력 + markdown 요약
        ↓
사용자 검토 (BLOCKING)
        ↓
/slide  ←  output/<project>/slide_plan.json 소비
        ↓
PPTX 산출
```

If `slide_plan.json` exists at `output/<project>/slide_plan.json` when `/slide` runs, `/slide` skips its own Eight Confirmations planning and consumes the plan instead.

---

## When to invoke this skill

**Use `/slide-plan` when:**
- The deck has > 8 slides and a story arc matters (not just an info dump)
- The user provides multiple source files and needs evidence mapping
- The deck targets a specific audience (executives, students, prospects) where role-aware structure helps
- The user asks for "narrative", "기획", "체계적", "스토리", "흐름"

**Skip `/slide-plan` (use `/slide` directly) when:**
- The deck is < 6 slides
- Content is a single source document being summarized
- The user wants a quick draft, no planning overhead
- The user explicitly says "간단하게", "빠르게", "그냥 슬라이드만"

When in doubt, ask the user once. Do NOT silently force `/slide-plan` for every request.

---

## Layer 1 — Universal Discipline (enforced by this skill)

Five rules, hard-enforced by `validate_plan.py` and re-checked by `/slide` Executor at render time:

- **R1. Per-slide rationale (4 fields)** — every slide populates `core_message` / `audience_takeaway` / `why_here` / `recommended_layout_family`.
- **R2. Visual-led slides require takeaway text** — `chart_strategy` set ⇒ non-empty `chart_takeaway`; `data` family with a table block ⇒ non-empty `table_takeaway`.
- **R3. Length pressure** — default 8–12 slides; decks > 20 need split/merge/defer candidates in `ordering_notes`.
- **R4. No lazy repetition** — no 3+ consecutive same `recommended_layout_family` (except `structure`) without justification; min 3 distinct families per deck.
- **R5. Evidence mapping** — every slide's `evidence_sources` non-empty (`content_inventory[]` IDs or `"inference"`).

**plan 검증 단계 진입 시 `references/layer1-universal-discipline.md`를 반드시 먼저 읽어라.**

---

## Workflow

### Step 0: Read the active preset's DESIGN.md

Locate the active preset:

```bash
python3 -c "import json; t=json.load(open('.claude/skills/slide/references/theme-active.json')); print(t['name'])"
```

Then read the preset's design vocabulary:

```
.claude/skills/slide/templates/layouts/<preset>/DESIGN.md
```

This file defines the `recommended_layout_family` enum (§5) and chart treatment (§8) you must use. If `DESIGN.md` is missing, stop and ask the user to run `/theme-init` first.

### Step 1: Read pipeline references

Read in this order:

1. `.claude/skills/slide/references/chart-rhetorical-roles.md` — `chart_strategy` enum
2. `.claude/skills/slide/references/slide-role-enum.md` — `slide_role` enum + diagnostic ratios
3. `.claude/skills/slide/references/anti-slop-core.md` — theme-agnostic anti-patterns (Layer 1 R1–R5 alignment)

### Step 2: Detect `deck_type` from user brief

Analyze the brief and pick one:

| `deck_type` | Triggers |
|---|---|
| `educational` | "강의", "수업", "lecture", "training", "워크숍", "course", "교재" |
| `report` | "리포트", "보고서", "분석", "research", "findings", "executive review" |
| `consulting` | "전략", "사업 리뷰", "경영진 보고", "strategic recommendation" |
| `sales` | "제품 소개", "pitching", "고객 제안", "pricing", "demo deck" |
| `internal_update` | "OKR", "주간 리뷰", "팀 공유", "status update", "progress" |
| `proposal` | "RFP", "사업 제안서", "vendor proposal", "bid" |
| `keynote` | "컨퍼런스 발표", "신제품 발표", "launch", "announcement" |
| `unknown` | none of the above clear; ASK the user explicitly |

If `unknown`, prompt: "이 데크의 성격이 어디에 가장 가까울까요? (educational / report / consulting / sales / internal_update / proposal / keynote)"

### Step 3: Select narrative arc

Each `deck_type` has a starting-point arc (not a hard requirement — adapt to brief):

#### educational
```
cover → context(why_now) → agenda
  → [concept × 1–2 → example × 1–3 → exercise × 0–2] × N chapters
  → recap → qna/cta
```

#### report
```
cover → executive_summary → context
  → findings × 2–5 → insight × 1–2 → comparison × 0–2
  → summary → cta → [appendix: methodology]
```

#### consulting
```
cover → bottom_line(insight) → executive_summary
  → analysis(evidence) × 1–3 → implication(comparison) × 0–2
  → recommendation(solution) → roadmap → cta
```

#### sales
```
cover → problem(context) → opportunity(insight)
  → solution × 1–2 → proof(evidence) × 1–3 → comparison(vs alternative)
  → pricing/roadmap → cta
```

#### internal_update
```
cover → status_summary → progress(evidence) × 2–4
  → blockers(comparison) → next_steps(roadmap) → asks(cta)
```

#### proposal / keynote
Adapt from brief; no enforced arc.

### Step 4: Build `content_inventory[]`

For each user-provided source file (or in-conversation source):

```json
{
  "source_id": "src_01",
  "source_type": "file",
  "summary": "2026 Q1 churn analysis report (PDF, 24p)",
  "relevance": "high",
  "usable_for": ["evidence", "findings", "executive_summary"]
}
```

If no sources provided, set `inference` mode:

```json
{ "source_id": "inference", "source_type": "prompt", "summary": "User brief only", "relevance": "high", "usable_for": ["all"] }
```

### Step 5: Write per-slide plans

For each slide, populate (minimum):

```json
{
  "slide_number": 3,
  "slide_role": "evidence",            // from slide-role-enum.md
  "page_family": "body",               // title | chapter | body | end
  "working_title": "MAU 18개월 성장 추이",
  "core_message": "2024 H2 이후 단일채널 의존도가 떨어지며 성장률이 안정화됨.",
  "audience_takeaway": "이제 채널 다변화는 가설이 아니라 검증된 전략.",
  "why_here": "context 슬라이드에서 'why now' 제시 직후, 첫 데이터 evidence로 배치.",
  "recommended_layout_family": "data",
  "content_blocks": [
    { "block_type": "title", "purpose": "anchor the evidence claim", "content_instruction": "MAU 18개월 성장 추이" },
    { "block_type": "chart", "purpose": "show 18-month trend", "content_instruction": "line chart, MAU monthly, accent series" },
    { "block_type": "callout", "purpose": "name the inflection", "content_instruction": "2024-09 채널 다변화 시작점 표기" }
  ],
  "chart_strategy": "growth-trend",
  "chart_takeaway": "18개월 연속 두 자릿수 성장. 단일 채널 의존도 감소 후 변동성도 감소.",
  "table_strategy": null,
  "table_takeaway": null,
  "content_constraints": {
    "must_include": ["월별 MAU 절대값", "9월 inflection annotation"],
    "must_not_include": ["수익 metric", "경쟁사 비교"],
    "evidence_to_use": ["src_01:p7", "src_01:p12"]
  },
  "evidence_sources": ["src_01"],
  "priority": "must"
}
```

### Step 5.5: Fact-check (web search-based claim verification)

**Activation:**
- Auto-on for decks ≥ 7 slides
- Forced ON when brief contains `사실 확인` / `출처 확인` / `fact check` / `verify`
- Skipped for ≤ 6-slide decks without explicit trigger (overhead-aware)

**What to verify (auto-extract claims):**

From each slide's `core_message`, `audience_takeaway`, `chart_data` values, and `content_constraints.must_include`:

| Priority | Pattern |
|---|---|
| HIGH | chart_data series values / must_include explicit numbers (counts, %, currency, units) |
| HIGH | Events/announcements within the last 3 years |
| HIGH | External person / organization attributions |
| MEDIUM | Numbers / years embedded in core_message |
| MEDIUM | Proper nouns (companies, products, people) |
| LOW (SKIP) | General knowledge / definitions |

Verify HIGH/MEDIUM only. Cap at 3 claims per slide to limit overhead.

**Execution:**

1. Load tools: `ToolSearch("select:WebSearch,WebFetch")`
2. For each claim: `WebSearch("<claim text> source authoritative 2025 2026")`
3. Pick 1–2 trustworthy sources (gov sites, official announcements, major outlets, Wikipedia). Use `WebFetch` for deep-check when ambiguous.
4. Classify: `verified` / `corrected` / `unverified`

**Plan integration:**

- **verified** → add `{"source_id": "web_NN", "source_type": "web", "summary": "<URL+summary>", "relevance": "high", "usable_for": ["evidence"]}` to `content_inventory`; append `web_NN` to slide's `evidence_sources`
- **corrected** → fix the claim in-place; record before/after in `fact_check_log`
- **unverified** → soften the claim ("≈X" → "estimated X–Y"); append `"inference-unverified"` to `evidence_sources`

**New root field `fact_check_log[]`:**

```json
"fact_check_log": [
  {
    "claim": "<text>",
    "slide_number": N,
    "priority": "HIGH" | "MEDIUM",
    "status": "verified" | "corrected" | "unverified",
    "source": "<URL or null>",
    "original": "<original text>",
    "corrected_to": "<fixed text or null>",
    "checked_at": "YYYY-MM-DD"
  }
]
```

**User-visible summary (printed in Step 8 review):**

```
Fact-check: verified N / corrected M / unverified K
unverified:
  - slide #N: "<claim>" — no authoritative source
corrected:
  - slide #M: "<orig>" → "<fix>" (source: <URL>)
```

> Design intent: Non-blocking. If a failed claim is critical, the user uses a Step 8 stop keyword to request plan edits. Internal / unpublished data legitimately can't be verified, so we never block on fact-check.

### Step 6: Self-validate against Layer 1 (R1–R5)

Run mental pass:
- R1: every slide has all 4 fields ✓
- R2: every chart slide has `chart_takeaway`; every table slide has `table_takeaway` ✓
- R3: 8–12 default; if > 20, `ordering_notes` filled ✓
- R4: no 3+ consecutive same family without justification ✓
- R5: every slide's `evidence_sources` non-empty ✓

### Step 7: Write `slide_plan.json` + run validator

```bash
python3 .claude/skills/slide-plan/scripts/validate_plan.py output/<project>/slide_plan.json
```

The validator enforces R1–R5 + chart_strategy enum + slide_role enum + diagnostic ratios. Fix any reported errors and re-run.

### Step 8: User review checkpoint (soft notice — non-blocking by default)

Present a markdown summary (one line per slide):

```markdown
## slide_plan.json 요약 — <project_name>
- **deck_type**: educational
- **target_length**: 11 slides (default 8–12)
- **narrative_arc**: cover → context → agenda → [concept × 2 → example × 2 → exercise × 1] → recap → cta

| # | role | family | working_title | core_message |
|---|---|---|---|---|
| 1 | cover | structure | ... | ... |
| 2 | context | insight | ... | ... |
...

체계적 모드 — Plan 작성 완료. 같은 턴 안에서 /slide로 진행합니다.
수정이 필요하면 `다시` / `수정` / `멈춰` / `잠깐` / `wait` / `stop` 중 하나로 응답하세요.
```

**진행 분기 (3개 슬라이드 파이프라인 공통):**

| 사용자 다음 메시지 | 행동 |
|---|---|
| `다시` / `수정` / `멈춰` / `잠깐` / `wait` / `stop` / `다른` / 슬라이드 N번 수정 같은 명시적 변경 요청 | plan 수정 모드 — 해당 필드/슬라이드만 갱신 후 `validate_plan.py` 재실행 → summary 재출력 |
| 그 외 (`/slide`, `OK`, `진행`, 응답 없음) | `/slide`로 즉시 진입 — plan 그대로 소비 |

**원격 환경 (Slack / OpenClaw / Telegram 등):** BLOCKING 대기 금지. summary 출력 + 같은 턴에 `/slide` 자동 진입. 사용자가 다음 턴에서 stop keyword를 주면 그때 plan 수정 모드로.

**로컬 + 명시적 BLOCKING 요청:** 사용자가 `--confirm-plan` / "확인하고 진행" 같이 명시한 경우에만 BLOCKING 유지.

> 설계 의도: BLOCKING은 plan dropped(채택률 0%)의 주된 원인이었다. 기본을 auto-proceed로 두고, stop keyword를 명시적으로 안내한다.

---

## `slide_plan.json` schema (reference)

```json
{
  "deck_meta": {
    "working_title": "string",
    "deck_goal": "string",
    "deck_type": "consulting | educational | report | sales | internal_update | proposal | keynote | unknown",
    "target_audience": "string",
    "tone": "string",
    "target_length": { "slides": 0, "reasoning": "string" }
  },
  "design_dependency": {
    "preset_name": "string (e.g., jangpm)",
    "design_md_path": ".claude/skills/slide/templates/layouts/<preset>/DESIGN.md",
    "allowed_layout_families": ["structure", "insight", "breakdown", "compare", "data", "process", "visual"],
    "consistency_notes": ["string"]
  },
  "story_arc": {
    "narrative_shape": "string (e.g., 'concept → example → exercise loop')",
    "why_this_order_is_persuasive": "string"
  },
  "content_inventory": [
    {
      "source_id": "string",
      "source_type": "file | prompt | inference",
      "summary": "string",
      "relevance": "high | medium | low",
      "usable_for": ["string"]
    }
  ],
  "slides": [
    {
      "slide_number": 1,
      "slide_role": "string (from slide-role-enum.md)",
      "page_family": "title | chapter | body | end",
      "working_title": "string",
      "core_message": "string",
      "audience_takeaway": "string",
      "why_here": "string",
      "recommended_layout_family": "string",
      "content_blocks": [
        {
          "block_type": "title | subtitle | bullets | chart | table | callout | quote | metric_cards | icon_group | infographic | diagram_flow | image | code | footer_note",
          "purpose": "string",
          "content_instruction": "string"
        }
      ],
      "chart_strategy": "string | null (from chart-rhetorical-roles.md)",
      "chart_takeaway": "string | null",
      "table_strategy": "string | null",
      "table_takeaway": "string | null",
      "content_constraints": {
        "must_include": ["string"],
        "must_not_include": ["string"],
        "evidence_to_use": ["string"]
      },
      "evidence_sources": ["string"],
      "priority": "must | should | could"
    }
  ],
  "ordering_notes": {
    "split_topics": ["string"],
    "merged_topics": ["string"],
    "deferred_topics": ["string"],
    "appendix_candidates": ["string"]
  }
}
```

> The schema is intentionally NOT shared across slide-html / slide-pencil / slide-svg presets. `recommended_layout_family` and `chart_strategy` enum values are preset-specific (drawn from each preset's `DESIGN.md`). The shape above is slide-svg's contract.

---

## Output paths

| Artifact | Path |
|---|---|
| Plan SSOT | `output/<project>/slide_plan.json` |
| Markdown summary (review) | printed to chat (not saved by default) |
| Validator log | `output/<project>/slide_plan.validation.log` (only on validation failure) |

---

## Reference files

| File | Role |
|---|---|
| `.claude/skills/slide/templates/layouts/<preset>/DESIGN.md` | `recommended_layout_family` enum + chart treatment |
| `.claude/skills/slide/references/chart-rhetorical-roles.md` | `chart_strategy` enum + chart template mapping |
| `.claude/skills/slide/references/slide-role-enum.md` | `slide_role` enum + arc defaults + diagnostic ratios |
| `.claude/skills/slide/references/anti-slop-core.md` | structural anti-patterns |
| `.claude/skills/slide-plan/scripts/validate_plan.py` | R1–R5 + enum + diagnostic ratio enforcement |

---

## Out of scope

- **Visual style decisions** — locked by active preset's `theme-active.json` and `DESIGN.md`. `slide-plan` plans content; it does NOT pick colors, fonts, or specific patterns within a family.
- **SVG generation** — `/slide` Executor's job (Step 6 of `/slide` SKILL.md).
- **Image generation** — `/slide` Image_Generator phase (Step 5).
- **PPTX export** — `/slide` Step 7.
- **Theme switching** — `/theme-init`'s job. `slide-plan` reads the active theme; it does not modify it.

---

## Failure modes

| Symptom | Cause | Fix |
|---|---|---|
| `validate_plan.py` reports R1 error | A slide is missing `core_message` / `audience_takeaway` / `why_here` / `recommended_layout_family` | populate the missing field(s) |
| `validate_plan.py` reports R2 error | `chart_strategy` set but `chart_takeaway` empty | write the takeaway sentence |
| `validate_plan.py` reports R5 error | `evidence_sources` empty | add a source_id from `content_inventory[]` or `"inference"` |
| `validate_plan.py` reports invalid enum | typo in `slide_role` / `recommended_layout_family` / `chart_strategy` | fix typo; consult enum reference files |
| Diagnostic warning: research dump | evidence ≫ insight count | add insight slides between findings |
| `/slide` does not pick up plan | wrong path | save to `output/<project>/slide_plan.json` exactly |

---

<!-- Authored 2026-04-28 as Phase 1 of slide-plan introduction. -->
