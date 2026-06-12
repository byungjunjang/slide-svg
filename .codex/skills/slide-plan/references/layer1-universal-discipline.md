> 이 파일은 /slide-plan의 Layer 1 검증 규칙 상세이며 plan 검증 단계에서 로드한다. R1/R2/R4/R5의 기계 검증은 scripts/validate_plan.py가 수행한다.

## Layer 1 — Universal Discipline (enforced by this skill)

These five rules are **hard-enforced** by `validate_plan.py` and are also re-checked by `/slide` Executor at render time. They are the quality contract between `slide-plan` and `/slide`.

### R1. Per-slide rationale (4 fields)

Every slide entry MUST populate:

| Field | Meaning |
|---|---|
| `core_message` | The single argument this slide makes |
| `audience_takeaway` | One line the audience leaves with |
| `why_here` | Why this slide is at this position (vs earlier / later / cut) |
| `recommended_layout_family` | One of: `structure` / `insight` / `breakdown` / `compare` / `data` / `process` / `visual` (see active preset's `DESIGN.md` §5) |

### R2. Visual-led slides require takeaway text

- Slides where `chart_strategy` is set MUST also have non-empty `chart_takeaway`.
- Slides where `recommended_layout_family == "data"` and a `block_type: table` exists MUST have non-empty `table_takeaway`.
- A chart / table without a takeaway sentence is rejected at plan time.

### R3. Length pressure

- If user does not specify slide count, default to **8–12 slides**.
- Decks > 20 slides require a second pass: split / merge / defer candidates listed in `ordering_notes`.
- Default heuristic: "tighter deck > bloated deck."

### R4. No lazy repetition

- No 3+ consecutive slides with the same `recommended_layout_family` (except `structure`).
- Same family for 3+ in a row requires a written justification in each slide's `why_here`.
- Min 3 distinct layout families per deck.

### R5. Evidence mapping

- Every slide's `evidence_sources` MUST be non-empty.
- Allowed values: source file IDs from `content_inventory[]`, OR the literal string `"inference"` if no source backs the claim.
- Empty `evidence_sources` is rejected at plan time.
