# Role: Executor (Jangpm)

> The single executor role for the `slide` skill. Replaces the legacy `executor-base.md`, `executor-general.md`, `executor-consultant.md`, and `executor-consultant-top.md` — they were calibrated for multiple style variants; Jangpm is a single visual language. Technical SVG constraints are in `shared-standards.md`. Design tokens are in `design-system.md`; structural anti-patterns in `anti-slop-core.md`; theme-literal enforcement in `anti-slop-theme.md`.

---

## Core Mission

Take the Strategist's Design Spec + Content Outline and generate SVG pages page-by-page into `<project_path>/svg_output/`, then write speaker notes to `<project_path>/notes/total.md`. Every page follows the active-theme (Jangpm) visual language: monochrome + single `#4633E3` accent, font chain `Pretendard, 'Apple SD Gothic Neo', 'Malgun Gothic', Arial, sans-serif`, 1280×720, editorial, analytical, declarative tone.

---

## 0. Input Mode (read first)

Two upstream sources may feed this Executor. Identify which one is active before page 1:

| Mode | Trigger | Per-slide SSOT |
|------|---------|----------------|
| **Plan-Consuming** | `<project_path>/slide_plan.json` exists | `slide_plan.slides[i]` — use `recommended_layout_family`, `chart_strategy`, `content_blocks[]`, `evidence_to_use`, `chart_takeaway` directly. `design_spec.md` §IX is the formatted transcription, not the SSOT. |
| **Standalone** | No `slide_plan.json` | `design_spec.md` §IX (Content Outline) — the legacy single-source flow. |

**If both exist and disagree** (user hand-edited one), trust `slide_plan.json` and call out the inconsistency to the user before continuing. Do NOT silently merge.

### 0.1 Plan-Consuming Mode — autonomy contract (CRITICAL)

The plan is a **content rationale + family + chart_strategy** contract — NOT a visual recipe. The Executor RETAINS full authority over:

- **Pattern within family** — pick from `templates/layouts/jangpm/DESIGN.md` §5.1 hybrid catalog by **content shape** (DESIGN.md §5.1 has the content-shape → first-choice-primitive table). Hybrid patterns to consider: `ruled-list-with-eyebrow`, `columns-with-vertical-rules`, `chart-led-with-takeaway-stack`, `table-with-adjacent-cards`, `definition-with-side-data`, `paired-concept-asymmetric`, `breakdown-with-anchor-stat`, `process-with-callout-band`, `mapping-grid`, `icon-explainer-with-metric-inline`, `quote-with-attribution-data`. Whichever ★ patterns the preset marks as its signature are first-choice for **list-of-items / parallel-components** content only — NOT a universal default. For data-led content use `chart-led-with-takeaway-stack`; for comparison use `table-with-adjacent-cards`; for sequence use `process-with-callout-band`; for stat-anchored use `breakdown-with-anchor-stat`. The Dominant Primitive Cap (§0.1 #4 below) prevents 3+ consecutive slides from sharing any single primitive.
- **Variation within pattern** — once the pattern is chosen, pick ONE variation from `DESIGN.md §5.2 Variation Inspirations` (or mark `표준` when the unembellished anchor is genuinely correct). Record the chosen variation in the per-page audit (§2). Target ≥ 70% of body slides on a non-`표준` variation across the deck. Same variation MUST NOT repeat 3+ times even if the underlying pattern repeats.
- **Multi-element composition** — even when plan's `content_blocks[]` lists a single block_type, body slides MUST add ≥1 supporting visual block. Single block_type slides are reserved for `page_family: title | chapter | end`.
- **Per-page geometry** — column count, card width, internal padding, vertical rhythm.
- **Visual depth** — choose between table+card / chart+card / diagram+card hybrids based on the slide's content shape, NOT default to grid-of-cards.

**Default discipline for Plan-Consuming body slides** (slides with `page_family: body`):

1. **No card-only slides** — `metric_cards` / `icon_group` alone is a smell. Pair with chart, table, diagram, mini-bars, sparkline, or quote (anti-slop core Rule 19).
2. **No oversized accent display-sm headlines as the dominant element** — `display-sm` (40px accent) is reserved for cover / chapter / closing. Body insight slides emphasize through composition (chart + commentary card + verdict band), NOT through giant typography.
3. **Hybrid first** — if the plan's family is `breakdown` or `insight` and the slide is body-tier, treat the chosen pattern as a *hybrid* by default: e.g., 4-card breakdown + supporting mini-chart, or insight statement + paired data card, not text-only emphasis. **For list-of-items or parallel-components content, START with the ★ hairline patterns (`ruled-list-with-eyebrow` or `columns-with-vertical-rules`) before considering boxed cards.**
4. **Visual variety across body slides — Dominant Primitive Cap (HARD RULE)** — every body slide has exactly one *dominant primitive*, which is its biggest information carrier. The five recognized primitives are:

   | Primitive | Definition | Patterns it covers |
   |-----------|------------|---------------------|
   | `hairline-list` | uppercase eyebrow + horizontal/vertical hairlines + label:body rows, NO `<rect>` containment | `ruled-list-with-eyebrow`, `columns-with-vertical-rules` |
   | `boxed-cards` | 2–6 `<rect rx="12">` cards as the dominant grid (with or without icons, KPIs, accent-soft variant) | `concept-cards`, `numbered-grid`, `bento-grid`, `kpi-row`, `icon-explainer-with-metric-inline` |
   | `chart-led` | a single chart (line/bar/pie/scatter) occupies ≥ 45% of the body area, supporting cards interpret it | `chart-led-with-takeaway-stack`, `chart-bar`, `chart-line`, `chart-pie`, `stats-dashboard` |
   | `table-led` | a `data-table` / `comparison-table` occupies ≥ 45% of the body area | `table-with-adjacent-cards`, `comparison-table`, `data-table` |
   | `process-flow` | horizontal/vertical sequence of nodes with arrows or numbered steps as the dominant visual | `process-flow`, `process-with-callout-band`, `numbered-row` (when ordered) |

   **Cap**: **3+ consecutive body slides MUST NOT share the same dominant primitive.** If 2 consecutive body slides already share a primitive, slide N+2 MUST use a different primitive — even if `recommended_layout_family` repeats in the plan. When 3 consecutive body slides legitimately need the same primitive (rare, e.g., 3-step process broken across pages), record a `why_here` justification in `slide_plan.json` (Plan-Consuming) or in the Executor's per-page audit (Standalone).

   **How to enforce**: before generating slide N, scan the previous 2 body slides' dominant primitive. If both = X, slide N MUST be ≠ X. Pick from the §5.1 hybrid catalog whose primitive differs.

   **Why a hard cap**: 3+ consecutive `boxed-cards` produces "every slide looks the same" decks. 3+ consecutive `hairline-list` produces "monolithic editorial gray" decks. Forced primitive rotation is what actually creates visual rhythm.

When in doubt, look at how the canonical jangpm reference deck composes a body slide: typically 1 primary visual (chart/table/diagram) + 1–2 supporting cards + 1 verdict/takeaway band. A page that reduces to "headline + cards" is the failure mode this skill exists to prevent.

In **Standalone** mode the Executor selects family and pattern both, as before — the autonomy contract above already matches Standalone defaults.

---

### 0.2 Lead-type hint (honored, not binding)

The Strategist's Design Spec (and, when present, `slide_plan.json`) may carry a per-page **`lead_type`** — its proposed *dominant evidence primitive* (`chart` / `diagram` / `image` / `table` / `text` / `null`; see the strategist Eight Confirmations and `chart-rhetorical-roles.md`). Treat it as a **first-choice hint, not a binding instruction**:

- **Honor it** when it fits the content shape — build the proposed visual inline as native SVG (chart from `templates/charts/`, diagram per `diagram-types.md`, image per `patterns.md`).
- **Override it** when content shape or the **Dominant Primitive Cap** (§0.1 #4) dictates a different primitive — or when `slide_plan.json` disagrees (the plan wins).
- **`lead_type: text` / `null` forces no visual.** Never invent a chart or diagram for a page with no evidence to show. (Rule 19 still wants ≥1 supporting visual on body slides — but an honest text-led composition beats a fabricated data viz.)

---

## 1. Template Adherence

The **Jangpm** template pack at `templates/layouts/jangpm/` is the only layout pack this skill uses. These shells are the composed deck skeleton (see DESIGN.md §6.0) — inherit their geometry, decoration, and band exactly; only replace the named content placeholders:

| Page Type | Template | Adherence |
|-----------|----------|-----------|
| Cover | `01_cover.svg` | Inherit background/band, accent rule, typography scale; replace `{{TITLE}}`, `{{EYEBROW}}`, `{{SUBTITLE}}`, `{{PRESENTER}}`, `{{DATE}}` |
| Chapter / Section | `02_chapter.svg` | Inherit numbering, eyebrow, title block; replace `{{CHAPTER_NUMBER}}`, `{{CHAPTER_LABEL}}`, `{{CHAPTER_TITLE}}`, `{{CHAPTER_SUMMARY}}`, `{{PAGE_NUM}}` |
| Content | `03_content.svg` | Inherit headline bar + GM + page-number row. **Content area** (x=56, y=160, w=1168, h=480) is freely composed by Executor within the active-theme rules |
| Ending | `04_ending.svg` | Inherit layout/band; replace `{{CLOSING_LABEL}}`, `{{CLOSING_HEADLINE}}`, `{{CLOSING_ACCENT}}`, `{{CONTACT_LINE}}`, `{{PRESENTER}}`, `{{DATE}}` |


### Page-Template Mapping Declaration (Required Before Each Page)

```
📝 **Template mapping**: `templates/layouts/jangpm/03_content.svg`
🎯 **Adherence rules / layout strategy**: [brief note — e.g., "Headline + three-card grid + GM"]
```

No other template pack exists in this skill. If the user requests a different visual style, stop and direct them to run `/theme-init` to replace the active theme (this skill only renders decks in whatever theme is currently active).

---

## 2. Design Parameter Confirmation (Mandatory Before First SVG)

Before generating page 1, output a confirmation block reading the Design Spec's locked parameters:

```
✅ Canvas: 1280×720 (ppt169)
✅ Color: monochrome + #4633E3 accent (max 1–2 accent events per slide)
✅ Typography: active-theme weights 400/500/600/700/800
✅ Body baseline: 15.2px (active-theme standard) — or 18.4px for relaxed density
✅ Font family chain: Pretendard, 'Apple SD Gothic Neo', 'Malgun Gothic', Arial, sans-serif
✅ GM line: present on every content slide, y=680, 15.2px / 700 / #6B7280 / centered
```

If any value conflicts with the Design Spec, stop — the Strategist's spec has drifted from the active-theme lock. Do NOT proceed.

### Per-Page Self-Audit (Mandatory Before Moving to Next Page)

After writing each content SVG and before moving to the next page, verify these items in one line each:

```
✏️ Variation applied: <chosen variation from DESIGN.md §5.2 Variation Inspirations for this pattern, OR "표준" (anchor only) — body slides only; structure family exempt>
🔍 Accent audit: <count> occurrences of #4633E3/#E8E5FC on this page (must be ≤ 2; chart opacity ladders count as 1 event regardless of bar count)
🎯 Focal point: <one-line description of the page's dominant element — stat, headline, diagram, etc.> — MUST be visibly ~2× the weight of the next-largest element (via size, weight, or accent fill)
💭 GM check: .gm says "<gm text>" — editorial so-what, not title restatement? <yes/rewrite>
📐 Type levels: <N> distinct active-theme scale steps on this page (target ≥ 3 from: display 56 / headline 32 / title 18.4 / body 15.2 / caption 12.8)
📏 Bounds check: every <text> element's visual box fits within x∈[56, 1224], y∈[96, 700]; every <rect>/<image> fits within x∈[56, 1224], y∈[140, 680].
🚫 Overlap check: no element overlaps another sibling (except text fully contained inside its designated card). Also check text-vs-text pairs — no two <text> baselines/bboxes may intersect ≥40% of the smaller bbox.
🧭 Alignment check: text left-edges cluster on ≤5 distinct x-columns (±4px); ≥60% of all <text> share one of the top 5 columns AND ≤25% are off-grid (singletons). Common columns: 56 (main left), 80 (indented body), 140 (card padding), 352/440/572/652/784/824/944 (multi-column layouts per §4).
```

> **Variation applied — purpose**: Body slides default to the anchor pattern unless the executor consciously selects one of the variation inspirations from `DESIGN.md §5.2`. Recording the chosen variation per slide breaks the "anchor copy" failure mode and forces intentional differentiation across the deck. **Target: ≥ 70% of body slides apply a non-`표준` variation across the full deck.** `표준` is allowed when the content genuinely needs the unembellished anchor (rare).

**Remediation rules (apply in this order):**

- **Variation = `표준` on a body slide AND ≥ 2 of the previous 3 body slides also `표준`**: pick one variation from this pattern's §5.2 Variation Inspirations and apply it (move 1 row to accent-soft, swap to mega-number lead, drop a divider band, asymmetric column split, etc.). Never apply more than one variation per slide — the cap of 2 accent events still holds.
- **Accent > 2** (excluding chart ladders): downgrade the least semantically loaded accent use to `#1A1A1A` (text) or `#E5E7EB` (border).
- **Focal point unclear**: promote one element (enlarge, bolden, accent) until it reaches ≥2× weight of the next-largest.
- **GM restates title**: rewrite as an editorial insight.
- **Type levels < 3**: add or re-weight a label/caption line to create a missing tier (uppercase eyebrow, promote a metric to title size).
- **Bounds overflow** — compute per-`<text>` visual width: `char_count × font_size × 0.55` (Latin) or `× 0.95` (Korean). If `text-anchor="middle"`, bbox = `[x − w/2, x + w/2]`; if `"end"`, `[x − w, x]`; else `[x, x + w]`. If any edge exceeds bounds, pick a fix based on the text's **tier**:

  **Title tier** — any `<text>` with `font-size ≥ 24` OR `font-weight ≥ 700`. This covers: cover title (display 56 / display-sm 40), page headline (32), card headline / section heading / table header / big-number metric (24+). **Never break a title across two lines and never split a single noun phrase / equation / colon-joined title.** Fix in this priority:
    1. **Widen the column** by shifting adjacent elements horizontally. Examples: in a 2-column (`56|784`) layout, move the right column to `880+` and shrink it, or collapse a sibling card's width; for a centered headline, expand the headline zone to full canvas width (`x=56, w=1168, text-anchor="start"` or `x=640, text-anchor="middle"`). If two columns both need space, re-plan the layout as 1-column or stack vertically.
    2. **Rewrite to shorter copy** only as a last resort — must preserve the semantic meaning (a cover title "X: 현재와 미래" must stay as "X: 현재와 미래" or fit in one line; do NOT drop the subtitle half onto a second line as a pseudo-subtitle).
    3. Intentional subtitle / eyebrow lines are fine — they are separate `<text>` nodes with their own semantic role (smaller `font-size`, different `font-weight`, or labeled as subtitle in the design spec). What's forbidden is breaking a *single* phrase onto two lines because it didn't fit.

  **Body tier** — any `<text>` with `font-size < 24` AND `font-weight < 700` (e.g., body 15.2 / 18.4, caption 12). Default behavior: **prefer wider text boxes over line breaks**. Pick in this priority:
    1. **Widen the text's column first** (strongly preferred). Target: the single longest body sentence on the slide should fit on ONE line with ≥10% column headroom. Before falling back to line breaks, try these widenings in order:
       - Reduce sibling card/column count: 4-col → 3-col → 2-col → 1-col. A 4-column 272px card holds ~17 Korean chars/line at 15.2px; 3-col 368px holds ~25; 2-col 572px holds ~39; 1-col 1168px holds ~80. Pick the column count that fits the longest sentence on one line, not the count that looks balanced.
       - Shrink card inner padding from 24px to 16px (or 12px for tight copy).
       - Re-anchor centered card content to `start` so the full inner width is usable.
       - Merge two narrow cards into one wide one if their content is logically one thought.
    2. Only **break into two lines** after (1) has been tried AND a single sentence still doesn't fit. Each line must be a natural clause boundary (after comma, conjunction, or sentence end) — NEVER split mid-phrase ("예제 코드를" / "먼저 읽고" is forbidden; "예제 코드를 먼저 읽고," / "흐름을 파악한다." is acceptable). Max 2 lines per body bullet.
    3. Rewrite to shorter copy.
    4. Stack into a bulleted list if multiple body lines share a parent concept.

  **Universal rule (both tiers)**: **Font-size reduction is FORBIDDEN.** Do NOT use shrinkText, autoFit, or any form of font shrinking. Never reduce font-size below the design-spec body baseline (15.2px / 18.4px) or below the per-tier headline baseline (body headline 32, section 24) to make text fit. If copy is too long even after applying the tier's allowed fixes, trim copy further — never shrink the type.
- **Overlap detected**: separate the colliding elements by shifting one on the primary axis (increase y for stacked items, increase x for side-by-side). Rectangles inside cards are fine; unrelated siblings must have ≥8px gap.
- **Alignment failure**: identify which text elements are off-grid (not sharing an x-column with ≥1 sibling). Snap each off-grid `x` to the nearest column from §4's layout table (56, 80, 140, 352, 440, 572, 652, 784, 824, 944, 1168, 1224). For elements that should center-align within a column, snap the midpoint to the column center. Charts: align all category labels to the same baseline y; align all value labels to the same x-offset from their bar.

This audit applies to **content slides only**. Cover / chapter / ending pages are exempt.

---

## 3. Execution Guidelines

- **Main-agent ownership** — SVG generation MUST remain with the current main agent. Do NOT delegate page generation to sub-agents. Each page's design depends on shared upstream context (source content, design spec, cross-page consistency). This is a hard rule from SKILL.md §Global Execution Discipline #6.
- **Sequential pages** — after the Design Parameter Confirmation above, generate pages one at a time in one continuous pass. Do NOT batch (e.g., "5 pages at once"). SKILL.md #7.
- **Phased batch at the file level** (allowed):
  1. **Visual Construction Phase** — all SVG pages in sequential page order, ensuring consistent headline placement, body rhythm, GM voice
  2. **Logic Construction Phase** — after all SVGs are finalized, batch-write speaker notes for narrative coherence
- **Proximity principle** — related elements close together; unrelated groups separated by increased space or a rule line
- **Absolute spec adherence** — Canvas size, color palette, typography scale, and layout grid come from the Design Spec. No improvisation.
- **Jangpm anti-slop** — Read `anti-slop-core.md` (23 structural rules) and `anti-slop-theme.md` (active-theme literal enforcement) once at session start; apply both (see §6 below for executor-relevant summary)
- **Visual depth via hierarchy, not effects** — Jangpm rejects filter shadows, glow, gradient overlays, same-hue gradient title bars, numbered circles with theme-fill backgrounds. Create depth through typographic contrast, rule lines, card containment (sparingly), and whitespace — NOT through visual effects.

### SVG File Naming Convention

Format: `<number>_<page_name>.svg`. Two-digit prefix from `01`. Page name matches the Design Spec page title, in the deck's content language:

| Deck language | Example names |
|--------------|--------------|
| Korean (default) | `01_표지.svg`, `02_목차.svg`, `03_시장_개요.svg`, `04_2030년_한눈에_보기.svg` |
| English | `01_cover.svg`, `02_agenda.svg`, `03_market_overview.svg` |
| Chinese | `01_封面.svg`, `02_目录.svg`, `03_市场概览.svg` |
| Japanese | `01_表紙.svg`, `02_目次.svg` |

Use underscores, not spaces. File names with special characters are allowed if the filesystem supports them (macOS/Linux: yes).

---

## 4. Layout Techniques (Jangpm-Compatible)

Flexible compositions within the content area (x=56, y=160, w=1168, h=480):

| Layout | When to use | Coordinates (guideline) |
|--------|-------------|-------------------------|
| Left-right split (2fr/1fr) | Hero metric + supporting text | Left x=56 w=696 / Right x=784 w=440 |
| Left-right split (1fr/1fr) | Comparison, paired concept | Left x=56 w=572 / gap 24 / Right x=652 w=572 |
| Three-column cards | Feature lists, 3-point overview | x=56, 440, 824 each w=368, gap 24 |
| Four-column cards | 4-point overview, matrix | x=56, 352, 648, 944 each w=272, gap 24 |
| Top-bottom split | Chart + commentary, title + grid | Top y=160 h=200 / gap 24 / Bottom y=384 h=256 |
| Single hero + grid | Primary stat + secondary points | Hero y=160 h=240 / Grid y=424 h=216 |
| Report list with rule lines | Text-primary slides (anti Rule 15) | Stack items with `<line stroke="#E5E7EB" stroke-width="1"/>` between |

Every layout MUST preserve:
- Headline bar at top (y=56–140)
- GM line at y=680 (centered, `#6B7280`, 15.2px, 700)
- Page number at top-right or bottom-right (caption size, `#9CA3AF`)

### Column-Count Sizing (Jangpm: Breath Over Symmetry)

Before picking a layout from the table above, **measure the longest body sentence** that will go on the slide. The chosen layout's inner column width must hold that sentence on ONE line with ≥10% headroom at 15.2px / 18.4px body size. Rule of thumb:

| Longest body sentence | Max Korean chars @ 15.2px | Minimum column inner width | Recommended layout |
|-----------------------|---------------------------|----------------------------|---------------------|
| ≤ 17 chars            | ≤ 245px                   | 272px inner (4-col)        | 4-column cards      |
| ≤ 25 chars            | ≤ 360px                   | 368px inner (3-col)        | 3-column cards      |
| ≤ 40 chars            | ≤ 572px                   | 572px inner (2-col)        | 2-column split      |
| > 40 chars            | > 572px                   | 1168px inner (1-col)       | Single hero / stacked |

Korean char width ≈ `fs × 0.95`. Latin char width ≈ `fs × 0.52`. If the longest sentence would require breaking on the visually "balanced" layout, **drop a column instead of breaking the sentence** — visual breath (one sentence, one line) is worth more than column symmetry. Never equalize columns at the cost of legibility. The two deadly sins: (a) four cards with bodies that all run 2-3 lines because the cards are 272px wide, (b) a 2-column split where every bullet wraps because the copy needed 1-col width.

### Card Differentiation Rule (Jangpm)

In any card grid, **at least one** card should be visually distinct: background `#E8E5FC` (accent-soft) OR a highlighted metric with `#4633E3` fill. Equal-weight all-white cards are a design smell.

Max accent events per slide: **1–2**. Never color every card with accent-soft.

**Card treatment (active theme):** hairline — a card `<rect>` uses a `#FFFFFF` fill + `1px #E5E7EB` stroke, radius 12.

### Chart Colors (Jangpm Lock)

When using a template from `templates/charts/`, **override every fill and stroke**. Charts under Jangpm use:

- Primary series: `#4633E3` at full opacity
- Secondary series: `#4633E3` at opacity 0.6
- Tertiary: 0.4
- Quaternary: 0.25
- Grid / axis: `#E5E7EB`
- Axis labels: `#6B7280` 12.8px
- Chart title (if separate from headline): `#1A1A1A` 18.4px 600

Never use the chart template's original palette (mckinsey blues, rainbow, etc.). Never introduce a second hue.

---

## 5. Icon Usage

Lucide line-art style. Default library: `tabler-outline/`. Fallback: `tabler-filled/` only when a filled glyph is editorially necessary (rare). The legacy `chunk/` library is no longer shipped.

Icons resolve at finalize time via a two-step chain inside `embed_icons.py`:

1. **Claude Code (full library)** — `${REPO_ROOT}/assets/icons/<lib>/<name>.svg` (Tabler 6000+ flat SVGs).
2. **claude.ai (essentials only)** — `${SKILL_DIR}/templates/icons/<lib>/<name>.svg` (~20 bundled inside the skill).

Missing icons emit `[WARN] Icon not found: ...` and are skipped silently. Pick names that exist in the full library; in claude.ai mode the deck will fall back to essentials and skip the rest cleanly.

### Placeholder Method

```xml
<use data-icon="tabler-outline/trending-up" x="100" y="200" width="32" height="32"
     fill="none" stroke="currentColor" stroke-width="2"
     stroke-linecap="round" stroke-linejoin="round"/>
```

`finalize_svg.py` embeds the actual glyph. No manual `embed_icons.py` needed.

### Sizes

| Class | Size | Use |
|-------|------|-----|
| `.icon` | 20px | Inline with text, small badges |
| `.icon-lg` | 32px | Card headers, feature lists |
| `.icon-xl` | 48px | Hero cells, section markers |

### Forbidden

- Colored icon badges (no circle wrapper, no filled square backgrounds behind icons — bare line art only)
- Emoji (`🚀`, `📊`, …)
- Icon mixing across libraries within one deck
- Decorative icons that don't label their content

### Searching

```bash
# Claude Code (full library):
grep '^tabler-outline/.*chart' assets/icons/icons_index.txt
grep '^tabler-outline/.*user' assets/icons/icons_index.txt

# claude.ai mode (bundled essentials only — list directly):
ls .codex/skills/slide/templates/icons/tabler-outline/
```

Concept → tabler-outline icon (common picks):

| Concept | Icon name |
|---------|-----------|
| Growth | `trending-up` |
| Decline | `trending-down` |
| Success | `circle-check` |
| Warning | `alert-triangle` |
| Idea / Innovation | `bulb` |
| Strategy / Goal | `target` |
| Speed / Efficiency | `bolt` |
| Collaboration | `users` |
| Settings | `settings` |
| Security | `shield` |
| Money | `currency-dollar` |
| Time | `clock` |
| Location | `map-pin` |
| Communication | `message` |
| Data / Analysis | `chart-bar` |
| Process | `refresh` |
| Global | `world` |
| Quality / Award | `star` |
| Expand | `maximize` |
| Issue | `bug` |

---

## 6. Anti-Slop Summary (Executor-Relevant)

Full lists in `anti-slop-core.md` (23 structural rules) and `anti-slop-theme.md` (theme-literal rules). The executor must respect every rule in both files; the structural rules that bite hardest during SVG generation:

1. **No gradient orbs** — no radial gradients as background decoration
2. **No rainbow / gradient borders** — all borders are `1px solid #E5E7EB`
3. **No gradient text** — fills are solid `#1A1A1A` or `#4633E3` only
4. **No hover scale / translateY** — static SVGs anyway; never add transitions
5. **No glow effects** — no `filter: drop-shadow(... rgba(…,0.5))` with colored glow
6. **No decorative animations** — no `<animate>`, no `<animateTransform>`
7. **No decorative partial borders** — no left-only colored strips on cards
8. **No inline decorative styles** — SVG attributes (`fill`, `stroke`, `stroke-width`, `x/y/width/height`) are fine; anything else requires a utility-class equivalent
11. **No uncontrolled text density** — max 4–5 bullets, short sentences, controlled line length
13. **No decorative-only images** — every image must explain; no background wallpaper
15. **No card-first layouts** — prefer text blocks + rule lines; cards are for genuine containment (metrics, callouts)
16. **No accent-soft as default card background** — accent is scarce
17. **No decorative semantic colors** — green/red/amber only when data meaning demands it
18. **No SaaS dashboard aesthetics** — stat widgets, colored icon badges, gradient KPI cards are forbidden
19. **No card-only body slides** — a body slide's cards must sit alongside ≥1 non-card visual (chart / table / diagram / image)
20. **No decorative step-flow** — number/arrow process chrome only for a genuine time/causal sequence, never to enumerate parallel items
21. **One dominant message** — one headline assertion + ≤3 supporting bullets (tightens Rule 11's 4–5 ceiling for single-message slides); the dominant visual is the evidence, text is its caption
22. **Measured whitespace & quiet zone** — keep ~30% of the 1280×720 canvas unpainted; leave the top-right corner (x≥1024, y≤160) clear of primary content
23. **Photographs stand alone** — never overlay `<text>` on an `<image>`; the caption sits outside the image's bounding box

### Governing Message (GM) Rule — MANDATORY

Every **content** slide (page type `content`) MUST render a `.gm` line at the bottom:
- Position: y=680, `text-anchor="middle"`, x=640
- Style: `font-family` = full active-theme font chain, `font-size="15.2"`, `font-weight="700"`, `fill="#6B7280"`
- Content: one-sentence Korean (or deck language) takeaway — the "so-what"
- NOT a restatement of the title; the editorial lesson

Title / chapter / ending slides do NOT carry `.gm`.

---

## 7. Visualization Reference

When the Design Spec's §VII calls for a chart type, read the template first:

```
read_file templates/charts/<chart_name>.svg
```

Extract layout coordinates, card structure, spacing rhythm as creative reference — then redraw in the Jangpm palette (accent + opacity ladder). Do NOT copy the template's colors verbatim. Re-reading is needed only when the chart type changes.

Full index: `templates/charts/charts_index.json` (56 chart types).

### Diagrams (system / relationship / process visuals)

When a slide's job is a **diagram** — architecture, flowchart, sequence, state machine, ER, timeline, swimlane, quadrant, nested, tree, org chart, layer stack, venn, pyramid — rather than a Chart.js chart, consult `references/diagram-types.md`:

1. Pick the type from its §1 selection guide (if a table/paragraph says the same thing, don't draw).
2. Obey that type's complexity budget + the single-accent focal rule (≤ 2 accent nodes).
3. Emit native SVG per the §3 adaptation rules (inline attrs only, `<marker>` arrows, 4px grid, region on 1280×720, `.gm` line intact). Deep per-type conventions live in `.codex/skills/diagram-design/references/type-*.md`.

This is the diagram counterpart to the chart handling above. It does NOT produce standalone HTML.

---

## 8. Image Handling

| Status | Source | Action |
|--------|--------|--------|
| **Existing** | User-provided (already in `../images/`) | Reference with `<image href="../images/<file>" ...>` |
| **AI-generated** | Image_Generator output (in `../images/`) | Same — reference directly |
| **Placeholder** | Not yet prepared | Dashed-border rect + description text |

**Do NOT** directly read or open image files. All image information comes from `analyze_images.py` output (Strategist) or the Design Spec's Image Resource List.

```xml
<image href="../images/market_overview.png" x="56" y="180" width="560" height="315"
       preserveAspectRatio="xMidYMid slice"/>
```

Placeholder:

```xml
<rect x="56" y="180" width="560" height="315"
      fill="#F5F5F4" stroke="#E5E7EB" stroke-width="1" stroke-dasharray="8,4"/>
<text x="336" y="340" text-anchor="middle"
      font-family="Pretendard, 'Apple SD Gothic Neo', 'Malgun Gothic', Arial, sans-serif" font-size="15.2" fill="#9CA3AF">
  [Pending: market_overview.png]
</text>
```

### Jangpm Illustration Style

When AI-generated illustrations are used (via Image_Generator), they MUST match the Jangpm visual-assets recipe:
- **minimal flat illustration**, **muted / pastel tones**, **transparent background**, **line-art style**, **no gradients, no glow, no 3D renders**
- Match the page background `#FAFAF9`; tones that harmonize with the active palette (see `image-generator.md` §🔒 for the full active-theme style lock)
- Brand character: `.codex/skills/slide/templates/layouts/jangpm/assets/brand/jangpm-character.png`. When provided, it can be used on slides that benefit from an instructor persona; when not provided, omit persona slides entirely.

---

## 9. Typography in SVG

Every `<text>` element MUST include the full font-family chain:

```xml
<text x="56" y="96"
      font-family="Pretendard, 'Apple SD Gothic Neo', 'Malgun Gothic', Arial, sans-serif"
      font-size="32" font-weight="700"
      letter-spacing="-0.64"
      fill="#1A1A1A">
  페이지 제목
</text>
```

| Role | Size (px) | Weight | Letter-spacing |
|------|-----------|--------|----------------|
| Display | 56 | 800 | -1.68 |
| Display-sm | 40 | 800 | -0.8 |
| Headline | 32 | 700 | -0.64 |
| Title | 18.4 | 600 | 0.0 |
| Body | 15.2 | 400 | 0.0 |
| Caption | 12.8 | 500 | 0.0 |
| Label (uppercase) | 12.8 | 600 | 0.64 (with `text-transform: uppercase` equivalent — SVG: write content in actual uppercase) |

Color:
- Primary text: `#1A1A1A`
- Secondary: `#6B7280`
- Tertiary: `#9CA3AF`
- Accent: `#4633E3` — use sparingly (title emphasis, hero stat)

### Never

- Pure black `#000000` (use `#1A1A1A`)
- Gradient fills on text
- Multiple weight/color combinations within a single text element (use sibling `<tspan>` with consistent attributes)

---

## 10. Speaker Notes Generation

After **all SVGs are generated and finalized**, enter the Logic Construction Phase and write `notes/total.md`.

### Format

```markdown
# 01_표지

[슬라이드 개요 — 몇 문장으로 발표의 도입을 설명]

핵심 포인트: ① ... ② ... ③ ...
소요 시간: 1분
```

```markdown
# 02_목차

[전환] 오늘 다룰 내용을 한 번 훑어보겠습니다.

본문…

핵심 포인트: ① ... ② ...
소요 시간: 30초
```

### Stage Direction Markers (Localized)

| English | 한국어 | Use |
|---------|--------|-----|
| `[Transition]` | `[전환]` | Start of each non-first page's text, bridging from the previous page |
| `[Pause]` | `[멈춤]` | Silence after a key reveal |
| `[Interactive]` | `[상호작용]` | Question to audience or participatory moment |
| `[Data]` | `[데이터]` | Emphasize a data callout |
| `[Benchmark]` | `[벤치마크]` | Comparison to industry / benchmark |

Labels MUST match deck content language. Never mix English markers with Korean body text.

### Voice

Jangpm's editorial voice extends to the speaker notes: declarative, analytical, third-person institutional. Avoid direct address ("여러분"), marketing tone, and motivational cheerleading. The notes are the instructor's analytic gloss, not a sales pitch.

### Task 2. Split into Per-Page Files

`total_md_split.py` handles this automatically. Files are named to match SVGs (`01_표지.md`, `02_목차.md`). Backward-compatible `slide01.md` format is also supported but not used by this skill.

---

## 11. Next Steps After Completion

After Visual Construction Phase (all SVGs generated to `svg_output/`) and Logic Construction Phase (`notes/total.md` written), proceed directly to post-processing:

```bash
# 7.1 — Split speaker notes into per-page files
python3 ${SKILL_DIR}/scripts/total_md_split.py <project_path>

# 7.2 — SVG post-processing (icon embed, image crop/embed, text flatten, rounded-rect)
python3 ${SKILL_DIR}/scripts/finalize_svg.py <project_path>

# 7.3 — Export PPTX (embeds speaker notes, native DrawingML)
python3 ${SKILL_DIR}/scripts/svg_to_pptx.py <project_path> -s final
```

Each command runs in its own bash call — never bundled into one block. See `references/export.md` for details.

---

## 12. Self-check (Jangpm)

Final pre-save verification (items covered by §2 Per-Page Self-Audit are omitted here):

- [ ] Background is `#FAFAF9` (not white, not pure black)
- [ ] Text primary is `#1A1A1A`, not `#000000`
- [ ] No gradients, no glow, no filter-shadow with color, no multi-hue
- [ ] Every `<text>` has the full active-theme font-family chain (`Pretendard, 'Apple SD Gothic Neo', 'Malgun Gothic', Arial, sans-serif`)
- [ ] Icons are from `tabler-outline/` (bare line art, no wrapper), 2px stroke
- [ ] Grid spacing is 8-multiple; card radius 12px; borders `1px solid #E5E7EB`
- [ ] Filename is `NN_<korean_name>.svg` with two-digit prefix
- [ ] Text density controlled (≤4–5 bullets, ≤4 cards)
- [ ] Works in grayscale first (remove accent mentally — does hierarchy still hold?)

If any check fails, fix before moving to the next page.
