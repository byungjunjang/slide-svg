# Slide Patterns Reference

> 24 patterns organized by category. Each pattern includes complete `<section>` HTML.
> PPTX consideration: prefer simple Grid/Flexbox layouts. Avoid `position: absolute`.
>
> ## PPTX Fidelity Notes
> These elements have known PPTX conversion constraints:
> - **accent-badge on title slides**: Rendered as fixed-width pill in PPTX, not full-width bar. Accept as cosmetic difference.
> - **Chart.js scales.y.min/max**: Pass `beginAtZero: false` and explicit `min`/`max` in Chart.js config so `convertChart()` preserves axis range. Without this, PPTX charts default to 0-based Y-axis.
> - **bento-grid layout**: The 3-column asymmetric grid (span-2 + row-2) requires careful coordinate math in PPTX. Each card's column/row position must be manually calculated. Common mistake: the 5th card (row 3) should be single-column `col3W`, not span-2 `col2W`.
> - **bare icons**: Icons use `<svg class="icon-lg">` without circle backgrounds. No `icon-circle` wrappers or semantic-soft backgrounds.
> - **number-badge text wrapping**: `addBadgeNumber()` now uses `wrap: false` to prevent "01" from splitting into "0\n1". Always pass the number as a string. Use `opts.fill` to set color (default: accent). For gray badges, use `{ fill: 'E5E7EB', color: '6B7280' }`.
> - **Card body text sizing**: In per-deck scripts, card body text MUST use `fontSize: TYPE_SCALE.body.size` (not caption). Caption is reserved for labels and annotations only. If card text appears too small in PPTX, the fontSize is likely wrong.
> - **Text alignment in cards**: Default to `align: 'left'` for card body text. Only use `align: 'center'` for stat-numbers, icon-text, and badges. Process-flow step descriptions should be left-aligned.
> - **Bento-grid 5th card**: Must be positioned at row 3, column 3 (single column width). Calculate: `x = col3X, y = row3Y, w = col1W, h = rowH`. Never use span-2 width for this card.
> - **Card internal vertical stacking**: Stack elements with 0.04-0.06" gaps (not 0.15"+). Icon+label → stat number → trend → context. Never leave >0.3" gap inside a card. If the PPTX card looks "empty in the bottom half", the internal gaps are too large.
> - **Font size minimum**: All text inside cards must use at least `TYPE_SCALE.caption.size` (10.2pt). Trend text, context lines, and metric captions must be readable at slide size. Never use hardcoded values smaller than caption.
> - **Text overflow prevention**: ALL card body text MUST include `fit: 'shrink'` in addText options. This auto-shrinks text that exceeds the box. Without it, long Korean text gets clipped at the card boundary. For Korean decks with >80 char body text, also reduce fontSize by 0.5pt and increase text box height by 20%.

## Diversity Rules
- No consecutive identical patterns (except `section`)
- Minimum 3 layout types per deck
- Minimum 40% pattern differentiation
- Every content slide must have ≥1 visual element (no text-only slides)

---

### title

**Category:** Structure
**Use when:** Opening slide of the presentation — sets topic, presenter, and date.
**Visual elements:** huge display text + whitespace only. No icons, no badges, no background patterns.

```html
<section data-pattern="title" class="slide-centered">
  <div class="flex-col gap-6">
    <span class="accent-badge">Topic Label</span>
    <h1 class="display">Presentation Title</h1>
    <p class="title text-secondary">Subtitle describing the presentation scope</p>
    <div class="flex-row gap-6 mt-auto">
      <span class="caption">Presenter Name</span>
      <span class="caption">2024.03</span>
    </div>
  </div>
</section>
```

---

### section

**Category:** Structure
**Use when:** Introducing a new chapter or major topic division within the deck.
**Visual elements:** display text only, clean background

```html
<section data-pattern="section" class="slide-centered">
  <div class="flex-col gap-4">
    <span class="accent-badge">Chapter 1</span>
    <h2 class="display">Section Title<br>Goes Here</h2>
    <p class="body text-secondary">Brief one-line description of what this section covers</p>
  </div>
</section>
```

---

### closing

**Category:** Structure
**Use when:** Final slide — thank-you message with optional contact information.
**Visual elements:** icons (centered)

```html
<section data-pattern="closing">
  <div class="flex-col gap-6 items-center text-center">
    <svg class="icon-lg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/></svg>
    <h2 class="display">Thank You</h2>
    <p class="body text-secondary">Feel free to reach out with any questions or feedback.</p>
    <div class="flex-col gap-2">
      <span class="caption">Team Name | contact@example.com</span>
    </div>
  </div>
</section>
```

---

### report-summary

**Category:** Report (Default)
**Use when:** Presenting a topic overview, background context, or analytical summary. Two-column text layout with a summary bar takeaway at the bottom.
**Visual elements:** section-sub headers, body paragraphs, summary-bar

```html
<section data-pattern="report-summary">
  <h2 class="headline">Slide Title</h2>
  <div class="slide-body">
    <div class="grid-2" style="gap: var(--space-8);">
      <div class="flex-col gap-3">
        <h3 class="section-sub">Left Column Heading</h3>
        <p class="body">Primary body text explaining the main point of this column. Keep to 3–4 sentences.</p>
        <p class="body text-secondary">Supporting detail or secondary context. Can include <strong>bold emphasis</strong> on key terms.</p>
      </div>
      <div class="flex-col gap-3">
        <h3 class="section-sub">Right Column Heading</h3>
        <p class="body">Primary body text for the right column. Match content density with the left.</p>
        <p class="body text-secondary">Supporting detail. Use text-secondary for secondary information.</p>
      </div>
    </div>
    <div class="summary-bar">
      <span class="title">One-line summary takeaway that synthesizes both columns.</span>
    </div>
  </div>
  <p class="gm">Governing message — the key insight from this slide.</p>
</section>
```

---

### icon-explainer

**Category:** Report (Default)
**Use when:** Explaining 3–4 concepts, components, or principles with icons and brief descriptions. Grid layout with icon + badge + description per item.
**Visual elements:** icon-xl (SVG), pill-badge, body text

```html
<section data-pattern="icon-explainer">
  <h2 class="headline">Slide Title</h2>
  <div class="slide-body">
    <div class="grid-4" style="gap: var(--space-6); text-align: center;">
      <div class="flex-col gap-4 items-center">
        <svg class="icon-xl" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><!-- icon path --></svg>
        <span class="pill-badge pill-dark">Label 1</span>
        <p class="body text-secondary">Brief description of this concept or component. 2–3 sentences max.</p>
      </div>
      <div class="flex-col gap-4 items-center">
        <svg class="icon-xl" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><!-- icon path --></svg>
        <span class="pill-badge pill-dark">Label 2</span>
        <p class="body text-secondary">Brief description of this concept or component. 2–3 sentences max.</p>
      </div>
      <div class="flex-col gap-4 items-center">
        <svg class="icon-xl" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><!-- icon path --></svg>
        <span class="pill-badge pill-dark">Label 3</span>
        <p class="body text-secondary">Brief description of this concept or component. 2–3 sentences max.</p>
      </div>
      <div class="flex-col gap-4 items-center">
        <svg class="icon-xl" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><!-- icon path --></svg>
        <span class="pill-badge pill-dark">Label 4</span>
        <p class="body text-secondary">Brief description of this concept or component. 2–3 sentences max.</p>
      </div>
    </div>
  </div>
  <p class="gm">Governing message — the key insight from this slide.</p>
</section>
```

---

### report-two-column

**Category:** Report (Default)
**Use when:** Detailed two-column breakdown where each column has multiple sub-sections with metric rows, dividers, or structured lists.
**Visual elements:** section-sub, metric-row, rule, icon, structured lists

```html
<section data-pattern="report-two-column">
  <h2 class="headline">Slide Title</h2>
  <div class="slide-body">
    <div class="grid-2" style="gap: var(--space-8);">
      <!-- Left column -->
      <div class="flex-col gap-4">
        <h3 class="section-sub">Left Section Heading</h3>
        <p class="body">Body text describing the left section content.</p>
        <hr class="rule" />
        <h3 class="section-sub">Second Sub-Section</h3>
        <ul class="body text-secondary" style="list-style: disc; padding-left: 1.2em;">
          <li>Key point one</li>
          <li>Key point two</li>
          <li>Key point three</li>
        </ul>
      </div>
      <!-- Right column -->
      <div class="flex-col gap-4">
        <h3 class="section-sub">Right Section Heading</h3>
        <div class="flex-col gap-4">
          <div class="metric-row">
            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" stroke-width="2"><!-- icon --></svg>
            <div class="flex-col gap-2" style="flex: 1;">
              <span class="title">Metric or Item Title</span>
              <span class="body text-secondary">Supporting detail for this item.</span>
            </div>
          </div>
          <hr class="rule" />
          <div class="metric-row">
            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" stroke-width="2"><!-- icon --></svg>
            <div class="flex-col gap-2" style="flex: 1;">
              <span class="title">Second Metric Title</span>
              <span class="body text-secondary">Supporting detail for this item.</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  <p class="gm">Governing message — the key insight from this slide.</p>
</section>
```

---

### goal-breakdown

**Category:** Report (Default)
**Use when:** Breaking down 2–4 goals, lessons, strategies, or initiatives into cards with structured detail.
**Visual elements:** pill-badge, card, rule, icon, bullet list

```html
<section data-pattern="goal-breakdown">
  <h2 class="headline">Slide Title</h2>
  <div class="slide-body">
    <div class="grid-2" style="gap: var(--space-6);">
      <div class="card flex-col gap-4">
        <span class="pill-badge">Item 1 Label</span>
        <div class="flex-row gap-3 items-center">
          <span class="title" style="flex: 1;">Item 1 Title</span>
          <svg class="icon-lg text-secondary" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><!-- icon --></svg>
        </div>
        <hr class="rule" />
        <ul class="body text-secondary" style="list-style: disc; padding-left: 1.2em;">
          <li>Key point one for this item</li>
          <li>Key point two for this item</li>
          <li>Key point three for this item</li>
        </ul>
      </div>
      <div class="card flex-col gap-4">
        <span class="pill-badge">Item 2 Label</span>
        <div class="flex-row gap-3 items-center">
          <span class="title" style="flex: 1;">Item 2 Title</span>
          <svg class="icon-lg text-secondary" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><!-- icon --></svg>
        </div>
        <hr class="rule" />
        <ul class="body text-secondary" style="list-style: disc; padding-left: 1.2em;">
          <li>Key point one for this item</li>
          <li>Key point two for this item</li>
          <li>Key point three for this item</li>
        </ul>
      </div>
    </div>
  </div>
  <p class="gm">Governing message — the key insight from this slide.</p>
</section>
```

---

### process-row

**Category:** Report (Default)
**Use when:** Explaining 3 parallel processes, workstreams, or categories, each with sub-items. Cards in a 3-column row.
**Visual elements:** pill-badge, icon-lg, rule, bullet list

```html
<section data-pattern="process-row">
  <h2 class="headline">Slide Title</h2>
  <div class="slide-body">
    <div class="grid-3" style="gap: var(--space-6);">
      <div class="card flex-col gap-4">
        <span class="pill-badge">Category 1</span>
        <svg class="icon-lg text-secondary" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><!-- icon --></svg>
        <span class="title fw-headline">Card 1 Title</span>
        <hr class="rule" />
        <ul class="body text-secondary" style="list-style: disc; padding-left: 1.2em;">
          <li>Key point one</li>
          <li>Key point two</li>
          <li>Key point three</li>
        </ul>
      </div>
      <div class="card flex-col gap-4">
        <span class="pill-badge">Category 2</span>
        <svg class="icon-lg text-secondary" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><!-- icon --></svg>
        <span class="title fw-headline">Card 2 Title</span>
        <hr class="rule" />
        <ul class="body text-secondary" style="list-style: disc; padding-left: 1.2em;">
          <li>Key point one</li>
          <li>Key point two</li>
          <li>Key point three</li>
        </ul>
      </div>
      <div class="card flex-col gap-4">
        <span class="pill-badge">Category 3</span>
        <svg class="icon-lg text-secondary" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><!-- icon --></svg>
        <span class="title fw-headline">Card 3 Title</span>
        <hr class="rule" />
        <ul class="body text-secondary" style="list-style: disc; padding-left: 1.2em;">
          <li>Key point one</li>
          <li>Key point two</li>
          <li>Key point three</li>
        </ul>
      </div>
    </div>
  </div>
  <p class="gm">Governing message — the key insight from this slide.</p>
</section>
```

---

### comparison-table

**Category:** Report (Default)
**Use when:** Comparing two options, tools, or approaches side-by-side. Two-column layout with report-table on the left and detail cards on the right.
**Visual elements:** section-sub, report-table, col-highlight, pill-badge, card

```html
<section data-pattern="comparison-table">
  <h2 class="headline">Slide Title</h2>
  <div class="slide-body">
    <div class="grid-2" style="gap: var(--space-8);">
      <div class="flex-col gap-4">
        <h3 class="section-sub">Feature Comparison</h3>
        <table class="report-table">
          <thead>
            <tr>
              <th>Feature</th>
              <th>Option A</th>
              <th class="col-highlight">Option B</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td class="fw-title">Feature 1</td>
              <td>Value A</td>
              <td class="col-highlight fw-title">Value B</td>
            </tr>
            <tr>
              <td class="fw-title">Feature 2</td>
              <td>Value A</td>
              <td class="col-highlight fw-title">Value B</td>
            </tr>
            <tr>
              <td class="fw-title">Feature 3</td>
              <td>Value A</td>
              <td class="col-highlight fw-title">Value B</td>
            </tr>
            <tr>
              <td class="fw-title">Feature 4</td>
              <td>Value A</td>
              <td class="col-highlight fw-title">Value B</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="flex-col gap-4">
        <h3 class="section-sub">Key Differences</h3>
        <div class="card flex-col gap-3">
          <span class="pill-badge" style="align-self: flex-start;">Difference 1</span>
          <p class="body text-secondary">Explanation of the first key difference between the two options.</p>
        </div>
        <div class="card flex-col gap-3">
          <span class="pill-badge" style="align-self: flex-start;">Difference 2</span>
          <p class="body text-secondary">Explanation of the second key difference between the two options.</p>
        </div>
      </div>
    </div>
  </div>
  <p class="gm">Governing message — the key insight from this slide.</p>
</section>
```

---

### kpi-row

**Category:** Report (Default)
**Use when:** Showing 3–4 key metrics or KPIs with trend indicators. Simple row of metric cards.
**Visual elements:** stat-number, trend badges, caption labels

```html
<section data-pattern="kpi-row">
  <h2 class="headline">Slide Title</h2>
  <div class="slide-body">
    <div class="grid-4" style="gap: var(--space-6);">
      <div class="card flex-col gap-3">
        <span class="caption text-secondary">Metric Label 1</span>
        <span class="stat-number">42%</span>
        <span class="caption trend-positive">↑ +12% vs last period</span>
        <span class="caption text-secondary">Supporting context line</span>
      </div>
      <div class="card flex-col gap-3">
        <span class="caption text-secondary">Metric Label 2</span>
        <span class="stat-number">1.2B</span>
        <span class="caption trend-positive">↑ +8% vs last period</span>
        <span class="caption text-secondary">Supporting context line</span>
      </div>
      <div class="card flex-col gap-3">
        <span class="caption text-secondary">Metric Label 3</span>
        <span class="stat-number">94%</span>
        <span class="caption trend-negative">↓ -2% vs last period</span>
        <span class="caption text-secondary">Supporting context line</span>
      </div>
      <div class="card flex-col gap-3">
        <span class="caption text-secondary">Metric Label 4</span>
        <span class="stat-number">18M</span>
        <span class="caption trend-positive">↑ +25% vs last period</span>
        <span class="caption text-secondary">Supporting context line</span>
      </div>
    </div>
  </div>
  <p class="gm">Governing message — the key insight from this slide.</p>
</section>
```

---

### content-cards

**Category:** Content
**Use when:** Presenting 4 related items (components, features, pillars) in a 2×2 grid.
**Visual elements:** number-badge, cards, caption tags
**Design guidance:**
- Prefer SVG icon badges (icon-lg) by default; use `number-badge` (01–04) only when sequential order is the primary message
- Each card has a caption tag (category/status) for density — use semantic colors where appropriate
- Body text should be 2+ sentences to fill card interior properly

```html
<section data-pattern="content-cards">
  <h2 class="headline">Four Key Components</h2>
  <div class="slide-body">
    <div class="grid-2">
      <div class="card flex-col gap-3">
        <div class="flex-row gap-3 items-center">
          <span class="number-badge">01</span>
          <span class="caption text-accent">Foundation</span>
        </div>
        <span class="title">First Item</span>
        <span class="body text-secondary">Description of the first item and its role in the broader system. Provides the base for everything else.</span>
      </div>
      <div class="card flex-col gap-3">
        <div class="flex-row gap-3 items-center">
          <span class="number-badge">02</span>
          <span class="caption" style="color: var(--positive)">Growth</span>
        </div>
        <span class="title">Second Item</span>
        <span class="body text-secondary">Description of the second item. Drives expansion and builds on the foundation established above.</span>
      </div>
      <div class="card flex-col gap-3">
        <div class="flex-row gap-3 items-center">
          <span class="number-badge">03</span>
          <span class="caption text-secondary">Operations</span>
        </div>
        <span class="title">Third Item</span>
        <span class="body text-secondary">Description of the third item. Ensures reliable execution and maintains quality standards across the system.</span>
      </div>
      <div class="card flex-col gap-3">
        <div class="flex-row gap-3 items-center">
          <span class="number-badge">04</span>
          <span class="caption text-secondary">Scale</span>
        </div>
        <span class="title">Fourth Item</span>
        <span class="body text-secondary">Description of the fourth item. Enables growth beyond current capacity with sustainable infrastructure.</span>
      </div>
    </div>
  </div>
  <p class="gm">Governing message summarizing the key takeaway from these four items.</p>
</section>
```

---

### concept-cards

**Category:** Content
**Use when:** Presenting 3 concepts, categories, or types in a single row.
**Visual elements:** bare SVG icons, cards, caption evidence line
**Design guidance:**
- All cards use plain `class="card"` with `surface-alt` background — no colored borders or backgrounds
- Each card includes a bare `<svg class="icon-lg">` (no icon-circle wrapper)
- Each card includes a caption evidence line at bottom for density
- Body text should be 2+ sentences

```html
<section data-pattern="concept-cards">
  <h2 class="headline">Three Core Concepts</h2>
  <div class="slide-body">
    <div class="grid-3">
        <div class="card flex-col gap-3">
          <svg class="icon-lg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 14a1 1 0 0 1-.78-1.63l9.9-10.2a.5.5 0 0 1 .86.46l-1.92 6.02A1 1 0 0 0 13 10h7a1 1 0 0 1 .78 1.63l-9.9 10.2a.5.5 0 0 1-.86-.46l1.92-6.02A1 1 0 0 0 11 14z"/></svg>
          <span class="title">Concept A</span>
          <span class="body text-secondary">Description of the first concept, its characteristics and when it applies to real scenarios.</span>
          <span class="caption text-secondary">Adopted by 78% of teams</span>
        </div>
        <div class="card flex-col gap-3">
          <svg class="icon-lg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 5a3 3 0 1 0-5.997.125 4 4 0 0 0-2.526 5.77 4 4 0 0 0 .556 6.588A4 4 0 1 0 12 18Z"/><path d="M12 5a3 3 0 1 1 5.997.125 4 4 0 0 1 2.526 5.77 4 4 0 0 1-.556 6.588A4 4 0 1 1 12 18Z"/><path d="M15 13a4.5 4.5 0 0 1-3-4 4.5 4.5 0 0 1-3 4"/><path d="M17.599 6.5a3 3 0 0 0 .399-1.375"/><path d="M6.003 5.125A3 3 0 0 0 6.401 6.5"/><path d="M3.477 10.896a4 4 0 0 1 .585-.396"/><path d="M19.938 10.5a4 4 0 0 1 .585.396"/><path d="M6 18a4 4 0 0 1-1.967-.516"/><path d="M19.967 17.484A4 4 0 0 1 18 18"/></svg>
          <span class="title">Concept B</span>
          <span class="body text-secondary">Description of the second concept, its characteristics and when it applies to real scenarios.</span>
          <span class="caption text-secondary">Growing 2.3x year-over-year</span>
        </div>
        <div class="card flex-col gap-3">
          <svg class="icon-lg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83Z"/><path d="m22 17.65-9.17 4.16a2 2 0 0 1-1.66 0L2 17.65"/><path d="m22 12.65-9.17 4.16a2 2 0 0 1-1.66 0L2 12.65"/></svg>
          <span class="title">Concept C</span>
          <span class="body text-secondary">Description of the third concept, its characteristics and when it applies to real scenarios.</span>
          <span class="caption text-secondary">Reduces overhead by 40%</span>
        </div>
      </div>
    </div>
  </div>
  <p class="gm">Governing message highlighting the relationship between these concepts.</p>
</section>
```

---

### numbered-grid

**Category:** Content
**Use when:** Presenting 5-6 enumerated items (steps, tools, features, tips) in a 3×2 grid with clear scanning order.
**Visual elements:** number-badge, cards, optional cmd-tag badges
**Note:** Card body text must be **explanatory sentences** — not keyword fragments. Each description should be a complete thought that readers can understand on its own.

```html
<section data-pattern="numbered-grid">
  <div class="flex-col gap-2">
    <h2 class="headline">Six Key Features</h2>
    <p class="body text-secondary">Subtitle explaining the overall context of these items.</p>
  </div>
  <div class="slide-body">
    <div class="grid-3">
        <div class="card flex-col gap-3">
          <div class="flex-row gap-3 items-center">
            <span class="number-badge">1</span>
            <span class="title">First Item</span>
          </div>
          <span class="body text-secondary">역할별 전문 에이전트를 직접 만들 필요 없이 검증된 플러그인을 가져와 브레인스토밍부터 코드 리뷰까지 자동화하세요.</span>
          <div class="flex-row gap-2 mt-auto">
            <span class="cmd-tag"><span class="cmd-label">CLI</span><span class="cmd-value">/plugin install</span></span>
          </div>
        </div>
        <div class="card flex-col gap-3">
          <div class="flex-row gap-3 items-center">
            <span class="number-badge">2</span>
            <span class="title">Second Item</span>
          </div>
          <span class="body text-secondary">순차적 작업을 그룹으로 묶어 프론트엔드, 백엔드, 테스트 등 여러 에이전트에 동시에 실행하여 작업 효율을 극대화하세요.</span>
        </div>
        <div class="card flex-col gap-3">
          <div class="flex-row gap-3 items-center">
            <span class="number-badge">3</span>
            <span class="title">Third Item</span>
          </div>
          <span class="body text-secondary">외부 도구 연결로 AI 능력을 확장하세요. 웹 검색, GitHub, Playwright 등 브라우저 제어 연동이 필수입니다.</span>
        </div>
        <div class="card flex-col gap-3">
          <div class="flex-row gap-3 items-center">
            <span class="number-badge">4</span>
            <span class="title">Fourth Item</span>
          </div>
          <span class="body text-secondary">Context 창이 가득 차 세션이 끊기기 전에 실시간으로 상태를 추적하고, 비용과 모델 선택을 최적화하세요.</span>
        </div>
        <div class="card flex-col gap-3">
          <div class="flex-row gap-3 items-center">
            <span class="number-badge">5</span>
            <span class="title">Fifth Item</span>
          </div>
          <span class="body text-secondary">매일 반복되는 에러 로그 모니터링, 콘텐츠 성과 분석, 브리핑 생성 등을 예약하여 백그라운드에서 자동 실행하세요.</span>
        </div>
        <div class="card flex-col gap-3">
          <div class="flex-row gap-3 items-center">
            <span class="number-badge">6</span>
            <span class="title">Sixth Item</span>
          </div>
          <span class="body text-secondary">개별 설정이 번거롭다면, 단 한 번의 설치로 위의 모든 환경을 한 번에 잡아주는 통합 래퍼 도구를 활용하세요.</span>
        </div>
      </div>
    </div>
  </div>
  <p class="gm">Governing message summarizing the key takeaway.</p>
</section>
```

---

### numbered-row

**Category:** Content
**Use when:** Presenting 4-6 enumerated items side by side in a single horizontal row. Best for parallel concepts or sequential steps where each item has equal weight.
**Visual elements:** number-badge, borderless cards in flex row
**Note:** No card borders. Each card gets `flex: 1` for equal width. Use 4-6 items; 3 or fewer should use `numbered-grid` instead.

```html
<section data-pattern="numbered-row">
  <h2 class="headline">Four Key Principles</h2>
  <div class="slide-body">
    <div class="numbered-row">
      <div class="numbered-row-card">
        <div class="flex-row gap-3 items-center">
          <span class="number-badge">1</span>
          <span class="title">First Item</span>
        </div>
        <span class="body text-secondary">핵심 내용을 완전한 문장으로 설명하세요. 키워드 조각이 아닌 독자가 맥락 없이도 이해할 수 있는 내용이어야 합니다.</span>
      </div>
      <div class="numbered-row-card">
        <div class="flex-row gap-3 items-center">
          <span class="number-badge">2</span>
          <span class="title">Second Item</span>
        </div>
        <span class="body text-secondary">두 번째 항목의 핵심 내용을 설명합니다. 각 카드는 동일한 분량을 유지해야 합니다.</span>
      </div>
      <div class="numbered-row-card">
        <div class="flex-row gap-3 items-center">
          <span class="number-badge">3</span>
          <span class="title">Third Item</span>
        </div>
        <span class="body text-secondary">세 번째 항목의 핵심 내용을 설명합니다. 카드 높이가 동일하게 유지되도록 내용 분량을 조절하세요.</span>
      </div>
      <div class="numbered-row-card">
        <div class="flex-row gap-3 items-center">
          <span class="number-badge">4</span>
          <span class="title">Fourth Item</span>
        </div>
        <span class="body text-secondary">네 번째 항목의 핵심 내용을 설명합니다. 필요시 5-6개까지 확장할 수 있습니다.</span>
      </div>
    </div>
  </div>
  <p class="gm">Governing message summarizing the key takeaway.</p>
</section>
```

---

### numbered-column

**Category:** Content
**Use when:** Presenting 4-6 enumerated items in a single vertical column. Best for sequential steps, ranked priorities, or lists where each item needs title + description.
**Visual elements:** number-badge, flex column layout

```html
<section data-pattern="numbered-column">
  <h2 class="headline">Five Key Steps</h2>
  <div class="slide-body">
    <div class="numbered-column">
      <div class="numbered-column-item">
        <span class="number-badge" style="flex-shrink: 0;">1</span>
        <div class="flex-col gap-1">
          <span class="title">First Step</span>
          <span class="body text-secondary">첫 번째 단계의 핵심 내용을 완전한 문장으로 설명하세요.</span>
        </div>
      </div>
      <div class="numbered-column-item">
        <span class="number-badge" style="flex-shrink: 0;">2</span>
        <div class="flex-col gap-1">
          <span class="title">Second Step</span>
          <span class="body text-secondary">두 번째 단계의 핵심 내용을 설명합니다.</span>
        </div>
      </div>
      <div class="numbered-column-item">
        <span class="number-badge" style="flex-shrink: 0;">3</span>
        <div class="flex-col gap-1">
          <span class="title">Third Step</span>
          <span class="body text-secondary">세 번째 단계의 핵심 내용을 설명합니다.</span>
        </div>
      </div>
      <div class="numbered-column-item">
        <span class="number-badge" style="flex-shrink: 0;">4</span>
        <div class="flex-col gap-1">
          <span class="title">Fourth Step</span>
          <span class="body text-secondary">네 번째 단계의 핵심 내용을 설명합니다. 필요시 5-6개까지 확장할 수 있습니다.</span>
        </div>
      </div>
      <div class="numbered-column-item">
        <span class="number-badge" style="flex-shrink: 0;">5</span>
        <div class="flex-col gap-1">
          <span class="title">Fifth Step</span>
          <span class="body text-secondary">다섯 번째 단계의 핵심 내용을 설명합니다.</span>
        </div>
      </div>
    </div>
  </div>
  <p class="gm">Governing message summarizing the key takeaway.</p>
</section>
```

---

### two-column

**Category:** Content
**Use when:** Comparing two approaches, options, or perspectives side by side.
**Visual elements:** icons, cards (with bullet points)

```html
<section data-pattern="two-column">
  <div class="flex-col gap-6">
    <h2 class="headline">Option A vs Option B</h2>
    <div class="grid-2">
      <div class="card flex-col gap-4">
        <div class="flex-row gap-3 items-center">
          <svg class="icon-lg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>
          <span class="title">Option A</span>
        </div>
        <div class="flex-col gap-3">
          <div class="flex-row gap-2">
            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
            <span class="body">First characteristic of option A</span>
          </div>
          <div class="flex-row gap-2">
            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
            <span class="body">Second characteristic of option A</span>
          </div>
          <div class="flex-row gap-2">
            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
            <span class="body">Third characteristic of option A</span>
          </div>
          <div class="flex-row gap-2">
            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
            <span class="body">Fourth characteristic of option A</span>
          </div>
        </div>
      </div>
      <div class="card flex-col gap-4">
        <div class="flex-row gap-3 items-center">
          <svg class="icon-lg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 14c.2-1 .7-1.7 1.5-2.5 1-.9 1.5-2.2 1.5-3.5A6 6 0 0 0 6 8c0 1 .2 2.2 1.5 3.5.7.7 1.3 1.5 1.5 2.5"/><path d="M9 18h6"/><path d="M10 22h4"/></svg>
          <span class="title text-accent">Option B</span>
        </div>
        <div class="flex-col gap-3">
          <div class="flex-row gap-2">
            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
            <span class="body">First characteristic of option B</span>
          </div>
          <div class="flex-row gap-2">
            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
            <span class="body">Second characteristic of option B</span>
          </div>
          <div class="flex-row gap-2">
            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
            <span class="body">Third characteristic of option B</span>
          </div>
          <div class="flex-row gap-2">
            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
            <span class="body">Fourth characteristic of option B</span>
          </div>
        </div>
      </div>
    </div>
    <div class="gm">Governing message highlighting the key difference between the two options.</div>
  </div>
</section>
```

---

### hero-statement

**Category:** Content
**Use when:** Emphasizing a key insight, quote, or takeaway with large typography paired with visual evidence.
**Visual elements:** hero metric, callout card, supporting evidence cards
**Design guidance:**
- **Top section**: 3 compact evidence cards in a `grid-3`, each with icon + title + body. These provide data backing the insight. Evidence comes first so readers build context before the conclusion.
- **Bottom section**: Full-width plain card with the key insight text (1-2 lines max, using `.title` weight). No colored backgrounds or borders — just a standard `.card` with surface-alt background. This is the editorial conclusion drawn from the evidence above.
- The key insight should feel like a confident editorial statement, not a quote in a box.
- Avoid the "big text left + cards right" 50/50 split layout — use full-width stacking instead.

**RULE:** `hero-statement` MUST always include at least one visual companion alongside the insight text. Acceptable companions: stat chip, evidence cards, icon list cards, comparison badge row. A text-only hero-statement is forbidden.

```html
<section data-pattern="hero-statement">
  <div class="flex-col gap-6">
    <h2 class="headline">Key Insight</h2>
    <div class="grid-3">
      <div class="card flex-col gap-3">
        <svg class="icon-lg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/></svg>
        <span class="title">LTV $18,200</span>
        <span class="body text-secondary">Customer lifetime value increased 22% year-over-year through expansion revenue.</span>
      </div>
      <div class="card flex-col gap-3">
        <svg class="icon-lg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
        <span class="title">CAC $4,333</span>
        <span class="body text-secondary">Acquisition cost reduced 15% through efficient marketing channel optimization.</span>
      </div>
      <div class="card flex-col gap-3">
        <svg class="icon-lg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
        <span class="title">Payback: 8.4 months</span>
        <span class="body text-secondary">30% faster than industry average of 12 months.</span>
      </div>
    </div>
    <div class="card flex-row gap-4 items-center">
      <div class="flex-col gap-1">
        <span class="title">When LTV/CAC exceeds 3x, the business has earned the right to invest aggressively in growth.</span>
        <span class="body text-secondary">This threshold separates sustainable scaling from premature spending.</span>
      </div>
    </div>
    <div class="gm">Governing message providing context or evidence for this statement.</div>
  </div>
</section>
```

---

### comparison

**Category:** Content
**Use when:** Presenting structured data across multiple dimensions in a labeled table format — feature comparisons, pricing tiers, pros/cons analysis.
**Visual elements:** comparison-table, card, accent-badge, check/x SVG indicators, recommended column highlight
**Design guidance:**
- One column should be visually highlighted as "recommended" with `accent-soft` background — never leave all columns equal-weight
- Column headers include a subtitle line (stat, price, or descriptor) for density
- Use inline check (✓) / cross (✗) SVG icons for binary feature rows to improve scannability
- Add a summary/verdict row at the bottom with accent styling
- Zebra-stripe rows with subtle `var(--bg)` alternation for readability
- Right-align numeric cells when present

```html
<section data-pattern="comparison">
  <div class="flex-col gap-6">
    <h2 class="headline">Feature Comparison Across Options</h2>
    <div class="slide-body">
      <div class="card" style="padding: 0; overflow: hidden;">
        <table class="comparison-table">
          <thead>
            <tr>
              <th>Criteria</th>
              <th>
                <span class="title" style="display: block; color: var(--text);">Option A</span>
                <span class="caption">From $29/mo</span>
              </th>
              <th class="col-recommended">
                <span class="title" style="display: block; color: var(--accent);">Option B</span>
                <span class="caption">From $79/mo · Recommended</span>
              </th>
              <th>
                <span class="title" style="display: block; color: var(--text);">Option C</span>
                <span class="caption">Custom pricing</span>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td class="title">Scalability</td>
              <td class="body">Vertical only</td>
              <td class="body col-recommended">Horizontal auto-scaling</td>
              <td class="body">Hybrid approach</td>
            </tr>
            <tr>
              <td class="title">SSO Integration</td>
              <td class="body"><svg class="icon" viewBox="0 0 24 24" fill="none" stroke="var(--text-secondary)" stroke-width="2"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg></td>
              <td class="body col-recommended"><svg class="icon" viewBox="0 0 24 24" fill="none" stroke="var(--positive)" stroke-width="2"><path d="M20 6 9 17l-5-5"/></svg></td>
              <td class="body"><svg class="icon" viewBox="0 0 24 24" fill="none" stroke="var(--positive)" stroke-width="2"><path d="M20 6 9 17l-5-5"/></svg></td>
            </tr>
            <tr>
              <td class="title">Setup Time</td>
              <td class="body">~2 weeks</td>
              <td class="body col-recommended"><span class="accent-badge">Hours</span></td>
              <td class="body">Days</td>
            </tr>
            <tr>
              <td class="title">Support Level</td>
              <td class="body">Community forum</td>
              <td class="body col-recommended">Dedicated CSM</td>
              <td class="body">24/7 phone + Slack</td>
            </tr>
            <tr class="comparison-verdict">
              <td class="title">Best For</td>
              <td class="caption">Startups, small teams</td>
              <td class="caption col-recommended" style="font-weight: var(--fw-title); color: var(--accent);">Growth-stage SaaS</td>
              <td class="caption">Enterprise, regulated</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <div class="gm">Governing message summarizing which option fits which scenario.</div>
  </div>
</section>
```

CSS additions for comparison (add to skeleton `<style>`):
```css
.col-recommended { background: var(--accent-soft); }
.comparison-table thead th { padding: var(--space-4) var(--space-4); vertical-align: bottom; }
.comparison-table tbody tr:nth-child(even) { background: var(--bg); }
.comparison-verdict td { border-bottom: none; padding-top: var(--space-4); padding-bottom: var(--space-4); }
```

---

### before-after

**Category:** Content
**Use when:** Showing a transformation from an old state to a new state.
**Visual elements:** cards, before-after-label, bullet dot SVGs
**Note:** Both cards are equal-width in a `grid-2`. No process arrow. Before uses neutral dots, After uses accent-colored dots to signal improvement.

```html
<section data-pattern="before-after">
  <h2 class="headline">Workflow Transformation</h2>
  <div class="slide-body">
    <div class="grid-2 gap-6">
      <div class="card flex-col gap-4">
        <span class="before-after-label">Before</span>
        <div class="flex-col gap-3">
          <div class="flex-row gap-3 items-center"><svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="4" fill="currentColor"/></svg><span class="body">First old state — brief description of the problem</span></div>
          <div class="flex-row gap-3 items-center"><svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="4" fill="currentColor"/></svg><span class="body">Second old state — brief description of the problem</span></div>
          <div class="flex-row gap-3 items-center"><svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="4" fill="currentColor"/></svg><span class="body">Third old state — brief description of the problem</span></div>
          <div class="flex-row gap-3 items-center"><svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="4" fill="currentColor"/></svg><span class="body">Fourth old state — brief description of the problem</span></div>
        </div>
      </div>
      <div class="card flex-col gap-4">
        <span class="before-after-label" style="background: var(--accent-soft); color: var(--accent);">After</span>
        <div class="flex-col gap-3">
          <div class="flex-row gap-3 items-center"><svg class="icon" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" stroke-width="2"><circle cx="12" cy="12" r="4" fill="var(--accent)"/></svg><span class="body">First new state — brief description of the improvement</span></div>
          <div class="flex-row gap-3 items-center"><svg class="icon" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" stroke-width="2"><circle cx="12" cy="12" r="4" fill="var(--accent)"/></svg><span class="body">Second new state — brief description of the improvement</span></div>
          <div class="flex-row gap-3 items-center"><svg class="icon" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" stroke-width="2"><circle cx="12" cy="12" r="4" fill="var(--accent)"/></svg><span class="body">Third new state — brief description of the improvement</span></div>
          <div class="flex-row gap-3 items-center"><svg class="icon" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" stroke-width="2"><circle cx="12" cy="12" r="4" fill="var(--accent)"/></svg><span class="body">Fourth new state — brief description of the improvement</span></div>
        </div>
      </div>
    </div>
  </div>
  <p class="gm">Governing message explaining the impact of this transformation.</p>
</section>
```

---

### checklist

**Category:** Content
**Use when:** Presenting a list of action items, requirements, or verification steps with check icons.
**Visual elements:** card, checklist-item rows, check-circle SVG icons

```html
<section data-pattern="checklist">
  <div class="flex-col gap-6">
    <h2 class="headline">Launch Readiness Checklist</h2>
    <div class="card flex-col" style="border: none;">
      <div class="checklist-item">
        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><path d="m9 11 3 3L22 4"/></svg>
        <span class="body">Define project scope and success criteria</span>
      </div>
      <div class="checklist-item">
        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><path d="m9 11 3 3L22 4"/></svg>
        <span class="body">Complete security audit and compliance review</span>
      </div>
      <div class="checklist-item">
        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><path d="m9 11 3 3L22 4"/></svg>
        <span class="body">Set up monitoring and alerting infrastructure</span>
      </div>
      <div class="checklist-item">
        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><path d="m9 11 3 3L22 4"/></svg>
        <span class="body">Prepare rollback plan and incident response procedures</span>
      </div>
      <div class="checklist-item">
        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><path d="m9 11 3 3L22 4"/></svg>
        <span class="body">Communicate launch timeline to all stakeholders</span>
      </div>
    </div>
    <div class="gm">Governing message emphasizing the importance of completing all items before proceeding.</div>
  </div>
</section>
```

CSS (included in design system):
```css
.checklist-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) 0;
  border-bottom: 1px solid var(--border);
}
.checklist-item:last-child { border-bottom: none; }
```

---

### agenda

**Category:** Content
**Use when:** Listing session topics or meeting agenda items, with the current item highlighted.
**Visual elements:** numbered items, accent-soft highlight for current item, duration annotations
**Design guidance:**
- Each item uses a `.number-badge` with sequential numbers (01–04)
- Current item gets `accent-soft` background + accent left-border + bold text
- Past items have reduced opacity (0.5)
- Each item includes a right-aligned duration caption for density
- Items are separated by subtle bottom borders within the card
- The card uses `padding: 0; overflow: hidden` — items handle their own internal padding

```html
<section data-pattern="agenda">
  <div class="flex-col gap-6">
    <h2 class="headline">Today's Agenda</h2>
    <div class="slide-body">
      <div class="card" style="padding: 0; overflow: hidden; border: none;">
        <div class="agenda-item agenda-item-past">
          <span class="number-badge" style="opacity: 0.5">01</span>
          <div class="flex-col" style="flex: 1">
            <span class="title text-secondary">Opening Remarks and Context Setting</span>
            <span class="caption text-secondary">Introduction and objectives</span>
          </div>
          <span class="caption text-secondary">10 min</span>
        </div>
        <div class="agenda-item agenda-item-current">
          <span class="number-badge">02</span>
          <div class="flex-col" style="flex: 1">
            <span class="title" style="color: var(--accent)">Current Topic — Key Findings and Analysis</span>
            <span class="caption text-accent">Data review and insights</span>
          </div>
          <span class="caption text-accent">20 min</span>
        </div>
        <div class="agenda-item">
          <span class="number-badge" style="background: var(--border); color: var(--text-secondary)">03</span>
          <div class="flex-col" style="flex: 1">
            <span class="title text-secondary">Strategy Discussion and Next Steps</span>
            <span class="caption text-secondary">Action items and ownership</span>
          </div>
          <span class="caption text-secondary">15 min</span>
        </div>
        <div class="agenda-item">
          <span class="number-badge" style="background: var(--border); color: var(--text-secondary)">04</span>
          <div class="flex-col" style="flex: 1">
            <span class="title text-secondary">Open Q&amp;A and Wrap-Up</span>
            <span class="caption text-secondary">Questions and closing</span>
          </div>
          <span class="caption text-secondary">15 min</span>
        </div>
      </div>
    </div>
    <div class="gm">Governing message noting the expected duration or focus of today's session.</div>
  </div>
</section>
```

---

### quote

**Category:** Content
**Use when:** Highlighting a memorable quotation or testimonial with attribution.
**Visual elements:** hero-quote accent-soft card, centered layout, italic text

```html
<section data-pattern="quote">
  <div class="flex-col gap-6 items-center text-center">
    <h2 class="headline">Words to Remember</h2>
    <div class="hero-quote flex-col gap-4 text-left">
      <p class="fs-display-sm italic">The best way to predict<br>the future is to <span class="text-accent">invent it</span>.</p>
      <span class="caption">— Alan Kay, Computer Scientist</span>
    </div>
    <div class="gm">Governing message connecting this quote to the presentation's theme.</div>
  </div>
</section>
```

---

### bento-grid

**Category:** Content
**Use when:** Displaying a feature matrix or information set with asymmetric visual emphasis.
**Visual elements:** bento-grid CSS Grid, cards with varying spans, bare SVG icons
**Design guidance:**
- All cards use plain `class="card"` with `surface-alt` background — no colored borders or accent-soft backgrounds
- Each card includes a bare `<svg class="icon-lg">` (no icon-circle wrapper)
- Each card body should be 2+ sentences with a caption metric line for density

```html
<section data-pattern="bento-grid">
  <div class="flex-col gap-6">
    <h2 class="headline">Platform Capabilities</h2>
    <div class="slide-body">
      <div class="bento-grid">
        <div class="card flex-col gap-3 bento-span-2">
          <div class="flex-row gap-3 items-center">
            <svg class="icon-lg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 14a1 1 0 0 1-.78-1.63l9.9-10.2a.5.5 0 0 1 .86.46l-1.92 6.02A1 1 0 0 0 13 10h7a1 1 0 0 1 .78 1.63l-9.9 10.2a.5.5 0 0 1-.86-.46l1.92-6.02A1 1 0 0 0 11 14z"/></svg>
            <span class="title">Core Engine</span>
          </div>
          <span class="body text-secondary">High-performance processing pipeline that handles millions of events per second with sub-millisecond latency.</span>
          <span class="caption text-secondary">99.99% uptime SLA</span>
        </div>
        <div class="card flex-col gap-3 bento-row-2">
          <div class="flex-row gap-3 items-center">
            <svg class="icon-lg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10"/></svg>
            <span class="title">Security</span>
          </div>
          <span class="body text-secondary">End-to-end encryption, role-based access control, and audit logging built into every layer of the stack.</span>
          <span class="caption text-secondary">SOC 2 Type II certified</span>
        </div>
        <div class="card flex-col gap-3">
          <div class="flex-row gap-3 items-center">
            <svg class="icon-lg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/><path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/><path d="M8 16H3v5"/></svg>
            <span class="title">Auto-Scaling</span>
          </div>
          <span class="body text-secondary">Elastic resources that adapt to demand in real time.</span>
          <span class="caption text-secondary">0-10K RPS in 30s</span>
        </div>
        <div class="card flex-col gap-3">
          <div class="flex-row gap-3 items-center">
            <svg class="icon-lg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>
            <span class="title">API First</span>
          </div>
          <span class="body text-secondary">RESTful and GraphQL endpoints for every feature.</span>
          <span class="caption text-secondary">200+ endpoints</span>
        </div>
        <div class="card flex-col gap-3">
          <div class="flex-row gap-3 items-center">
            <svg class="icon-lg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 5a3 3 0 1 0-5.997.125 4 4 0 0 0-2.526 5.77 4 4 0 0 0 .556 6.588A4 4 0 1 0 12 18Z"/><path d="M12 5a3 3 0 1 1 5.997.125 4 4 0 0 1 2.526 5.77 4 4 0 0 1-.556 6.588A4 4 0 1 1 12 18Z"/><path d="M15 13a4.5 4.5 0 0 1-3-4 4.5 4.5 0 0 1-3 4"/><path d="M17.599 6.5a3 3 0 0 0 .399-1.375"/><path d="M6.003 5.125A3 3 0 0 0 6.401 6.5"/><path d="M3.477 10.896a4 4 0 0 1 .585-.396"/><path d="M19.938 10.5a4 4 0 0 1 .585.396"/><path d="M6 18a4 4 0 0 1-1.967-.516"/><path d="M19.967 17.484A4 4 0 0 1 18 18"/></svg>
            <span class="title">AI-Powered</span>
          </div>
          <span class="body text-secondary">Machine learning models for anomaly detection and prediction.</span>
          <span class="caption text-secondary">3ms avg inference</span>
        </div>
      </div>
    </div>
    <div class="gm">Governing message summarizing the platform's key differentiators.</div>
  </div>
</section>
```

CSS (included in design system):
```css
.bento-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  grid-template-rows: auto auto;
  gap: var(--card-gap);
}
.bento-span-2 { grid-column: span 2; }
.bento-row-2 { grid-row: span 2; }
```

---

### stats-dashboard

**Category:** Data
**Use when:** Displaying 3–4 key performance indicators or metrics at a glance.
**Visual elements:** grid-4, cards, stat-number, icons, trend indicators
**Design guidance:**
- All cards use plain `class="card"` with `surface-alt` background — no colored borders
- Semantic colors are used ONLY in trend indicator text (e.g., `class="trend-positive"`) and sparkline SVG strokes — not on card borders or backgrounds

```html
<section data-pattern="stats-dashboard">
  <h2 class="headline">Performance Overview — Q4</h2>
  <div class="slide-body">
    <div class="grid-4">
      <div class="card flex-col gap-3">
        <div class="flex-row gap-3 items-center">
          <svg class="icon-lg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
          <span class="caption text-secondary">Total Revenue</span>
        </div>
        <div class="flex-row gap-3 items-end">
          <span class="stat-number">$4.2M</span>
          <svg width="60" height="20" viewBox="0 0 60 20"><polyline points="0,18 10,15 20,12 30,10 40,7 50,4 60,2" fill="none" stroke="var(--accent)" stroke-width="1.5"/></svg>
        </div>
        <span class="caption trend-positive">+12% vs last quarter</span>
        <span class="caption text-secondary">Top 15% in SaaS benchmarks</span>
      </div>
      <div class="card flex-col gap-3">
        <div class="flex-row gap-3 items-center">
          <svg class="icon-lg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
          <span class="caption text-secondary">Active Users</span>
        </div>
        <div class="flex-row gap-3 items-end">
          <span class="stat-number">18.5K</span>
          <svg width="60" height="20" viewBox="0 0 60 20"><polyline points="0,16 10,14 20,12 30,9 40,7 50,5 60,3" fill="none" stroke="var(--positive)" stroke-width="1.5"/></svg>
        </div>
        <span class="caption trend-positive">+8% vs last quarter</span>
        <span class="caption text-secondary">DAU/MAU ratio: 42%</span>
      </div>
      <div class="card flex-col gap-3">
        <div class="flex-row gap-3 items-center">
          <svg class="icon-lg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>
          <span class="caption text-secondary">Conversion Rate</span>
        </div>
        <div class="flex-row gap-3 items-end">
          <span class="stat-number">3.2%</span>
          <svg width="60" height="20" viewBox="0 0 60 20"><polyline points="0,5 10,7 20,9 30,10 40,12 50,13 60,14" fill="none" stroke="var(--negative)" stroke-width="1.5"/></svg>
        </div>
        <span class="caption trend-negative">-0.5% vs last quarter</span>
        <span class="caption text-secondary">Industry avg: 2.8%</span>
      </div>
      <div class="card flex-col gap-3">
        <div class="flex-row gap-3 items-center">
          <svg class="icon-lg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><path d="m9 11 3 3L22 4"/></svg>
          <span class="caption text-secondary">Customer Satisfaction</span>
        </div>
        <div class="flex-row gap-3 items-end">
          <span class="stat-number">94%</span>
          <svg width="60" height="20" viewBox="0 0 60 20"><polyline points="0,14 10,12 20,10 30,8 40,6 50,4 60,3" fill="none" stroke="var(--positive)" stroke-width="1.5"/></svg>
        </div>
        <span class="caption trend-positive">+2% vs last quarter</span>
        <span class="caption text-secondary">NPS: 72 (excellent)</span>
      </div>
    </div>
  </div>
  <div class="gm">Governing message interpreting the overall trend across these metrics.</div>
</section>
```

---

### chart-bar

**Category:** Data
**Use when:** Visualizing categorical data as a bar chart with Chart.js.
**Visual elements:** card, canvas (Chart.js bar chart)

```html
<section data-pattern="chart-bar">
  <div class="flex-col gap-6">
    <h2 class="headline">Revenue by Category ($M)</h2>
    <div class="card" style="border: none;">
      <div style="height: 400px">
        <canvas id="barChart"></canvas>
      </div>
    </div>
    <div class="gm">Governing message highlighting the key insight from this data distribution.</div>
  </div>
</section>
```

Chart.js initialization (place in `<script>` after Chart.js and Reveal.js are loaded):
```javascript
var barCtx = document.getElementById('barChart').getContext('2d');
var barChart = new Chart(barCtx, {
  type: 'bar',
  data: {
    labels: ['Category A', 'Category B', 'Category C', 'Category D'],
    datasets: [{
      label: 'Revenue ($M)',
      data: [42, 68, 55, 31],
      // Single-accent opacity ladder (anti-slop T4) — never multi-hue.
      // Executor substitutes the ACTIVE theme accent at use-time.
      backgroundColor: [
        'rgba(70, 51, 227, 0.85)',
        'rgba(70, 51, 227, 0.60)',
        'rgba(70, 51, 227, 0.40)',
        'rgba(70, 51, 227, 0.25)'
      ],
      borderRadius: 6,
      barThickness: 40
    }]
  },
  options: {
    indexAxis: 'y',
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          label: function(context) {
            return '$' + context.parsed.x + 'M';
          }
        }
      }
    },
    scales: {
      x: {
        beginAtZero: true,
        ticks: { font: { size: 13 }, callback: function(v) { return '$' + v + 'M'; } },
        grid: { color: 'rgba(0,0,0,0.05)' }
      },
      y: {
        ticks: { font: { size: 14, weight: '600' } },
        grid: { display: false }
      }
    }
  }
});
```

Note: The canvas container uses an inline `style="height: 320px"` — this is an allowed exception for chart containers.

---

### chart-line

**Category:** Data
**Use when:** Showing trends or changes over time with a continuous line and optional area fill.
**Visual elements:** Chart.js line chart, card container

```html
<!-- Requires: <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script> -->
<!-- Add before charts: <script>Chart.defaults.animation = false;</script> -->
<section data-pattern="chart-line">
  <div class="flex-col gap-6">
    <h2 class="headline">Revenue Growth 2020–2024</h2>
    <div class="card" style="border: none;">
      <div style="height: 400px">
        <canvas id="lineChart"></canvas>
      </div>
    </div>
    <div class="gm">Governing message summarizing the trend shown in the chart.</div>
  </div>
</section>
```

Chart.js initialization (place in `<script>` after Chart.js and Reveal.js are loaded):
```javascript
var lineCtx = document.getElementById('lineChart').getContext('2d');
var lineChart = new Chart(lineCtx, {
  type: 'line',
  data: {
    labels: ['2020', '2021', '2022', '2023', '2024'],
    datasets: [{
      label: 'Revenue ($M)',
      data: [120, 145, 178, 210, 260],
      // Single accent (anti-slop T4) — Executor substitutes the ACTIVE theme accent.
      borderColor: 'rgba(70, 51, 227, 0.85)',
      backgroundColor: 'rgba(70, 51, 227, 0.12)',
      fill: true,
      tension: 0.3,
      pointBackgroundColor: 'rgba(70, 51, 227, 1)',
      pointRadius: 5,
      pointHoverRadius: 7,
      borderWidth: 3
    }]
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          label: function(context) {
            return '$' + context.parsed.y + 'M';
          }
        }
      }
    },
    scales: {
      x: {
        ticks: { font: { size: 13 } },
        grid: { color: 'rgba(0,0,0,0.05)' }
      },
      y: {
        beginAtZero: false,
        ticks: { font: { size: 13 }, callback: function(v) { return '$' + v + 'M'; } },
        grid: { color: 'rgba(0,0,0,0.05)' }
      }
    }
  }
});
```

Note: The canvas container uses an inline `style="height: 320px"` — this is an allowed exception for chart containers.

---

### chart-pie

**Category:** Data
**Use when:** Showing proportional breakdown or market share across segments.
**Visual elements:** Chart.js doughnut chart, card container, companion callout cards
**Design guidance:**
- Use 70/30 layout: doughnut chart (70%) + 2-3 companion callout cards (30%) with key takeaways
- Callout cards extract the top 2-3 insights from the chart data (e.g., "Segment A leads at 28%")
- Use semantic border colors on callout cards to match chart segment colors
- Doughnut `cutout: '65%'` for readability

```html
<!-- Requires: <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script> -->
<!-- Add before charts: <script>Chart.defaults.animation = false;</script> -->
<section data-pattern="chart-pie">
  <div class="flex-col gap-6">
    <h2 class="headline">Market Share by Segment</h2>
    <div class="slide-body">
      <div style="display: grid; grid-template-columns: 7fr 3fr; gap: var(--card-gap);">
        <div class="card" style="border: none;">
          <div style="height: 360px">
            <canvas id="doughnutChart"></canvas>
          </div>
        </div>
        <div class="flex-col gap-4">
          <div class="card flex-col gap-2">
            <span class="caption">Largest segment</span>
            <span class="title">Segment A</span>
            <span class="stat-number-sm">28%</span>
          </div>
          <div class="card flex-col gap-2">
            <span class="caption">Fastest growing</span>
            <span class="title">Segment B</span>
            <span class="stat-number-sm">22%</span>
          </div>
          <div class="card flex-col gap-2">
            <span class="caption">Emerging</span>
            <span class="title">Segment C</span>
            <span class="stat-number-sm">18%</span>
          </div>
        </div>
      </div>
    </div>
    <div class="gm">Governing message explaining the distribution shown in the chart.</div>
  </div>
</section>
```

Chart.js initialization (place in `<script>` after Chart.js and Reveal.js are loaded):
```javascript
var doughnutCtx = document.getElementById('doughnutChart').getContext('2d');
var doughnutChart = new Chart(doughnutCtx, {
  type: 'doughnut',
  data: {
    labels: ['Segment A', 'Segment B', 'Segment C', 'Segment D', 'Others'],
    datasets: [{
      data: [28, 22, 18, 14, 18],
      // Single-accent opacity ladder (anti-slop T4); trailing neutral gray for the residual "Others" slice.
      // Executor substitutes the ACTIVE theme accent at use-time.
      backgroundColor: [
        'rgba(70, 51, 227, 0.85)',
        'rgba(70, 51, 227, 0.60)',
        'rgba(70, 51, 227, 0.40)',
        'rgba(70, 51, 227, 0.25)',
        'rgba(107, 114, 128, 0.40)'
      ],
      borderWidth: 2,
      borderColor: '#FFFFFF'
    }]
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    cutout: '65%',
    plugins: {
      legend: {
        position: 'right',
        labels: {
          font: { size: 13, weight: '500' },
          padding: 16,
          usePointStyle: true,
          pointStyleWidth: 12
        }
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            return context.label + ': ' + context.parsed + '%';
          }
        }
      }
    }
  }
});
```

Note: The canvas container uses an inline `style="height: 320px"` — this is an allowed exception for chart containers.

---

### data-table

**Category:** Data
**Use when:** Presenting structured data with multiple columns and rows in a styled HTML table.
**Visual elements:** comparison-table inside card

```html
<section data-pattern="data-table">
  <div class="flex-col gap-6">
    <h2 class="headline">Performance Comparison by Product</h2>
    <div class="card" style="border: none;">
      <table class="comparison-table">
        <thead>
          <tr>
            <th>Rank</th>
            <th>Company</th>
            <th>Revenue</th>
            <th>Growth</th>
            <th>Category</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td class="title">1</td>
            <td class="body">Acme Corp</td>
            <td class="body text-accent">$12.4B</td>
            <td class="body">+18%</td>
            <td><span class="accent-badge">Enterprise</span></td>
          </tr>
          <tr>
            <td class="title">2</td>
            <td class="body">Globex Inc</td>
            <td class="body text-accent">$8.7B</td>
            <td class="body">+14%</td>
            <td><span class="accent-badge">Platform</span></td>
          </tr>
          <tr>
            <td class="title">3</td>
            <td class="body">Initech</td>
            <td class="body text-accent">$6.2B</td>
            <td class="body">+22%</td>
            <td><span class="accent-badge">SaaS</span></td>
          </tr>
          <tr>
            <td class="title">4</td>
            <td class="body">Umbrella Ltd</td>
            <td class="body text-accent">$4.8B</td>
            <td class="body">+11%</td>
            <td><span class="accent-badge">Enterprise</span></td>
          </tr>
          <tr>
            <td class="title">5</td>
            <td class="body">Stark Industries</td>
            <td class="body text-accent">$3.5B</td>
            <td class="body">+29%</td>
            <td><span class="accent-badge">Platform</span></td>
          </tr>
          <tr>
            <td class="title">6</td>
            <td class="body">Wayne Enterprises</td>
            <td class="body text-accent">$2.9B</td>
            <td class="body">+16%</td>
            <td><span class="accent-badge">SaaS</span></td>
          </tr>
        </tbody>
      </table>
    </div>
    <div class="gm">Governing message highlighting a key insight from the tabular data.</div>
  </div>
</section>
```

CSS (included in design system):
```css
.comparison-table { width: 100%; border-collapse: collapse; }
.comparison-table th, .comparison-table td {
  padding: var(--space-3) var(--space-4);
  text-align: left;
  border-bottom: 1px solid var(--border);
}
.comparison-table th {
  font-size: var(--fs-caption);
  font-weight: var(--fw-title);
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.comparison-table td { font-size: var(--fs-body); }
```

---

### process-flow

**Category:** Data
**Use when:** Illustrating a sequential process, workflow, or decision path with connected steps.
**Visual elements:** process-step cards, SVG arrows, number-badges, metric captions
**Design guidance:**
- All steps use plain `.process-step` with `surface` background — no colored borders
- Last step title uses `text-accent` to mark the destination
- Each step includes a metric/stat caption (e.g., "~2 weeks", "3 touchpoints") for information density
- Number badges (01-04) indicate sequence; icons complement but don't replace numbers
- Add an `insight-bar` below the process to summarize the overall journey

```html
<section data-pattern="process-flow">
  <div class="flex-col gap-6">
    <h2 class="headline">Implementation Process</h2>
    <div class="slide-body">
      <div class="flex-row gap-4 items-center">
        <div class="process-step flex-col gap-2 text-center">
          <span class="number-badge">01</span>
          <span class="title">Discovery</span>
          <span class="caption">Identify requirements and gather stakeholder input</span>
          <span class="caption text-accent" style="font-weight: var(--fw-title);">~2 weeks</span>
        </div>
        <svg class="process-arrow" viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 16h20"/><path d="M20 10l6 6-6 6"/></svg>
        <div class="process-step flex-col gap-2 text-center">
          <span class="number-badge">02</span>
          <span class="title">Design</span>
          <span class="caption">Create architecture and define technical approach</span>
          <span class="caption text-accent" style="font-weight: var(--fw-title);">~3 weeks</span>
        </div>
        <svg class="process-arrow" viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 16h20"/><path d="M20 10l6 6-6 6"/></svg>
        <div class="process-step flex-col gap-2 text-center">
          <span class="number-badge">03</span>
          <span class="title">Build</span>
          <span class="caption">Develop, test, and iterate on the solution</span>
          <span class="caption text-accent" style="font-weight: var(--fw-title);">~6 weeks</span>
        </div>
        <svg class="process-arrow" viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 16h20"/><path d="M20 10l6 6-6 6"/></svg>
        <div class="process-step flex-col gap-2 text-center">
          <span class="number-badge">04</span>
          <span class="title text-accent">Launch</span>
          <span class="caption">Deploy to production and monitor results</span>
          <span class="caption text-accent" style="font-weight: var(--fw-title);">Day 1</span>
        </div>
      </div>
      <div class="insight-bar">Total timeline: ~12 weeks from discovery to production launch</div>
    </div>
    <div class="gm">Governing message about the overall process and expected outcomes.</div>
  </div>
</section>
```

CSS (included in design system):
```css
.process-step {
  flex: 1;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--card-radius);
  padding: var(--space-4);
}
.process-arrow {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
}
```

---

### image-text

**Category:** Visual
**Use when:** Pairing an image or visual with descriptive text in a side-by-side layout.
**Visual elements:** image placeholder, two-column grid

```html
<section data-pattern="image-text">
  <div class="flex-col gap-6">
    <h2 class="headline">Visual Overview</h2>
    <div class="grid-2 gap-6">
      <div class="card" style="display:flex;align-items:center;justify-content:center;min-height:280px;">
        <span class="caption">Image Placeholder</span>
      </div>
      <div class="flex-col gap-4">
        <span class="title">Feature Highlight</span>
        <span class="body text-secondary">This layout pairs a visual element on the left with descriptive text on the right. Use it to showcase a product screenshot, diagram, or photograph alongside key details and context.</span>
        <div class="flex-col gap-3">
          <div class="flex-row gap-2">
            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
            <span class="body">First supporting detail about the visual</span>
          </div>
          <div class="flex-row gap-2">
            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
            <span class="body">Second supporting detail about the visual</span>
          </div>
          <div class="flex-row gap-2">
            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
            <span class="body">Third supporting detail about the visual</span>
          </div>
        </div>
      </div>
    </div>
    <div class="gm">Governing message connecting the visual to the overall narrative.</div>
  </div>
</section>
```

Note: The image placeholder uses inline styles — this is an allowed exception for placeholder containers in Phase 1.

---

### image-annotated

**Category:** Visual
**Use when:** Displaying an image or diagram with labeled callout badges at specific positions.
**Visual elements:** image placeholder, caption badges with relative/absolute positioning

```html
<section data-pattern="image-annotated">
  <div class="flex-col gap-6">
    <h2 class="headline">Annotated Diagram</h2>
    <div class="card" style="position:relative;min-height:380px;display:flex;align-items:center;justify-content:center;">
      <span class="caption">Diagram Placeholder</span>
      <span class="accent-badge" style="position:absolute;top:12%;left:15%;">Label A</span>
      <span class="accent-badge" style="position:absolute;top:12%;right:15%;">Label B</span>
      <span class="accent-badge" style="position:absolute;bottom:18%;left:25%;">Label C</span>
      <span class="accent-badge" style="position:absolute;bottom:18%;right:25%;">Label D</span>
    </div>
    <div class="gm">Governing message explaining the key areas highlighted in the diagram.</div>
  </div>
</section>
```

Note: This pattern uses `position: absolute` for callout badges. It is **not recommended for PPTX export** — use `image-text` or `content-cards` instead when PPTX output is needed.

---

### diagram

**Category:** Visual
**Use when:** Showing a flowchart, sequence, or relationship diagram using Mermaid syntax.
**Visual elements:** Mermaid diagram
**Design guidance:**
- Diagram MUST fill the content area — wrap in `.slide-body` and set `.mermaid-container` to `flex: 1` so the SVG expands to use all available vertical space
- Use `items-center` on the container for horizontal centering
- The `.mermaid` div should NOT be inside a `.card` — cards add padding that shrinks the diagram. Use a borderless full-bleed container instead.
- Mermaid SVG auto-scales: set `width: 100%; height: 100%;` on the container and the SVG will fill it

```html
<!-- Requires: <script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script> -->
<section data-pattern="diagram">
  <h2 class="headline">System Architecture</h2>
  <div class="slide-body">
    <div class="mermaid-container">
      <div class="mermaid">
graph TD
  A[User Request] --> B[API Gateway]
  B --> C[Auth Service]
  B --> D[Core Service]
  D --> E[Database]
  D --> F[Cache Layer]
  F --> G[Response]
  E --> G
      </div>
    </div>
  </div>
  <div class="gm">Governing message describing the architecture and data flow.</div>
</section>
```

CSS for `.mermaid-container` (add to skeleton `<style>`):
```css
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
```

Note: Use `mermaid@11` (not @10). Init MUST be in a separate `<script>` block from `hljs.highlightAll()`. Use the all-slides-visible init pattern from `libraries.md`.

---

### code-explain

**Category:** Visual
**Use when:** Presenting a code sample alongside a point-by-point explanation of key concepts.
**Visual elements:** terminal-window (dark titlebar + black code area), bullet explanations
**Note:** The code block uses a macOS-style terminal window with traffic light dots. Code background is pure black with white base text; syntax colors are provided by github-dark theme.

```html
<!-- Requires: <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/highlight.js@11.9.0/styles/github-dark.min.css"> -->
<!-- Requires: <script src="https://cdn.jsdelivr.net/npm/highlight.js@11.9.0/lib/highlight.min.js"></script> -->
<!-- Add init: <script>hljs.highlightAll();</script> -->
<section data-pattern="code-explain">
  <h2 class="headline">Understanding the Pattern</h2>
  <div class="slide-body">
    <div class="grid-2 gap-6">
      <div class="terminal-window">
        <div class="terminal-titlebar">
          <span class="terminal-dot terminal-dot-red"></span>
          <span class="terminal-dot terminal-dot-yellow"></span>
          <span class="terminal-dot terminal-dot-green"></span>
        </div>
        <pre><code class="language-javascript">async function fetchData(url) {
  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(response.status);
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Fetch failed:', error);
    return null;
  }
}</code></pre>
      </div>
      <div class="card flex-col gap-4">
        <span class="title text-accent">Key Concepts</span>
        <div class="flex-col gap-3">
          <div class="flex-row gap-2">
            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
            <span class="body"><strong>async/await</strong> simplifies asynchronous control flow</span>
          </div>
          <div class="flex-row gap-2">
            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
            <span class="body"><strong>try/catch</strong> handles both network and parsing errors</span>
          </div>
          <div class="flex-row gap-2">
            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
            <span class="body"><strong>response.ok</strong> checks for HTTP-level errors</span>
          </div>
          <div class="flex-row gap-2">
            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
            <span class="body"><strong>Graceful fallback</strong> returns null instead of crashing</span>
          </div>
        </div>
      </div>
    </div>
  </div>
  <p class="gm">Governing message about the coding pattern and when to apply it.</p>
</section>
```

---

## Content Density Guidelines

Slides should feel **information-rich without being crowded**. Avoid sparse slides with excessive whitespace and minimal content. Target the density level of Notion/Linear product pages.

### Minimum Content Per Slide Type

| Pattern | Minimum Content | Dense Variant |
|---------|----------------|---------------|
| **stats-dashboard** | 4 stat cards with value + label | Add 1-line description per card + trend indicator (↑12%) |
| **content-cards** | 3-4 cards with title + 1-line body | Add 2-3 line description + icon per card |
| **concept-cards** | 3 cards with icon + title + body | Add sub-bullets or stat chip per card |
| **numbered-grid** | 5-6 numbered cards with title + 2-3 line body | Add cmd-tag badges, text-highlight on key phrases |
| **comparison** | 2 columns with 3+ items each | Add header stats, icon per item, summary row |
| **two-column** | 2 columns with 3+ items | Add icon per bullet, subtitle per column |
| **chart-*** | Chart + title + subtitle | Add 2-3 key stat callouts alongside chart |
| **data-table** | 5+ rows with 4+ columns | Add status badges, trend indicators in cells |
| **bento-grid** | 4+ cells with mixed sizes | Fill each cell with title + 2-line content minimum |
| **process-flow** | 3-4 steps with title + body | Add icon per step, connector labels |

### Density Rules

1. **No empty visual space > 30%** — if a slide has large blank areas, add supporting content (sub-stats, context text, supplementary data)
2. **Cards need substance** — every card must have: icon/visual + title + at least 1-2 lines of body text. A card with only a title is too sparse.
3. **Chart slides need context** — don't leave charts alone. Add 2-3 stat callout boxes (key numbers extracted from the chart) or a brief annotation.
4. **Stat cards need description** — large numbers alone are meaningless. Always include: value + label + 1-line context (e.g., "2020-2024 cumulative global AI investment")
5. **Comparison slides need depth** — each column should have 4-5 comparison items with icon + text, not just 2-3 plain bullets
6. **Card grids allow more items** — bullet list slides max 4-5 items, but card/numbered-grid layouts support up to 6 items when each card body is concise (title + 2-3 lines)

### Card Body Writing Style

Card body text must be **explanatory sentences**, not keyword fragments or noun phrases.

**Forbidden:**
```
"실시간 모니터링, 비용 추적, 모델 최적화"
"에러 로그 / 콘텐츠 분석 / 브리핑 생성"
```

**Correct:**
```
"Context 창이 가득 차 세션이 끊기기 전에 실시간으로 상태를 추적하고, 비용과 모델 선택을 최적화하세요."
"매일 반복되는 에러 로그 모니터링, 콘텐츠 성과 분석, 브리핑 생성 등을 예약하여 백그라운드에서 자동 실행하세요."
```

**Why:** Readers should understand the concept from the card text alone, without needing the presenter's verbal explanation. Complete sentences deliver the "so what" that keyword lists cannot.

### Text-Level Highlight

Use `.text-highlight` or `.text-highlight-strong` to emphasize key phrases within body text, titles, or closing statements. This replaces the need for bold-only emphasis and adds visual weight through accent-colored backgrounds.

```html
<!-- Subtle marker effect (underline-style highlight) -->
<span class="text-highlight">핵심 키워드</span>

<!-- Strong badge-style highlight (accent background + color) -->
<span class="text-highlight-strong">중요한 개념</span>
```

**When to use:**
- Title slides: highlight the core topic phrase
- Closing/insight bars: highlight the key takeaway words
- Card body: highlight 1-2 critical terms per card (don't overuse)

### Insight Bar (Optional)

Use `.insight-bar` as a closing takeaway at the bottom of content slides. It replaces or supplements `.gm` when you want a **bolder, more prominent** closing message that answers "So What?"

```html
<!-- Instead of or in addition to .gm -->
<div class="insight-bar">
  AI가 모든 것을 다 하는 시대에 사람이 해야 할 일은 <span class="text-highlight-strong">이해하는 것</span>입니다.
</div>
```

**When to use:** When the slide's content leads to a strong concluding insight that deserves visual prominence. Not every slide needs it — use on slides where the "so what" message is the most important takeaway.

**`.gm` vs `.insight-bar`:**
| | `.gm` | `.insight-bar` |
|---|---|---|
| Visual weight | Subtle, small caption | Bold, full-width card |
| Position | Absolute bottom, border-top | Flex mt-auto, rounded card |
| Purpose | Running commentary | Key takeaway |
| Use frequency | Every content slide | Select slides with strong conclusions |

---

## Diagram Family (native SVG — see references/diagram-types.md)

Beyond the chart / section / card patterns above, **diagrams** (architecture, flowchart, sequence, state, ER, timeline, swimlane, quadrant, nested, tree, org chart, layers, venn, pyramid) are a distinct layout family. For diagram slides, select a type and follow the grammar in `references/diagram-types.md` (theme-agnostic, strict SVG subset). It counts as its own family for the no-consecutive-identical / family-diversity rules above. Deep per-type conventions live in `.codex/skills/diagram-design/references/type-*.md`.
