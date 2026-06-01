# Diagram Types (native-SVG bridge for /slide)

> Theme-agnostic bridge between the vendored `diagram-design` reference library
> (`.codex/skills/diagram-design/`) and the `/slide` native-DrawingML pipeline.
> When a slide's job is a **system / relationship / process** visual (not a Chart.js
> chart), pick a type here, obey its complexity budget + the single-accent focal rule,
> and emit native SVG per `references/shared-standards.md`. Colors and fonts resolve from
> the **active theme** (`references/design-system.md` / `theme-active.json`) — this file
> hardcodes none, so it survives `/theme-init` swaps untouched.

This is the diagram counterpart to `executor.md` §7 (charts). It does **not** produce
standalone HTML; the upstream `diagram-design` skill's HTML output is unused in this repo.

---

## 1. Selection guide

| If you're showing… | Use | Deep ref (Claude Code local) |
|---|---|---|
| Components + connections in a system | **Architecture** | `.codex/skills/diagram-design/references/type-architecture.md` |
| Decision logic with branches | **Flowchart** | `…/references/type-flowchart.md` |
| Time-ordered messages between actors | **Sequence** | `…/references/type-sequence.md` |
| States + transitions + guards | **State machine** | `…/references/type-state.md` |
| Entities + fields + relationships | **ER / data model** | `…/references/type-er.md` |
| Events positioned in time | **Timeline** | `…/references/type-timeline.md` |
| Cross-functional process with handoffs | **Swimlane** | `…/references/type-swimlane.md` |
| Two-axis positioning / prioritization | **Quadrant** | `…/references/type-quadrant.md` |
| Hierarchy through containment / scope | **Nested** | `…/references/type-nested.md` |
| Parent → children relationships | **Tree** | `…/references/type-tree.md` |
| Ownership / reporting / escalation | **Org chart** | `…/references/type-org-chart.md` |
| Stacked abstraction levels | **Layer stack** | `…/references/type-layers.md` |
| Overlap between sets | **Venn** | `…/references/type-venn.md` |
| Ranked hierarchy / conversion drop-off | **Pyramid / funnel** | `…/references/type-pyramid.md` |

**Before drawing:** if a 3-column table or one well-written paragraph says the same thing,
don't draw — that is the `executor.md` "no card-only / earn the visual" discipline applied to
diagrams. If you're combining two types, pick the dominant axis; don't hybridize grammars.

---

## 2. Per-type capsules

Each capsule: **When** · **Budget** (split when exceeded → overview + detail) · **Layout** ·
**Anti-patterns** · **Deep ref**. The accent budget is the slide-svg single-accent rule:
≤ 2 focal elements carry the active accent; everything else is `text` / `border` neutrals.

### Architecture
- **When:** components + their connections in a running system.
- **Budget:** ≤ 9 nodes, ≤ 12 arrows, ≤ 2 accent (focal) nodes.
- **Layout:** group by tier (input → service → store), left-to-right or top-down; draw arrows before boxes so z-order puts lines behind nodes; opaque mask rect behind every node so arrows don't bleed through.
- **Anti-patterns:** identical boxes for every node (erases hierarchy); accent on > 2 nodes; a floating legend inside the diagram area (put it as a bottom strip).
- **Deep ref:** `…/type-architecture.md`

### Flowchart
- **When:** decision logic with branches and outcomes.
- **Budget:** ≤ 9 process/decision nodes, ≤ 12 edges, ≤ 2 accent.
- **Layout:** one dominant flow direction (top-down); diamonds for decisions with edge labels `Yes`/`No` masked by an opaque rect; merge points align on a shared column.
- **Anti-patterns:** crossing edges that could be untangled by reordering; unlabeled decision branches; a decision diamond with > 2 exits (split the logic).
- **Deep ref:** `…/type-flowchart.md`

### Sequence
- **When:** time-ordered messages between actors/services.
- **Budget:** ≤ 5 lifelines, ≤ 12 messages, ≤ 2 accent.
- **Layout:** lifelines as vertical hairlines from header boxes; messages as horizontal arrows top-to-bottom in time order; activation bars as thin rects on the lifeline; return messages dashed (`stroke-dasharray="4,4"`).
- **Anti-patterns:** > 5 lifelines (the slide gets unreadable — split by phase); messages out of vertical time order; vertical `writing-mode` text on arrows.
- **Deep ref:** `…/type-sequence.md`

### State machine
- **When:** states + transitions + guard conditions.
- **Budget:** ≤ 9 states, ≤ 12 transitions, ≤ 2 accent.
- **Layout:** rounded-rect states; a filled start dot and a ringed end state; transition labels (event `[guard]`) on a masked rect at the edge midpoint; self-loops as a small arc above the state.
- **Anti-patterns:** unreachable states; transitions with no trigger label; accent used to mean "active" on many states (reserve accent for the 1–2 focal states).
- **Deep ref:** `…/type-state.md`

### ER / data model
- **When:** entities, their fields, and relationships.
- **Budget:** ≤ 8 entities, ≤ 12 relationships, ≤ 2 accent.
- **Layout:** entity = titled box with a field list (name left in `node-name`, type right in `sublabel`); crow's-foot or `1`/`N` cardinality markers at line ends; key fields marked with a small `PK`/`FK` tag rect (`rx=2`).
- **Anti-patterns:** every field shown when only keys + a few matter (trim); relationship lines crossing entities; rounded-pill tags (use rectangular `rx=2`).
- **Deep ref:** `…/type-er.md`

### Timeline
- **When:** events positioned along time.
- **Budget:** ≤ 9 events, ≤ 2 accent (the milestone(s) that matter).
- **Layout:** one baseline axis (horizontal) with tick marks; event markers as dots with a label stack; alternate label sides above/below to avoid collision; the focal milestone gets the accent dot.
- **Anti-patterns:** uneven time spacing presented as even (or vice-versa) — be honest about the scale; > 9 events (group into phases); accent on every milestone.
- **Deep ref:** `…/type-timeline.md`

### Swimlane
- **When:** a cross-functional process with handoffs between roles.
- **Budget:** ≤ 5 lanes, ≤ 12 steps total, ≤ 2 accent.
- **Layout:** horizontal lanes with a labeled header column; steps flow left-to-right; handoff arrows cross lane boundaries (the moment of handoff is the story — accent it sparingly); lane dividers are hairlines.
- **Anti-patterns:** > 5 lanes; steps that don't sit clearly in one lane; lane backgrounds as saturated fills (use `paper-2` at most).
- **Deep ref:** `…/type-swimlane.md`

### Quadrant
- **When:** two-axis positioning / prioritization.
- **Budget:** ≤ 12 plotted items, ≤ 2 accent.
- **Layout:** two axes crossing at center with axis labels at the ends; four quadrant labels in the corners (`eyebrow` style); items as small dots + labels; the recommended/focal item(s) accented. (For a BCG/McKinsey 2×2 scenario matrix, see upstream's consultant variant — but keep the single-accent + Pretendard lock.)
- **Anti-patterns:** crowding all items into one quadrant (then a quadrant isn't the right type); axis labels that don't state a real spectrum; gridline clutter.
- **Deep ref:** `…/type-quadrant.md`

### Nested
- **When:** hierarchy expressed through containment / scope.
- **Budget:** ≤ 6 nesting levels, ≤ 2 accent.
- **Layout:** concentric or boxes-in-boxes; inner padding constant (8/12/16); outermost = broadest scope; label each boundary at its top-left in `eyebrow`; the focal inner element accented.
- **Anti-patterns:** > 6 levels (unreadable nesting); equal visual weight at every level (vary stroke/opacity by depth); using nesting where a tree reads clearer.
- **Deep ref:** `…/type-nested.md`

### Tree
- **When:** parent → children relationships (taxonomy, decomposition).
- **Budget:** ≤ 4 depth levels, ≤ 9 nodes per visible level, ≤ 2 accent.
- **Layout:** top-down; connectors as elbow lines (orthogonal), drawn before boxes; siblings share a baseline y; collapse deep branches into a "+N more" leaf rather than overflowing.
- **Anti-patterns:** depth > 4 on one slide (split); diagonal spaghetti connectors; accent on a whole branch.
- **Deep ref:** `…/type-tree.md`

### Org chart
- **When:** ownership, reporting, escalation, routing between people/agents/teams.
- **Budget:** ≤ 4 depth levels, ≤ 12 nodes, ≤ 2 accent.
- **Layout:** top-down reporting lines (orthogonal elbows); role in `node-name`, owner/team in `sublabel`; dotted line (`stroke-dasharray="4,4"`) for indirect/escalation paths; the focal role accented.
- **Anti-patterns:** mixing reporting and process flow in one chart; > 12 nodes (show one sub-tree); photos/avatars as required chrome.
- **Deep ref:** `…/type-org-chart.md`

### Layer stack
- **When:** stacked abstraction levels (e.g., protocol/stack/platform layers).
- **Budget:** ≤ 6 layers, ≤ 2 accent.
- **Layout:** full-width horizontal bands stacked vertically; equal height unless a layer's importance justifies more; layer name left, optional sublabel right; the focal layer accented (tint fill + accent stroke).
- **Anti-patterns:** > 6 layers; arrows between adjacent layers when adjacency already implies the relationship (remove them); gradient fills on bands.
- **Deep ref:** `…/type-layers.md`

### Venn
- **When:** overlap between 2–3 sets.
- **Budget:** ≤ 3 circles, ≤ 2 accent.
- **Layout:** 2 or 3 overlapping circles with `fill-opacity` (never `rgba`, never `<g opacity>` — set per-circle `fill-opacity`); set labels outside the circles; the intersection label centered; the focal region accented.
- **Anti-patterns:** 4+ circles (a Venn stops being legible — use a different type); opaque fills that hide the overlap; group opacity (forbidden — per-element only).
- **Deep ref:** `…/type-venn.md`

### Pyramid / funnel
- **When:** a ranked hierarchy or a conversion drop-off.
- **Budget:** ≤ 6 layers, ≤ 2 accent.
- **Layout:** stacked trapezoids narrowing toward the apex (pyramid) or downward (funnel); each tier labeled inside or to the side; value/percent in `sublabel`; the focal tier (the bottleneck or the apex) accented.
- **Anti-patterns:** implying quantitative width when the tiers aren't measured (a pyramid shape suggests proportion — only use it if proportion is real); > 6 tiers; 3-D extrusion.
- **Deep ref:** `…/type-pyramid.md`

---

## 3. SVG-subset adaptation rules (the bridge — non-negotiable)

Re-cast upstream's HTML/CSS conventions into the strict subset of `references/shared-standards.md`.
The upstream type files assume HTML+CSS+Google Fonts; in slide-svg the same layouts become native SVG:

- **Inline attributes only** — `fill` / `stroke` / `stroke-width` on each element. **No** `<style>`, `class`, `@font-face`, Google Fonts `<link>`, `<foreignObject>`, `textPath`, `mask`, `<animate>`, or `<symbol>`/`<use>` (the only allowed `<use>` is the `data-icon` placeholder). `id` inside `<defs>` is fine.
- **Text** — every `<text>` carries the full active font chain (`Pretendard, 'Apple SD Gothic Neo', 'Malgun Gothic', Arial, sans-serif`); express hierarchy with size/weight/`letter-spacing` (one font only). Manual line breaks via `<tspan>`.
- **Arrows** — connector lines use a `<marker>` defined in `<defs>` with `orient="auto"`, a triangle/diamond/oval head whose `fill` **matches** the line `stroke` (shared-standards §1.1). For chunky/block arrows use a standalone `<polygon>`/`<path>`, not a marker. Diagonal polygon arrows must rotate their vertices (shared-standards §7).
- **Opacity** — `fill-opacity` / `stroke-opacity` **per element**. Never `rgba(...)`, never `<g opacity>`. (Upstream's `ink @ 0.05`, `accent @ 0.50 dashed` etc. become `fill="<ink>" fill-opacity="0.05"` and `stroke="<accent>" stroke-opacity="0.5" stroke-dasharray="4,4"`, where `<ink>` / `<accent>` are the active theme's `text` / `accent` hex resolved from `design-system.md`.)
- **Optional / async / return edges** — `stroke-dasharray="4,4"` (or `8,4` for flow connectors).
- **Background** — **drop** the diagram's own full-bleed `paper` rect and the dot-pattern; the diagram is a **region** inside the slide's content zone, sitting on the slide background. Arrow-label and node mask rects use the slide background fill (the active `bg`), not a diagram-local paper.
- **Grid** — every coord / size / gap divisible by 4; radius 4–8 (matches `theme-active.json` `radius.xs/sm`).
- **Canvas** — 1280×720 is permanently locked. The diagram occupies a region; the slide still carries its mandatory `.gm` governing-message line and its title/header per the layout pack.
- **Accent** — the active theme accent on ≤ 2 focal elements (single-accent principle). No second hue, no gradient/glow on diagram nodes. Use `accent-soft` for the focal node's tint fill, `accent` for its stroke.
- **Grouping** — wrap each node (box + mask + label + sublabel + tag) in a plain `<g id="…">` per shared-standards §4, so the export produces clean PowerPoint groups.

### Per-page self-audit (additions for diagram slides)
Fold these into `executor.md` §"Per-Page Self-Audit": (a) node count ≤ the type's budget; (b) accent on ≤ 2 elements; (c) every arrow either a qualifying `<marker>` connector or a standalone polygon; (d) no `<style>`/`class`/`@font-face`/`rgba`/`<g opacity>`; (e) `.gm` line present.

---

## 4. Where colors and fonts come from

Resolve `accent`, `text`, `border`, `bg`, etc. from `references/design-system.md` (rendered from the
active `theme-active.json`). The role → token map lives in the vendored
`.codex/skills/diagram-design/references/style-guide.md`. This bridge stays theme-agnostic so a
`/theme-init` swap needs no edit here — the next deck's diagrams pick up the new accent automatically.
