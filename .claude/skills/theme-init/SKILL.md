---
name: theme-init
description: >
  One-shot design-system replacement for the slide-svg `/slide` skill. The
  calling agent reads the user's design guide, extracts tokens into a theme
  JSON matching the v1 token contract, runs the render pipeline, and every
  downstream reference (SVG layouts, HTML gallery CSS, design-system.md,
  anti-slop-theme.md, strategist.md, executor.md) is regenerated so the next
  `/slide` run produces decks in the new visual language. Use when the user
  asks to "change the design system", "replace the theme", "set up a new
  brand", "테마 교체", "디자인 시스템 바꿔", "새 브랜드 적용", or invokes
  "/theme-init".
---

# /theme-init — Active-Theme Replacement

> **Model.** One user = one design system. The slide-svg pipeline bakes
> tokens into DrawingML at export time, so runtime multi-theming is
> impossible. `/theme-init` is a **one-shot full replacement** — every
> reference file is rewritten from `theme-active.json` and every SVG
> layout is re-rendered from `_source/*.tpl.svg`. Run `/theme-init` again
> with a different guide to switch.
>
> **Agent-driven extraction.** You (the agent invoking this skill) read
> the design guide and produce `theme-active.json` yourself. There is no
> internal LLM call, no Anthropic API dependency, no API key. The Python
> scripts under `scripts/` handle only deterministic work: fill-nulls,
> schema validation, and template rendering.

## When to run

- First-time onboarding for a new brand (replace the stock Jangpm theme)
- Rebranding an existing deck system (new primary color, new font chain,
  new voice guidelines)
- Editing `theme-active.json` by hand and needing to regenerate derived
  files

Do **NOT** run this skill to generate slides — that's `/slide`.

## Workflow (what you, the agent, do)

### 1. Read the design guide

The user will point you at a markdown file (or paste guide text directly).
Read the whole thing. Watch for:

- **Name**: lowercase-kebab identifier (`acme-warm`, `nova-dark`) + human
  display name (`"Acme Warm"`)
- **Colors**: hex values or named colors you can resolve (e.g. "crimson
  red" → `#DC143C`). If the guide only names a primary accent, infer the
  `accent-soft` / `accent-ink` / surface / border shades to match (lighter
  tint of accent for soft, darker for ink; warm/cool neutrals for
  surfaces based on the overall tone).
- **Typography**: primary font family. If the guide only names it (e.g.,
  "Noto Sans KR"), assemble a full CSS chain with the appropriate
  regional fallbacks (`'Apple SD Gothic Neo'`, `'Malgun Gothic'`,
  `sans-serif` for Korean; `-apple-system, 'Segoe UI', Roboto,
  sans-serif` for Latin-first).
- **Voice**: tone, POV, register, forbidden phrases, GM style hint

### 2. Produce the theme JSON

Write a JSON object conforming to the v1 token contract
(`references/token-contract.json` — read it before your first extraction).
Key rules:

1. **Use `null` for anything the guide doesn't specify.** The downstream
   `fill_theme_defaults.py` substitutes monochrome grayscale defaults for
   nulls. Do **NOT** invent brand-looking values for missing tokens —
   null + safe default is better than a plausible-but-wrong color.
2. **Color format: 6-digit uppercase hex (`#RRGGBB`).** Lowercase or
   3-digit shorthand will fail schema validation.
3. **Font chain must be complete.** Primary first, then regional
   fallbacks, ending with `sans-serif`. If the guide only names the
   primary family, assemble the chain yourself.
4. **Preserve the 7-step type scale defaults** unless the guide
   explicitly overrides specific sizes. The defaults (display 56 /
   display-sm 40 / headline 32 / title 18.4 / body 15.2 / caption 12.8 /
   label 12.8) are calibrated to the 1280×720 canvas — changing them
   without cause breaks layout geometry.
5. **Spacing / radius / stroke**: override only when the guide
   explicitly calls for a non-standard rhythm. The 8px-grid defaults are
   usually right.
6. **`voice.forbidden_phrases`** is the phrases the author *explicitly*
   says to avoid. Empty array `[]` if none specified — do NOT fill in
   guesses.

Write your output to a scratch file, for example
`/tmp/theme-draft.json`.

### 3. Fill + validate + render (one command)

```bash
python3 .claude/skills/theme-init/scripts/init_theme.py \
    --fill-from /tmp/theme-draft.json
```

This runs:

1. **`fill_theme_defaults.py`** — reads your draft, fills any nulls /
   missing tokens with monochrome safe defaults, writes the complete
   theme to `.claude/skills/slide/references/theme-active.json`
2. **`validate_theme.py`** — schema check against the v1 contract.
   Rejects with a pointed error list if anything is malformed.
3. **`validate_fonts.py`** — checks the primary family in
   `typography.font-chain` against `assets/fonts/`. If files are present
   it logs OK; if not, it warns and (when "Arial" is missing from the
   chain) auto-injects "Arial" before the trailing generic family so the
   gallery and SVG output have a guaranteed system fallback.
4. **Diff summary** — shows which token groups changed since the prior
   theme.
5. **Render chain** — regenerates `templates/layouts/<name>/*.svg`,
   `colors_and_type.css` (HTML gallery), `design-system.md`,
   `anti-slop-theme.md`, `strategist.md`, `executor.md`, and a
   `templates/layouts/<name>/DESIGN.md` skeleton (only when the file
   does not already exist — hand-authored DESIGN.md is preserved on
   re-runs; pass `--force` to `render_design_md.py` to overwrite).

The HTML gallery's `@font-face` block is generated dynamically from
whatever weight files actually exist under `assets/fonts/` matching the
active primary font (`<Family>-<Weight>.{otf,ttf,woff,woff2}`), so a new
theme that supplies its own font files just needs them dropped into
`assets/fonts/` before re-running.

If the validator rejects your draft, fix the specific field(s) it flags
and re-run — the script is idempotent.

### 4. Author the DESIGN.md content (agent task — required for slide-plan)

The render chain produces a DESIGN.md *skeleton* at
`.claude/skills/slide/templates/layouts/<theme.name>/DESIGN.md`. Token-driven
sections (palette table, type scale, font chain, spacing grid, voice
anchors) are pre-filled from `theme-active.json`. Sections requiring
preset-specific judgment are marked with `<!-- AGENT-FILL §N ... -->`
comments — these MUST be authored by the agent before `/slide-plan` can
consume this preset.

Sections requiring agent authorship:

| § | Section | What to write |
|---|---|---|
| 1 | Visual theme & atmosphere | mood adjectives, moodboard, anti-mood, litmus test |
| 2.2 | Contrast & accent budget | accent events per slide, semantic color policy |
| 2.3 | Background hierarchy | bg → surface-alt → surface → accent-soft rules |
| 3.3 | Typography hierarchy rules | display vs headline use, body density rules |
| 4.2 | Slide-level spacing | outer / card padding values |
| 4.3 | Density floors | min content layers, text-only slide policy |
| 4.4 | Density vs sparsity | preset's density philosophy |
| 5 | **Layout grammar** | this preset's `recommended_layout_family` vocabulary — group `references/patterns.md` patterns into 5–8 families |
| 5.1 | **Hybrid Pattern Catalog** | 7–11 multi-element body patterns + content-shape → first-choice-primitive table |
| 5.2 | **Variation Inspirations** | 4–6 intentional variations per hybrid pattern (recorded per slide via executor.md §2 audit) |
| 6.1–6.6 | Page anatomy | header / title / body / GM / footer rules |
| 7 | Page flow | chapter slide cadence, agenda placement |
| 8.1 | Chart role → template map | rhetorical role × `charts_index.json` template |
| 8.2–8.4 | Chart / table styling | legend chrome, table header treatment, chart-takeaway adjacency |
| 9.2–9.6 | Icon system specifics | placeholder syntax, sizing, badge rules, wrapper policy |
| 10 | Anti-patterns | 12–18 plan-time rejects |

**Reference example:** the canonical jangpm DESIGN.md at
`.claude/skills/slide/templates/layouts/jangpm/DESIGN.md` is hand-authored
and complete. Use it as the calibration for the level of specificity
expected in each section.

**User review checkpoint (BLOCKING):** after authoring, present a one-page
summary of the DESIGN.md to the user (which families were chosen, which
chart roles were mapped, key anti-patterns) and obtain explicit
confirmation before proceeding. The DESIGN.md is the contract between
this preset and `/slide-plan` — the user must agree before downstream
decks inherit it.

### 5. Verify

After the render completes:

1. **Token check.** `git diff` should show the expected token values in
   `design-system.md` (color table) and `strategist.md` §e (Color
   Scheme).
2. **Gallery check.**
   ```bash
   python3 -m http.server -d .claude/skills/slide/references/jangpm-patterns 8000
   ```
   Open `http://localhost:8000/` — every page should reflect the new
   accent color and font chain.
3. **Live slide build.** Run `/slide` on a 5-page sample brief. Generated
   SVGs under `svg_output/*.svg` must use the new accent hex, the full
   active-theme font chain, and a GM line on every content slide.
4. **PPTX export.** Run the standard post-processing (`total_md_split.py`
   → `finalize_svg.py` → `svg_to_pptx.py -s final`). Open in PowerPoint /
   Keynote / the mobile viewer — text must render in the primary font
   with correct color tokens.

## Alternative entry points

### Re-render after hand-editing theme-active.json

If you edited `theme-active.json` directly (not a new extraction), just
run without `--fill-from`:

```bash
python3 .claude/skills/theme-init/scripts/init_theme.py
```

This skips fill, goes straight to validate → render.

### Dry run

Stop after validate, don't touch the render outputs:

```bash
python3 .claude/skills/theme-init/scripts/init_theme.py \
    --fill-from /tmp/draft.json --dry-run
```

### Interactive approval gate

Pause after the diff summary and prompt the operator for `y/N` before
running the render chain — handy for local runs where you want to
eyeball what's about to change:

```bash
python3 .claude/skills/theme-init/scripts/init_theme.py \
    --fill-from /tmp/draft.json --confirm
```

`--confirm` aborts safely if stdin is not a tty (e.g., piped or run
from a non-interactive harness) so a misused pipe never auto-accepts
the render. For non-interactive flows just omit the flag — the pipeline
runs to completion with only the diff summary printed.

## Requirements

- `jsonschema>=4.17.0` (listed in `.claude/skills/slide/requirements.txt`)

That's it. No API key, no external SDK. The agent's extraction is done
natively before the script runs.

## Output

After a successful run the following files are updated in place:

| Path | Role |
|------|------|
| `.claude/skills/slide/references/theme-active.json` | Source of truth for all downstream renders |
| `.claude/skills/slide/references/design-system.md` | Human-readable design token reference (rendered) |
| `.claude/skills/slide/references/anti-slop-theme.md` | Theme-literal enforcement rules (rendered) |
| `.claude/skills/slide/references/strategist.md` | Eight-Confirmations prompt with active-theme values |
| `.claude/skills/slide/references/executor.md` | SVG-generation prompt with active-theme values |
| `.claude/skills/slide/references/colors_and_type.css` | CSS vars powering the HTML gallery |
| `.claude/skills/slide/templates/layouts/<theme-name>/*.svg` | Cover / chapter / content / ending shells |

## Canvas lock (non-negotiable)

1280×720 is **permanently locked** across themes. Changing canvas size
breaks every coordinate in `_source/*.tpl.svg` and the executor's layout
remediation rules. A different aspect ratio is out of scope for
`/theme-init` — it requires a separate tooling project.

## Failure modes

| Symptom | Cause | Fix |
|---------|-------|-----|
| `jsonschema missing` | Deps not installed | `pip install -r .claude/skills/slide/requirements.txt` |
| `could not parse input as JSON` from fill step | Your draft is not valid JSON (trailing comma, missing quote, etc.) | Fix the draft and re-run |
| `theme-active.json FAILS the v1 token contract (N error(s))` | Draft violated the schema after filling (wrong hex shape, non-numeric size) | Read the stderr list, fix the specific fields in your draft, re-run |
| `render error: missing theme token: foo.bar` | A template references a token the schema doesn't contain | Update the template OR update the contract v1 (+ version bump) |
| SVG renders with 3-element font chain instead of 5 | The tpl.svg was hand-edited and the old chain crept back in | Run the render again; the scripts are idempotent |

## Locks that persist across themes

| Lock | Why |
|------|-----|
| Canvas 1280×720 | Hard-coded in layout templates and executor's remediation math |
| Serial pipeline discipline | Executor Step 6 main-agent ownership + sequential pages — see slide/SKILL.md §Global Execution Discipline |
| GM line on every content slide | Core anti-slop principle (rule T6) — every theme must define its GM style hint |
| Native SVG→PPTX (no image flattening) | The export pipeline's entire value prop |

## Extraction cheat-sheet

When reading the design guide, the 15 required theme-identity fields are:

```
name                    lowercase-kebab
display_name            human label
description             one-sentence summary
colors.accent           primary brand hex
colors.accent-soft      accent-tinted bg (lighter)
colors.accent-ink       accent pressed (darker)
colors.bg               page background
colors.surface          card background
colors.text             primary text (never pure #000)
colors.text-secondary   muted secondary
colors.border           default divider
typography.font-chain   complete CSS font-family chain
voice.tone              e.g. "editorial, analytical, declarative"
voice.pov               e.g. "third-person institutional"
voice.register          e.g. "Korean lecture / report"
```

The other ~25 tokens (surface-alt, text-tertiary, border-strong, semantic
colors + soft variants, full type scale, radius/stroke/spacing, icon
pack, forbidden phrases, GM hint) fall back to safe defaults if the
guide doesn't specify them. Fill them in explicitly only when the guide
calls for something different.

### Derived-color hints

When the design guide gives you only a primary `accent` and base `bg` /
`surface` / `border` / `text`, derive the missing siblings rather than
leaving them `null` for monochrome defaults. This produces a more
on-brand result than the grayscale fallback.

| Token | Derivation rule | Why |
|-------|----------------|-----|
| `accent-soft` | accent lightened by ~85% (mix with white at ~15% opacity), or use accent's hue at very high lightness (~92–95% L in HSL) | accent-tinted backgrounds for highlight columns / soft chips |
| `accent-ink` | accent darkened by ~25–35% (mix with black at ~30% opacity), or drop ~20–25% L in HSL | pressed/active variant + dark-mode-safe accent |
| `surface-alt` | bg darkened by 1–3% (warm brands: warmer; cool brands: cooler) | grouped-row stripes, subtle nesting |
| `text-secondary` | text lightened ~30–40% toward bg (mid-gray that still passes 4.5:1 against surface) | captions, GM line |
| `text-tertiary` | text lightened ~50–60% toward bg | page numbers, very-secondary annotations |
| `border-strong` | border darkened ~20% (or one step darker on the same gray ramp) | emphasis dividers, table headers |
| `positive-soft` / `negative-soft` / `warning-soft` | corresponding semantic hue at ~92% L (same recipe as `accent-soft`) | data badges, status pills |

Keep all derivations in the same hue family as the source — don't shift
warm→cool when darkening accent, etc. If the guide explicitly publishes
a different value for any of these, the published value always wins.

For the soft-variant trio (positive/negative/warning), if the guide only
gives the saturated semantic colors, deriving the soft variants by the
recipe above is **strongly preferred** over null — null leaves data
badges with insufficient contrast against `bg`.

**`assets.character` is optional.** Set it to a path string (relative
to repo root, e.g.,
`.claude/skills/slide/templates/layouts/<theme>/assets/brand/<image>.png`)
when the brand provides an instructor-persona illustration; otherwise
leave it `null`. Templates render `_(not provided)_` for null and the
strategist/executor instructions tell the pipeline to skip persona
slides rather than invent a stand-in.

See `examples/acme-warm.md` for a reference design guide and
`.claude/skills/slide/references/theme-active.json` (Jangpm) for a fully
populated theme.

## Design notes

Institutional knowledge for anyone touching theme-init internals. These
gotchas are not derivable from the code alone and have repeatedly cost
time when re-discovered.

**Agent-driven extraction is the leverage point.** `/theme-init` makes
no external API call — the calling Claude agent reads the design guide
and produces the JSON itself. `fill_theme_defaults.py` only fills
missing fields with safe defaults; it does not improve extraction
quality. The lever for better Carbon-from-IBM-guide / Acme-warm-from-PDF
output is **strengthening this SKILL.md's extraction rules**, not the
Python.

**Canvas 1280×720 is a cross-theme lock.** Layout coordinates in
`_source/*.tpl.svg` and the executor's text-overflow remediation math
(`char_count × font_size × 0.55` and friends) are calibrated to this
canvas. A v2 token contract may extend tokens but must not change
canvas — anything else is a slide-svg fork, not a theme.

**`theme-active.json` is overwritten in place.** No backup is taken on
init_theme; rollback is `git log -- .claude/skills/slide/references/theme-active.json`
followed by `git show <sha>:<path>`. A future
`themes/<name>.json` registry would solve this structurally, but until
that lands, treat each `/theme-init` run as destructive.

**The render chain is idempotent.** Running `init_theme.py` twice on
the same theme must produce a clean `git diff`. This is the regression
check — if a same-theme rerun shows changes, a template or script
drifted. The pytest smoke under `tests/` covers the unit-level pieces;
idempotence at the orchestration level is asserted by repeat runs.

**No external LLM calls remain in this skill.** The early Phase-1
`parse_design_guide.py` used the Anthropic API + prompt caching to do
extraction. That code was removed in commit `0f1908a` when the model
flipped to agent-driven. If a future need re-introduces an external LLM
hop, do not revert-reference that commit — write the new path fresh,
since the old design assumed Opus calling itself, which is
now-obsolete.

**Out of scope for this skill** (so contributors stop asking):
- Runtime multi-theme. Structurally impossible — PPTX export bakes
  tokens into DrawingML. Each `/theme-init` is full replacement.
- Canvas format expansion (e.g., 1920×1080, A4). Separate tooling
  project; not a theme concern.
- Image generation (AI illustrations). Lives in the `/codex-image`
  skill / Image_Generator role, intentionally decoupled.
