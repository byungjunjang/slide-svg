<!-- Rendered from skeleton.tpl.md by render_prompts.py on /theme-init. Never hand-edit skeleton.md — edit skeleton.tpl.md. -->
# HTML Skeleton Template

> Every `/slide` output MUST start from this skeleton.
>
> The colors, font chain, weights, and accent tints in `:root` below are the
> **active theme** tokens (rendered from `theme-active.json`) — NOT literal jangpm
> values. A `/theme-init` swap re-renders them.

## Complete Template

```html
<!DOCTYPE html>
<html lang="<!-- LANGUAGE: ko, en, ja, zh -->">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title><!-- TITLE --></title>
  <!-- Font: active theme chain (Pretendard, 'Apple SD Gothic Neo', 'Malgun Gothic', Arial, sans-serif). The chain ends in a
       generic fallback, so the preview degrades gracefully when the primary font isn't
       installed/loaded in-browser. The exported PPTX bundles the primary font separately. -->

  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/reveal.css">

  <!-- Optional CDN libraries — add only if the deck uses that feature -->
  <!-- Highlight.js: <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/highlight.js@11.9.0/styles/github-dark.min.css"><script src="https://cdn.jsdelivr.net/npm/highlight.js@11.9.0/lib/highlight.min.js"></script> -->
  <!-- Mermaid: <script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script> -->

  <style>
    /* === RESET === */
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    /* === CSS CUSTOM PROPERTIES === */
    :root {
      /* Colors — active theme tokens (rendered from theme-active.json) */
      --bg: #FAFAF9;
      --surface: #FFFFFF;
      --text: #1A1A1A;
      --text-secondary: #6B7280;
      --accent: #4633E3;
      --accent-soft: #E8E5FC;
      --border: #E5E7EB;

      /* Semantic */
      --positive: #059669;
      --positive-soft: #ECFDF5;
      --negative: #E11D48;
      --negative-soft: #FFF1F2;
      --warning: #D97706;
      --warning-soft: #FFFBEB;

      /* Typography — font chain + weights from tokens; rem sizes are a preview scale */
      --font-sans: Pretendard, 'Apple SD Gothic Neo', 'Malgun Gothic', Arial, sans-serif;
      --fs-display: 3rem;
      --fs-display-sm: 2.5rem;
      --fs-headline: 2rem;
      --fs-title: 1.15rem;
      --fs-body: 0.95rem;
      --fs-caption: 0.8rem;
      --fw-display: 800;
      --fw-headline: 700;
      --fw-title: 600;
      --fw-body: 400;
      --fw-caption: 500;

      /* Spacing (8px grid) */
      --space-1: 0.25rem;
      --space-2: 0.5rem;
      --space-3: 0.75rem;
      --space-4: 1rem;
      --space-5: 1.25rem;
      --space-6: 1.5rem;
      --space-8: 2rem;
      --space-10: 2.5rem;
      --space-12: 3rem;
      --space-14: 3.5rem;
      --space-16: 4rem;

      /* Card */
      --card-padding: var(--space-6);
      --card-gap: var(--space-6);
      --card-radius: 0.75rem;
    }

    /* === REVEAL.JS OVERRIDES === */
    .reveal {
      font-family: var(--font-sans);
      font-size: var(--fs-body);
      font-weight: var(--fw-body);
      color: var(--text);
    }
    .reveal .slides { text-align: left; }
    .reveal .slides section {
      padding: var(--space-14);
      padding-bottom: var(--space-16);
      height: 720px;
      width: 1280px;
      display: flex;
      flex-direction: column;
      gap: var(--space-6);
      background: var(--bg);
    }
    /* Override Reveal.js's display:block on .present to keep flex layout */
    .reveal .slides > section.present,
    .reveal .slides > section > section.present {
      display: flex !important;
    }
    /* Reveal.js v5 scroll mode override (mobile):
       reveal.css injects `.reveal-viewport.reveal-scroll .scroll-page section { display: block !important }`
       with specificity (0,3,1) — higher than our .reveal .slides section (0,2,1).
       Matching the same selector in this later-declared stylesheet wins via source order. */
    .reveal-viewport.reveal-scroll .scroll-page section {
      display: flex !important;
      flex-direction: column;
      gap: var(--space-6);
    }
    /* Title, section divider, closing slides: fully centered */
    .slide-centered {
      justify-content: center;
    }
    /* Content slides: title at top, body vertically centered in remaining space */
    .slide-body {
      flex: 1;
      display: flex;
      flex-direction: column;
      justify-content: center;
      gap: var(--space-6);
      min-height: 0;
    }

    /* === TYPOGRAPHY === */
    .display { font-size: var(--fs-display); font-weight: var(--fw-display); line-height: 1.08; letter-spacing: -0.03em; color: var(--text); }
    .headline { font-size: var(--fs-headline); font-weight: var(--fw-headline); line-height: 1.2; letter-spacing: -0.02em; color: var(--text); }
    .title { font-size: var(--fs-title); font-weight: var(--fw-title); line-height: 1.3; color: var(--text); }
    .body { font-size: var(--fs-body); font-weight: var(--fw-body); line-height: 1.6; color: var(--text); }
    .caption { font-size: var(--fs-caption); font-weight: var(--fw-caption); line-height: 1.4; color: var(--text-secondary); }
    .text-secondary { color: var(--text-secondary); }
    .text-accent { color: var(--accent); }

    /* === CARD === */
    .card {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--card-radius);
      padding: var(--card-padding);
    }

    /* === UTILITIES === */
    .accent-badge {
      display: inline-flex;
      align-items: center;
      gap: var(--space-2);
      padding: var(--space-2) var(--space-4);
      background: var(--accent-soft);
      color: var(--accent);
      border-radius: 9999px;
      font-size: var(--fs-body);
      font-weight: var(--fw-title);
    }
    .accent-badge-sm {
      display: inline-flex;
      align-items: center;
      gap: var(--space-1);
      padding: var(--space-1) var(--space-3);
      background: var(--accent-soft);
      color: var(--accent);
      border-radius: 9999px;
      font-size: var(--fs-caption); /* 0.8rem — use for table cell tags and dense layouts */
      font-weight: var(--fw-title);
    }
    .stat-number {
      font-size: var(--fs-display-sm); /* 2.5rem — use for hero KPI values */
      font-weight: var(--fw-display);
      color: var(--accent);
      line-height: 1;
    }
    .stat-number-sm {
      font-size: var(--fs-headline); /* 2rem — use for chart callout values when 3+ numbers per slide */
      font-weight: var(--fw-display);
      color: var(--accent);
      line-height: 1;
    }
    .icon {
      width: 20px;
      height: 20px;
      stroke: currentColor;
      fill: none;
      stroke-width: 2;
      stroke-linecap: round;
      stroke-linejoin: round;
    }
    .icon-lg { width: 32px; height: 32px; }

    /* === GRID HELPERS === */
    .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: var(--card-gap); }
    .grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: var(--card-gap); }
    .grid-4 { display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: var(--card-gap); }
    .flex-col { display: flex; flex-direction: column; }
    .flex-row { display: flex; flex-direction: row; }
    .gap-2 { gap: var(--space-2); }
    .gap-3 { gap: var(--space-3); }
    .gap-4 { gap: var(--space-4); }
    .gap-6 { gap: var(--space-6); }
    .items-center { align-items: center; }
    .text-center { text-align: center; }
    .text-left { text-align: left; }
    .italic { font-style: italic; }
    .fs-display-sm { font-size: var(--fs-display-sm); }
    .mt-auto { margin-top: auto; }

    /* === AGENDA ITEM === */
    .agenda-item {
      display: flex;
      align-items: center;
      gap: var(--space-4);
      padding: var(--space-4) var(--space-6);
      border-bottom: 1px solid var(--border);
    }
    .agenda-item:last-child { border-bottom: none; }
    .agenda-item-past { opacity: 0.5; }
    .agenda-item-current {
      background: var(--accent-soft);
      border-left: 3px solid var(--accent);
    }
    .agenda-item-current .title { font-weight: var(--fw-title); }

    /* === LABEL CAPTION (uppercase taxonomy marker) === */
    .label-caption {
      font-size: var(--fs-caption);
      font-weight: var(--fw-title);
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-secondary);
    }

    /* === STAT TREND === */
    .trend-positive { color: var(--positive); }
    .trend-negative { color: var(--negative); }

    /* === GOVERNING MESSAGE === */
    .gm {
      position: absolute;
      bottom: var(--space-6);
      left: var(--space-14);
      right: var(--space-14);
      font-size: var(--fs-body);
      font-weight: var(--fw-headline);
      color: var(--text-secondary);
      text-align: center;
    }

    /* === HERO QUOTE === */
    .hero-quote {
      background: var(--accent-soft);
      border: 1px solid var(--border);
      border-radius: var(--card-radius);
      padding: var(--space-8);
    }

    /* === IMAGE === */
    .slide-image {
      max-width: 100%;
      height: auto;
      border-radius: var(--card-radius);
      object-fit: contain;
    }

    .text-highlight-strong {
      background: var(--accent-soft);
      padding: var(--space-1) var(--space-2);
      border-radius: 4px;
      font-weight: var(--fw-title);
      color: var(--accent);
    }

    /* === COMMAND TAG === */
    .cmd-tag {
      display: inline-flex;
      align-items: center;
      gap: var(--space-2);
      font-size: var(--fs-caption);
      line-height: 1;
    }
    .cmd-tag .cmd-label {
      padding: var(--space-1) var(--space-2);
      background: var(--accent);
      color: white;
      border-radius: 4px 0 0 4px;
      font-weight: var(--fw-title);
      text-transform: uppercase;
      letter-spacing: 0.03em;
    }
    .cmd-tag .cmd-value {
      padding: var(--space-1) var(--space-2);
      background: var(--surface);
      border: 1px solid var(--border);
      border-left: none;
      border-radius: 0 4px 4px 0;
      font-family: 'SF Mono', 'Fira Code', monospace;
    }

    /* === NUMBER BADGE === */
    .number-badge {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 28px;
      height: 28px;
      background: var(--accent);
      color: white;
      border-radius: 50%;
      font-size: var(--fs-caption);
      font-weight: var(--fw-display);
      flex-shrink: 0;
    }

    /* === INSIGHT BAR === */
    .insight-bar {
      margin-top: auto;
      padding: var(--space-5) var(--space-6);
      background: var(--accent-soft);
      border-radius: var(--card-radius);
      font-size: var(--fs-body);
      font-weight: var(--fw-body);
      color: var(--text);
      line-height: 1.5;
      text-align: center;
    }

    /* === MERMAID DIAGRAM FULL-BLEED === */
    .mermaid-container {
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 0;
    }
    .mermaid-container svg {
      max-width: 100%;
      max-height: 100%;
      height: auto;
    }

    /* === COMPARISON TABLE ENHANCEMENTS === */
    .col-recommended { background: var(--accent-soft); }
    .comparison-table thead th { padding: var(--space-4) var(--space-4); vertical-align: bottom; }
    .comparison-table tbody tr:nth-child(even) { background: var(--bg); }
    .comparison-verdict td { border-bottom: none; padding-top: var(--space-4); padding-bottom: var(--space-4); }

    /* === REPORT PRIMITIVES === */
    .section-sub { font-size: var(--fs-title); font-weight: var(--fw-headline); color: var(--text); display: flex; align-items: center; gap: var(--space-2); }
    .section-sub::before { content: '\203A'; color: var(--accent); font-size: 1.4em; font-weight: 700; }
    .rule { border: none; border-top: 1px solid var(--border); margin: 0; }
    .rule-accent { border: none; border-top: 2px solid var(--accent); margin: 0; }
    .summary-bar { display: flex; align-items: center; padding: var(--space-4) var(--space-6); background: var(--surface); border-radius: var(--card-radius); border: 1px solid var(--border); }
    .metric-row { display: flex; align-items: center; gap: var(--space-4); }
    .kpi-circle { display: flex; align-items: center; justify-content: center; width: 56px; height: 56px; border-radius: 50%; background: var(--surface); }
    .icon-xl { width: 48px; height: 48px; }
    .fw-title { font-weight: var(--fw-title); }
    .fw-headline { font-weight: var(--fw-headline); }
    .display-sm { font-size: var(--fs-display-sm); font-weight: var(--fw-display); line-height: 1; }

    /* === PILL BADGE === */
    .pill-badge { display: inline-flex; align-items: center; width: fit-content; padding: var(--space-1) var(--space-4); background: var(--accent); color: white; border-radius: 9999px; font-size: var(--fs-caption); font-weight: var(--fw-title); white-space: nowrap; }
    .pill-dark { background: var(--text); color: var(--bg); }
    .pill-positive { background: var(--positive); color: white; }
    .pill-warning { background: var(--warning); color: white; }
    .pill-negative { background: var(--negative); color: white; }

    /* === REPORT TABLE === */
    .report-table { width: 100%; border-collapse: collapse; font-size: var(--fs-body); }
    .report-table thead th { background: var(--accent-soft); color: var(--accent); font-weight: var(--fw-title); padding: var(--space-3) var(--space-4); text-align: center; }
    .report-table thead th:first-child { text-align: left; }
    .report-table tbody td { padding: var(--space-3) var(--space-4); border-bottom: 1px solid var(--border); text-align: center; }
    .report-table tbody td:first-child { text-align: left; }
    .col-highlight { border-left: 2px solid var(--accent); border-right: 2px solid var(--accent); background: rgba(70, 51, 227, 0.03); }

    /* === BEFORE/AFTER LABEL === */
    .before-after-label {
      display: inline-block;
      padding: var(--space-1) var(--space-3);
      background: var(--border);
      border-radius: 4px;
      font-size: var(--fs-title);
      font-weight: var(--fw-title);
      color: var(--text-secondary);
    }

    /* === NUMBERED ROW === */
    .numbered-row { display: flex; flex-direction: row; gap: var(--card-gap); }
    .numbered-row-card { flex: 1; display: flex; flex-direction: column; gap: var(--space-3); }

    /* === NUMBERED COLUMN === */
    .numbered-column { display: flex; flex-direction: column; gap: var(--space-4); }
    .numbered-column-item { display: flex; flex-direction: row; align-items: flex-start; gap: var(--space-4); }

    /* === TERMINAL WINDOW (code-explain) === */
    .terminal-window { border-radius: var(--card-radius); overflow: hidden; display: flex; flex-direction: column; }
    .terminal-titlebar { display: flex; align-items: center; gap: var(--space-2); padding: var(--space-3) var(--space-4) var(--space-4); background: #2d2d2d; }
    .terminal-dot { width: 12px; height: 12px; border-radius: 50%; flex-shrink: 0; }
    .terminal-dot-red { background: #FF5F57; }
    .terminal-dot-yellow { background: #FFBD2E; }
    .terminal-dot-green { background: #28C840; }
    .terminal-window pre { flex: 1; margin: 0; background: #000000; padding: var(--space-4); }
    .terminal-window pre code { border-radius: 0 !important; background: #000000 !important; color: #e6edf3 !important; padding: 0 !important; }

    /* === PROCESS FLOW === */
    .process-step { flex: 1; background: var(--surface); border: 1px solid var(--border); border-radius: var(--card-radius); padding: var(--space-4); }
    .process-arrow { flex-shrink: 0; width: 32px; height: 32px; stroke: var(--text-secondary); fill: none; stroke-width: 2; stroke-linecap: round; stroke-linejoin: round; }

    /* === CODE === */
    pre { margin: 0; }
    pre code { font-family: 'SF Mono', 'Fira Code', monospace; font-size: 0.85rem; line-height: 1.5; border-radius: var(--card-radius); padding: var(--space-4) !important; }

    /* === CHECKLIST === */
    .checklist-item { display: flex; align-items: center; gap: var(--space-3); padding: var(--space-3) 0; border-bottom: 1px solid var(--border); }
    .checklist-item:last-child { border-bottom: none; }

    /* === ADDITIONAL PATTERN CSS (add as needed) === */

    /* === PRINT CSS === */
    @media print {
      .reveal .slides section { page-break-after: always; }
    }
  </style>
</head>
<body>
  <div class="reveal">
    <div class="slides">

      <!-- SLIDES GO HERE -->
      <!-- Every <section> MUST include data-pattern="{pattern-name}" attribute -->

    </div>
  </div>

  <script src="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/reveal.js"></script>
  <!-- INITIALIZATION SCRIPTS -->
  <script>
    var deck = Reveal.initialize({
      center: false,
      width: 1280,
      height: 720,
      margin: 0,
      hash: true,
      transition: 'none',
      controls: false,
      progress: true,
      navigationMode: 'linear',
      view: 'slide'
    });
  </script>
</body>
</html>
```

## Key Differences from visualize skeleton

- No theme toggle (light mode only)
- No menu/navigation plugins
- No animations or transitions
- No html-to-image dependencies
- Reveal.js (1280×720 slides) instead of scrollable viewport
- Single file output (no build pipeline)

## Font

Decks use the active theme font chain: `Pretendard, 'Apple SD Gothic Neo', 'Malgun Gothic', Arial, sans-serif`. The chain
ends in a generic fallback, so the in-browser preview degrades gracefully when the
primary font isn't installed/loaded. The exported PPTX bundles the primary font separately.

## Print CSS

Each `<section>` gets `page-break-after: always` for PDF export via browser print.
