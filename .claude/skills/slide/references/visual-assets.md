# Visual Assets Guide

Reference for integrating AI-generated illustrations and website screenshots into slide decks.

---

## When to Use Visual Assets

### Use codex-image (AI Illustration)

- **Concept explanation slides** — abstract ideas that benefit from visual metaphor (e.g., "cloud computing", "neural network")
- **Hero statement slides** — a striking illustration reinforces the key message
- **Process flow slides** — step illustrations make processes more memorable

### Use capture-screenshot (Website Screenshot)

- **Product UI demos** — show the actual interface being discussed
- **Website introductions** — capture landing pages, dashboards, documentation
- **Competitive analysis** — side-by-side screenshots of competing products

### Do NOT Use Visual Assets

- **Data-heavy slides** — charts and tables ARE the visual element; adding images clutters
- **Code explanation slides** — code blocks ARE the visual element
- **Checklist/agenda slides** — icons and structure provide sufficient visual interest
- **When the topic is purely abstract** — forced illustrations look generic

### Decision Rule

Ask: "Does an image add information that text/icons/charts cannot?" If yes → use visual asset. If no → rely on existing visual elements (icons, cards, charts).

---

## codex-image Integration (the ONLY AI image path)

**AI illustrations MUST be generated through `/codex-image` — and nothing else.** Do NOT use
nanobanana2, Gemini, DALL·E, Midjourney, Stable Diffusion, FLUX, Imagen, any MCP image tool,
or any other generator. codex-image (Codex CLI OAuth → `gpt-image-2`) is the single sanctioned
backend. Full recipe (sizes, negative handling, pacing, auth preflight): `references/image-generator.md` §4.3.

### Calling the Skill

```
/codex-image --size <1536x1024|1024x1024|1024x1536> --quality high \
  --out <project_path>/images --filename <slot_name> \
  "<active-theme anchor> prompt describing the illustration  Avoid: <negative list>"
```

Within the `/slide` workflow this runs in Step 5 (Image_Generator). If codex-image is
unavailable (Codex CLI missing or `codex login` expired), **halt** and ask the user to fix it —
do NOT silently fall back to any other generator.

### Prompt Guidelines

**Good prompts** — specific, describe the visual concept:
- "Minimal flat illustration of a robot reading documents, pastel blue tones, transparent background"
- "Isometric illustration of a data pipeline with three stages, clean lines, transparent background"
- "Simple line art of two people collaborating on a whiteboard, minimal style, transparent background"

**Bad prompts** — vague, describe the topic not the visual:
- "AI" (too vague)
- "Machine learning illustration" (no style direction)
- "Something about data" (meaningless)

### Style Keywords

Use these in prompts for consistent visual tone:
- **Style**: `minimal`, `flat`, `isometric`, `line art`, `geometric`
- **Tone**: `professional`, `clean`, `modern`, `simple`
- **Background**: Always include `transparent background`
- **Colors**: `pastel`, `monochrome`, `muted tones` (avoid vibrant/neon)

### Output Constraints

- Format: PNG with transparent background
- Max per slide: 2 images
- Min resolution: 640×480
- File location: `output/{slug}/assets/{slug}-{n}.png`

---

## Screenshot Integration

### Calling the Skill

```
/capture-screenshot https://example.com
```

### Viewport Settings

- Default: 1280×800 (desktop)
- Mobile: 375×812 (iPhone viewport)
- Tablet: 768×1024

### Capture Tips

- Wait for full page load before capture
- Specify element selector for partial captures: `--selector ".hero-section"`
- Crop to relevant area — full-page screenshots rarely fit well in slides

### Output Constraints

- Format: PNG
- Min width: 640px
- File location: `output/{slug}/assets/screenshot-{domain}-{n}.png`

---

## Image Placement Rules

### Size Constraints

- **Maximum width**: 50% of slide (640px)
- **Maximum height**: 60% of slide (432px)
- **Minimum size**: 200×150px
- Images must share space with text content — no full-bleed image slides

### CSS Class

All slide images use the `.slide-image` class defined in the skeleton:

```css
.slide-image {
  max-width: 100%;
  height: auto;
  border-radius: var(--card-radius);
  object-fit: contain;
}
```

### Pattern Integration

| Pattern | Image Placement | Notes |
|---------|----------------|-------|
| `report-two-column` | One column reserved for image/screenshot | Use when the visual is actual evidence |
| `chart-with-callout` | Chart on one side, visual only if it adds evidence | Avoid decorative pairing |
| `evidence-grid` | One or two visual cells within the grid | Use sparingly |
| `diagram` | Prefer Mermaid before raster image | Use image only if Mermaid is insufficient |

### HTML Reference

```html
<!-- In report-two-column pattern -->
<div class="grid-2">
  <div>
    <img src="assets/illustration-1.png" alt="Description" class="slide-image">
  </div>
  <div>
    <h3 class="title">Heading</h3>
    <p class="body">Explanation text...</p>
  </div>
</div>
```

---

## File Management

### Directory Structure

```
output/
└── my-presentation/
    ├── my-presentation.html
    └── assets/
        ├── robot-illustration-1.png
        ├── pipeline-diagram-1.png
        └── screenshot-example-com-1.png
```

### Naming Convention

- codex-image: `{topic-slug}-{index}.png` (e.g., `ai-robot-1.png`)
- Screenshots: `screenshot-{domain}-{index}.png` (e.g., `screenshot-github-com-1.png`)

### HTML Reference Path

Always use relative paths from the HTML file:

```html
<img src="assets/ai-robot-1.png" alt="AI robot illustration" class="slide-image">
```

### Cleanup

Each deck keeps its own `output/{slug}/assets/` directory. Remove unused deck folders or asset files when they are no longer needed.
