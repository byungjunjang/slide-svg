# Design System Reference — {{TOKEN:display_name}}

> **Active theme:** `{{TOKEN:name}}` — {{TOKEN:description}}
>
> This file is rendered from `theme-active.json` by `render_design_system.py`. Never hand-edit — edits will be overwritten on the next `/theme-init` run. The template source is `design-system.tpl.md`.

## Design Tone

- Generous whitespace, restrained color (single accent), clear typographic hierarchy
- Forbidden: excessive decoration, icon spam, dense card interiors
- **Single accent color** — `{{TOKEN:colors.accent}}` only; all other colors must be achromatic (black/gray/white) or from the tokens below
- **Visually full slides** — fill the slide with one **dominant visual** (chart/diagram/image/table), never with more text; "full" means visually *led*, not packed (bounded by the Restraint counterweights below — Rules 21–22)
- **No text-only slides** — even quote/hero patterns require at least one visual element alongside the text
- **High content density** — a slide should feel informationally rich via its dominant visual + concise supporting context (subtitle, benchmark comparison, trend annotation, a takeaway card) — **not** via dense body text or stacked cards. Stats cards should include a context line (e.g., "vs industry avg 3.2%"). Bounded by the Restraint counterweights below: one message, ≤3 bullets, ≥30% whitespace.
- **Restraint counterweights (warn — `anti-slop-core.md` Rules 20–23)** — the density guidance above is *bounded* by: one dominant message with text as caption (≤3 bullets), ≥30% whitespace, a clear top-right quiet zone, photographs standing alone (no text overlay), and no decorative step-flow. "Visually full" and "high density" mean one **dominant visual as evidence** (≥~55% of the content area) — not dense body text or stacked cards. Rich visual paired with restrained text is the target, not crowding.
- **Card differentiation rule** — In any card grid, at least one card should be visually distinct (accent-soft background or highlighted metric). Equal-weight cards are a design smell.
- **Density minimum** — Every card should contain at least 3 content layers (e.g., icon/badge + title + body + caption/metric). Two-layer cards (icon + title only) look unfinished.
- **Icon badges preferred, number badges for steps** — Default to SVG icon badges for card grids. Use `.number-badge` (01–04) only when sequential order is the primary information (numbered steps, ranked priorities). Mix icons and numbers when appropriate — icons are more visually interesting.
- **Charts use single accent with opacity** — `rgba({{TOKEN:colors.accent|rgb}}, 0.85/0.6/0.4/0.25)`; never multiple distinct hues
- **Semantic colors in data contexts** — Use `--positive` (`{{TOKEN:colors.positive}}`), `--negative` (`{{TOKEN:colors.negative}}`), `--warning` (`{{TOKEN:colors.warning}}`) to encode meaning in trend indicators, metric badges, and chart colors. Example: churn rate trend arrow uses `color: var(--negative)`, growth metric badge uses `color: var(--positive)`
- **Chart container height** — Use `height: 400px` (not 320px) for single-chart slides to fill vertical space properly
- **Comparison tables need a winner** — Always highlight one column with `col-recommended` class (accent-soft background). Equal-weight columns are a design smell. Add subtitle/stat in column headers for density. Use check/x SVG icons for binary features. Include a verdict/summary bottom row.
- **Bare line icons only** — Use bare SVG line icons (`icon-lg` class) without any circle wrapper or background. Icons should be simple, monochrome line art that lets typography and layout carry the visual weight.
- **Bento-grid visual hierarchy** — The `bento-span-2` (hero) card uses `background: var(--accent-soft); border: 1px solid var(--accent)`. Other cards use `background: var(--surface-alt)` for subtle differentiation. No colored left-borders.
- **Concept-cards differentiation** — Differentiate cards through content hierarchy (number-badge or icon + title + body + caption), not through color coding. Use `var(--surface-alt)` background for all cards. The accent card (primary concept) may use `var(--accent-soft)` background for emphasis.
- **Label captions as taxonomy markers** — When a caption serves as a category label (e.g., "Foundation", "Growth", "Enterprise"), use `text-transform: uppercase; letter-spacing: 0.05em` for a polished SaaS feel. This applies to: card category captions, agenda item subtitles, and comparison header subtitles. Regular captions (metrics, descriptions) remain sentence-case.
- **Agenda pattern polish** — Agenda items use number-badges (not plain text numbers), each item includes a subtitle caption + right-aligned duration annotation. Current item has accent left-border + accent-soft bg. The card wrapper uses `padding: 0; overflow: hidden` so items control their own internal spacing with consistent bottom borders.

## Color Tokens

| Token | Value | Usage |
|-------|-------|-------|
| `--bg` | `{{TOKEN:colors.bg}}` | Body background |
| `--surface` | `{{TOKEN:colors.surface}}` | Card/container background |
| `--surface-alt` | `{{TOKEN:colors.surface-alt}}` | Subtle grouped background |
| `--text` | `{{TOKEN:colors.text}}` | Main text (never pure `#000`) |
| `--text-secondary` | `{{TOKEN:colors.text-secondary}}` | Secondary text |
| `--text-tertiary` | `{{TOKEN:colors.text-tertiary}}` | Captions, page numbers |
| `--accent` | `{{TOKEN:colors.accent}}` | Primary accent |
| `--accent-soft` | `{{TOKEN:colors.accent-soft}}` | Accent-tinted background / highlight column |
| `--accent-ink` | `{{TOKEN:colors.accent-ink}}` | Accent pressed / darker variant |
| `--border` | `{{TOKEN:colors.border}}` | Default border |
| `--border-strong` | `{{TOKEN:colors.border-strong}}` | Stronger divider |

## Semantic Colors

| Token | Value | Use Case |
|-------|-------|----------|
| `--positive` | `{{TOKEN:colors.positive}}` | Success, growth, positive metrics |
| `--positive-soft` | `{{TOKEN:colors.positive-soft}}` | Light positive background for trend badges, table cell highlights |
| `--negative` | `{{TOKEN:colors.negative}}` | Error, decline, negative metrics. **Also use for trend indicators on negative-direction metrics** (e.g., churn increase = `trend-negative` even if the number has a `+` sign) |
| `--negative-soft` | `{{TOKEN:colors.negative-soft}}` | Light negative background for trend badges, table cell highlights |
| `--warning` | `{{TOKEN:colors.warning}}` | Caution, attention needed |
| `--warning-soft` | `{{TOKEN:colors.warning-soft}}` | Light warning background for trend badges, table cell highlights |

> **Semantic colors are used ONLY in data contexts:** trend indicators, metric badges, chart colors, table cell highlights. Never as card backgrounds or border decorations.

## Typography

**Font chain (applied verbatim to every `<text>` in SVG):**

```
{{TOKEN:typography.font-chain}}
```

**Scale:**

| Level | Size (px) | Weight | Line-height | Letter-spacing (px) | Use Case |
|-------|-----------|--------|-------------|---------------------|----------|
| Display | {{TOKEN:typography.display.size}} | {{TOKEN:typography.display.weight}} | {{TOKEN:typography.display.line-height}} | {{TOKEN:typography.display.letter-spacing}} | Title slide large text |
| Display-sm | {{TOKEN:typography.display-sm.size}} | {{TOKEN:typography.display-sm.weight}} | {{TOKEN:typography.display-sm.line-height}} | {{TOKEN:typography.display-sm.letter-spacing}} | Hero stat, closing accent |
| Headline | {{TOKEN:typography.headline.size}} | {{TOKEN:typography.headline.weight}} | {{TOKEN:typography.headline.line-height}} | {{TOKEN:typography.headline.letter-spacing}} | Content slide titles |
| Title | {{TOKEN:typography.title.size}} | {{TOKEN:typography.title.weight}} | {{TOKEN:typography.title.line-height}} | {{TOKEN:typography.title.letter-spacing}} | Card titles, subtitles |
| Body | {{TOKEN:typography.body.size}} | {{TOKEN:typography.body.weight}} | {{TOKEN:typography.body.line-height}} | {{TOKEN:typography.body.letter-spacing}} | Body text |
| Caption | {{TOKEN:typography.caption.size}} | {{TOKEN:typography.caption.weight}} | {{TOKEN:typography.caption.line-height}} | {{TOKEN:typography.caption.letter-spacing}} | Labels, annotations |
| Label | {{TOKEN:typography.label.size}} | {{TOKEN:typography.label.weight}} | {{TOKEN:typography.label.line-height}} | {{TOKEN:typography.label.letter-spacing}} | Uppercase taxonomy labels (eyebrow) |

## Spacing System

8px grid system. All spacing uses CSS custom properties:

| Token | Value (px) |
|-------|------------|
| `--space-1` | {{TOKEN:spacing.1}} |
| `--space-2` | {{TOKEN:spacing.2}} |
| `--space-3` | {{TOKEN:spacing.3}} |
| `--space-4` | {{TOKEN:spacing.4}} |
| `--space-5` | {{TOKEN:spacing.5}} |
| `--space-6` | {{TOKEN:spacing.6}} |
| `--space-8` | {{TOKEN:spacing.8}} |
| `--space-10` | {{TOKEN:spacing.10}} |
| `--space-12` | {{TOKEN:spacing.12}} |
| `--space-14` | {{TOKEN:spacing.14}} |
| `--space-16` | {{TOKEN:spacing.16}} |

Key spacing values:
- Slide padding: `var(--space-14)` (bottom padding `var(--space-16)` to reserve GM space)
- Card padding: `var(--card-padding)` = `var(--space-6)`
- Card gap: `var(--card-gap)` = `var(--space-6)`

## Radius

| Token | Value (px) | Usage |
|-------|------------|-------|
| `--radius-xs` | {{TOKEN:radius.xs}} | chip, tight badge |
| `--radius-sm` | {{TOKEN:radius.sm}} | small callout, inline tag |
| `--radius-md` | {{TOKEN:radius.md}} | default card |
| `--radius-lg` | {{TOKEN:radius.lg}} | hero card |
| `--radius-xl` | {{TOKEN:radius.xl}} | large container |
| `--radius-pill` | {{TOKEN:radius.pill}} | fully rounded pill |

## Stroke

| Role | Value (px) | Usage |
|------|------------|-------|
| icon | {{TOKEN:stroke.icon}} | line-art icon stroke |
| divider | {{TOKEN:stroke.divider}} | default structural divider |
| emphasis | {{TOKEN:stroke.emphasis}} | accent rule, highlight underline |

## Assets

| Token | Value |
|-------|-------|
| `icon-pack-default` | `{{TOKEN:assets.icon-pack-default}}` |
| `icon-pack-fallback` | `{{TOKEN:assets.icon-pack-fallback}}` |
| `character` | `{{TOKEN:assets.character|optional}}` |

## Voice

- **Tone:** {{TOKEN:voice.tone}}
- **Point of view:** {{TOKEN:voice.pov}}
- **Register:** {{TOKEN:voice.register}}
- **Forbidden phrases:** {{TOKEN:voice.forbidden_phrases|csv}}
- **GM line hint:** {{TOKEN:voice.gm_style_hint}}

## Slide Layout

- Title/section/closing slides: add `.slide-centered` class for `justify-content: center`
- Content slides: title (`<h2 class="headline">`) stays at top, body content wrapped in `<div class="slide-body">` which fills remaining space from the top
- **CRITICAL: Content slides MUST use `<div class="slide-body">` wrapper** — NOT `<div class="flex-col gap-6">`. The `.slide-body` class has `flex: 1; justify-content: flex-start; padding-top: var(--space-4);` which places content immediately below the headline, maximizing fill rate.
- Structure for content slides: `<section> → <h2 class="headline"> + <div class="slide-body"> (content fills from top) + <div class="gm"> (absolutely positioned bottom)`
- GM is absolutely positioned at the bottom; do NOT add `position: relative` to section (Reveal.js's own positioning serves as context)
- Must add `.reveal .slides > section.present { display: flex !important; }` to override Reveal.js's `display: block`
- `.accent-badge` uses `padding: var(--space-2) var(--space-4)` and `font-size: var(--fs-body)` — NOT caption size
- `.display` class is reserved for title slides, section dividers, and closing slides only
- Body content slides should use `.headline` for emphasized text, never `.display`

## Card System

**Card treatment:**{{IF:surface.card_style=hairline}} **hairline** (default) — a `1px solid var(--border)` rule on a `var(--surface)` fill. Differentiate the hero card with a `var(--accent-soft)` background.{{/IF}}{{IF:surface.card_style=filled}} **filled** — `var(--surface-alt)` / `var(--surface)` fill, **no** border; differentiate the hero card with a `var(--accent-soft)` background.{{/IF}}{{IF:surface.card_style=borderless}} **borderless** — do **not** draw a `<rect>` card container. Group content with whitespace + a single hairline rule (`var(--border)`) and the type hierarchy. No filled or bordered rectangles as containers; differentiate the hero block with weight/size, not a fill.{{/IF}}

| Property | Value |
|----------|-------|
| `--card-padding` | `var(--space-6)` |
| `--card-gap` | `var(--space-6)` |
| `--card-radius` | `{{TOKEN:radius.md}}px` |
| Background | per treatment (default `var(--surface)` / `var(--surface-alt)`) |
| Border | per treatment (hairline default: `1px solid var(--border)`) |

## Calibration Anchors

| Score | Reference |
|-------|-----------|
| 10점 | Notion/Linear quality — generous whitespace, minimal color, clear hierarchy |
| 8점 | Clean SaaS intro page — well-organized but less refined |
| 6점 | Generic Bootstrap template — functional but generic |

<!-- Rendered by render_design_system.py from theme-active.json -->
