# slide_role Enum — slide-svg

> **Authority:** SSOT for `slide_role` values in `slide_plan.json`. `slide-plan` validator enforces this enum; `/slide` Executor consults it to pick layout family and density rhythm.
> **Adapted from:** internal slide-plan design guide §Layer 2 + slide-svg's primary use cases (educational / report).

---

## Why a constrained enum?

Free-text role labels drift across decks ("introduction", "intro", "opener", "overview" all mean the same thing). A fixed enum gives:
- Plan-time validation (typos rejected immediately)
- Layout family inference defaults (e.g., `cover` → `structure`, `evidence` → `data`)
- Pacing diagnostics (a deck with 12 `evidence` and 0 `insight` is a research dump, not a story)

---

## Structure: 8 universal roles + per-deck-type extensions

### Universal 8 (always available, deck-type independent)

| `slide_role` | Meaning | Default `recommended_layout_family` | Default `page_family` |
|---|---|---|---|
| `cover` | Opening slide — topic, presenter, date | `structure` | `title` |
| `context` | Why this matters now / what set the stage | `breakdown` or `insight` | `body` |
| `insight` | The single core argument or so-what | `insight` | `body` |
| `evidence` | Data / case / source supporting an insight | `data` or `breakdown` | `body` |
| `solution` | Recommended action / proposed approach | `breakdown` or `process` | `body` |
| `summary` | Recap / key points consolidation | `breakdown` or `insight` | `body` |
| `cta` | Closing call-to-action / next steps | `structure` or `insight` | `end` |
| `appendix` | Supporting material kept after the main story | varies | `body` (after closing) |

### Extensions by `deck_type`

`slide-plan` detects `deck_type` from the user brief; the matching extension set unlocks. Universal 8 are always available across all deck types.

#### `educational` (slide-svg primary use case)

| `slide_role` | Meaning | Default layout family | Notes |
|---|---|---|---|
| `agenda` | Session topics list | `structure` (`agenda` pattern) | early-deck position |
| `concept` | Definition / theory / principle introduction | `breakdown` or `insight` | core teaching unit |
| `example` | Worked example illustrating a concept | `visual` or `data` | follows `concept` |
| `exercise` | Practice problem / activity prompt | `breakdown` (`numbered-row`) | optional, mid-deck |
| `recap` | Lesson recap before next chapter | `summary`-equivalent for educational | end of chapter |
| `qna` | Open Q&A slide | `structure` | optional, near end |

**Educational arc default:**
```
cover → context(why_now) → agenda
  → [concept × 1–2 → example × 1–3 → exercise × 0–2] × N chapters
  → recap → qna/cta
```

#### `report` (slide-svg secondary use case)

| `slide_role` | Meaning | Default layout family | Notes |
|---|---|---|---|
| `executive_summary` | One-page TL;DR of findings | `breakdown` (`kpi-row` or `goal-breakdown`) | slide 2 (after cover) |
| `findings` | Discrete finding with data | `data` or `breakdown` | the meat |
| `methodology` | How the analysis was done | `process` or `breakdown` | optional, often appendix |

**Report arc default:**
```
cover → executive_summary → context
  → findings × 2–5 → insight × 1–2 → comparison × 0–2
  → summary → cta → [appendix: methodology]
```

#### `consulting`

| `slide_role` | Meaning | Default layout family | Notes |
|---|---|---|---|
| `problem` | Statement of the problem being solved | `insight` or `breakdown` | early |
| `comparison` | A vs B contrast (options matrix) | `compare` | implication phase |
| `roadmap` | Time-staged execution plan | `process` (`process-flow`) | post-recommendation |

#### `sales`

| `slide_role` | Meaning | Default layout family | Notes |
|---|---|---|---|
| `problem` | Buyer's pain | `insight` | early |
| `proof` | Case study / testimonial / benchmark | `data` or `visual` | mid |
| `comparison` | Vs alternative / status quo | `compare` | late-mid |
| `pricing` | Pricing tiers | `compare` (`comparison_columns`) | near end |
| `roadmap` | Implementation timeline | `process` | optional |

#### `internal_update`

| `slide_role` | Meaning | Default layout family | Notes |
|---|---|---|---|
| `status_summary` | Overall status snapshot | `breakdown` (`kpi-row`) | slide 2 |
| `progress` | What shipped / advanced | `data` or `breakdown` | core |
| `blockers` | What's stuck and why | `compare` or `breakdown` | mid |
| `next_steps` | Upcoming work | `process` or `breakdown` | late |
| `asks` | Asks of the audience | `insight` | end |

#### `proposal`

| `slide_role` | Meaning | Default layout family | Notes |
|---|---|---|---|
| `problem` | Buyer's stated need | `insight` | early |
| `comparison` | Why us vs others | `compare` | mid |
| `pricing` | Cost / scope tiers | `compare` | late |
| `team` | Who will deliver | `breakdown` (`numbered-row` of profiles) | mid-late |
| `roadmap` | Delivery timeline | `process` | late |

#### `keynote`

| `slide_role` | Meaning | Default layout family | Notes |
|---|---|---|---|
| `hook` | Attention-grabbing opener (after cover) | `insight` | slide 2 |
| `vision` | Future-state declaration | `insight` (`hero-statement`) | core |
| `demo` | Product demonstration | `visual` (`image-text` or `image-annotated`) | mid |
| `availability` | When/how to access | `structure` or `breakdown` | end |

---

## Diagnostic ratios (warned at plan-time)

`validate_plan.py` emits a warning — not a hard reject — when a deck's role distribution is structurally unbalanced.

| Symptom | Diagnostic | Suggested fix |
|---|---|---|
| **research dump** | `evidence` count > 5× `insight` count | add insights between findings |
| **assertion only** | `insight` count > `evidence` count and total > 8 slides | back insights with data |
| **no opening punch** | no `insight` / `hook` / `executive_summary` in first 3 slides | add an early-deck so-what |
| **buried CTA** | no `cta` in last 2 slides | add closing call-to-action |
| **methodology bloat** | `methodology` > 20% of slides for `report` deck_type | move to appendix |

These are heuristics, not rules. `slide-plan` may justify any distribution via the `slides[].why_here` field.

---

## When `deck_type == "unknown"`

Use only the universal 8. Do not infer extension roles from brief text alone. Prompt the user to confirm `deck_type` before locking the plan.

---

## Mapping summary (cheat sheet)

```
Universal:  cover · context · insight · evidence · solution · summary · cta · appendix
educational: + agenda · concept · example · exercise · recap · qna
report:     + executive_summary · findings · methodology
consulting: + problem · comparison · roadmap
sales:      + problem · proof · comparison · pricing · roadmap
internal:   + status_summary · progress · blockers · next_steps · asks
proposal:   + problem · comparison · pricing · team · roadmap
keynote:    + hook · vision · demo · availability
```

---

<!-- Hand-authored 2026-04-28 as Phase 0.3 of slide-plan introduction. -->
