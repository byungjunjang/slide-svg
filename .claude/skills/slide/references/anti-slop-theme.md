# Anti-Slop Reference (Theme): Active-Theme Literal Enforcement

Theme-specific anti-patterns for the **Jangpm** theme (`jangpm`). Structural rules that apply regardless of theme live in `anti-slop-core.md`.

> **Regenerate on theme change.** This file is rendered from `theme-active.json` each time `/theme-init` runs. Never hand-edit — edits will be overwritten.

---

## Rule T1: Exclusive Accent Hex

**Forbidden:** introducing any color beyond the locked palette. Especially, introducing a second "accent" hue alongside `#4633E3`.

**Allowed color values** — these are the only hex values permitted in generated SVG / CSS:

| Token | Value |
|-------|-------|
| `accent` | `#4633E3` |
| `accent-soft` | `#E8E5FC` |
| `accent-ink` | `#2E1FB3` |
| `text` | `#1A1A1A` |
| `text-secondary` | `#6B7280` |
| `text-tertiary` | `#9CA3AF` |
| `bg` | `#FAFAF9` |
| `surface` | `#FFFFFF` |
| `surface-alt` | `#F5F5F4` |
| `border` | `#E5E7EB` |
| `border-strong` | `#D4D4D4` |
| `positive` | `#059669` (data contexts only) |
| `negative` | `#E11D48` (data contexts only) |
| `warning` | `#D97706` (data contexts only) |

**Why:** The slide-svg pipeline bakes tokens into DrawingML at export time, so runtime multi-theming is impossible. One file = one theme. Introducing off-palette colors guarantees a visual inconsistency that cannot be fixed post-export.

---

## Rule T2: Accent Rarity Budget (≤ 2 per slide)

**Forbidden:** painting multiple elements with `#4633E3` or `#E8E5FC` just to add visual variety.

**Allowed:** at most **two** accent "events" per content slide. An event is any of:
- Accent-colored text (`fill="#4633E3"`)
- Accent-soft filled container (`fill="#E8E5FC"`)
- Accent-stroked emphasis rule (`stroke="#4633E3"`)

**Why:** Accent is a pointer, not a palette. Multiple accents per slide cancel each other out and produce a "colorful SaaS dashboard" read instead of an editorial read.

---

## Rule T3: Font Chain Lock

**Forbidden:** any `<text>` element missing the full font chain, or using a different family.

**Correct:**
```xml
<text font-family="Pretendard, 'Apple SD Gothic Neo', 'Malgun Gothic', Arial, sans-serif" ...>
```

**Why:** If a viewer lacks the primary font, the chain degrades gracefully through Korean/Latin fallbacks. A missing or truncated chain causes system default rendering — typically a serif — which breaks the editorial tone instantly.

---

## Rule T4: Chart Palette — Single-Accent Opacity Ladder

**Forbidden:** multi-hue Chart.js palettes.

**Correct:** single accent with an opacity ladder. For `#4633E3`:

```js
backgroundColor: [
  'rgba(70, 51, 227, 0.85)',
  'rgba(70, 51, 227, 0.60)',
  'rgba(70, 51, 227, 0.40)',
  'rgba(70, 51, 227, 0.25)',
]
```

Semantic columns (growth vs. decline) may use `#059669` / `#E11D48` **only when the color encodes data meaning**.

**Why:** Chart.js cannot resolve CSS variables, so the palette must be literal. Multi-hue palettes re-introduce the "every series gets its own color" dashboard aesthetic that the single-accent discipline exists to prevent.

---

## Rule T5: Icon Library Lock

**Forbidden:** icons from packs other than `tabler-outline` (fallback: `tabler-filled`). Mixing multiple icon styles on one slide.

**Correct:** placeholder form processed by `finalize_svg.py`:

```xml
<use data-icon="tabler-outline/<name>"
     x="..." y="..." width="..." height="..."
     stroke="currentColor" stroke-width="2" />
```

**Why:** Mixing icon packs (outline + filled, line + glyph) is a dead giveaway of AI composition. A single family carries the visual through the whole deck.

---

## Rule T6: Voice & GM Tone Lock

**Forbidden phrases in GM and speaker notes:**
- 여러분
- 우리는
- 함께해요

**Required tone:**
- Register: Korean lecture / report
- Point of view: third-person institutional
- Tone: editorial, analytical, declarative

**GM composition hint:** One declarative sentence stating the so-what / takeaway. Never a restatement of the page title. Korean-first, ≤30 chars ideal.

**Why:** The GM line is the editorial contract between slide and audience. Tone drift is the fastest path to "AI-generated" smell; it's also the easiest to accidentally slip into via marketing-style filler.

---

## Rule T7: Radius Discipline

**Forbidden:** ad-hoc `rx="<arbitrary>"` values on `<rect>` elements.

**Allowed radius values** (in px):

| Name | Value | Usage |
|------|-------|-------|
| `xs` | 4 | chip, tight badge |
| `sm` | 8 | small callout, inline tag |
| `md` | 12 | default card |
| `lg` | 12 | hero card |
| `xl` | 20 | large container |
| `pill` | 9999 | fully rounded pill |

**Why:** Mixing radii within a deck (12px card next to 6px card next to 16px card) breaks the rhythm. The scale above is the only valid set.

---

## Rule T8: Stroke Width Discipline

**Allowed stroke widths:**

| Role | Value (px) | Usage |
|------|------------|-------|
| icon | 2 | line-art icons |
| divider | 1 | default structural dividers |
| emphasis | 2 | accent rule, highlight underline |

**Forbidden:** hairline strokes (<1px), display-weight strokes (>3px), or decorative dashed/dotted patterns.

**Why:** Stroke inconsistency is the other half of radius discipline. Together they set the deck's mechanical precision; drifting from these values is visible at a glance.

---

<!-- Rendered by render_anti_slop_theme.py from theme-active.json -->
