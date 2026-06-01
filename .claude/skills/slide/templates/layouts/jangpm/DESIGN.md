# DESIGN.md — Jangpm

> Preset-level design vocabulary for `slide-plan` consumption.
> Pairs with `theme-active.json` (token SSOT) and `references/patterns.md` (HTML pattern catalog).
>
> **Purpose:** Give `slide-plan` the structured vocabulary it needs to produce `slide_plan.json` entries (`recommended_layout_family`, `chart_strategy`) that `/slide` Executor can consume without re-deciding visual style.
>
> **Scope:** Jangpm only. Other presets supply their own `DESIGN.md` via `/theme-init`.

---

## 1. Visual Theme & Atmosphere

- **Tone:** editorial, analytical, declarative. Korean lecture / report register.
- **Reference moodboard:** Notion / Linear / Vercel sensibility adapted to instructional content. Korean broadsheet typography density.
- **Atmosphere:** generous whitespace, restrained color, clear typographic hierarchy. Reads as a *report*, not a *deck*.
- **Anti-mood:** "colorful SaaS dashboard," "marketing keynote with rainbow gradients," "PowerPoint with clip art."

**One-line litmus:** If a slide could be cropped and pasted into a Korean business weekly without looking out of place, it passes the Jangpm read.

---

## 2. Palette & Contrast Behavior

### 2.1 Allowed colors (literal, locked)

Jangpm is a **monochrome + single accent** system. The ONLY hex values that may appear in any generated SVG / CSS / Chart.js palette are listed below.

| Token | Hex | Role |
|---|---|---|
| `--bg` | `#FAFAF9` | page background |
| `--surface` | `#FFFFFF` | card / container |
| `--surface-alt` | `#F5F5F4` | grouped row / nested card |
| `--text` | `#1A1A1A` | primary text (never pure `#000`) |
| `--text-secondary` | `#6B7280` | secondary text |
| `--text-tertiary` | `#9CA3AF` | captions, page numbers |
| `--border` | `#E5E7EB` | default divider |
| `--border-strong` | `#D4D4D4` | emphasis divider |
| `--accent` | `#4633E3` | sole brand pointer |
| `--accent-soft` | `#E8E5FC` | accent-tinted highlight bg |
| `--accent-ink` | `#2E1FB3` | accent pressed / dark |
| `--positive` | `#059669` | data context only — growth / success |
| `--negative` | `#E11D48` | data context only — decline / error |
| `--warning` | `#D97706` | data context only — caution |

### 2.2 Contrast & accent budget

- **≤ 2 accent events per content slide.** An "event" is any of: accent text fill, accent-soft container, accent-stroked emphasis rule. More than two cancels the pointer effect.
- **Card differentiation rule:** in any card grid, at least one card must be visually distinct (accent-soft bg or highlighted metric). Equal-weight grids are a design smell.
- **Semantic colors are data-only.** `--positive`/`--negative`/`--warning` are valid only when the color encodes a meaning the reader must decode (trend arrow, churn metric, status pill). Never decorative.
- **Charts use single-accent opacity ladder:** `rgba(70, 51, 227, 0.85 / 0.60 / 0.40 / 0.25)`. Multi-hue palettes are forbidden (see §8).

### 2.3 Background hierarchy

`--bg` (page) → `--surface-alt` (grouped) → `--surface` (focal card) → `--accent-soft` (highlighted card). Drop one rung at a time; skipping rungs reads as visual stuttering.

---

## 3. Typography Hierarchy

### 3.1 Font chain (locked)

```
Pretendard, 'Apple SD Gothic Neo', 'Malgun Gothic', Arial, sans-serif
```

Every `<text>` element in generated SVG uses this exact chain. Truncated or substituted chains fail Anti-Slop Rule T3.

### 3.2 Type scale

| Role | Size (px) | Weight | LH | Tracking | Use |
|---|---|---|---|---|---|
| Display | 56 | 800 | 1.08 | -1.68 | title slide hero |
| Display-sm | 40 | 800 | 1.10 | -0.80 | hero stat / closing accent |
| Headline | 32 | 700 | 1.20 | -0.64 | content slide title |
| Title | 18.4 | 600 | 1.30 | 0 | card title, subtitle |
| Body | 15.2 | 400 | 1.60 | 0 | body text (default density) |
| Caption | 12.8 | 500 | 1.40 | 0 | annotations |
| Label | 12.8 | 600 | 1.40 | 0.64 | uppercase taxonomy (eyebrow) |

### 3.3 Hierarchy rules

- **Display vs Headline:** `.display` is reserved for title / section / closing slides. Body content slides use `.headline`.
- **Body baseline 15.2px** is calibrated for "report density" (the default). Low-density training decks (3–4 items / page) may raise body to 18.4px — exception, not norm.
- **Label as taxonomy marker:** uppercase + 0.64 letter-spacing only when the caption labels a category (e.g., "FOUNDATION" / "GROWTH" / "ENTERPRISE"). Regular metric captions stay sentence-case.

---

## 4. Spacing & Density

### 4.1 8px grid

`--space-1` 4 / `--space-2` 8 / `--space-3` 12 / `--space-4` 16 / `--space-5` 20 / `--space-6` 24 / `--space-8` 32 / `--space-10` 40 / `--space-12` 48 / `--space-14` 56 / `--space-16` 64.

### 4.2 Slide-level

- Slide outer padding: `--space-14` (56px); bottom padding `--space-16` (64px) reserves GM line space.
- Card padding: `--space-6` (24px). Card gap: `--space-6` (24px).
- Internal card stacking: 0.04–0.06" (~5–8px) gaps between icon → label → metric → context. Never leave > 0.3" (~24px) gap inside a card — empty bottom-half is the symptom.

### 4.3 Density floors (Jangpm-specific, override theme-agnostic minimums)

- **Every card has ≥ 3 content layers** (icon/badge + title + body + caption/metric). Two-layer cards (icon + title only) read as unfinished.
- **No text-only slides.** Even quote / hero patterns require ≥ 1 visual element alongside the text.
- **Stats cards include context** (e.g., "vs industry avg 3.2%"). Bare numbers read as placeholder.
- **Chart container height ≥ 400px** for single-chart slides. 320px feels squeezed.

### 4.4 Density vs sparsity

Jangpm leans dense **with visuals, not text** — when tempted to add text to fill space, add a *visual* instead (chart, diagram, micro-chart, callout, divider rule). This is **bounded by `anti-slop-core.md` Rules 21–22**: one dominant message, ≤3 bullets, ≥30% whitespace, a clear top-right quiet zone. "Dense" means a **dominant evidence visual carrying the page** — never a wall of body text or stacked cards. Sparsity is acceptable on title / section / closing pages.

---

## 5. Layout Grammar (= `recommended_layout_family` vocabulary)

This is the canonical vocabulary `slide-plan` writes into `recommended_layout_family`. Each family bundles 2–8 patterns from `references/patterns.md` that share an information shape.

> **Why family-level, not pattern-level?** `slide-plan` decides the *shape* of information; `/slide` Executor picks the specific pattern based on item count, evidence type, and visual rhythm. Family is the right abstraction for plan-level decisions.

| Family | Patterns (from patterns.md) | Use when | Item-count guide |
|---|---|---|---|
| **structure** | `title`, `section`, `closing`, `agenda` | Deck scaffolding — opening / chapter break / table of contents / closing | 1 hero element |
| **insight** | `hero-statement`, `quote`, `before-after` | Single-takeaway slides — the "so-what" hits hard | 1 statement + 1 visual evidence |
| **breakdown** | `report-summary`, `icon-explainer`, `report-two-column`, `goal-breakdown`, `process-row`, `kpi-row`, `content-cards`, `concept-cards`, `numbered-grid`, `numbered-row`, `numbered-column`, `two-column`, `checklist`, `bento-grid` | N parallel concepts, components, principles, items | 2–6 cards (2×2 / 2×3 / 1×3 / 1×4 / asymmetric) |
| **compare** | `comparison-table`, `comparison`, `two-column` (when contrastive) | Side-by-side contrast — A vs B, options matrix, pros/cons | 2–4 columns |
| **data** | `stats-dashboard`, `chart-bar`, `chart-line`, `chart-pie`, `data-table`, `kpi-row` | Metrics, charts, tables — the evidence is numeric | 1 chart + 1 takeaway card, OR 3–4 KPI cards |
| **process** | `process-flow`, `agenda` (when sequential), `numbered-row` (when ordered) | Time-ordered or step-ordered content — pipeline, journey, methodology | 3–8 steps |
| **visual** | `image-text`, `image-annotated`, `diagram`, `code-explain` | Image / diagram / code-led explanation | 1 primary visual + annotation |

**Layout selection heuristics:**
- 3–4 parallel items → `breakdown` (`numbered-row` or `concept-cards`)
- 5–6 parallel items → `breakdown` (`numbered-grid` or `bento-grid`)
- 2 contrastive items → `compare` (`comparison-table` or `two-column`)
- "growth over time" → `data` (`chart-line`)
- "share / proportion" → `data` (`chart-pie`)
- "ranked categories" → `data` (`chart-bar`)
- methodology stages → `process` (`process-flow`)
- single insight needing punch → `insight` (`hero-statement`)

**Diversity rules** (enforced in `/slide` Executor):
- No consecutive identical patterns (except `section`)
- Min 3 layout types per deck
- Min 40% pattern differentiation
- Same family ≥ 3 consecutive slides → require justification in `slide_plan.json` (`why_here` field)

### 5.1 Hybrid Pattern Catalog — body slide default vocabulary

A body slide that reduces to "headline + 1×N cards" is the failure mode this preset most often slides into. Below are the **hybrid patterns** that should be the *default starting point* for body slides — not exotic alternatives, but the baseline. Each hybrid combines 2–3 primitives so that no single visual primitive carries the slide alone.

> **Use this catalog as Executor's first-look when picking a pattern within a plan-decided family.** Only fall back to single-primitive patterns when the slide is genuinely a single thought (cover / chapter / hero closing).

| Hybrid pattern | Composition | Best-fit roles | Notes |
|---|---|---|---|
| **ruled-list-with-eyebrow** ★ | uppercase eyebrow label + horizontal hairline (`#E5E7EB`, 1px) + stack of `bold-label : body-text` rows separated by hairlines (NO card boxes, NO `rect rx=12` containment). Each row = `<text>` for label + `<text>` for body + `<line>` divider beneath. | `concept`, `recap`, `solution` (any list-of-items where each item has a name + description) | **jangpm signature pattern**. Replaces 1×N card grids. Visually lighter, editorial. Matches Rule 15 (No Card-First Layouts). Use for "what it contains / what each does / what to avoid" lists. |
| **columns-with-vertical-rules** ★ | uppercase eyebrow label + horizontal hairline + N columns (3–4) separated by **vertical hairlines** (1px `#E5E7EB`, NO card boxes). Each column = `bold-title` + body lines, no surrounding `<rect>`. Bottom horizontal hairline closes the section. | `concept`, `breakdown`, `comparison`, `executive_summary` | **jangpm signature pattern**. Replaces 1×N card grids when items are short and parallel. Lighter than cards, table-like rhythm without table heaviness. Use for "components / categories / pillars" rows. |
| **chart-led-with-takeaway-stack** | left chart (≈60% width) + right column with 2–3 stacked cards (gap / metric / takeaway) | `evidence`, `findings`, `executive_summary` (data-rich) | data family default; primary chart drives, cards interpret |
| **table-with-adjacent-cards** | left comparison table (≈55%) + right column mini-cards or callouts | `comparison`, `evidence`, `findings` | one column of the table = `col-recommended` (accent-soft) |
| **definition-with-side-data** | left big definition / quote / concept name (≈50%) + right supporting chart, mini-stat, or mapping diagram | `concept`, `insight` (body-tier) | replaces "giant accent text + cards" anti-pattern; the *concept* and *evidence* sit side-by-side |
| **paired-concept-asymmetric** | 1:1 split where one side is a representative *visualization* (mini-bars / share doughnut / icon group) and the other is text-led | `insight`, `concept`, `comparison` | jangpm slide type for "X has Y mix vs Z is single-focus" — visualization carries the contrast, not color |
| **breakdown-with-anchor-stat** | top hero stat (display-sm) + bottom 1×3 or 1×4 cards that decompose the stat | `evidence`, `findings`, `solution` | hero stat anchors why the cards matter |
| **process-with-callout-band** | horizontal chevron / numbered_steps row + bottom accent-soft callout strip with the rule-of-thumb | `process`, `solution`, `methodology` | the callout band gives the "why this order" so the process isn't just shapes |
| **mapping-grid (3-row triplet)** | 3 rows of `label : map-target : implication` — small typography, dense | `concept`, `insight`, `recap` | when the slide's job is to map A↔B for ≥3 pairs (e.g., metaphor ↔ AI mapping) |
| **icon-explainer with metric inline** | icon-grid pattern but each tile has `icon + title + body + 1 metric/stat` | `concept`, `evidence` (qualitative-led but numeric-supported) | replaces card-grid-of-3-text-only |
| **quote-with-attribution-data** | large pull quote + small attribution row + 1 supporting data card | `insight`, `cta`, `recap` | pull quote alone is a slop signal — always pair with concrete attribution / number |

**Rule of thumb for picking within a family:**
- `breakdown` for **list-of-items with name+description** → **`ruled-list-with-eyebrow`** (★ first choice — jangpm signature) or `columns-with-vertical-rules` over plain 1×N cards
- `breakdown` for **parallel concepts (3–4)** → **`columns-with-vertical-rules`** (★ first choice) over 1×4 boxed cards
- `breakdown` for **stat-anchored decomposition** → `breakdown-with-anchor-stat` or `icon-explainer with metric inline`
- `insight` (body) → prefer `definition-with-side-data` or `paired-concept-asymmetric` over giant accent headline + cards
- `compare` → prefer `table-with-adjacent-cards` over plain 2-column text
- `data` → prefer `chart-led-with-takeaway-stack` over chart + bottom-band-only
- `process` → prefer `process-with-callout-band` over numbered_steps alone
- `concept` (definition + components) → **`columns-with-vertical-rules`** for the components row, with the definition occupying the top half (★ jangpm signature combo)

**Pick by content shape, not default.** The two ★ patterns (`ruled-list-with-eyebrow`, `columns-with-vertical-rules`) are the jangpm editorial signature for **list-of-items / parallel-components / definition-of-N-things** content — they replace 1×N card grids when the items are short, parallel, and need no containment. They are NOT a universal default; falling back to ★ for every slide produces "monolithic gray editorial" decks where the whole deck reads as one repeated hairline-list pattern.

| Content shape | First-choice primitive | Why |
|---|---|---|
| list-of-items with name + description (3–6 items) | ★ `hairline-list` | jangpm signature; lighter than cards |
| parallel concepts / pillars / categories (3–4) | ★ `hairline-list` (`columns-with-vertical-rules`) | table-rhythm without table heaviness |
| numeric evidence / growth / share / forecast | `chart-led` (`chart-led-with-takeaway-stack`) | chart drives, cards interpret |
| structured comparison (A vs B / matrix) | `table-led` (`table-with-adjacent-cards`) | one column accent-soft for the recommended choice |
| time-ordered / step-ordered methodology | `process-flow` (`process-with-callout-band`) | sequence is the message; cards collapse it |
| stat-anchored decomposition | `boxed-cards` (`breakdown-with-anchor-stat`) | hero stat anchors why the cards matter |
| single-thought body insight (definition / metaphor) | `boxed-cards` (`definition-with-side-data` / `paired-concept-asymmetric`) | text + paired evidence beats giant headline |

**Reach for the ★ pattern only when the content is genuinely a list-of-items or parallel-components.** For data, comparison, process, or stat-anchored content, the first-choice primitive is `chart-led` / `table-led` / `process-flow` / `boxed-cards` respectively — NOT ★. The Dominant Primitive Cap (executor.md §0.1 #4) prevents 3+ consecutive slides from sharing any single primitive, including ★, so naturally diverse content forces primitive rotation.

**Visual specification for ★ hairline patterns:**

```
┌─ vertical position guide (no actual lines drawn here, just spacing) ─┐
                                                                       
EYEBROW LABEL              ← 12.8 / 600 / 0.64 tracking / #6B7280 / uppercase
─────────────────          ← <line stroke="#E5E7EB" stroke-width="1"/>
                           ← gap ≈ 16–20px
ROW 1 LABEL    BODY TEXT   ← label: 15.2/700/#1A1A1A, body: 15.2/400/#6B7280
─────────────────          ← <line stroke="#E5E7EB" stroke-width="1"/>
ROW 2 LABEL    BODY TEXT
─────────────────
...
```

**Implementation discipline for ★ patterns:**
- NO `<rect rx="12">` wrapping the list/columns — that immediately turns it into a card
- Hairlines are `<line x1=... x2=... y1=... y2=... stroke="#E5E7EB" stroke-width="1"/>` — NOT `<rect>` thin strips
- Vertical column separators in `columns-with-vertical-rules` are full-height `<line>` between adjacent columns (NOT box borders)
- The eyebrow uses the `label` type style (uppercase + 0.64 tracking) — that's the *only* typographic flag the section needs; no card chrome required
- One accent emphasis per section is enough — usually a single accent-soft horizontal band at the bottom for the "verdict / takeaway / focal item", everything else in monochrome typography

**Single-primitive patterns are for**:
- `structure` family on cover / chapter / closing (not body)
- An unusually data-poor body slide where the single thought genuinely fills the page (rare — < 10% of body slides)

---

### 5.2 Variation Inspirations (per hybrid pattern)

> **Purpose:** Each hybrid pattern in §5.1 has an *anchor* shape — the standard composition. Without an explicit catalog of *intentional variations*, the LLM defaults to "anchor copy" and the deck reads as the same pattern repeated. This subsection gives 4–6 concrete variations per pattern so the executor can pick one consciously.
>
> **How to use**: Per-page audit (`executor.md §2`) requires recording one applied variation per body slide. Pick from the variations below, OR mark `표준` if the unembellished anchor is genuinely correct for the slide. Across the deck, target ≥ 70% of body slides on a non-`표준` variation. **Cap still applies — only ONE variation per slide, and the per-slide accent ≤ 2 budget is unchanged.**
>
> **What counts as a variation**: a single, intentional deviation from the anchor (one row promoted, one column dark, one column added, one segment in a different visual register). NOT a wholesale redesign — the pattern's silhouette must remain recognizable. Stacking 2+ variations on one slide is forbidden (it reads as random).

#### `ruled-list-with-eyebrow` ★

- **Hero first row** — top row's label is title-tier (18.4/700) + body 2 lines, remaining rows stay at 15.2. The first row anchors why the rest matters.
- **Accent-soft row highlight** — exactly one row's hairline-divided strip becomes `<rect fill="#E8E5FC">` background (full-row span, no `rx`). Reserved for the focal item / verdict.
- **Rightmost number column** — append a third column (right-edge): each row gains a number / KPI / percentage in `tabular-nums`, body becomes 18.4 weight 700 accent for the focal value only.
- **Multi-section list** — split rows into 2 or 3 sub-sections, each with its own uppercase eyebrow + hairline. Replaces a single 6-row list with a `2 + 2 + 2` structured taxonomy.
- **Verdict band closer** — final row replaced by a full-width accent-soft band with one declarative sentence (the "so-what"). The list builds, the band lands.
- **Inline icon column** — insert a small (20px) `tabler-outline` icon column at the leftmost position; icons label the row category (warning / check / arrow), body unchanged.

#### `columns-with-vertical-rules` ★

- **Hero column wider** — one of N columns becomes 1.6× the width of siblings (e.g., 1.6fr : 1fr : 1fr) for the strongest pillar; remaining columns stay narrow.
- **Accent-soft column tint** — exactly one column's body area gets `<rect fill="#E8E5FC">` (column-bounded, no `rx`); reserved for the recommended / focal pillar.
- **Numbered eyebrow** — each column's eyebrow gains a `01 / 02 / 03` prefix (uppercase 12.8 + accent number). Adds rank / order without collapsing into a process flow.
- **Bottom KPI row** — append a single horizontal hairline beneath all columns + a 1-line KPI / metric per column underneath (label 12.8 / value 24 weight 700). Columns become a "taxonomy + supporting metric".
- **Asymmetric 2 + 1** — instead of N parallel columns, split as `(col A | col B) | col C` where A+B share an outer hairline and C is the standalone "outlier / antithesis" column. Useful for comparison-leaning content.
- **Top hero band + columns** — full-width accent-soft band above the columns with one display-sm 40 statement; columns become the explanation / decomposition.

#### `chart-led-with-takeaway-stack`

- **Mega-number lead** — top of the takeaway stack becomes a display-sm 40 (accent or `#1A1A1A`) value with a 1-line label below. The chart confirms the number; the number is the message.
- **Inline insight band** — full-width accent-soft band immediately below the chart (between chart and footer), one sentence verdict. Stack on the right shrinks to 2 cards instead of 3.
- **Two stacked mini-charts** — replace 1 large chart with 2 smaller charts vertically (e.g., 2 line charts comparing two metrics or two periods). Takeaway stack remains.
- **Asymmetric 65/35** — instead of 60/40 split, push to 65/35 with chart dominant; stack contains 1 mega-number + 1 verdict line only.
- **Chart annotation callouts** — embed 1–2 inline `<text>` callouts directly inside the chart (e.g., "Q3 inflection", "Forecast region") with a 1px hairline pointing to the data. Stack carries summary, callouts carry the story-on-chart.
- **Verdict band footer** — full-width accent-soft strip at y=620 spanning entire body, replacing the bottom card in the stack with a longer prose verdict.

#### `table-with-adjacent-cards`

- **Recommended-row strip** — one full row (not column) of the table becomes accent-soft background with accent left-rule. Reserved for the row that decisively wins.
- **Mini-bar inline column** — append one numeric column rendered as inline mini-bars (bar width = `value / max × column_width`, single accent fill, 6px height) instead of pure numbers. Visual ranking emerges without separate chart.
- **Sparkline column** — append one column where each cell holds a 60×16 mini sparkline (single accent, 1.5px stroke). Use for trend per row.
- **Adjacent verdict-only card** — collapse the right-side "mini-cards" into one tall verdict card (full table-height) with a numbered / hierarchical recommendation, not 2–3 stacked mini-cards.
- **Footer verdict row** — append a final "Verdict" row spanning all columns with accent-soft background and one declarative sentence; mini-cards on the right become optional.
- **Two header tiers** — split the header into two rows (e.g., "Category" / "Q1 / Q2 / Q3 / Q4"), turning a flat table into a grouped table. Use when columns have a natural sub-grouping.

#### `definition-with-side-data`

- **Inverted layout** — flip to data-on-left + definition-on-right. Useful when the chart / mapping diagram is the more familiar element and the definition is the surprise.
- **Definition as pull-quote** — wrap the definition in `<rect fill="#FAFAF9" stroke="#E5E7EB" stroke-width="1"/>` + a 24px accent left-rule, body inside is 18.4. Side data unchanged.
- **Stacked side data** — right column splits into 2 stacked mini-blocks (mini-chart + mini-stat) instead of one supporting visual. Definition stays solid.
- **Numbered definition** — definition prefaced with `01 / 02 / 03` accent eyebrow when the slide is one of a series (e.g., "First principle", "Second principle"); side data unchanged.
- **Side data as caption strip** — instead of a chart, side becomes a stacked caption strip (3 small label:body rows) — turns the slide into "definition + 3 supporting facts".
- **Display-sm definition** — definition becomes display-sm 40 weight 800 (the term itself, not the explanation). Explanation moves under as 15.2 body. Side data shrinks.

#### `paired-concept-asymmetric`

- **Visual ratio shift** — push the asymmetry harder: 70/30 instead of 50/50 with the visual larger. Forces the visualization to lead.
- **Inverted polarity** — left side becomes accent-soft background, right side stays `#FFFFFF`. The accent-soft side carries the focal concept.
- **Opposing visualizations** — both halves get a small visualization (mini-bars vs single-icon vs doughnut vs sparkline) that contrast in *form* not just data. Visual contrast carries the comparison.
- **Top headline + paired body** — full-width headline at top stating the contrast ("X has Y mix vs Z is single-focus"), paired halves below as the evidence. Headline does the asserting; halves prove it.
- **Center divider rule** — explicit vertical accent rule (1px `#4633E3`) between halves instead of just whitespace. Reads as binary contrast.
- **Verdict band closer** — full-width accent-soft strip at the bottom spanning both halves with the synthesis sentence.

#### `breakdown-with-anchor-stat`

- **Mega-stat hero** — anchor stat becomes display-sm 40 weight 800 accent (single largest element on slide), cards below are smaller (3 instead of 4, body 12.8) — emphasizes the stat as the "north star".
- **Stat with trend annotation** — anchor stat gains a small inline `↑ 12% vs prior quarter` annotation in `--positive` (semantic data-only). Cards explain how the trend was earned.
- **Single dark card** — exactly one of the 3–4 decomposition cards becomes `fill="#1A1A1A"` with white text. Reserved for the most surprising / counterintuitive driver.
- **Asymmetric card row** — cards become `2fr : 1fr : 1fr` instead of equal width; the `2fr` card carries the dominant explanation, narrower cards carry secondary drivers.
- **Inline mini-charts in cards** — each card gains a 60×24 mini-bar or sparkline at the bottom (single accent), making the row a "stat + 3 micro-evidence" composition.
- **Stat with comparator** — anchor row contains 2 stats side-by-side (e.g., "2024: 18%" / "2030 forecast: 42%") with a connecting `→` rule; cards explain the gap.

#### `process-with-callout-band`

- **Bottom band → side band** — replace the bottom rule-of-thumb band with a vertical accent-soft strip on the right (full-height) holding the rule. Process becomes 70/30 horizontally.
- **Numbered + iconized nodes** — nodes gain both `01 / 02 / 03` eyebrow AND a small `tabler-outline` icon (20px). Each node is "number + icon + label + body".
- **One node hero** — exactly one node in the process becomes 1.5× the size of others (the critical / bottleneck step). Body inside is 2 lines instead of 1.
- **Branching arrow** — replace linear sequence with a Y-fork at one step (e.g., "if A → outcome 1, if B → outcome 2"). Callout band annotates the branch logic.
- **Forecast tail** — last 1–2 nodes get dashed connectors (forecast region), accent-soft tinted nodes. Indicates "future / projected" steps.
- **Cyclical** — replace linear flow with a closed loop (curved arrow back to step 1). Callout band carries the cycle's velocity / cadence statement.

#### `mapping-grid (3-row triplet)`

- **Hero mapping row** — first row's `label : map-target : implication` is title-tier (18.4) + 2-line implication, remaining rows stay 15.2. Establishes "main mapping + supporting mappings".
- **Single accent implication** — exactly one implication cell gets accent text fill `#4633E3`. Reserved for the most important mapping.
- **Diagonal accent rule** — accent hairline (1px `#4633E3`) connects each row's `label` to its `map-target`, visualizing the mapping. NOT the rows themselves — the connectors.
- **Bottom synthesis row** — append a 4th row with a single full-width accent-soft band that synthesizes the 3 mappings into one rule.
- **Inverted columns** — `map-target : label : implication` instead of `label : map-target : implication`. Useful when the *target* is the unfamiliar element and the *label* is the familiar one.
- **Row icons** — leftmost column becomes a small (20px) icon column representing the *category* of mapping (e.g., temporal / structural / behavioral).

#### `icon-explainer-with-metric-inline`

- **One tile dark** — exactly one tile becomes `fill="#1A1A1A"` with white text + accent metric. The dark tile is the focal item.
- **Asymmetric grid** — `2fr : 1fr : 1fr : 1fr` instead of equal 4-tile grid; first tile carries 2-line body, narrower tiles carry single-sentence explanations.
- **Metric row at top** — instead of inline metric, all metrics float as a top row above the icon-tile grid (display-sm 40 each, accent for one). Tiles below are pure icon + label + body.
- **Mini-bar inside tile** — each tile gains a 60×8 mini-bar at the bottom showing the metric's relative magnitude across the 4 tiles.
- **Inline trend** — each metric gains a `↑ 12%` or `↓ 5%` annotation in semantic color (`#059669` / `#E11D48`) — data-only semantic, not decorative.
- **3 tiles + verdict tile** — replace 1 tile with a verdict cell (text-only, no icon, no metric, just a 1-sentence editorial conclusion in 15.2 weight 700).

#### `quote-with-attribution-data`

- **Pull quote oversized** — quote becomes display-sm 40 weight 800 (not 32), forcing it to dominate. Attribution + data card shrink to baseline 15.2.
- **Data card mega-number** — the supporting data card holds a single display-sm 40 number + 1-line context. The number IS the supporting evidence.
- **Two attributions** — instead of 1 attribution + 1 data card, use 2 attributions side-by-side (e.g., 2 customer voices saying the same thing) — quote at top, attributions in 2 columns below.
- **Quote with chart counter** — supporting data card replaced by a small chart (mini-bar / sparkline) that visually reinforces the quote's claim.
- **Inverted layout** — data card on the LEFT, quote on the right (50/50). Useful when the data is more striking than the quote and the quote contextualizes the data.
- **Quote inside accent-soft band** — wrap the quote in a full-width accent-soft `<rect>` (no `rx`, just hairline-bounded), attribution + data sit below in monochrome.

> **Default discipline**: Across the full deck, distribute variations so no single variation type repeats more than twice. If the deck has 12 body slides and 3 of them are `breakdown-with-anchor-stat`, each must apply a *different* variation (e.g., one mega-stat hero, one with stat trend, one single dark card). Repeating the same variation 3+ times collapses the variation back into a new anchor.

---

## 6. Header / Body / Footer Structure

### 6.1 Page anatomy (1280×720)

```
┌─────────────────────────────────────────────┐
│ Header zone        (y: 56–96, h: ~40)       │  ← optional eyebrow / page label
│                                             │
│ Title              (y: 96–148, h: 52)       │  ← .headline (32/700) for content
│                                             │     .display (56/800) for cover/section
│ Body               (y: 168–656, h: 488)     │  ← .slide-body (flex:1, justify-start)
│                                             │
│ GM line            (y: 672–696, h: 24)      │  ← .gm absolute-positioned bottom
└─────────────────────────────────────────────┘
   Safe area: 1200×640 (40px outer margin)
```

### 6.2 Header zone

- **Optional.** Use only when an eyebrow label adds taxonomic clarity (e.g., chapter number, category tag).
- Style: `.label` (12.8/600 uppercase, 0.64 tracking).
- Position: aligned-left with body, 40px from top edge.

### 6.3 Title zone

- **Content slides** use `<h2 class="headline">` (32px). Keep ≤ 2 lines. **No line break in title.**
- **Cover / section / closing** use `.display` (56px) inside `.slide-centered` flex container.
- Title never spans full slide width if it's < 1200px wide — leave breathing room on the right.

### 6.4 Body zone

- **CRITICAL:** content slides must wrap body in `<div class="slide-body">` (`flex: 1; justify-content: flex-start; padding-top: var(--space-4)`). NOT `<div class="flex-col gap-6">`.
- This places content immediately below headline and maximizes vertical fill.

### 6.5 GM (governing message) line — non-negotiable

- **Every content slide** has a single-line `.gm` at absolute bottom (~24px from bottom edge).
- Style: 12.8px / `--text-secondary`, no decoration.
- **Voice:** declarative third-person institutional. Korean-first. ≤ 30 chars ideal.
- **Forbidden:** restating the page title. The GM is the editorial *so-what*, not a label.
- **Forbidden phrases:** 여러분, 우리는, 함께해요.

### 6.6 Footer / page number

- Page number bottom-right (`--text-tertiary`, 12.8px, format: `01 / 12`).
- Brand mark / logo bottom-left only on cover and closing.

---

## 7. Page Flow (Title → Body → End)

Jangpm decks follow a 4-zone flow. `slide-plan` writes `page_family` to bind each slide to one zone.

| `page_family` | Layout templates | Typical position | Required fields |
|---|---|---|---|
| `title` | `01_cover.svg` (`title` pattern) | slide 1 | hero text only, no GM |
| `body` | `03_content.svg` + any `breakdown`/`compare`/`data`/`process`/`insight`/`visual` family | slides 2 to N-1 | title + body + GM |
| `chapter` | `02_chapter.svg` (`section` pattern) | between major divisions | section number + chapter title, no GM |
| `end` | `04_ending.svg` (`closing` pattern) | slide N | thank-you + contact, no GM |

**Flow conventions:**
- Title slide → optional agenda (1 slide) → body slides interleaved with chapter slides → closing.
- Chapter slides every 4–6 body slides for decks ≥ 12 pages. Optional for short decks (< 8).
- Agenda slide is itself a `body` family member using the `agenda` pattern.

---

## 8. Chart & Table Treatment (Rhetorical Roles → Visual Implementation)

Jangpm honors the 9 rhetorical roles defined in `references/chart-rhetorical-roles.md`. Below is the Jangpm-specific *implementation* layer — what visual to use and how to style it.

### 8.1 Role → primary chart template (subset)

| `chart_strategy` | Primary | Alt |
|---|---|---|
| `growth-trend` | `chart-line` (single series) | `chart-bar` (annual buckets) |
| `forecast` | `chart-line` with forecast region (right portion uses dashed stroke + lighter opacity) | `process-flow` with timeline annotation |
| `structural-break` | `chart-line` with vertical break-line + annotation | `data-table` with before/after rows |
| `focus-comparison` | `chart-bar` with one bar accent-filled, others grayscale | `comparison-table` with one column highlighted |
| `distribution` | `chart-bar` (histogram-style) | `data-table` with sparkline column |
| `quadrant` | `diagram` (matrix_2x2 SVG template) | `comparison-table` (2×2) |
| `priority-matrix` | `data-table` (3×3) with cell shading | `diagram` (matrix_2x2 with extra rules) |
| `split-segment` | `chart-pie` (≤ 6 segments) | `chart-bar` (stacked) |
| `funnel` | `diagram` (funnel SVG template) | `process-flow` (decreasing-width nodes) |
| `custom` | choose closest pattern; document choice in `chart_takeaway` | — |

### 8.2 Chart styling rules (Jangpm lock)

- **Color palette:** single-accent opacity ladder (rule T4). Multi-series uses opacity tiers, not hue tiers.
- **Semantic exception:** growth bar in `--positive`, decline bar in `--negative` only when color encodes data meaning.
- **No legend chrome:** prefer inline labels at the end of each line/bar.
- **No drop shadows, no 3D, no gradient fills, no glow.**
- **Axis labels:** `--text-secondary`, body-12.8 weight 500.
- **Data labels:** on the chart itself (not in a side legend), accent for the focus value.

### 8.3 Table styling rules

- **Header row:** `--surface-alt` background, `.label` typography (uppercase, 0.64 tracking).
- **Recommended column:** `--accent-soft` background, accent left-border 2px (rule: comparison tables need a winner).
- **Cell text:** body 15.2 default; numerics tabular-nums and right-aligned.
- **Verdict row:** at the bottom, summarizing the recommendation in one sentence.

### 8.4 Required adjacency: chart + takeaway

**Every `data` family slide pairs the chart with a takeaway card** (right column or below). The card holds:
- 1 metric (display-sm)
- 1 trend annotation (caption + semantic color)
- 1 contextual line ("vs industry avg X")

A chart without a takeaway card fails Layer 1 R2 and is rejected at plan-time.

---

## 9. Icon System

### 9.1 Library lock

- **Default:** `tabler-outline` (Lucide-compatible line-art, 2px stroke, bare).
- **Fallback:** `tabler-filled` only when an editorial reason demands a solid glyph (e.g., solid arrow inside a data callout).
- **Forbidden:** `chunk` pack, emoji, unicode glyph icons, mixed packs.

### 9.2 Usage

```xml
<use data-icon="tabler-outline/<name>"
     x="..." y="..." width="..." height="..."
     stroke="currentColor" stroke-width="2" />
```

`finalize_svg.py` resolves the placeholder to the actual `<symbol>` at post-processing. **Do NOT inline the SVG content** — the placeholder is the contract.

### 9.3 Search before use

```bash
ls .claude/skills/slide/templates/icons/tabler-outline/ | grep <keyword>
```

Always cite the verified filename (without `.svg`) in `slide_plan.json` `content_blocks[].content_instruction`.

### 9.4 Sizing

- Card icon: 28–32px box, stroke 2px.
- Hero icon (insight slide): 56–64px box, stroke 2px.
- Inline icon (in body text): 16px box, stroke 2px.

### 9.5 Icon vs number badges

- **Default:** SVG icon badges for card grids (more visually interesting).
- **Number badges (01–04):** only when sequential order is the primary information (numbered steps, ranked priorities).
- **Mix is allowed:** icons in concept cards + number badges in adjacent process row reads as intentional.

### 9.6 No icon wrappers

Bare line icons only. **No** circle wrappers, **no** colored badges around the icon, **no** semantic-soft backgrounds. The icon carries itself; the layout carries the slide.

---

## 10. Anti-Patterns (Reject at Plan Time)

These are the patterns `slide-plan` validator must reject. They duplicate / strengthen `anti-slop-core.md` and `anti-slop-theme.md` rules into plan-level checks.

| # | Anti-pattern | Detect via | Fix |
|---|---|---|---|
| A1 | `title + 3 bullets repeated 4+ times` | same `recommended_layout_family` 3+ consecutive | force layout variation; require `why_here` justification |
| A2 | Chart slide without `chart_takeaway` | `chart_strategy` set but `chart_takeaway` empty | reject; require takeaway text |
| A3 | Empty `evidence_sources` | array length 0 | reject; mark as `inference` if source-less is intentional |
| A4 | Multi-hue chart palette | `chart_strategy` describes multi-hue need | reject; remap to opacity ladder or split into multiple charts |
| A5 | Multi-icon-pack mixing | icon names across 2+ packs in same deck | reject; pick one pack |
| A6 | GM restating title | GM text contains > 60% title tokens | reject; rewrite as so-what |
| A7 | Forbidden voice phrases | GM / speaker notes contain 여러분 / 우리는 / 함께해요 | reject; rewrite |
| A8 | Text-only slide | `content_blocks[]` has no chart / table / diagram / icon-group / image | reject; require ≥ 1 visual block |
| A9 | Equal-weight card grid | `breakdown` family with all cards same role / no accent card | warn; recommend differentiation |
| A10 | 2-layer card | card has only icon + title (no body / caption / metric) | warn; recommend 3rd layer |
| A11 | Decorative-only image | `block_type: image` with `purpose: decoration` | reject; image must explain content |
| A12 | Bullet-list dominance | `block_type: bullets` is sole non-title block | warn; recommend converting to icon-group / numbered-row |
| A13 | Emoji in any block | unicode emoji codepoint detected | reject; replace with tabler-outline icon |
| A14 | 3+ accent events on one slide | accent-fill / accent-soft-bg / accent-stroke count > 2 | reject; cut to ≤ 2 |
| A15 | Title with `<br>` / `\n` | line break in headline text | reject; rewrite shorter |
| A16 | Off-palette hex | any hex outside §2.1 table | reject; map to nearest token |
| A17 | Gradient / drop-shadow / glow | any of `linearGradient`, `filter:drop-shadow`, `filter:blur` | reject; flatten |
| A18 | Sparse slide on body family | body slide with < 3 content blocks | warn; recommend adding context card or annotation |

---

## Appendix — `slide-plan` quick reference

**Family vocabulary** (use one per slide): `structure` / `insight` / `breakdown` / `compare` / `data` / `process` / `visual`.

**Chart strategy vocabulary**: see `references/chart-rhetorical-roles.md`.

**Page family** (use one per slide): `title` / `chapter` / `body` / `end`.

**Slide role enum**: see `references/slide-role-enum.md`.

---

<!-- Hand-authored 2026-04-28 from theme-active.json + design-system.md + patterns.md + anti-slop-theme.md + jangpm-patterns/*.html. Future presets generate this file via /theme-init. -->
