# Chart Rhetorical Roles — 9 Vocabulary × charts_index.json Mapping

> **Purpose:** Bridge between `slide-plan`'s deck-design vocabulary (rhetorical) and `/slide` Executor's implementation library (technical).
> **Authority:** This file is the SSOT for `chart_strategy` values in `slide_plan.json`. Executor consults this map to pick a concrete template from `templates/charts/charts_index.json`.
> **Adapted from:** internal slide-plan design guide §Layer 2 (mckinsey-pptx column-chart 4-way split + extended palette).

---

## How `slide-plan` writes `chart_strategy`

```json
{
  "slide_number": 7,
  "chart_strategy": "growth-trend",
  "chart_takeaway": "MAU 18개월 연속 두 자릿수 성장. 단일 채널 의존도 감소가 주효.",
  ...
}
```

`slide-plan` chooses **one of the 10 values** below (9 named + `custom`). `/slide` Executor consults the **Implementation column** to pick the actual SVG template from `charts_index.json`.

---

## Canonical mapping (10 values)

### 1. `growth-trend` — single metric over time

| | Value |
|---|---|
| **Use when** | one metric's trajectory matters (revenue, MAU, NPS, retention curve) |
| **Information shape** | continuous time axis × 1 series |
| **Primary** (charts_index.json) | `line_chart` |
| **Alt** | `area_chart`, `bar_chart` (annual buckets), `dual_axis_line_chart` (when 2 metrics share a story) |
| **Layout family** | `data` |
| **Takeaway hint** | name the inflection or the headline rate (% YoY) |
| **Reject** when content has < 4 time points (use a hero stat instead) |

### 2. `forecast` — past actuals + future projection

| | Value |
|---|---|
| **Use when** | story crosses an "as of today" line — past observed + future modeled |
| **Information shape** | continuous time axis × 1–2 series, with a visual break separating actual from projection |
| **Primary** | `line_chart` (right portion dashed, lighter opacity) |
| **Alt** | `gantt_chart`, `timeline`, `roadmap_vertical` |
| **Layout family** | `data` (or `process` for milestone-led narratives) |
| **Takeaway hint** | name the projected milestone year + value |
| **Required visual cue** | vertical break line + "Today" annotation between actual and forecast |

### 3. `structural-break` — growth rate inflection

| | Value |
|---|---|
| **Use when** | the story is a *change in slope* — pre-COVID vs post-COVID, before-after intervention |
| **Information shape** | continuous time axis × 1 series, with annotation calling out the break |
| **Primary** | `line_chart` (with vertical annotation rule + segment-CAGR labels) |
| **Alt** | `waterfall_chart` (when decomposing the break), `dumbbell_chart` (before/after pairs) |
| **Layout family** | `data` |
| **Takeaway hint** | name the inflection cause + the slope change |

### 4. `focus-comparison` — categorical with one hero

| | Value |
|---|---|
| **Use when** | comparing 3–8 categories where one is the answer / focus |
| **Information shape** | discrete categories × 1 metric, one bar accent-colored, rest grayscale |
| **Primary** | `bar_chart`, `horizontal_bar_chart` (long labels) |
| **Alt** | `dumbbell_chart` (paired comparison), `bullet_chart` (target vs actual) |
| **Layout family** | `data` |
| **Takeaway hint** | "X leads / lags Y by Z%" |
| **Required visual cue** | the focus bar uses `--accent`, others use `--text-secondary` |

### 5. `distribution` — spread / scatter / density

| | Value |
|---|---|
| **Use when** | the shape of the data matters more than any single value (clusters, outliers, spread) |
| **Information shape** | 2D continuous, points or buckets |
| **Primary** | `scatter_chart`, `bubble_chart`, `heatmap_chart`, `box_plot_chart` |
| **Alt** | `bar_chart` (when histogrammed) |
| **Layout family** | `data` |
| **Takeaway hint** | name the cluster or the outlier; do not list individual points |

### 6. `quadrant` — 2×2 strategic positioning

| | Value |
|---|---|
| **Use when** | classifying items along 2 axes (importance × urgency, growth × share, capability × demand) |
| **Information shape** | 2×2 grid with axis labels, items placed by position |
| **Primary** | `matrix_2x2` |
| **Alt** | `swot_analysis`, `comparison_table` (2×2) |
| **Layout family** | `data` (or `compare` when only 2–4 items in cells) |
| **Takeaway hint** | name the cell that contains the recommendation |
| **Visual lock** | grid lines `--border`, axis labels `.label` (uppercase 12.8/600) |

### 7. `priority-matrix` — 3×3 ranked classification

| | Value |
|---|---|
| **Use when** | finer-grain ranking than 2×2 — RICE scores, severity × frequency, effort × impact bands |
| **Information shape** | 3×3 grid with intensity shading |
| **Primary** | `matrix_2x2` (extended to 3×3 via cell duplication), `heatmap_chart` (numeric) |
| **Alt** | `pareto_chart` (when sortable), `fishbone_diagram` (when causal) |
| **Layout family** | `data` |
| **Takeaway hint** | name the top-priority cell + the count of items in it |

### 8. `split-segment` — composition / share

| | Value |
|---|---|
| **Use when** | "what makes up the total" — market share, expense breakdown, traffic source mix |
| **Information shape** | 1 total decomposed into ≤ 6 parts (more parts = treemap or table) |
| **Primary** | `donut_chart`, `pie_chart` (≤ 6 segments) |
| **Alt** | `stacked_bar_chart`, `stacked_area_chart` (across time), `treemap_chart` (≤ 12 hierarchical), `pyramid_chart` (when ordered/hierarchical) |
| **Layout family** | `data` |
| **Takeaway hint** | name the dominant segment + its share, OR the surprising outlier |
| **Reject** when segments < 3 (use a single hero stat) or > 12 (use table) |

### 9. `funnel` — staged narrowing

| | Value |
|---|---|
| **Use when** | conversion / drop-off / pipeline / TAM-SAM-SOM |
| **Information shape** | sequential stages, each smaller than the previous, conversion % between |
| **Primary** | `funnel_chart` |
| **Alt** | `sankey_chart` (when flow has multiple endpoints), `pyramid_chart` (when hierarchical) |
| **Layout family** | `data` (or `process` if methodology-led) |
| **Takeaway hint** | name the worst-conversion stage + the absolute drop |

### 10. `custom` — fallback

| | Value |
|---|---|
| **Use when** | none of the 9 cleanly fit |
| **Required field** | `chart_takeaway` MUST also describe what visual was chosen and why (free text), so Executor can still implement it |
| **Examples that go to `custom`** | radar (multi-axis capability assessment), org chart, gantt, Venn, mind map, hub-and-spoke, fishbone, isometric stairs |

If `custom` is used > 30% of chart slides in a deck, that's a signal the rhetorical vocabulary needs extension. File a follow-up to add the missing role.

---

## Reverse lookup — chart template → role

Use this to validate post-hoc when reading existing decks or to disambiguate when several roles seem to fit.

| `charts_index.json` template | Most likely `chart_strategy` |
|---|---|
| `line_chart` / `area_chart` | `growth-trend`, `forecast`, `structural-break` |
| `dual_axis_line_chart` | `growth-trend` (when 2 metrics co-move) |
| `bar_chart` / `horizontal_bar_chart` | `focus-comparison` |
| `grouped_bar_chart` | `focus-comparison` (multi-period) |
| `stacked_bar_chart` / `stacked_area_chart` | `split-segment` |
| `pie_chart` / `donut_chart` / `treemap_chart` | `split-segment` |
| `bullet_chart` | `focus-comparison` (target vs actual) |
| `dumbbell_chart` / `butterfly_chart` | `focus-comparison`, `structural-break` (before-after) |
| `waterfall_chart` | `structural-break` (decomposed change) |
| `funnel_chart` / `sankey_chart` | `funnel` |
| `pyramid_chart` | `split-segment` (hierarchical), `funnel` (when narrowing) |
| `scatter_chart` / `bubble_chart` | `distribution` |
| `heatmap_chart` / `box_plot_chart` | `distribution` |
| `matrix_2x2` | `quadrant`, `priority-matrix` |
| `swot_analysis` / `porter_five_forces` | `quadrant` (strategic) |
| `pareto_chart` | `priority-matrix`, `focus-comparison` |
| `radar_chart` | `custom` (capability) |
| `kpi_cards` / `gauge_chart` / `progress_bar_chart` | `custom` (single-metric KPI — usually NOT a chart slide; use `data` family stats-dashboard instead) |
| `gantt_chart` / `timeline` / `roadmap_vertical` | `forecast`, `process` family non-chart |
| `process_flow` / `numbered_steps` / `chevron_process` / `cycle_diagram` / `snake_flow` | `process` family — NOT a `chart_strategy`; these go in `recommended_layout_family: process` |
| `org_chart` / `mind_map` / `hub_spoke` / `fishbone_diagram` / `venn_diagram` / `sector_diagram` / `concentric_circles` / `isometric_stairs` | `custom` (relational / hierarchical) |

> **Important boundary:** `process_flow` and friends are **layouts**, not charts. They live in `recommended_layout_family: process`, not `chart_strategy`. Use `chart_strategy` only when the slide has a numeric / quantitative payload.

---

## Validation rules (enforced by `validate_plan.py`)

1. If `chart_strategy` is set, `chart_takeaway` MUST be non-empty (Layer 1 R2).
2. If `chart_strategy == "custom"`, `chart_takeaway` MUST also describe the chosen visual (Executor needs the cue).
3. `chart_strategy` MUST appear only on slides whose `recommended_layout_family == "data"`. (`process` family uses `process_flow`-style layouts, not charts.)
4. If the deck has > 30% `custom` chart strategies, validator emits a warning suggesting vocabulary extension.

---

## Jangpm-specific styling lock (applied by `/slide` Executor)

Regardless of which template is chosen:

- **Palette:** single-accent opacity ladder `rgba(70, 51, 227, 0.85 / 0.60 / 0.40 / 0.25)`. Multi-hue is forbidden (anti-slop T4).
- **Semantic exception:** growth in `--positive`, decline in `--negative`, only when color encodes data meaning.
- **Annotations:** axis labels `--text-secondary` (12.8/500), data labels accent-colored only on the focus value.
- **No** drop shadows, 3D, gradient fills, glow, or legend chrome.
- **Required adjacency:** every chart slide pairs with a takeaway card holding 1 metric + 1 trend annotation + 1 contextual line.

> See `templates/layouts/jangpm/DESIGN.md` §8 for the full Jangpm chart treatment spec.

---

<!-- Hand-authored 2026-04-28 as Phase 0.2 of slide-plan introduction. -->
