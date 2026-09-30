<!-- Rendered from libraries.tpl.md by render_prompts.py on /theme-init. Never hand-edit libraries.md — edit libraries.tpl.md. The chart palette + font below are active-theme tokens, not literal jangpm values. -->
# Libraries Reference

## Reveal.js 5.x

### CDN
```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/reveal.css">
<script src="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/reveal.js"></script>
```

### Initialization
```js
var deck = Reveal.initialize({
  center: false,
  width: 1280,
  height: 720,
  margin: 0,
  hash: true,
  transition: 'none',
  controls: false,
  progress: true,
  navigationMode: 'linear'
});
```

### Structure
```html
<div class="reveal">
  <div class="slides">
    <section>...</section>
  </div>
</div>
```

---

## Chart.js 4.x

### CDN
```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
```

### Critical Rules
- MUST set `Chart.defaults.animation = false` immediately after the CDN script tag
- MUST set `Chart.defaults.font.size = 13` for readable axis labels at presentation distance
- MUST use `maintainAspectRatio: false` and `responsive: true` in every chart config — no exceptions, including secondary/tertiary charts on multi-chart slides
- MUST use `rgba()` for colors — CSS variables do NOT work inside Chart.js
- Canvas container must have a fixed height via its parent div (not on the canvas itself)

### Canonical Chart Init Snippet
Every chart in the deck MUST clone this options block. When a slide has multiple charts, each one independently includes `responsive: true` and `maintainAspectRatio: false`:
```js
Chart.defaults.animation = false;
Chart.defaults.font.size = 13;
```

### Minimal Bar Chart Example
```html
<div style="height: 300px;">
  <canvas id="myChart"></canvas>
</div>

<script>
Chart.defaults.animation = false;

const ctx = document.getElementById('myChart').getContext('2d');
new Chart(ctx, {
  type: 'bar',
  data: {
    labels: ['A', 'B', 'C'],
    datasets: [{
      label: 'Values',
      data: [10, 20, 15],
      // Single-accent opacity ladder — active theme accent (anti-slop Rule T4). Never multi-hue.
      backgroundColor: [
        'rgba(70, 51, 227, 0.85)',
        'rgba(70, 51, 227, 0.6)',
        'rgba(70, 51, 227, 0.4)'
      ]
    }]
  },
  options: {
    responsive: true,
    maintainAspectRatio: false
  }
});
</script>
```

---

## Mermaid 11.x

### CDN
```html
<script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
```

### Initialization (CRITICAL: Reveal.js compatibility)

Mermaid must render AFTER all slides are temporarily made visible. Without this, diagrams on non-active slides render as 16x16px broken SVGs because Mermaid's layout engine needs visible containers to measure dimensions.

```js
mermaid.initialize({ startOnLoad: false, theme: 'neutral' });

// Render Mermaid after Reveal.js is ready, with all slides temporarily visible
Reveal.on('ready', function() {
  var sections = document.querySelectorAll('.reveal .slides > section');
  var origStyles = [];
  sections.forEach(function(s, i) {
    origStyles[i] = { opacity: s.style.opacity, display: s.style.display, visibility: s.style.visibility };
    s.style.opacity = '1';
    s.style.display = 'flex';
    s.style.visibility = 'visible';
  });
  mermaid.run().then(function() {
    sections.forEach(function(s, i) {
      s.style.opacity = origStyles[i].opacity;
      s.style.display = origStyles[i].display;
      s.style.visibility = origStyles[i].visibility;
    });
  });
});
```

**NEVER use `startOnLoad: true`** with Reveal.js — it triggers before slides are laid out.
**NEVER call `mermaid.run()` inside `deck.then()`** without making all slides visible first.
**ALWAYS use `mermaid@11`** (not @10).

### Container
```html
<div class="mermaid">graph TD; A-->B;</div>
```

---

## Highlight.js

### CDN
```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/highlight.js@11.9.0/styles/github.min.css">
<script src="https://cdn.jsdelivr.net/npm/highlight.js@11.9.0/lib/highlight.min.js"></script>
```

### Initialization
```js
hljs.highlightAll();
```

### Code Block
```html
<pre><code class="language-xxx">...</code></pre>
```

---

## Lucide Icons

### Approach
Inline SVG — no CDN dependency required.

### Standard Attributes
```html
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <!-- paths here -->
</svg>
```

### Size Classes
```css
.icon    { width: 20px; height: 20px; }
.icon-lg { width: 32px; height: 32px; }
```

### Icon SVG Paths

**arrow-right**
```html
<path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>
```

**check**
```html
<path d="M20 6 9 17l-5-5"/>
```

**check-circle**
```html
<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><path d="m9 11 3 3L22 4"/>
```

**star**
```html
<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
```

**lightbulb**
```html
<path d="M15 14c.2-1 .7-1.7 1.5-2.5 1-.9 1.5-2.2 1.5-3.5A6 6 0 0 0 6 8c0 1 .2 2.2 1.5 3.5.7.7 1.3 1.5 1.5 2.5"/><path d="M9 18h6"/><path d="M10 22h4"/>
```

**zap**
```html
<path d="M4 14a1 1 0 0 1-.78-1.63l9.9-10.2a.5.5 0 0 1 .86.46l-1.92 6.02A1 1 0 0 0 13 10h7a1 1 0 0 1 .78 1.63l-9.9 10.2a.5.5 0 0 1-.86-.46l1.92-6.02A1 1 0 0 0 11 14z"/>
```

**brain**
```html
<path d="M12 5a3 3 0 1 0-5.997.125 4 4 0 0 0-2.526 5.77 4 4 0 0 0 .556 6.588A4 4 0 1 0 12 18Z"/><path d="M12 5a3 3 0 1 1 5.997.125 4 4 0 0 1 2.526 5.77 4 4 0 0 1-.556 6.588A4 4 0 1 1 12 18Z"/><path d="M15 13a4.5 4.5 0 0 1-3-4 4.5 4.5 0 0 1-3 4"/><path d="M17.599 6.5a3 3 0 0 0 .399-1.375"/><path d="M6.003 5.125A3 3 0 0 0 6.401 6.5"/><path d="M3.477 10.896a4 4 0 0 1 .585-.396"/><path d="M19.938 10.5a4 4 0 0 1 .585.396"/><path d="M6 18a4 4 0 0 1-1.967-.516"/><path d="M19.967 17.484A4 4 0 0 1 18 18"/>
```

**refresh-cw**
```html
<path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/><path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/><path d="M8 16H3v5"/>
```

**users**
```html
<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>
```

**chart-bar** (bar-chart-2)
```html
<line x1="18" x2="18" y1="20" y2="10"/><line x1="12" x2="12" y1="20" y2="4"/><line x1="6" x2="6" y1="20" y2="14"/>
```

**code**
```html
<polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/>
```

**layers**
```html
<path d="m12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83Z"/><path d="m22 17.65-9.17 4.16a2 2 0 0 1-1.66 0L2 17.65"/><path d="m22 12.65-9.17 4.16a2 2 0 0 1-1.66 0L2 12.65"/>
```

**shield**
```html
<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/>
```

**target**
```html
<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>
```

**trending-up**
```html
<polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/>
```

---

## Fonts

Use the active theme font chain (rendered from `theme-active.json`):

```css
--font-sans: Pretendard, 'Apple SD Gothic Neo', 'Malgun Gothic', Arial, sans-serif;
```

The chain ends in a generic fallback, so the in-browser preview degrades gracefully
when the primary font isn't installed/loaded. Do not add ad-hoc Google Fonts links or
language-specific font overrides — the chain already carries the fallbacks.

---

## HTML Preview Discipline

These rules apply only to the HTML preview (Reveal.js / Chart.js). SVG→PPTX slides carry no CSS, JavaScript, or Reveal.js, so `anti-slop-core.md` keeps the structural rules and lists Rules 8, 9, 14 as pointers here.

### Rule 8: Avoid Inline Styles

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

### Rule 9: No Hardcoded HEX Values in CSS

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


### Rule 14: No `position: relative` on Slide Sections

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


### Production Principles

These rules apply to all JavaScript in slide files. They are theme-agnostic; palette-specific guidance lives in `anti-slop-theme.md`.

#### Variable Declarations

Use `var` for top-level JS variables to prevent Temporal Dead Zone (TDZ) errors in slides:

```js
// Correct — var hoists to function scope, safe for slide execution order
var chartData = { ... };
var ctx = document.getElementById('myChart');

// Forbidden — let/const TDZ can cause ReferenceError if script order shifts
let chartData = { ... };
const ctx = document.getElementById('myChart');
```

#### Disable Chart Animations

Set `Chart.defaults.animation = false` before any chart instantiation:

```js
// Correct
Chart.defaults.animation = false;

var ctx = document.getElementById('chart').getContext('2d');
var myChart = new Chart(ctx, { ... });

// Forbidden — animation plays during presentation, distracts audience
var myChart = new Chart(ctx, { ... }); // animation not disabled
```

#### Chart Colors Must Be Literal rgba()

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

#### Spacing

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
