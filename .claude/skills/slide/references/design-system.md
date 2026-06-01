# Design System Reference — Jangpm

> **Active theme:** `jangpm` — Editorial, minimal, Korean lecture / report visual language. Notion/Linear/Vercel sensibility adapted to instructional content.
>
> This file is rendered from `theme-active.json` by `render_design_system.py`. Never hand-edit — edits will be overwritten on the next `/theme-init` run. The template source is `design-system.tpl.md`.

## Design Tone

- Generous whitespace, restrained color (single accent), clear typographic hierarchy
- Forbidden: excessive decoration, icon spam, dense card interiors
- **Single accent color** — `#4633E3` only; all other colors must be achromatic (black/gray/white) or from the tokens below
- **Visually full slides** — fill the slide with one **dominant visual** (chart/diagram/image/table), never with more text; "full" means visually *led*, not packed (bounded by the Restraint counterweights below — Rules 21–22)
- **No text-only slides** — even quote/hero patterns require at least one visual element alongside the text
- **High content density** — a slide should feel informationally rich via its dominant visual + concise supporting context (subtitle, benchmark comparison, trend annotation, a takeaway card) — **not** via dense body text or stacked cards. Stats cards should include a context line (e.g., "vs industry avg 3.2%"). Bounded by the Restraint counterweights below: one message, ≤3 bullets, ≥30% whitespace.
- **Restraint counterweights (warn — `anti-slop-core.md` Rules 20–23)** — the density guidance above is *bounded* by: one dominant message with text as caption (≤3 bullets), ≥30% whitespace, a clear top-right quiet zone, photographs standing alone (no text overlay), and no decorative step-flow. "Visually full" and "high density" mean one **dominant visual as evidence** (≥~55% of the content area) — not dense body text or stacked cards. Rich visual paired with restrained text is the target, not crowding.
- **Card differentiation rule** — In any card grid, at least one card should be visually distinct (accent-soft background or highlighted metric). Equal-weight cards are a design smell.
- **Density minimum** — Every card should contain at least 3 content layers (e.g., icon/badge + title + body + caption/metric). Two-layer cards (icon + title only) look unfinished.
- **Icon badges preferred, number badges for steps** — Default to SVG icon badges for card grids. Use `.number-badge` (01–04) only when sequential order is the primary information (numbered steps, ranked priorities). Mix icons and numbers when appropriate — icons are more visually interesting.
- **Charts use single accent with opacity** — `rgba(70, 51, 227, 0.85/0.6/0.4/0.25)`; never multiple distinct hues
- **Semantic colors in data contexts** — Use `--positive` (`#059669`), `--negative` (`#E11D48`), `--warning` (`#D97706`) to encode meaning in trend indicators, metric badges, and chart colors. Example: churn rate trend arrow uses `color: var(--negative)`, growth metric badge uses `color: var(--positive)`
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
| `--bg` | `#FAFAF9` | Body background |
| `--surface` | `#FFFFFF` | Card/container background |
| `--surface-alt` | `#F5F5F4` | Subtle grouped background |
| `--text` | `#1A1A1A` | Main text (never pure `#000`) |
| `--text-secondary` | `#6B7280` | Secondary text |
| `--text-tertiary` | `#9CA3AF` | Captions, page numbers |
| `--accent` | `#4633E3` | Primary accent |
| `--accent-soft` | `#E8E5FC` | Accent-tinted background / highlight column |
| `--accent-ink` | `#2E1FB3` | Accent pressed / darker variant |
| `--border` | `#E5E7EB` | Default border |
| `--border-strong` | `#D4D4D4` | Stronger divider |

## Semantic Colors

| Token | Value | Use Case |
|-------|-------|----------|
| `--positive` | `#059669` | Success, growth, positive metrics |
| `--positive-soft` | `#ECFDF5` | Light positive background for trend badges, table cell highlights |
| `--negative` | `#E11D48` | Error, decline, negative metrics. **Also use for trend indicators on negative-direction metrics** (e.g., churn increase = `trend-negative` even if the number has a `+` sign) |
| `--negative-soft` | `#FFF1F2` | Light negative background for trend badges, table cell highlights |
| `--warning` | `#D97706` | Caution, attention needed |
| `--warning-soft` | `#FFFBEB` | Light warning background for trend badges, table cell highlights |

> **Semantic colors are used ONLY in data contexts:** trend indicators, metric badges, chart colors, table cell highlights. Never as card backgrounds or border decorations.

## Typography

**Font chain (applied verbatim to every `<text>` in SVG):**

```
Pretendard, 'Apple SD Gothic Neo', 'Malgun Gothic', Arial, sans-serif
```

**Scale:**

| Level | Size (px) | Weight | Line-height | Letter-spacing (px) | Use Case |
|-------|-----------|--------|-------------|---------------------|----------|
| Display | 56 | 800 | 1.08 | -1.68 | Title slide large text |
| Display-sm | 40 | 800 | 1.1 | -0.8 | Hero stat, closing accent |
| Headline | 32 | 700 | 1.2 | -0.64 | Content slide titles |
| Title | 18.4 | 600 | 1.3 | 0.0 | Card titles, subtitles |
| Body | 15.2 | 400 | 1.6 | 0.0 | Body text |
| Caption | 12.8 | 500 | 1.4 | 0.0 | Labels, annotations |
| Label | 12.8 | 600 | 1.4 | 0.64 | Uppercase taxonomy labels (eyebrow) |

## Spacing System

8px grid system. All spacing uses CSS custom properties:

| Token | Value (px) |
|-------|------------|
| `--space-1` | 4 |
| `--space-2` | 8 |
| `--space-3` | 12 |
| `--space-4` | 16 |
| `--space-5` | 20 |
| `--space-6` | 24 |
| `--space-8` | 32 |
| `--space-10` | 40 |
| `--space-12` | 48 |
| `--space-14` | 56 |
| `--space-16` | 64 |

Key spacing values:
- Slide padding: `var(--space-14)` (bottom padding `var(--space-16)` to reserve GM space)
- Card padding: `var(--card-padding)` = `var(--space-6)`
- Card gap: `var(--card-gap)` = `var(--space-6)`

## Radius

| Token | Value (px) | Usage |
|-------|------------|-------|
| `--radius-xs` | 4 | chip, tight badge |
| `--radius-sm` | 8 | small callout, inline tag |
| `--radius-md` | 12 | default card |
| `--radius-lg` | 12 | hero card |
| `--radius-xl` | 20 | large container |
| `--radius-pill` | 9999 | fully rounded pill |

## Stroke

| Role | Value (px) | Usage |
|------|------------|-------|
| icon | 2 | line-art icon stroke |
| divider | 1 | default structural divider |
| emphasis | 2 | accent rule, highlight underline |

## Assets

| Token | Value |
|-------|-------|
| `icon-pack-default` | `tabler-outline` |
| `icon-pack-fallback` | `tabler-filled` |
| `character` | `.claude/skills/slide/templates/layouts/jangpm/assets/brand/jangpm-character.png` |

## Voice

- **Tone:** editorial, analytical, declarative
- **Point of view:** third-person institutional
- **Register:** Korean lecture / report
- **Forbidden phrases:** "여러분", "우리는", "함께해요"
- **GM line hint:** One declarative sentence stating the so-what / takeaway. Never a restatement of the page title. Korean-first, ≤30 chars ideal.

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

**Card treatment:** **hairline** (default) — a `1px solid var(--border)` rule on a `var(--surface)` fill. Differentiate the hero card with a `var(--accent-soft)` background.

| Property | Value |
|----------|-------|
| `--card-padding` | `var(--space-6)` |
| `--card-gap` | `var(--space-6)` |
| `--card-radius` | `12px` |
| Background | per treatment (default `var(--surface)` / `var(--surface-alt)`) |
| Border | per treatment (hairline default: `1px solid var(--border)`) |

## Calibration Anchors

| Score | Reference |
|-------|-----------|
| 10점 | Notion/Linear quality — generous whitespace, minimal color, clear hierarchy |
| 8점 | Clean SaaS intro page — well-organized but less refined |
| 6점 | Generic Bootstrap template — functional but generic |

<!-- Rendered by render_design_system.py from theme-active.json -->
