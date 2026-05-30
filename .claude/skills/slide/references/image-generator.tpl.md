# Image_Generator Reference Manual

<!-- RENDERED FILE: do not edit image-generator.md by hand. Edit this template
     (image-generator.tpl.md) and re-run theme-init's render chain
     (render_prompts.py). theme-init regenerates image-generator.md from this
     template every time theme-active.json changes. -->

> This file is the streamlined reference for the Image_Generator role. Common standards (SVG technical constraints, canvas formats, post-processing pipeline, etc.) are in [shared-standards.md](./shared-standards.md). {{TOKEN:name|cap}} visual-asset conventions are in [visual-assets.md](./visual-assets.md).

## 🔒 {{TOKEN:name|cap}} Style Lock — DEFAULT FOR EVERY IMAGE

Under the `slide` skill, **every AI-generated image MUST follow the {{TOKEN:name|cap}} illustration recipe**, which is the default and the only recommended style:

**Style directive** (prepend to every prompt):
> `minimal flat illustration, line-art style, restrained clean tones, transparent background, no gradients, no glow, no 3D rendering, no photorealism, harmonized with a {{TOKEN:colors.bg}} backdrop and a single {{TOKEN:colors.accent}} accent`

**Deck Style Anchor** (shared prefix for all images in a deck):
> `{{TOKEN:name|cap}} lecture deck illustration — minimal flat line-art, restrained clean tones aligned with the single {{TOKEN:colors.accent}} accent and {{TOKEN:colors.bg}} background, transparent background`

**Negative prompt** (always include):
> `text, watermark, logo, photograph, photorealistic, 3D render, gradient, glow, neon, vibrant colors, rainbow, dashboard UI, stock photo, shutterstock, low quality, blurry`

**What to avoid** ({{TOKEN:name|cap}} anti-slop alignment):
- Gradient skies, radial-glow orbs, atmospheric fog — anti-slop Rule 1 & 5
- Multi-hue rainbow palettes — color rule
- Gradient text inside illustrations — Rule 3
- 3D renders, isometric renders with heavy shadows — violates minimal flat
- Photorealistic stock imagery — Rule 13 (decorative-only images)
- Colored icon-badge illustration style — Rule 18 (SaaS dashboard aesthetics)

Overrides below (style keywords table, industry presets) are kept for completeness but **must yield to the {{TOKEN:name|cap}} lock**. If the Strategist's Design Spec requests a different illustration style, stop — the spec has drifted from the {{TOKEN:name|cap}} lock.

---

## Core Mission

Receive the "Image Resource List" from the Design Specification & Content Outline output by the Strategist, create optimized prompts for each image pending generation, generate images **via the `/codex-image` skill — the only sanctioned backend** — and save them to the project's `images/` directory.

**Trigger condition**: When AI image generation is needed (standalone use or invoked within pipeline)

| Mode | Trigger | Description |
|------|---------|-------------|
| **Standalone** | Directly describe image needs | Generate single or multiple AI images |
| **In-pipeline** | `generate-ppt` with AI image generation selected | Batch-generate image assets for a project |

> Next step in pipeline: Executor generates SVGs

---

## 1. Input & Output

### Input

- **Design Specification & Content Outline** (from Strategist): project theme, target audience, design style, color scheme, canvas format
- **Image Resource List** (key input):

  | Filename | Dimensions | Purpose | Type | Status | Generation Description |
  |----------|-----------|---------|------|--------|----------------------|
  | cover_bg.png | 1920x1080 | Cover background | Background | Pending | Modern tech abstract background, deep blue gradient |

### Output

| Deliverable | Path / Description | Requirements |
|------------|-------------------|--------------|
| Prompt document | `project/images/image_prompts.md` | **Must** be saved using file write tool — cannot just be output in conversation |
| Optimized prompts | Individual prompt per image | Directly usable with AI image generation tools; doubles as alt text |
| Image files | `project/images/` directory | Named per the resource list filenames |
| Updated list | Status changes | "Pending" → "Generated" |

---

## 2. Unified Prompt Structure

### 2.1 Standard Output Format

Every image must be output in the following format:

```markdown
### Image N: {filename}

| Attribute | Value |
| --------- | ----- |
| Purpose   | {which page / what function} |
| Type      | {Background / Illustration / Photography / Diagram / Decorative} |
| Dimensions | {width}x{height} ({aspect ratio}) |
| Original description | {description provided by user in the list} |

**Prompt**:
{subject description}, {style directive}, {color directive}, {composition directive}, {quality directive}

**Negative Prompt**:
{elements to exclude}

**Alt Text**:
> {Description for accessibility and image captions}
```

### 2.2 Prompt Components

| Component | Description | Example |
|-----------|-------------|---------|
| Subject description | Core content | `Abstract geometric shapes`, `Team collaboration scene` |
| Style directive | Visual style | `flat design`, `3D isometric`, `watercolor style` |
| Color directive | Color scheme | `color palette: navy blue (#1E3A5F), gold (#D4AF37)` |
| Composition directive | Layout ratio | `16:9 aspect ratio`, `centered composition` |
| Quality directive | Resolution quality | `high quality`, `4K resolution`, `sharp details` |
| Negative prompt | Exclude elements | `text, watermark, blurry, low quality` |

### 2.3 Style Keywords — LOCKED ({{TOKEN:name|cap}})

**Under this skill, only one style is valid.** The table below is kept for reference only; do NOT use it.

| Design Style | Image Style | Core Keywords |
|-------------|-------------|---------------|
| **{{TOKEN:name|cap}} (locked default)** | Minimal flat line-art, restrained clean tones | `minimal flat illustration`, `line-art style`, `restrained clean tones`, `transparent background`, `no gradients`, `no glow`, `harmonized with the single {{TOKEN:colors.accent}} accent` |

<details>
<summary>Legacy style presets (DO NOT USE — kept for historical reference)</summary>

| Design Style | Recommended Image Style | Core Keywords |
|-------------|------------------------|---------------|
| ~~General Versatile~~ | ~~Modern illustration, flat design~~ | ~~`modern`, `flat design`, `gradient`, `vibrant colors`~~ |
| ~~General Consulting~~ | ~~Clean professional, corporate~~ | ~~`professional`, `clean`, `corporate`, `minimalist`~~ |
| ~~Top Consulting~~ | ~~Premium minimal, abstract geometric~~ | ~~`premium`, `sophisticated`, `geometric`, `abstract`, `elegant`~~ |
| ~~Technology / SaaS~~ | ~~Futuristic, digital~~ | ~~`futuristic`, `digital`, `tech grid`, `circuit pattern`, `neon accents`, `dark background`~~ |
| ~~Education / Training~~ | ~~Friendly, instructional~~ | ~~`friendly`, `instructional`, `whiteboard style`, `pastel colors`, `simple shapes`~~ |
| ~~Marketing / Branding~~ | ~~Bold, energetic~~ | ~~`bold`, `energetic`, `dynamic composition`, `vivid colors`, `action-oriented`~~ |
| ~~Healthcare / Medical~~ | ~~Clean, reassuring~~ | ~~`clean`, `clinical`, `soft blue-green palette`, `organic curves`, `reassuring`~~ |
| ~~Finance / Banking~~ | ~~Conservative, trustworthy~~ | ~~`conservative`, `trustworthy`, `blue-gray palette`, `structured`, `precise`~~ |
| ~~Creative / Design~~ | ~~Artistic, experimental~~ | ~~`artistic`, `experimental`, `asymmetric`, `textured`, `hand-crafted feel`~~ |

These legacy presets conflict with {{TOKEN:name|cap}}'s anti-slop rules (gradients, vibrant colors, dark backgrounds, colored badges). They are preserved only so callers who strayed from the {{TOKEN:name|cap}} lock can recognize why their output looked wrong.

</details>

### 2.4 Color Integration — LOCKED ({{TOKEN:name|cap}})

Under the `slide` skill, the color directive for every prompt is fixed:

```
color palette: {{TOKEN:colors.bg}} background, restrained clean midtones harmonized with the single {{TOKEN:colors.accent}} accent, neutral grays ({{TOKEN:colors.text}} text, {{TOKEN:colors.text-secondary}} secondary)
```

Do NOT extract a bespoke palette from the Design Spec (the Design Spec is already locked to the {{TOKEN:name|cap}} palette — extraction is redundant). Do NOT introduce a second hue.

### 2.5 Canvas Format & Aspect Ratio — LOCKED

Under the `slide` skill, the deck canvas is always 1280×720 (16:9). Image aspect ratio defaults to **16:9** for backgrounds/hero illustrations, or **1:1** for inline illustrations within cards.

| Usage | Aspect Ratio | Recommended Resolution |
|-------|--------------|-----------------------|
| Hero / full-width illustration | 16:9 | 1920×1080 or 2560×1440 |
| Inline card illustration | 1:1 | 1024×1024 |
| Two-column left-right illustration | 3:4 or 4:3 | 1024×1365 or 1365×1024 |

> **Note (Method 0 / codex-image path)**: gpt-image-2 has no true 16:9 size. 16:9 slots are generated at `1536×1024` and SVG `preserveAspectRatio="xMidYMid slice"` crops to 1280×720. See §4.3 Method 0 for the full size mapping.

### 2.6 Multi-Image Coherence Strategy

When generating multiple images for a single deck, visual coherence is critical. Use a **Deck Style Anchor** — a shared prefix of 15-25 words prepended to every image prompt.

**Construction**: Combine style keywords (Section 2.3) + color directive (Section 2.4) + quality directive into one reusable prefix.

**Example**:
```
Deck Style Anchor:
"modern flat design illustration, color palette: deep navy (#1E3A5F), light gray (#F8F9FA), gold accent (#D4AF37), clean minimalist, high quality, 4K"

Image 1 prompt: [Deck Style Anchor], abstract technology network showing connected nodes...
Image 2 prompt: [Deck Style Anchor], team of professionals collaborating at a desk...
Image 3 prompt: [Deck Style Anchor], growth chart with upward trending line...
```

**Exception**: Background images may replace style keywords with `background`, `backdrop`, `negative space for text overlay` while keeping the same color directive. This ensures color consistency without compromising background functionality.

**Rule**: Define the Deck Style Anchor once in the prompt document header (Section 5), then reference it in every individual prompt.

---

## 3. Image Type Classification & Handling

### Type Determination Flow

1. Full-page / large-area backdrop → **Background** (3.1)
2. Real scenes / people / products → **Photography** (3.2)
3. Flat / illustration / cartoon style → **Illustration** (3.3)
4. Process / architecture / relationships → **Diagram** (3.4)
5. Partial decoration / texture → **Decorative Pattern** (3.5)

### 3.1 Background

**Identifying characteristics**: Full-page background for covers or chapter pages; must support text overlay

| Key Point | Description |
|-----------|-------------|
| Emphasize background nature | Add `background`, `backdrop` |
| Reserve text area | `negative space in center for text overlay` |
| Avoid strong subjects | Use abstract, gradient, geometric elements |
| Low-contrast details | `subtle`, `soft`, `muted` |

**Template**: `Abstract {theme element} background, {style} style, {primary color} to {secondary color} gradient, subtle {decorative elements}, clean negative space in center for text overlay, {aspect ratio} aspect ratio, high resolution, professional presentation background`

**Negative prompt**: `text, letters, watermark, faces, busy patterns, high contrast details`

### 3.2 Photography

**Identifying characteristics**: Real scenes, people, products, architecture — photographic quality

| Key Point | Description |
|-----------|-------------|
| Emphasize realism | `photography`, `photorealistic`, `real photo` |
| Lighting effects | `natural lighting`, `soft shadows`, `studio lighting` |
| Background handling | `white background` / `blurred background` / `contextual setting` |
| People diversity | `diverse`, `professional attire` |

**Template**: `{subject description}, professional photography, {lighting type} lighting, {background type} background, color grading matching {color scheme}, high quality, sharp focus, 8K resolution`

**Negative prompt**: `watermark, text overlay, artificial, CGI, illustration, cartoon, distorted faces`

### 3.3 Illustration

**Identifying characteristics**: Flat design, vector style, cartoon, concept diagrams

| Key Point | Description |
|-----------|-------------|
| Specify style | `flat design`, `isometric`, `vector style`, `hand-drawn` |
| Simplify details | `simplified`, `clean lines`, `minimal details` |
| Unified palette | Strictly use design spec colors |
| Background choice | `white background` or `transparent background` |

**Template**: `{subject description}, {illustration style} illustration style, {detail level} with clean lines, color palette: {color list}, {background type} background, professional {purpose} illustration`

**Negative prompt**: `realistic, photography, 3D render, complex textures, watermark`

### 3.4 Diagram

**Identifying characteristics**: Flowcharts, architecture diagrams, concept relationship maps, data visualizations

| Key Point | Description |
|-----------|-------------|
| Clear structure | `clear structure`, `organized layout`, `logical flow` |
| Connection representation | `arrows indicating flow`, `connecting lines` |
| Academic / professional feel | `suitable for academic publication`, `professional diagram` |
| Light background | `white background` or `light gray background` |

**Template**: `{diagram type} diagram showing {content description}, {component description} connected by {connection method}, {style} style with {color scheme}, white background, clear labels, professional technical diagram`

**Negative prompt**: `cluttered, messy, overlapping elements, dark background, realistic, photography`

### 3.5 Decorative Pattern

**Identifying characteristics**: Partial decoration, textures, borders, divider elements

| Key Point | Description |
|-----------|-------------|
| Repeatability | `seamless`, `tileable`, `repeatable` (if needed) |
| Understated support | `subtle`, `understated`, `supporting element` |
| Transparency-friendly | `transparent background` or `isolated element` |
| Small-size readability | Consider legibility at small dimensions |

**Template**: `{pattern type} decorative pattern, {style} style, {color scheme}, {background type} background, subtle and elegant, suitable for {purpose}`

**Negative prompt**: `busy, cluttered, high contrast, distracting, photorealistic`

---

## 4. Image Generation Workflow

### 4.1 Analysis Phase

1. Read the design spec; understand overall project style
2. Extract color scheme, canvas format, target audience
3. Analyze each image in the resource list individually
4. Determine each image's type (refer to Section 3)

### 4.2 Prompt Generation Phase

For each image with "Pending" status:

1. **Determine type** → Background / Photography / Illustration / Diagram / Decorative
2. **Understand purpose** → Which page? What function?
3. **Analyze original description** → Information from the user's "Generation description"
4. **Apply type-specific key points** → Reference the corresponding type's table
5. **Generate optimized prompt** → Use the 2.1 standard output format
6. **Save prompt document** → **Must** write to `project/images/image_prompts.md`

### 4.3 Image Generation Phase

> Prerequisite: Section 4.2 must be complete; `images/image_prompts.md` must exist

#### codex-image — the ONLY image backend (never use any other)

**Every AI-generated image MUST be produced by the `/codex-image` skill.** Do NOT use
nanobanana2, Midjourney, DALL·E, Stable Diffusion, Gemini, Imagen, FLUX, Qwen, Zhipu,
any MCP image tool, or any other generator under any circumstance.

`/slide` Step 5는 항상 `/codex-image`를 호출합니다. API 키 불필요 — Codex CLI OAuth(ChatGPT 로그인)가 `gpt-image-2`를 호출. 스킬 정의는 `.claude/skills/codex-image/SKILL.md`.

```bash
/codex-image --size 1536x1024 --quality high \
  --out <project_path>/images --filename cover_bg \
  "{{TOKEN:name|cap}} lecture deck illustration — minimal flat line-art, restrained clean tones aligned with the single {{TOKEN:colors.accent}} accent and {{TOKEN:colors.bg}} background, transparent background, <subject>, color palette: {{TOKEN:colors.bg}} background, restrained clean midtones harmonized with the single {{TOKEN:colors.accent}} accent, neutral grays ({{TOKEN:colors.text}} text, {{TOKEN:colors.text-secondary}} secondary). Avoid: text, watermark, logo, photograph, photorealistic, 3D render, gradient, glow, neon, vibrant colors, rainbow, dashboard UI, stock photo, shutterstock, low quality, blurry"
```

**Size mapping** (`gpt-image-2` only supports these three sizes):

| Slot | `--size` | SVG handling |
|------|----------|--------------|
| Hero / full-bleed 16:9 | `1536x1024` | `preserveAspectRatio="xMidYMid slice"` → crops to 1280×720 |
| Inline card 1:1 | `1024x1024` | Use as-is |
| Portrait card 3:4 | `1024x1536` | `preserveAspectRatio="xMidYMid slice"` |

**Negative prompt handling**: codex-image has no separate negative-prompt arg. Append the §2.4 / §6 negative list to the prompt body as `Avoid: <comma-separated list>`. gpt-image-2 honors this convention reliably.

**Filename**: `--filename <slot_name>` (no extension) writes directly to `<project_path>/images/<slot_name>.png`, matching the Image Resource List filename. Omit `--filename` only for standalone (non-pipeline) use.

**Pacing**: One image at a time, confirm file exists before next, 2–5 s spacing. codex exec has a 2-min timeout per image; if it times out, retry with `--quality medium`.

**Auth precondition**: `codex login status` must return "Logged in". If not, stop and instruct: "Run `codex login` in terminal." Do not silently skip image slots.

#### If codex-image is unavailable → HALT (no fallback backend)

codex-image is the **only** AI image path. If the Codex CLI is missing or `codex login` is
expired/sandboxed (e.g. claude.ai upload), **do NOT** switch to any other generator. Instead:
stop, keep the saved `images/image_prompts.md`, and tell the user to run `codex login` in their
terminal. (If they would rather supply their own assets, they can re-run with the Strategist's
"B) user-provided" image option and drop files into `project/images/` themselves — but the skill
never calls a non-codex-image generator on their behalf.)

### 4.4 Verification Phase

- Confirm all images are saved to `images/` directory
- Check filenames match the resource list
- Update image resource list status to "Generated"

---

## 5. Prompt Document Template

Use the following structure when creating `project/images/image_prompts.md`:

```markdown
# Image Generation Prompts

> Project: {project_name}
> Generated: {date}
> Color scheme: Primary {#HEX} | Secondary {#HEX} | Accent {#HEX}

---

## Image List Overview

| # | Filename | Type | Dimensions | Status |
|---|----------|------|-----------|--------|
| 1 | cover_bg.png | Background | 1920x1080 | Pending |

---

## Detailed Prompts

### Image 1: cover_bg.png

| Attribute | Value |
|-----------|-------|
| Purpose | Cover background |
| Type | Background |
| Dimensions | 1920x1080 (16:9) |
| Original description | Modern tech abstract background, deep blue gradient |

**Prompt**:
Abstract futuristic background with flowing digital waves...

**Alt Text**:
> Modern tech abstract background with deep blue gradient, digital waves, and particle effects

---

## Usage Instructions

1. Images are generated automatically via `/codex-image` (the only sanctioned backend)
2. codex-image unavailable? Halt and run `codex login` — do not substitute another generator
3. Rename generated images to the corresponding filenames
4. Place in the `images/` directory
```

---

## 6. Negative Prompt Quick Reference

### By Image Type

| Type | Recommended Negative Prompt |
|------|---------------------------|
| Background | `text, letters, watermark, faces, busy patterns, high contrast details` |
| Photography | `watermark, text overlay, artificial, CGI, illustration, cartoon, distorted faces` |
| Illustration | `realistic, photography, 3D render, complex textures, watermark` |
| Diagram | `cluttered, messy, overlapping elements, dark background, realistic` |
| Decorative pattern | `busy, cluttered, high contrast, distracting, photorealistic` |

### Universal Negative Prompts

- **Standard**: `text, watermark, signature, blurry, distorted, low quality`
- **Extended** (people scenarios): `text, watermark, signature, blurry, low quality, distorted, extra fingers, mutated hands, poorly drawn face, bad anatomy, extra limbs, disfigured, deformed`

---

## 7. Common Issues

### Default Inference When No "Generation Description" Provided

| Purpose | Default Inference |
|---------|------------------|
| Cover background | Abstract gradient background, reserve central text area |
| Chapter page background | Clean geometric pattern, monochrome focus |
| Team introduction page | Team collaboration scene illustration (flat style) |
| Data display page | Clean geometric pattern or solid color background |
| Product showcase | Product photography style, white or gradient background |

### When Images Are Unsatisfactory

Diagnose the problem category and apply a targeted prompt fix:

| Problem | Diagnosis | Prompt Adjustment |
|---------|-----------|-------------------|
| Wrong style | Image looks photorealistic when flat design was intended | Change style directive: replace `photography` with `flat design illustration` |
| Wrong colors | Colors don't match the design spec palette | Strengthen color directive: add explicit HEX codes, repeat color names |
| Wrong composition | Subject is off-center or layout doesn't fit the slide | Adjust composition directive: add `centered composition`, `rule of thirds`, or `wide negative space on left` |
| Wrong subject | Image depicts something different from what was described | Rewrite subject description with more specificity and concrete details |
| Low quality | Image is blurry, has artifacts, or lacks detail | Add `highly detailed, sharp focus, professional quality, 8K resolution` |

**Variant workflow**:
1. Keep the original prompt as "Variant A" in `image_prompts.md`
2. Create modified prompt as "Variant B" with targeted fixes from the table above
3. If needed, create "Variant C" with a different stylistic approach
4. Label all variants clearly so the user can compare results

---

## 8. Role Collaboration

### Handoff with Strategist

| Direction | Content |
|-----------|---------|
| Receives | Design Specification & Content Outline (with image resource list) |
| Trigger condition | User selected "C) AI generation" in "Image usage" |
| Key information | Color scheme, design style, canvas format |

### Handoff with Executor

| Direction | Content |
|-----------|---------|
| Delivers | All images placed in `project/images/` directory |
| Executor reference | `<image href="../images/xxx.png" .../>` |
| Path note | SVGs in `svg_output/`, images in `images/`; use relative path `../images/` |

---

## 9. Task Completion Checkpoint

### Must-complete Items

- [ ] Created prompt document `project/images/image_prompts.md`
- [ ] Each image has: type determination + optimized prompt + negative prompt + Alt Text
- [ ] Uses unified output format (2.1 standard format)
- [ ] Phase completion confirmation output

### Image Readiness (at least one must be satisfied)

- [ ] All images saved to `project/images/` directory
- [ ] Or: User clearly informed to self-generate using `image_prompts.md`

### Pipeline Flow

- [ ] User prompted to proceed to next step (switch to Executor role)

> **Critical check**: If `images/image_prompts.md` was not created, or the output format does not comply with 2.1 standard, the task is NOT complete.

### Completion Confirmation Output Format

```markdown
## Image_Generator Phase Complete

- [x] Created prompt document `project/images/image_prompts.md`
- [x] Generated optimized prompts for X images
- [x] All images saved to `images/` directory
- [x] Updated image resource list status

**Image Status Summary**:

| Filename | Type | Dimensions | Status |
|----------|------|-----------|--------|
| cover_bg.png | Background | 1920x1080 | Generated |

**Next step**: Switch to Executor role to begin SVG generation
```
