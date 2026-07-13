# slide-svg Integration

How chart-design plugs into the slide-svg pipeline: token flow, embedding
contract, rhetorical-role mapping, and theme-change behavior.

## 1. Token flow (no hardcoded style, by construction)

```
theme-init --activate <preset>
   └─▶ slide/references/theme-active.json     (render copy of the active theme)
          └─▶ chartlib/tokens.py resolve_style()   (read at every render)
                 └─▶ ChartStyle contract → renderers
```

- **Single source**: `slide/references/theme-active.json` — the same file every
  slide-svg reference doc is rendered from. chart-design reads it at RENDER
  time; nothing is cached or copied into this skill.
- **Contract**: token names follow
  `theme-init/references/token-contract.json` v1. chart-design consumes:
  `colors.*` (bg, surface, surface-alt, text, text-secondary, text-tertiary,
  border, border-strong, accent, accent-soft, accent-ink, positive/negative/
  warning + softs), `typography.font-chain` + role scales (display-sm, headline,
  title, body, caption, label), `radius.*`, `stroke.*`, `spacing.*`,
  `surface.card_style`, `palette_mode`.
- **Series palette** (anti-slop-theme.md Rule T4): single-accent opacity ladder
  `(accent, 0.85 / 0.60 / 0.40 / 0.25)` emitted as `fill="<accent hex>"` +
  `fill-opacity` — every hex in output is a literal theme-palette hex, so
  `svg_quality_checker.py`'s off-theme scan stays green. Semantic
  positive/negative/warning appear only where color encodes data meaning
  (waterfall deltas, KPI deltas).
- **Failure mode**: missing/contract-violating theme → `TokenResolutionError`
  (exit 3). By design there is NO default fallback — fix the theme via
  theme-init; never hand-patch colors into a chart.

## 2. Embedding contract (Executor)

1. Decide the chart region on the 1280×720 canvas — typically below the
   headline block: x 60–1220, y ≈ 190–660 (safe area: x 56–1224, y 40–680).
2. Write the spec with that region's `width`/`height`.
3. Render with `--pos X,Y` — coordinates are **baked into the fragment**
   (no wrapper transform; the quality checker's regex text scanner cannot
   resolve ancestor transforms, so absolute coords keep safe-area and overlap
   checks accurate).
4. Paste the `<g id="chart_…" data-chart-type="…">` fragment into the slide
   SVG body. The `<g id>` satisfies the mandatory element-grouping rule and
   doubles as the animation anchor.
5. Charts assume the slide `bg` behind them — don't place fragments on top of
   accent-colored bands. On `surface` cards the ladder still reads correctly.
6. **Takeaway adjacency** (chart-rhetorical-roles.md styling lock): every chart
   slide pairs the chart with a takeaway card/line — 1 metric + 1 trend
   annotation + 1 contextual line. The chart never stands alone.
7. Multiple fragments on one slide: keep ≥24px between fragment bounding boxes
   (label gutters extend slightly beyond the declared region).

Post-processing: fragments pass `finalize_svg.py` and both converter modes
(`svg_to_pptx.py` native + SVG-reference) unchanged — validated end-to-end.
`<text>` elements survive as editable DrawingML runs with `font-chain` intact.

## 3. `chart_strategy` (slide-plan) → chart-design type

`chart-rhetorical-roles.md` stays the SSOT for WHICH rhetorical role a slide
carries; this table maps each role to the renderer that implements it:

| `chart_strategy` | Primary type | Alternates (data-shape permitting) |
|---|---|---|
| `growth-trend` | `line` | `area` (volume emphasis), `bar` (annual buckets), `combo` (2 co-moving metrics) |
| `forecast` | `line` (split series: actual + projected) | — render two series; mark the break with a slide-level annotation |
| `structural-break` | `line` + slide-level annotation rule | `waterfall` (decomposed change), `bullet` (before/after pairs) |
| `focus-comparison` | `bar` / `horizontal_bar` with `options.focus` | `bullet` (vs target), `grouped_bar` (multi-period) |
| `distribution` | `scatter` | `heatmap` (two categorical axes), `bar` (histogrammed buckets) |
| `quadrant` | (layout template `matrix_2x2`, not chart-design) | `scatter` when both axes are numeric |
| `priority-matrix` | `heatmap` | — |
| `split-segment` | `donut` / `pie` (≤5) | `stacked_bar` / `stacked_bar_100` (across groups), `treemap` (6–12) |
| `funnel` | `funnel` | `stacked_bar` (when stages don't narrow) |
| `custom` | judgment via SKILL.md §1 | `radar`, `gauge`, `kpi_cards`, `progress`, `waterfall`, `combo` |

Boundary notes:
- KPI/gauge/progress slides are usually `data`-family stat layouts, not
  "chart slides" — no `chart_strategy` required to use them.
- Non-numeric structure (process/org/venn/mind-map) is NOT chart-design's job —
  that's `diagram-design` / layout templates via `lead_type: diagram`.

## 4. Theme changes

Charts are pure functions of (spec, active theme). After
`init_theme.py --activate <preset>`:

1. Keep each deck's spec JSONs alongside the project (specs are the source of
   truth for the numbers — SVGs are derived artifacts).
2. Re-render every chart spec and re-paste fragments (or re-run the deck's
   build step if the project scripted it).
3. Refresh skill examples: `python3 .claude/skills/chart-design/scripts/build_examples.py`
   (also the quickest smoke test that the new theme satisfies the contract).

No chart-design file changes are ever needed for a theme swap — if a swap
seems to require one, the theme violates the token contract; fix it in
theme-init, not here.

## 5. Relationship to `templates/charts/` (static library)

The 52 static templates remain the browsing/selection REFERENCE for what a
finished visualization looks like; chart-design is the data-driven RENDERER
that computes real geometry from real numbers for the 21 quantitative types.
When a slide needs one of those 21 types with actual data, render it here
instead of hand-adapting the static template — hand-adapted geometry is where
mis-scaled bars and wrong percentages come from. Types outside the 21
(sankey, gantt, org chart, SWOT, …) still follow the template library path.
