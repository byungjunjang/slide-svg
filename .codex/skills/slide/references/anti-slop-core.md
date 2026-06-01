# Anti-Slop Reference (Core): Theme-Agnostic Structural Rules

Patterns that must never appear in generated slides **regardless of which theme is active**. For each rule: what is forbidden, what to use instead, and why.

> **Scope.** Core rules constrain structure, markup, and CSS discipline. Theme-specific enforcement (exclusive accent hex, font chain, voice, chart palette) lives in `anti-slop-theme.md`, which is regenerated from `theme-active.json` each time `/theme-init` runs.

---

## Rule 1: No Floating Gradient Orbs

**Forbidden:**
```css
.slide::before {
  content: '';
  position: absolute;
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, rgba(99,102,241,0.3), transparent);
  border-radius: 50%;
  top: -100px;
  left: -100px;
  filter: blur(60px);
}
```

**Correct alternative:**
```css
/* Title and section slides only */
.slide-title .slide-bg,
.slide-section .slide-bg {
  background-image: var(--bg-dots);
}
```

**Why:** Gradient orbs are visual noise that distract from content and render inconsistently across display environments.

---

## Rule 2: No Rainbow/Gradient Borders

**Forbidden:**
```css
.card {
  border: 2px solid;
  border-image: linear-gradient(135deg, #6366f1, #8b5cf6, #ec4899) 1;
}

.highlight-box {
  border: 3px solid transparent;
  background: linear-gradient(white, white) padding-box,
              linear-gradient(to right, #f97316, #eab308) border-box;
}
```

**Correct alternative:**
```css
.card {
  border: 1px solid var(--border);
}
```

**Why:** Gradient borders add visual complexity without communicating meaning, violating the principle that decoration must earn its place.

---

## Rule 3: No Headline Gradient Text

**Forbidden:**
```css
h1, h2, .headline {
  background: linear-gradient(135deg, #6366f1, #8b5cf6, #ec4899);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
```

**Correct alternative:**
```css
h1, h2 {
  color: var(--text);
}

.headline-accent {
  color: var(--accent);
}
```

**Why:** Gradient text is a dated effect that reduces readability and fails accessibility contrast requirements.

---

## Rule 4: No Hover Scale/TranslateY

**Forbidden:**
```css
.card:hover {
  transform: scale(1.05);
}

.list-item:hover {
  transform: translateY(-4px);
}
```

**Correct alternative:**
```css
/* Hover shadow change only — but note: slides are static, avoid hover entirely */
.card:hover {
  box-shadow: var(--shadow-md);
}
```

**Why:** Slides are presented content, not interactive UIs — hover animations create motion sickness risk and serve no communication purpose.

---

## Rule 5: No Glow Effects

**Forbidden:**
```css
.icon-wrapper {
  box-shadow: 0 0 20px rgba(99, 102, 241, 0.6),
              0 0 60px rgba(99, 102, 241, 0.3);
}

.button {
  box-shadow: 0 0 0 4px rgba(139, 92, 246, 0.4);
}
```

**Correct alternative:**
```css
.icon-wrapper {
  box-shadow: var(--shadow-md);
}
```

**Why:** Colored glow effects are stylistic excess that bleeds into surrounding content and undermines visual hierarchy.

---

## Rule 6: No Decorative Animations

**Forbidden:**
```css
@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

@keyframes pulse-glow {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; box-shadow: 0 0 30px var(--accent); }
}

.icon {
  animation: float 3s ease-in-out infinite;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
```

**Correct alternative:**
```css
/* No animation blocks. Static elements only. */
.icon {
  color: var(--accent);
}
```

**Why:** Animations in slide content are distracting, inaccessible, and add no informational value.

---

## Rule 7: No Decorative Partial Borders

**Forbidden:**
```css
.card {
  border-left: 4px solid var(--accent);
  border-top: none;
  border-right: none;
  border-bottom: none;
}

.feature-card {
  border-top: 3px solid #6366f1;
}
```

**Correct alternative:**
```css
/* Borders are structural dividers, not decoration */
.card {
  border: 1px solid var(--border);
}

/* Rule lines separate content zones — consistent weight, neutral color */
.content-zone + .content-zone {
  border-top: 1px solid var(--border);
  padding-top: var(--space-6);
}

/* Semantic emphasis allowed only when data meaning requires it */
.metric-negative {
  border-left: 3px solid var(--negative);
}
```

**Why:** In a report-style system, borders serve as structural dividers between content zones. Decorative partial borders (accent-colored left/top strips on cards) belong to SaaS card aesthetics and undermine the clean, document-like visual hierarchy.

---

## Rule 8: Avoid Inline Styles

**Forbidden:**
```html
<div style="background: #6366f1; padding: 16px; border-radius: 8px; color: white;">
  Content
</div>

<h2 style="font-size: 2.5rem; font-weight: 700; color: #1e293b;">
  Title
</h2>
```

**Correct alternative:**
```html
<!-- Use CSS variables + utility classes -->
<div class="card card-accent">
  Content
</div>

<h2 class="slide-title">
  Title
</h2>
```

**Why:** Arbitrary inline styles bypass the design system, making global updates impossible and producing inconsistent output.

**Allowed inline styles (exhaustive list):**
- Chart canvas container height: `<div style="height: 320px;">` (Chart.js requires fixed pixel height on parent)
- SVG attributes: `width`, `height`, `viewBox`, `stroke`, `fill`, `stroke-width` on `<svg>` / `<path>` elements
- Position callouts: `position: absolute; top: Xpx; left: Xpx;` on annotated image overlays (canonical pattern in `patterns.md`)
- Token-driven emphasis: `color: var(--accent);` or `color: var(--positive);` on individual `<span>` when no utility class exists
- `max-width` on text blocks: `style="max-width: 680px;"` when controlling line length for readability
- Grid column ratio overrides: `style="grid-template-columns: 2fr 1fr;"` for non-standard splits not covered by `.grid-2`

**Everything else is forbidden.** If you find yourself writing `style="background: ...; padding: ...;"`, create a CSS class instead.

**Self-check before saving:** Scan the entire HTML for `style="` attributes. Remove every instance that is not in the allowed list above. Use utility classes (`.text-left`, `.italic`, `.fs-display-sm`, `.trend-positive`, `.trend-negative`, `.agenda-item`, etc.) or CSS variables instead.

---

## Rule 9: No Hardcoded HEX Values in CSS

**Forbidden:**
```css
.heading {
  color: #1e293b;
}

.card {
  background: #f8fafc;
  border-color: #e2e8f0;
}

.accent-text {
  color: #6366f1;
}
```

**Correct alternative:**
```css
.heading {
  color: var(--text);
}

.card {
  background: var(--surface);
  border-color: var(--border);
}

.accent-text {
  color: var(--accent);
}
```

**Why:** Hardcoded values break theme switching and make design-system maintenance impossible.

---

## Rule 10: (Removed — text-only restriction no longer applies)

Well-structured text blocks with clear typographic hierarchy are valid visual modules in the report-style system. A slide with a heading, subheading, and a concise bulleted list does not need a card, icon, or chart to justify its existence.

---

## Rule 11: No Uncontrolled Text Density

**Forbidden:**
```html
<ul>
  <li>This is the first very long bullet point that goes on for multiple lines explaining everything in exhaustive detail without any line-length control</li>
  <li>Second bullet with additional explanation and context that exceeds what a slide should contain, running edge to edge</li>
  <li>Third fourth fifth sixth seventh eighth bullets all crammed in</li>
</ul>
```

**Correct alternative:**
```html
<!-- Report-style text blocks are acceptable when line length and density are controlled -->
<div class="text-block" style="max-width: 680px;">
  <p class="lead">Key insight stated in one sentence.</p>
  <ul>
    <li>Supporting point A — concise</li>
    <li>Supporting point B — concise</li>
    <li>Supporting point C — concise</li>
  </ul>
</div>

<!-- Or a two-column text layout for longer content -->
<div class="grid grid-2" style="gap: var(--gap);">
  <div class="text-block">
    <h3>Left column heading</h3>
    <p>Paragraph with controlled line length.</p>
  </div>
  <div class="text-block">
    <h3>Right column heading</h3>
    <p>Paragraph with controlled line length.</p>
  </div>
</div>
```

**Why:** The problem is not text itself but uncontrolled text — lines running the full 1280px width, 8+ bullets with no hierarchy, or paragraph blocks with no max-width. Report-style text with controlled line length (max ~680px or two columns) and clear heading hierarchy is readable and professional.

---

## Rule 12: No Inconsistent Spacing

**Forbidden:**
```css
.cards-container {
  display: flex;
  flex-wrap: wrap;
}

.card:nth-child(1) { margin: 8px; }
.card:nth-child(2) { margin: 12px 8px; }
.card:nth-child(3) { margin: 8px 16px; }
```

**Correct alternative:**
```css
.cards-container {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--gap);
  align-items: stretch;
}

.card {
  height: 100%;
}
```

**Why:** CSS Grid with uniform `gap` eliminates alignment math and guarantees consistent visual rhythm across all elements.

---

## Rule 13: No Decorative-Only Images

**Forbidden:**
```html
<!-- Image added purely for visual interest, not content -->
<div class="slide-content">
  <h2>System Architecture</h2>
  <img src="abstract-network.jpg" alt="decorative background" class="bg-decoration">
  <p>Our architecture uses microservices...</p>
</div>
```

**Correct alternative:**
```html
<!-- Images must directly explain or illustrate the content -->
<div class="slide-content">
  <h2>System Architecture</h2>
  <img src="architecture-diagram.png" alt="Three-tier architecture: client, API gateway, services layer">
  <p>Each service communicates through the API gateway...</p>
</div>
```

**Why:** Decorative images compete with content for attention and add file weight without adding understanding.

---

## Rule 14: No `position: relative` on Slide Sections

**Forbidden:**
```css
.reveal .slides section {
  position: relative;
}
```

**Correct alternative:**
```css
/* Do NOT set position on .reveal .slides section — Reveal.js manages it internally */
.reveal .slides section {
  /* position is controlled by Reveal.js (absolute) — never override */
}
```

**Why:** Reveal.js requires `position: absolute` on `<section>` elements to overlay slides and apply transforms for navigation. Setting `position: relative` causes all slides to stack vertically in normal document flow, making only the first (title) slide visible in the viewport while all other slides are pushed below.

---

## Rule 15: No Card-First Layouts

**Forbidden:**
```html
<!-- Defaulting to card grids when content doesn't need containment -->
<div class="grid grid-3">
  <div class="card">
    <span class="icon">📊</span>
    <h3>Point A</h3>
    <p>Short explanation</p>
  </div>
  <div class="card">
    <span class="icon">📈</span>
    <h3>Point B</h3>
    <p>Short explanation</p>
  </div>
  <div class="card">
    <span class="icon">📉</span>
    <h3>Point C</h3>
    <p>Short explanation</p>
  </div>
</div>
```

**Correct alternative:**
```html
<!-- Text blocks + rule lines as the primary layout tool -->
<div class="content-list">
  <div class="content-item">
    <h3>Point A</h3>
    <p>Short explanation</p>
  </div>
  <hr class="rule-line">
  <div class="content-item">
    <h3>Point B</h3>
    <p>Short explanation</p>
  </div>
  <hr class="rule-line">
  <div class="content-item">
    <h3>Point C</h3>
    <p>Short explanation</p>
  </div>
</div>

<!-- Cards are a secondary tool — use when content genuinely needs containment,
     e.g., metric callouts, comparison boxes, or visually distinct modules -->
```

**Why:** Card grids are a SaaS dashboard default. In a report-style system, text blocks separated by rule lines or whitespace are the primary layout. Cards should be reserved for content that genuinely benefits from visual containment (metrics, comparisons, callouts) — not used as the automatic wrapper for every group of items.

> **Related:** Rule 19 (No Card-Only Body Slides) enforces this principle specifically on body slides — see below.

---

## Rule 16: No `accent-soft` as Default Background

**Forbidden:**
```css
/* Coloring every card or section with accent-soft */
.card { background: var(--accent-soft); }
.highlight { background: var(--accent-soft); }
.section-intro { background: var(--accent-soft); }

/* Result: accent-tinted everything, no visual hierarchy */
```

**Correct alternative:**
```css
/* Default: surface backgrounds. Accent is rare and intentional. */
.card { background: var(--surface); }
.highlight { background: var(--surface); }

/* Max 1-2 accent events per slide — e.g., one key metric or one callout */
.key-callout {
  background: var(--accent-soft);
  border: 1px solid var(--border);
}
```

**Why:** Slides should work in black + white + gray first. When accent-soft is the default background for cards and sections, every element competes for attention and the slide loses hierarchy. Accent color should be a scarce resource — used to draw the eye to one or two focal points per slide, not applied uniformly. Exact accent event budget per theme lives in `anti-slop-theme.md`.

---

## Rule 17: No Decorative Semantic Colors

**Forbidden:**
```css
/* Using positive/negative/warning colors for decoration or eye flow */
.card:nth-child(1) { border-left: 3px solid var(--positive); }
.card:nth-child(2) { border-left: 3px solid var(--accent); }
.card:nth-child(3) { border-left: 3px solid var(--warning); }
.card:nth-child(4) { border-left: 3px solid var(--negative); }

/* Or coloring cards to create a "traffic light" visual pattern */
.feature-a { background: rgba(16, 185, 129, 0.1); }
.feature-b { background: rgba(245, 158, 11, 0.1); }
.feature-c { background: rgba(239, 68, 68, 0.1); }
```

**Correct alternative:**
```css
/* Semantic colors only when data meaning demands it */
.trend-positive { color: var(--positive); }  /* actual growth */
.trend-negative { color: var(--negative); }  /* actual decline */
.status-warning { color: var(--warning); }   /* actual risk */

/* For non-data items, use neutral styling */
.card {
  background: var(--surface);
  border: 1px solid var(--border);
}
```

**Why:** Positive (green), negative (red), and warning (amber) colors carry specific data meanings — growth, decline, risk. Using them as decorative palette to differentiate cards or create visual variety trains the audience to ignore semantic signals. In a report-style system, color must mean something or be absent.

---

## Rule 18: No SaaS Dashboard Aesthetics

**Forbidden:**
```html
<!-- Stat widget cards with big numbers and trend arrows -->
<div class="grid grid-4">
  <div class="card stat-widget">
    <span class="stat-label">Revenue</span>
    <span class="stat-value">$2.4M</span>
    <span class="trend-up">↑ 12%</span>
  </div>
  <div class="card stat-widget">...</div>
  <div class="card stat-widget">...</div>
  <div class="card stat-widget">...</div>
</div>

<!-- Colored icon badge systems -->
<div class="feature-card">
  <div class="icon-badge" style="background: var(--accent-soft);">
    <span class="icon">🔒</span>
  </div>
  <h3>Security</h3>
  <p>Enterprise-grade protection</p>
</div>
```

**Correct alternative:**
```html
<!-- Report-style metrics: clean table or labeled values -->
<table class="data-table">
  <tr><td>Revenue</td><td class="text-right">$2.4M</td><td class="trend-positive text-right">+12%</td></tr>
  <tr><td>Users</td><td class="text-right">84K</td><td class="trend-positive text-right">+8%</td></tr>
  <tr><td>Churn</td><td class="text-right">3.2%</td><td class="trend-negative text-right">+0.4%</td></tr>
</table>

<!-- Features as structured text, not badge cards -->
<div class="content-item">
  <h3>Security</h3>
  <p>Enterprise-grade protection with SOC 2 compliance.</p>
</div>
```

**Why:** Stat widgets, colored card grids, icon badge systems, and dashboard-like layouts are SaaS product UI patterns. Slides are communication documents, not dashboards. Present data in tables, charts, or structured text — not in miniature widget replicas that prioritize visual density over narrative clarity.

---

## Rule 19: No Card-Only Body Slides

> **Complementary to Rule 15 (No Card-First Layouts).** Rule 15 sets the general default — text blocks + rule lines as the primary layout vocabulary. Rule 19 enforces that default specifically on body slides where the regression failure is most common.

**Body slides** (slides with `page_family: body`) MUST contain at least one **non-card visual primitive** alongside any cards. Allowed non-card primitives include: `chart`, `table`, `diagram_flow`, `image`, `image_annotated`, `quote`, `code`, mini-bars, sparklines, donut/pie segments, timeline tracks.

**Forbidden** in a body slide:

```
[ headline ] + [ 1×3 metric_cards ] + [ GM ]
[ headline ] + [ 2×2 metric_cards ] + [ GM ]
[ accent display-sm headline ] + [ 2-column text cards ] + [ GM ]
```

These reduce the slide to "headline + cards" — a single visual primitive carrying the entire page. The result reads as a generic SaaS web page, not an editorial deck.

**Correct** body slide composition (one of these — the hybrid is the *default*, single-primitive is the *exception*):

```
[ headline ] + [ chart (60%) ] + [ side cards stack (40%) ] + [ takeaway band ] + [ GM ]
[ headline ] + [ comparison_table ] + [ adjacent mini cards ] + [ verdict row ] + [ GM ]
[ headline ] + [ definition (50%) ] + [ supporting chart/diagram (50%) ] + [ GM ]
[ headline ] + [ paired panels: viz + text-led ] + [ GM ]
[ headline ] + [ hero stat / display-sm ] + [ decomposition cards row ] + [ GM ]
```

See `templates/layouts/<theme>/DESIGN.md` §5.1 (Hybrid Pattern Catalog) for the canonical hybrid patterns this preset is calibrated to.

**Exempt slides:**
- `page_family: title` (cover) — single hero text composition allowed
- `page_family: chapter` (section dividers) — chapter number + title only
- `page_family: end` (closing / CTA) — Display + Display-sm + CTA card composition allowed

**Why:** A body slide whose only visual primitive is a card grid loses the editorial layering that distinguishes this preset from a generic dashboard. Cards are *supporting* primitives — they decorate, label, and decompose other primitives (charts, tables, definitions). When cards stand alone, the slide has no anchor.

**Detection heuristic:** if the slide's `<rect rx="12">` count exceeds 3 AND there is no `<polyline>`, `<path d=...>` (chart/diagram), `<table>`-equivalent (`<line>` grid + multi-row text), or `<image>` element, it almost certainly violates Rule 19.

**Repair:** introduce one of the hybrid patterns from DESIGN.md §5.1 by replacing the lowest-priority card with the appropriate non-card primitive. Often the card containing the "verdict" or "takeaway" can be replaced with a horizontal accent-soft band (still cardless visually because it spans the slide width).

---

## Rule 20: No Decorative Step-Flow / Process Chrome

> **Sibling to Rule 15 (No Card-First Layouts).** Where Rule 15 forbids the card grid as a default container, Rule 20 forbids the *step / process strip* as a default for non-sequential content.

**Forbidden** (a row of ordinal chips implying a sequence the content does not have):

```
[ 01 ▸ Discovery ] → [ 02 ▸ Analysis ] → [ 03 ▸ Delivery ]   ← but the three items are PARALLEL, not a process
```

In SVG terms: ≥3 congruent `<rect>` chips at a constant `Δx`, each carrying an ordinal badge (`01/02/03`, `1·2·3`) and joined by `→`/chevron/`snake_flow` arrows, used merely to enumerate points that have no time or causal order.

**Correct alternative:**

- If the items are **not** a real sequence → text blocks + rule lines (Rule 15), or a plain list. No numbers, no arrows.
- Reserve `numbered_steps` / `chevron_process` / `snake_flow` / `process_flow` for genuine processes (a temporal or causal axis the reader must follow in order).

**Why:** Arrows and `01/02/03` badges are a promise of sequence. Spending that chrome on parallel or unordered content is decoration masquerading as structure — it tells the audience "follow this order" when there is no order to follow.

**Detection heuristic (warn):** ≥3 congruent chips (same `width`/`height`, near-constant horizontal pitch) bearing ordinal labels or joined by arrow `<marker>`/`<path>`, with no accompanying time axis, date row, or causal connective in the copy → likely decorative step-flow.

---

## Rule 21: One Dominant Message, Text as Caption

A content slide makes **one** core assertion. The `.gm` line carries the so-what; the dominant **visual is the evidence**; the remaining text is a *caption* to that visual — not a second essay.

**Forbidden:**

```
[ headline A + 3 bullets ]   [ headline B + 3 bullets ]     ← two co-equal messages competing
[ headline ] + [ 6-bullet list running the full width ]     ← the slide became a document page
```

**Correct alternative:**

```
[ one headline assertion ]
[ dominant visual = evidence (chart / diagram / image / table) ]
[ ≤3 concise bullets or a one-line caption ]
[ GM ]
```

- **Max 3 supporting bullets**, each ideally ≤1 line (this tightens Rule 11's 4–5 ceiling for a single-message body slide). A fourth point means either the slide is doing two jobs (split it) or a bullet is not load-bearing (cut it).
- One headline-weight text block per slide beyond the title.

**The visual-evidence principle:** the governing message states the claim; the **dominant visual is its evidence** and should clearly lead the content area, with the text deliberately thin (caption, not essay).

**Reconciliation with `design-system.md` ("high content density" / "visually full").** Density means a **dominant visual carrying the page**, *not* dense text or stacked cards. "Visually full" = visually *dominant* (the evidence clearly leads the content area), with the text restrained. A slide can be visually rich and textually restrained at the same time — that is the target, not a contradiction.

**Why:** When the visual is the argument and the text is its caption, the so-what lands in one read. Two competing messages, or a wall of bullets, dilute the point and push the slide back toward a generic document.

**Detection heuristic (warn):** in the content area, >3 sibling bullet `<text>`/`<tspan>` rows, OR ≥2 headline-weight (`font-size ≥ 28`) text blocks beyond the page title, OR total body copy past a generous character budget → flag for "more than one message."

---

## Rule 22: Measured Whitespace & Top-Right Quiet Zone

On the fixed **1280×720** canvas, restraint is measurable.

- **Whitespace ≥ 30%.** At least ~30% of the canvas stays unpainted — outer margins, gutters between modules, and breathing room around the dominant visual. The outer content margin (≥56px, per the content-shell spec) is never crossed by primary content.
- **Top-right quiet zone.** The corner **x ≥ 1024, y ≤ 160** (a ~256×160 region) is kept clear of primary content — at most a small eyebrow/label or the page chrome lives there. It is the eye's entry/rest point.

**Forbidden:** edge-to-edge fills; content touching all four margins; a card, metric, or chart packed into the top-right corner; a slide whose painted elements blanket the canvas with no quiet region.

**Correct alternative:** let the dominant visual breathe inside the margins; group supporting text in one column; leave the top-right open.

**Reconciliation:** "visually full" (design-system) is satisfied by a *dominant* visual that clearly leads the content area (Rule 21) **plus** ≥30% whitespace as the breathing room around it — not by ~70%+ ink coverage. Full ≠ crowded.

**Why:** Whitespace is the editorial signal of confidence; a quiet corner gives the eye somewhere to enter and rest. A canvas painted corner-to-corner reads as a dashboard, not a considered argument.

**Detection heuristic (warn):** union bounding box of painted elements (exclude the background `<rect>`) covers >70% of `1280×720` → whitespace < 30% warn. Any `<rect>` / `<image>` / non-marker visual whose bbox intersects the top-right `x∈[1024,1280], y∈[0,160]` box → quiet-zone warn.

---

## Rule 23: Photographs Stand Alone as Evidence

A photographic `<image>` is **evidence shown at legible size**, never wallpaper behind text.

**Forbidden:**

```
<image .../>                 ← full-bleed photo
<text> headline over photo   ← text overlaid on the image
```

— a headline or body set on top of a photo; a photo dropped in at low opacity as a background; a thumbnail-sized decorative photo beside a wall of text.

**Correct alternative:** the photo occupies a dedicated region (≥~40% width) as the evidence; its caption/label sits **outside** the image bounding box (adjacent, not on top); the GM goes below. Text and image share the slide side-by-side, not stacked through each other.

**Why:** Text on a photograph harms legibility for both, and demotes the photograph from *evidence* to *decoration*. The image has to be readable **as** the argument (the visual-evidence principle: the visual is the evidence), which it cannot be with type sitting on it.

**Detection heuristic (warn):** any `<text>`/`<tspan>` whose anchor lies inside an `<image>`'s `x/y/width/height` bbox → text-on-photo warn. An `<image>` with bbox area < ~15% of canvas placed alongside heavy body copy → decorative-thumbnail warn.

---

## Production Principles

These rules apply to all JavaScript in slide files. They are theme-agnostic; palette-specific guidance lives in `anti-slop-theme.md`.

### Variable Declarations

Use `var` for top-level JS variables to prevent Temporal Dead Zone (TDZ) errors in slides:

```js
// Correct — var hoists to function scope, safe for slide execution order
var chartData = { ... };
var ctx = document.getElementById('myChart');

// Forbidden — let/const TDZ can cause ReferenceError if script order shifts
let chartData = { ... };
const ctx = document.getElementById('myChart');
```

### Disable Chart Animations

Set `Chart.defaults.animation = false` before any chart instantiation:

```js
// Correct
Chart.defaults.animation = false;

var ctx = document.getElementById('chart').getContext('2d');
var myChart = new Chart(ctx, { ... });

// Forbidden — animation plays during presentation, distracts audience
var myChart = new Chart(ctx, { ... }); // animation not disabled
```

### Chart Colors Must Be Literal rgba()

Use `rgba()` for chart dataset colors. Never use CSS variables in Chart.js config — Chart.js cannot resolve CSS variables at paint time:

```js
// Correct shape — use rgba literals
data: {
  datasets: [{
    backgroundColor: 'rgba(<r>, <g>, <b>, 0.8)',
    borderColor: 'rgba(<r>, <g>, <b>, 1)',
  }]
}

// Forbidden
data: {
  datasets: [{
    backgroundColor: 'var(--accent)',
    borderColor: 'var(--border)',
  }]
}
```

**The exact rgba values for the active theme's accent** (including the opacity ladder for multi-series charts) are specified in `anti-slop-theme.md`.

### Spacing

Use CSS Grid `gap` for all multi-element layouts. Never use margin hacks:

```css
/* Correct */
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--gap);
}

/* Forbidden */
.grid > * + * {
  margin-left: 16px;
}
.grid > *:nth-child(2) {
  margin-top: 0;
}
```
