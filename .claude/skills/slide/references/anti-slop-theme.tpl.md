# Anti-Slop Reference (Theme): Active-Theme Literal Enforcement

Theme-specific anti-patterns for the **{{TOKEN:display_name}}** theme (`{{TOKEN:name}}`). Structural rules that apply regardless of theme live in `anti-slop-core.md`.

> **Regenerate on theme change.** This file is rendered from `theme-active.json` each time `/theme-init` runs. Never hand-edit — edits will be overwritten.

---

## Rule T1: Exclusive Accent Hex

**Forbidden:** introducing any color beyond the locked palette. Especially, introducing a second "accent" hue alongside `{{TOKEN:colors.accent}}`.

**Allowed color values** — these are the only hex values permitted in generated SVG / CSS:

| Token | Value |
|-------|-------|
| `accent` | `{{TOKEN:colors.accent}}` |
| `accent-soft` | `{{TOKEN:colors.accent-soft}}` |
| `accent-ink` | `{{TOKEN:colors.accent-ink}}` |
| `text` | `{{TOKEN:colors.text}}` |
| `text-secondary` | `{{TOKEN:colors.text-secondary}}` |
| `text-tertiary` | `{{TOKEN:colors.text-tertiary}}` |
| `bg` | `{{TOKEN:colors.bg}}` |
| `surface` | `{{TOKEN:colors.surface}}` |
| `surface-alt` | `{{TOKEN:colors.surface-alt}}` |
| `border` | `{{TOKEN:colors.border}}` |
| `border-strong` | `{{TOKEN:colors.border-strong}}` |
| `positive` | `{{TOKEN:colors.positive}}` (data contexts only) |
| `negative` | `{{TOKEN:colors.negative}}` (data contexts only) |
| `warning` | `{{TOKEN:colors.warning}}` (data contexts only) |

**Why:** The slide-svg pipeline bakes tokens into DrawingML at export time, so runtime multi-theming is impossible. One file = one theme. Introducing off-palette colors guarantees a visual inconsistency that cannot be fixed post-export.
{{IF:colors.shell-bg}}
**Narrative-shell band colors** — additionally permitted, but ONLY on the narrative shells (`01_cover`, `02_chapter`, `04_ending`). NEVER on content slides:

| Token | Value | Scope |
|-------|-------|-------|
| `shell-bg` | `{{TOKEN:colors.shell-bg}}` | narrative band fill (full-bleed) |
| `shell-text` | `{{TOKEN:colors.shell-text|optional}}` | text on the band |
| `shell-text-secondary` | `{{TOKEN:colors.shell-text-secondary|optional}}` | muted text on the band |
| `shell-accent` | `{{TOKEN:colors.shell-accent|optional}}` | CTA / accent on the band |
| `shell-spectrum` | {{TOKEN:colors.shell-spectrum|csv}} | decorative brand dots (narrative only) |
{{/IF}}
---

## Rule T2: Accent Rarity Budget (≤ 2 per slide)

**Forbidden:** painting multiple elements with `{{TOKEN:colors.accent}}` or `{{TOKEN:colors.accent-soft}}` just to add visual variety.

**Allowed:** at most **two** accent "events" per content slide. An event is any of:
- Accent-colored text (`fill="{{TOKEN:colors.accent}}"`)
- Accent-soft filled container (`fill="{{TOKEN:colors.accent-soft}}"`)
- Accent-stroked emphasis rule (`stroke="{{TOKEN:colors.accent}}"`)

**Why:** Accent is a pointer, not a palette. Multiple accents per slide cancel each other out and produce a "colorful SaaS dashboard" read instead of an editorial read.

---

## Rule T3: Font Chain Lock

**Forbidden:** any `<text>` element missing the full font chain, or using a different family.

**Correct:**
```xml
<text font-family="{{TOKEN:typography.font-chain}}" ...>
```

**Why:** If a viewer lacks the primary font, the chain degrades gracefully through Korean/Latin fallbacks. A missing or truncated chain causes system default rendering — typically a serif — which breaks the editorial tone instantly.

---

## Rule T4: Chart Palette — Single-Accent Opacity Ladder

**Forbidden:** multi-hue Chart.js palettes.

**Correct:** single accent with an opacity ladder. For `{{TOKEN:colors.accent}}`:

```js
backgroundColor: [
  'rgba({{TOKEN:colors.accent|rgb}}, 0.85)',
  'rgba({{TOKEN:colors.accent|rgb}}, 0.60)',
  'rgba({{TOKEN:colors.accent|rgb}}, 0.40)',
  'rgba({{TOKEN:colors.accent|rgb}}, 0.25)',
]
```

Semantic columns (growth vs. decline) may use `{{TOKEN:colors.positive}}` / `{{TOKEN:colors.negative}}` **only when the color encodes data meaning**.

**Why:** Chart.js cannot resolve CSS variables, so the palette must be literal. Multi-hue palettes re-introduce the "every series gets its own color" dashboard aesthetic that the single-accent discipline exists to prevent.

---

## Rule T5: Icon Library Lock

**Forbidden:** icons from packs other than `{{TOKEN:assets.icon-pack-default}}` (fallback: `{{TOKEN:assets.icon-pack-fallback}}`). Mixing multiple icon styles on one slide.

**Correct:** placeholder form processed by `finalize_svg.py`:

```xml
<use data-icon="{{TOKEN:assets.icon-pack-default}}/<name>"
     x="..." y="..." width="..." height="..."
     stroke="currentColor" stroke-width="{{TOKEN:stroke.icon}}" />
```

**Why:** Mixing icon packs (outline + filled, line + glyph) is a dead giveaway of AI composition. A single family carries the visual through the whole deck.

---

## Rule T6: Voice & GM Tone Lock

**Forbidden phrases in GM and speaker notes:**
{{TOKEN:voice.forbidden_phrases|bulleted}}

**Required tone:**
- Register: {{TOKEN:voice.register}}
- Point of view: {{TOKEN:voice.pov}}
- Tone: {{TOKEN:voice.tone}}

**GM composition hint:** {{TOKEN:voice.gm_style_hint}}

**Why:** The GM line is the editorial contract between slide and audience. Tone drift is the fastest path to "AI-generated" smell; it's also the easiest to accidentally slip into via marketing-style filler.

---

## Rule T7: Radius Discipline

**Forbidden:** ad-hoc `rx="<arbitrary>"` values on `<rect>` elements.

**Allowed radius values** (in px):

| Name | Value | Usage |
|------|-------|-------|
| `xs` | {{TOKEN:radius.xs}} | chip, tight badge |
| `sm` | {{TOKEN:radius.sm}} | small callout, inline tag |
| `md` | {{TOKEN:radius.md}} | default card |
| `lg` | {{TOKEN:radius.lg}} | hero card |
| `xl` | {{TOKEN:radius.xl}} | large container |
| `pill` | {{TOKEN:radius.pill}} | fully rounded pill |

**Why:** Mixing radii within a deck (12px card next to 6px card next to 16px card) breaks the rhythm. The scale above is the only valid set.

---

## Rule T8: Stroke Width Discipline

**Allowed stroke widths:**

| Role | Value (px) | Usage |
|------|------------|-------|
| icon | {{TOKEN:stroke.icon}} | line-art icons |
| divider | {{TOKEN:stroke.divider}} | default structural dividers |
| emphasis | {{TOKEN:stroke.emphasis}} | accent rule, highlight underline |

**Forbidden:** hairline strokes (<1px), display-weight strokes (>3px), or decorative dashed/dotted patterns.

**Why:** Stroke inconsistency is the other half of radius discipline. Together they set the deck's mechanical precision; drifting from these values is visible at a glance.

---

## Card Treatment Lock

The active theme's card treatment is **{{IF:surface.card_style=hairline}}hairline{{/IF}}{{IF:surface.card_style=filled}}filled{{/IF}}{{IF:surface.card_style=borderless}}borderless{{/IF}}**. Apply it consistently across the whole deck.

**Forbidden:** mixing card treatments within one deck, or ignoring the active treatment.
{{IF:surface.card_style=borderless}}
**Borderless lock:** NEVER draw a `<rect>` as a card container. Group with whitespace + a single hairline rule (`{{TOKEN:colors.border}}`) and the type hierarchy. A filled or bordered rectangle used as a card box is a violation.
{{/IF}}{{IF:surface.card_style=filled}}
**Filled lock:** card boxes use a `{{TOKEN:colors.surface-alt}}` / `{{TOKEN:colors.surface}}` fill with **no** border. Do not add a 1px border on top of the fill.
{{/IF}}
**Why:** Card treatment is a structural identity signal. One file = one theme = one treatment; mixing hairline, filled, and borderless boxes reads as AI-assembled rather than designed.
{{IF:colors.shell-bg}}
---

## Rule T9: Narrative-Shell Band Scope

**Allowed:** the `shell-*` band fill and `shell-spectrum` hues appear ONLY on the narrative shells — `01_cover`, `02_chapter`, `04_ending`. These may render full-bleed on `{{TOKEN:colors.shell-bg}}`, place `shell-text` / `shell-accent` text on the band, and show the brand spectrum as a decorative dot / bar row.

**Forbidden:**
- Any `shell-bg` band, `shell-spectrum` hue, or `shell-text` color on a **content** slide (`03_content` and every Executor-composed body slide). Content stays light: `{{TOKEN:colors.bg}}` / `{{TOKEN:colors.surface}}` backgrounds, `{{TOKEN:colors.text}}` / `{{TOKEN:colors.text-secondary}}` ink, single `{{TOKEN:colors.accent}}` accent.
- Using `shell-spectrum` as a data palette. It is decorative brand identity for narrative shells only — charts still use the single-accent opacity ladder (Rule T4).

**Budget:** spectrum dots are a single narrative-shell decoration and are NOT counted against the content accent budget (Rule T2); the spectrum row counts as one composition element and must not exceed the published `shell-spectrum` length.

**Why:** The light-mode relaxation is deliberately scoped. A dark hero on the cover / closing reads as branded and intentional; the same band on a dense content slide destroys the editorial, report-style legibility the deck depends on.
{{/IF}}
---

<!-- Rendered by render_anti_slop_theme.py from theme-active.json -->
