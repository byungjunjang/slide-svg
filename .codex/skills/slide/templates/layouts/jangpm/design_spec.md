# Jangpm Lecture Deck — Design Spec

> Prefilled defaults for the Jangpm template pack. Executor inherits these for every deck generated under the `slide` skill. Per-project values (title, page count, audience) are filled by the Strategist.

## I. Project Information

| Item | Value |
| ---- | ----- |
| **Project Name** | [Filled by Strategist] |
| **Canvas Format** | PPT 16:9 (1280×720) |
| **Page Count** | [Filled by Strategist] |
| **Design Style** | Jangpm — editorial, minimal, Korean lecture / report style |
| **Target Audience** | [Filled by Strategist — typically Korean professional / training] |
| **Use Case** | Lecture, workshop, strategic briefing |
| **Created Date** | [auto] |

---

## II. Canvas Specification

| Property | Value |
| -------- | ----- |
| **Format** | PPT 16:9 |
| **Dimensions** | 1280×720 |
| **viewBox** | `0 0 1280 720` |
| **Margins** | Left/right `56px` (`--space-14`), bottom `64px` (`--space-16`, reserved for GM line) |
| **Content Area** | x=56, y=160, w=1168, h=480 on content pages (below headline, above GM) |

---

## III. Visual Theme — LOCKED

The Jangpm lock forbids deviation. Executor does not recolor.

### Color Scheme

| Role | HEX | Token | Purpose |
| ---- | --- | ----- | ------- |
| **Background** | `#FAFAF9` | `--bg` | Page background (warm off-white) |
| **Surface** | `#FFFFFF` | `--surface` | Card / container |
| **Surface alt** | `#F5F5F4` | `--surface-alt` | Subtle grouped background |
| **Text primary** | `#1A1A1A` | `--text` | Main text (never pure black) |
| **Text secondary** | `#6B7280` | `--text-secondary` | Body secondary, GM |
| **Text tertiary** | `#9CA3AF` | `--text-tertiary` | Captions, page numbers |
| **Border** | `#E5E7EB` | `--border` | Default dividers, card borders |
| **Border strong** | `#D4D4D4` | `--border-strong` | Stronger divider |
| **Accent** | `#4633E3` | `--accent` | Single indigo-violet accent — **max 1–2 events per slide** |
| **Accent soft** | `#E8E5FC` | `--accent-soft` | Accent-tinted background, recommended column |
| **Accent ink** | `#2E1FB3` | `--accent-ink` | Accent pressed / darker |
| **Positive** | `#059669` | `--positive` | Data-meaning only (growth trend) |
| **Negative** | `#E11D48` | `--negative` | Data-meaning only (decline) |
| **Warning** | `#D97706` | `--warning` | Data-meaning only (risk) |

### Color Rules (Jangpm Lock)

- Monochrome first; every slide must read in grayscale before accent is applied
- Single accent `#4633E3` — never multiple hues, never gradient text/borders, never glow
- Accent is scarce: max 1–2 events per slide (one key metric, one callout, or one highlighted column)
- Semantic colors only in data contexts (trend indicators, chart bars, metric badges) — never as decoration
- Charts use single accent with opacity ladder: `rgba(70,51,227, 0.85 / 0.6 / 0.4 / 0.25)`

### Gradients

**Forbidden** under Jangpm lock. Do NOT define `<linearGradient>`, `<radialGradient>`, or gradient text fills. Solid fills and flat opacity only.

---

## IV. Typography System

### Font Plan

| Role | Font | Weight | Size (px) | Line-height | Letter-spacing |
| ---- | ---- | ------ | --------- | ----------- | -------------- |
| Display | Pretendard | 800 | 56 | 1.08 | -1.68 (-0.03em) |
| Display-sm | Pretendard | 800 | 40 | 1.10 | -0.8 (-0.02em) |
| Headline | Pretendard | 700 | 32 | 1.20 | -0.64 (-0.02em) |
| Title | Pretendard | 600 | 18.4 | 1.30 | 0 |
| Body | Pretendard | 400 | 15.2 | 1.60 | 0 |
| Caption | Pretendard | 500 | 12.8 | 1.40 | 0 |
| Label (uppercase taxonomy) | Pretendard | 600 | 12.8 | 1.40 | 0.64 (0.05em), `text-transform: uppercase` |

**Fallback chain** (for viewers without Pretendard installed):
`Pretendard, "Apple SD Gothic Neo", "Malgun Gothic", Arial, sans-serif`

Executor MUST write this full chain in `font-family` on every `<text>` element.

### Font Files

`assets/fonts/Pretendard-{Thin,ExtraLight,Light,Regular,Medium,SemiBold,Bold,ExtraBold,Black}.otf` + `PretendardVariable.ttf`. Distribute with the PPTX for recipients who will re-edit the deck.

---

## V. Layout Principles

- **8 px grid** — every x/y/width/height on an 8-multiple (or one of `--space-N`)
- **Slide padding** — 56px left/right, 56px top, 64px bottom (GM reserve)
- **Headline zone** — y=56 to y=140 (`{{PAGE_TITLE}}` + optional eyebrow + accent rule)
- **Body zone** — y=160 to y=640
- **GM zone** — y=648 to y=704 (text centered at y=680)
- **Card padding** — 24px (`--space-6`); card gap 24px
- **Card radius** — 12px (`--radius-lg`)
- **Borders** — always `1px solid #E5E7EB`; no decorative partial borders (no left-only accent bars)
- **Max elements** — 4–5 bullets or 3–4 cards per slide. Dense interiors forbidden.

---

## VI. Icon Usage

- **Style** — Lucide / Tabler line-art only; bare icons (no circle wrappers, no colored badges)
- **Stroke** — `currentColor`, 2px stroke, round linecap/linejoin
- **Size scale** — `.icon` 20px, `.icon-lg` 32px, `.icon-xl` 48px
- **Library** — `templates/icons/tabler-outline/` (Lucide-compatible, preferred for Jangpm)
  - Fallback: `templates/icons/tabler-filled/` for rare cases needing filled glyphs (e.g., a solid arrow)
  - **Do NOT** mix libraries. **Do NOT** use `chunk/` (too chunky, violates Jangpm line-art rule).
- **Usage rule** — `<use data-icon="tabler-outline/<name>" x="..." y="..." width="..." height="..." fill="none" stroke="currentColor" stroke-width="2"/>`; `finalize_svg.py` embeds the glyph
- **Emoji / unicode icons** — FORBIDDEN (anti-slop rule)

---

## VII. Visualization Reference List

[Filled by Strategist — select chart types from `templates/charts/`. Under Jangpm: chart colors MUST be overridden to `--accent` opacity ladder regardless of the template's original fill.]

---

## VIII. Image Resource List

[Filled by Strategist. For AI-generated images, use the Jangpm visual-assets prompt recipe: `minimal flat illustration, muted / pastel tones, transparent background, line-art style, no gradients, no glow`.]

---

## IX. Content Outline

[Filled by Strategist — per-page breakdown with page type (cover / chapter / content / ending), headline, body plan, GM line.]

### GM (Governing Message) Rule

Every content slide MUST have a `.gm` line:
- One sentence, declarative
- The "so-what" / takeaway / lesson — not a restatement of the title
- Korean-first (match deck language); concise (ideally ≤30 characters)
- Rendered at y=680, centered, `#6B7280`, 15.2px, weight 700

Example GM lines (from reference deck):
- "안정적 매출 유지, 수익성 개선 및 확장 단계"
- "덜 사고, 더 따진다 / 온라인 증가, 오프라인 감소"
- "월 평균 매출 4억 → 4.8억"

Title, chapter, and ending slides do NOT require `.gm`.

---

## X. Speaker Notes Requirements

- Language: match deck content language (Korean default)
- Format: per SKILL.md §Speaker Notes framework; localize markers (`[Transition]` → `[전환]`, `[Pause]` → `[멈춤]`, etc.)
- Voice: declarative, analytical, third-person institutional (match Jangpm's editorial tone — no direct address, no marketing tone)

---

## XI. Technical Constraints Reminder

- Canvas: 1280×720 only (see `references/canvas-formats.md`)
- SVG constraints: per `references/shared-standards.md` (banned: `<style>`, `class`, `<foreignObject>`, `mask`, `textPath`, animations)
- Post-processing: `finalize_svg.py` handles icon embedding, image cropping, text flattening, rounded-rect conversion. Do NOT substitute `cp`.
- Export: `svg_to_pptx.py <project> -s final` produces native DrawingML PPTX. Use `_svg.pptx` fallback only if native fails.

---

## Template Files

| File | Purpose |
| ---- | ------- |
| `01_cover.svg` | Cover / title slide |
| `02_chapter.svg` | Chapter / section divider |
| `03_content.svg` | Content slide shell (header / footer / GM; Executor fills body) |
| `04_ending.svg` | Closing / thank-you slide |

Each template contains `{{PLACEHOLDER}}` tokens that the Executor replaces per slide. Executor may freely compose additional SVG in the content area of `03_content.svg` (x=56, y=160, w=1168, h=480) while preserving the headline bar and GM line.
