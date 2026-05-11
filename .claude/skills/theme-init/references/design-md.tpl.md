# DESIGN.md — {{TOKEN:display_name}}

> Preset-level design vocabulary for `slide-plan` consumption.
> Pairs with `theme-active.json` (token SSOT) and `references/patterns.md` (HTML pattern catalog).
>
> **Purpose:** Give `slide-plan` the structured vocabulary it needs to produce `slide_plan.json` entries (`recommended_layout_family`, `chart_strategy`) that `/slide` Executor can consume without re-deciding visual style.
>
> **Scope:** {{TOKEN:display_name}} only. Other presets supply their own `DESIGN.md` via `/theme-init`.

---

## 1. Visual Theme & Atmosphere

<!-- AGENT-FILL §1
   Describe the preset's *mood* in 3–6 lines. Cover:
   - Tone in 3–5 adjectives (e.g., "editorial, analytical, declarative")
   - Reference moodboard (e.g., "Notion / Linear / Vercel sensibility")
   - Atmosphere — what does the deck *feel* like to read?
   - Anti-mood — what should it explicitly NOT feel like?
   - One-line litmus test (a concrete sentence the operator can use to judge a slide)
   See jangpm DESIGN.md §1 as a reference example.
-->

**Voice anchors (from theme-active.json):**
- **Tone:** {{TOKEN:voice.tone}}
- **Point of view:** {{TOKEN:voice.pov}}
- **Register:** {{TOKEN:voice.register}}

---

## 2. Palette & Contrast Behavior

### 2.1 Allowed colors (literal, locked)

This preset is monochrome + single accent. The ONLY hex values that may appear in any generated SVG / CSS / Chart.js palette are:

| Token | Hex | Role |
|---|---|---|
| `--bg` | `{{TOKEN:colors.bg}}` | page background |
| `--surface` | `{{TOKEN:colors.surface}}` | card / container |
| `--surface-alt` | `{{TOKEN:colors.surface-alt}}` | grouped row / nested card |
| `--text` | `{{TOKEN:colors.text}}` | primary text |
| `--text-secondary` | `{{TOKEN:colors.text-secondary}}` | secondary text |
| `--text-tertiary` | `{{TOKEN:colors.text-tertiary}}` | captions, page numbers |
| `--border` | `{{TOKEN:colors.border}}` | default divider |
| `--border-strong` | `{{TOKEN:colors.border-strong}}` | emphasis divider |
| `--accent` | `{{TOKEN:colors.accent}}` | sole brand pointer |
| `--accent-soft` | `{{TOKEN:colors.accent-soft}}` | accent-tinted highlight bg |
| `--accent-ink` | `{{TOKEN:colors.accent-ink}}` | accent pressed / dark |
| `--positive` | `{{TOKEN:colors.positive}}` | data context only |
| `--negative` | `{{TOKEN:colors.negative}}` | data context only |
| `--warning` | `{{TOKEN:colors.warning}}` | data context only |

### 2.2 Contrast & accent budget

<!-- AGENT-FILL §2.2
   Define the preset's accent rules:
   - Max accent events per slide (jangpm: 2)
   - Card differentiation rule
   - Semantic color usage policy (when allowed, when forbidden)
   - Chart palette rule (jangpm: single-accent opacity ladder)
-->

### 2.3 Background hierarchy

<!-- AGENT-FILL §2.3
   Define the visual hierarchy of backgrounds:
   bg → surface-alt → surface → accent-soft (or this preset's equivalent).
   State whether skipping rungs is forbidden.
-->

---

## 3. Typography Hierarchy

### 3.1 Font chain (locked)

```
{{TOKEN:typography.font-chain}}
```

Every `<text>` element in generated SVG uses this exact chain.

### 3.2 Type scale

| Role | Size (px) | Weight | LH | Tracking | Use |
|---|---|---|---|---|---|
| Display | {{TOKEN:typography.display.size}} | {{TOKEN:typography.display.weight}} | {{TOKEN:typography.display.line-height}} | {{TOKEN:typography.display.letter-spacing}} | title slide hero |
| Display-sm | {{TOKEN:typography.display-sm.size}} | {{TOKEN:typography.display-sm.weight}} | {{TOKEN:typography.display-sm.line-height}} | {{TOKEN:typography.display-sm.letter-spacing}} | hero stat / closing accent |
| Headline | {{TOKEN:typography.headline.size}} | {{TOKEN:typography.headline.weight}} | {{TOKEN:typography.headline.line-height}} | {{TOKEN:typography.headline.letter-spacing}} | content slide title |
| Title | {{TOKEN:typography.title.size}} | {{TOKEN:typography.title.weight}} | {{TOKEN:typography.title.line-height}} | {{TOKEN:typography.title.letter-spacing}} | card title, subtitle |
| Body | {{TOKEN:typography.body.size}} | {{TOKEN:typography.body.weight}} | {{TOKEN:typography.body.line-height}} | {{TOKEN:typography.body.letter-spacing}} | body text |
| Caption | {{TOKEN:typography.caption.size}} | {{TOKEN:typography.caption.weight}} | {{TOKEN:typography.caption.line-height}} | {{TOKEN:typography.caption.letter-spacing}} | annotations |
| Label | {{TOKEN:typography.label.size}} | {{TOKEN:typography.label.weight}} | {{TOKEN:typography.label.line-height}} | {{TOKEN:typography.label.letter-spacing}} | uppercase taxonomy (eyebrow) |

### 3.3 Hierarchy rules

<!-- AGENT-FILL §3.3
   Define preset-specific typography rules:
   - When to use Display vs Headline (which slide types)
   - Body baseline density (default vs exception)
   - Label as taxonomy marker convention (uppercase when?)
   - Any preset-specific tracking / weight conventions
-->

---

## 4. Spacing & Density

### 4.1 8px grid

`--space-1` {{TOKEN:spacing.1}} / `--space-2` {{TOKEN:spacing.2}} / `--space-3` {{TOKEN:spacing.3}} / `--space-4` {{TOKEN:spacing.4}} / `--space-5` {{TOKEN:spacing.5}} / `--space-6` {{TOKEN:spacing.6}} / `--space-8` {{TOKEN:spacing.8}} / `--space-10` {{TOKEN:spacing.10}} / `--space-12` {{TOKEN:spacing.12}} / `--space-14` {{TOKEN:spacing.14}} / `--space-16` {{TOKEN:spacing.16}}.

### 4.2 Slide-level

<!-- AGENT-FILL §4.2
   - Slide outer padding values
   - Card padding / gap values
   - Internal card stacking gaps
-->

### 4.3 Density floors

<!-- AGENT-FILL §4.3
   Preset-specific density rules:
   - Min content layers per card
   - Text-only slide policy
   - Stats card context requirements
   - Chart container minimums
-->

### 4.4 Density vs sparsity

<!-- AGENT-FILL §4.4
   Where this preset falls on the density spectrum and how to handle "empty space" temptation.
-->

---

## 5. Layout Grammar (= `recommended_layout_family` vocabulary)

This is the canonical vocabulary `slide-plan` writes into `recommended_layout_family`. Each family bundles 2–8 patterns from `references/patterns.md` that share an information shape.

> **Why family-level, not pattern-level?** `slide-plan` decides the *shape* of information; `/slide` Executor picks the specific pattern based on item count, evidence type, and visual rhythm.

<!-- AGENT-FILL §5
   Group this preset's `references/patterns.md` patterns into 5–8 families.
   Required columns: Family | Patterns | Use when | Item-count guide.
   Suggested baseline (adapt to your preset's pattern catalog):
     - structure (deck scaffolding)
     - insight (single-takeaway)
     - breakdown (N parallel concepts)
     - compare (side-by-side contrast)
     - data (charts/tables/metrics)
     - process (time/step-ordered)
     - visual (image/diagram/code-led)
   Then provide layout-selection heuristics ("3–4 parallel items → breakdown, etc.")
   and diversity rules (no consecutive identical, min N families per deck, etc.).

   IMPORTANT — §5.1 "Hybrid Pattern Catalog" subsection (REQUIRED) for body-slide
   default patterns (multi-element compositions). At minimum include:
     - ★ ruled-list-with-eyebrow: uppercase eyebrow + horizontal hairline + (label:body)
       row stack separated by hairlines, NO card boxes. Replaces 1×N card grids for
       list-of-items content. (jangpm-style editorial pattern.)
     - ★ columns-with-vertical-rules: eyebrow + horizontal hairline + N columns
       separated by vertical hairlines, NO card boxes. Replaces 1×N card grids for
       parallel-components content.
     - chart-led-with-takeaway-stack: chart (≈60%) + side cards (40%).
     - definition-with-side-data: text-led definition (≈50%) + supporting data viz.
     - table-with-adjacent-cards: table + side mini-cards.
     - breakdown-with-anchor-stat: hero stat + decomposition cards row.
     - process-with-callout-band: chevron/numbered_steps row + bottom callout band.
     - paired-concept-asymmetric / mapping-grid / icon-explainer-with-metric-inline /
       quote-with-attribution-data (additional optional hybrids).

   Frame the ★ patterns as "first choice for list-of-items / parallel-components
   content" — NOT a universal default. For data-led, comparison, sequence, or
   stat-anchored content, the first-choice primitive is chart-led /
   table-with-adjacent / process-with-callout-band / breakdown-with-anchor-stat
   respectively. Include a content-shape → first-choice-primitive table that maps
   each common content shape to its primary hybrid pattern. This prevents the
   deck from devolving into ★-pattern monotony (every slide a hairline list).

   IMPORTANT — §5.2 "Variation Inspirations" subsection (REQUIRED). For each
   hybrid pattern in §5.1, list 4–6 concrete *intentional variations* — single
   deviations from the anchor that the executor can pick consciously per slide.
   Examples (from jangpm DESIGN.md §5.2, adapt to this preset):
     - ruled-list-with-eyebrow → "hero first row" / "accent-soft row highlight" /
       "rightmost number column" / "multi-section list" / "verdict band closer" /
       "inline icon column"
     - chart-led-with-takeaway-stack → "mega-number lead" / "inline insight band" /
       "two stacked mini-charts" / "asymmetric 65/35" / "annotation callouts" /
       "verdict band footer"
     - breakdown-with-anchor-stat → "mega-stat hero" / "stat with trend annotation" /
       "single dark card" / "asymmetric card row" / "inline mini-charts" /
       "stat with comparator"
   Each variation must remain recognizable as the same pattern (anchor silhouette
   intact). Cap: only ONE variation per slide; per-slide accent ≤ 2 still holds.
   Cross-deck cap: no single variation may repeat 3+ times even when the pattern
   repeats. The executor's per-page audit (`executor.md §2`) records the chosen
   variation per body slide and targets ≥ 70% non-`표준` adoption across the deck.
   See jangpm DESIGN.md §5.2 for the canonical example.
-->

---

## 6. Header / Body / Footer Structure

### 6.1 Page anatomy (1280×720)

<!-- AGENT-FILL §6.1
   ASCII-diagram the page anatomy with y-coordinates and zone heights.
   Identify: header zone (optional), title zone, body zone, GM line, footer.
-->

### 6.2 Header zone

<!-- AGENT-FILL §6.2
   When to use, style, position. State explicitly if "optional".
-->

### 6.3 Title zone

<!-- AGENT-FILL §6.3
   Content vs cover/section/closing title differences.
   Line-break policy on titles.
-->

### 6.4 Body zone

<!-- AGENT-FILL §6.4
   Required wrapper class / structure.
   Vertical fill behavior.
-->

### 6.5 GM (governing message) line

- **Voice:** {{TOKEN:voice.tone}}, {{TOKEN:voice.pov}}, {{TOKEN:voice.register}}
- **Composition hint:** {{TOKEN:voice.gm_style_hint}}
- **Forbidden phrases:** {{TOKEN:voice.forbidden_phrases|csv}}

<!-- AGENT-FILL §6.5
   Add: position (e.g., absolute bottom 24px), typography (size / color),
   length policy ("≤ 30 chars ideal"), and the cardinal rule
   (e.g., "Never a restatement of the page title.").
-->

### 6.6 Footer / page number

<!-- AGENT-FILL §6.6
   Page number format and color, brand mark placement.
-->

---

## 7. Page Flow (Title → Body → End)

| `page_family` | Layout templates | Typical position | Required fields |
|---|---|---|---|
| `title` | `01_cover.svg` | slide 1 | <!-- AGENT-FILL: required content, GM presence --> |
| `body` | `03_content.svg` + family templates | slides 2 to N-1 | <!-- AGENT-FILL --> |
| `chapter` | `02_chapter.svg` | between major divisions | <!-- AGENT-FILL --> |
| `end` | `04_ending.svg` | slide N | <!-- AGENT-FILL --> |

<!-- AGENT-FILL §7
   Flow conventions:
   - When to insert chapter slides (every N slides? optional below threshold?)
   - Agenda slide placement
   - Closing slide composition
-->

---

## 8. Chart & Table Treatment (Rhetorical Roles → Visual Implementation)

This preset honors the 9 rhetorical roles defined in `references/chart-rhetorical-roles.md`. Below is the preset-specific implementation layer.

### 8.1 Role → primary chart template

<!-- AGENT-FILL §8.1
   Map each chart_strategy to your preset's preferred chart_index.json template.
   Rows: growth-trend / forecast / structural-break / focus-comparison /
         distribution / quadrant / priority-matrix / split-segment / funnel / custom.
   Columns: Primary | Alt.
-->

### 8.2 Chart styling rules

- **Palette:** single-accent opacity ladder using `{{TOKEN:colors.accent}}`
- **Semantic exception:** `{{TOKEN:colors.positive}}` / `{{TOKEN:colors.negative}}` / `{{TOKEN:colors.warning}}` only when color encodes data meaning

<!-- AGENT-FILL §8.2 (additional)
   - Legend chrome policy (inline labels vs side legend)
   - Forbidden chart effects (drop-shadow, 3D, gradient, glow)
   - Axis label color and weight
-->

### 8.3 Table styling rules

<!-- AGENT-FILL §8.3
   - Header row treatment (bg color, typography)
   - "Recommended column" highlight (when comparison table)
   - Cell text alignment / numerics
   - Verdict row convention
-->

### 8.4 Required adjacency: chart + takeaway

<!-- AGENT-FILL §8.4
   How charts pair with takeaway cards in this preset:
   - Required adjacency (right column? below?)
   - Card composition (metric + trend + context)
   - Plan-time enforcement note
-->

---

## 9. Icon System

### 9.1 Library lock

- **Default:** {{TOKEN:assets.icon-pack-default}}
- **Fallback:** {{TOKEN:assets.icon-pack-fallback}}
- **Forbidden:** other packs, emoji, unicode glyph icons, mixed packs.

### 9.2 Usage

<!-- AGENT-FILL §9.2
   Show the placeholder syntax for icons in this preset's pipeline.
   Note any post-processing transformations (e.g., finalize_svg.py role).
-->

### 9.3 Search before use

```bash
ls .claude/skills/slide/templates/icons/{{TOKEN:assets.icon-pack-default}}/ | grep <keyword>
```

### 9.4 Sizing

<!-- AGENT-FILL §9.4
   Card icon size, hero icon size, inline icon size, stroke widths.
-->

### 9.5 Icon vs number badges

<!-- AGENT-FILL §9.5
   When icons preferred, when number badges preferred, mixing rules.
-->

### 9.6 Icon wrappers / decorations

<!-- AGENT-FILL §9.6
   Whether circle wrappers / badges / colored backgrounds around icons are allowed.
-->

---

## 10. Anti-Patterns (Reject at Plan Time)

These are the patterns `slide-plan` validator must reject. They duplicate / strengthen `anti-slop-core.md` and `anti-slop-theme.md` rules into plan-level checks.

<!-- AGENT-FILL §10
   List 12–18 anti-patterns specific to this preset.
   Required columns: # | Anti-pattern | Detect via | Fix.
   Use jangpm DESIGN.md §10 as a reference for the level of specificity expected.
   Cover at minimum:
     - Lazy repetition (same family 3+ consecutive)
     - Dominant primitive 3+ consecutive (hairline-list / boxed-cards / chart-led /
       table-led / process-flow — see executor.md §0.1 #4 Dominant Primitive Cap)
     - Same variation repeated 3+ times across the deck (see §5.2)
     - Chart without takeaway
     - Empty evidence_sources
     - Multi-hue chart palette
     - Multi-icon-pack mixing
     - GM restating title
     - Forbidden voice phrases
     - Text-only slide
     - Off-palette hex
     - Effects (gradient, drop-shadow, glow)
-->

---

## Appendix — `slide-plan` quick reference

**Family vocabulary** (use one per slide): <!-- AGENT-FILL: list this preset's families from §5 -->

**Chart strategy vocabulary**: see `references/chart-rhetorical-roles.md`.

**Page family** (use one per slide): `title` / `chapter` / `body` / `end`.

**Slide role enum**: see `references/slide-role-enum.md`.

---

<!-- Rendered from design-md.tpl.md by render_design_md.py. AGENT-FILL markers must be replaced by the agent invoking /theme-init. -->
