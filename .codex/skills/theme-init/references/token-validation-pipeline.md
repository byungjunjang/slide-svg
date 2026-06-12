# Token Validation Pipeline — /theme-init Step 3 상세

> 이 파일은 /theme-init Step 3의 상세 절차이며 해당 스텝 진입 시 로드한다.

### 3. Fill + validate + render (one command)

```bash
python3 .codex/skills/theme-init/scripts/init_theme.py \
    --fill-from /tmp/theme-draft.json
```

This runs:

1. **`fill_theme_defaults.py`** — reads your draft, fills any nulls /
   missing tokens with monochrome safe defaults, writes the complete
   theme to `.codex/skills/slide/references/theme-active.json`
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
   `anti-slop-theme.md`, `strategist.md`, `executor.md`,
   `image-generator.md` (AI-illustration palette/style lock — rendered
   from `image-generator.tpl.md`), and a
   `templates/layouts/<name>/DESIGN.md` skeleton (only when the file
   does not already exist — hand-authored DESIGN.md is preserved on
   re-runs; pass `--force` to `render_design_md.py` to overwrite).
   `render_layouts.py` is **source-aware**: it renders the per-theme
   composed source `templates/layouts/<name>/_shell_src/*.tpl.svg` when
   it exists (the Step 5 output below), otherwise the global baseline
   `templates/layouts/_source/*.tpl.svg` (stock jangpm geometry).
6. **`validate_shells.py`** (FATAL) — checks the rendered shells against
   the permanent locks (1280×720, font chain on every `<text>`, GM line
   on the content shell, no banned SVG features, content shell stays
   light). Aborts the chain before any downstream file references a
   broken shell.
7. **`preview_shells.py`** (non-fatal) — rasterizes the shells with
   sample content into `templates/layouts/<name>/_preview/` for the
   Step 5 review checkpoint. If neither `cairosvg` nor `svglib` is
   installed it can only write filled SVGs (no PNG thumbnails) — the
   Step 5c BLOCKING review then has nothing to show. Install a rasterizer
   first (`pip install cairosvg`, the crispest path) so the PNG review
   works; see the Step 5 header note.

> The first `/theme-init` run for a brand-new theme has no `_shell_src/`
> yet, so Step 3 renders the **baseline** (global `_source/`) shells —
> these are the reference Step 5 then re-composes.

The HTML gallery's `@font-face` block is generated dynamically from
whatever weight files actually exist under `assets/fonts/` matching the
active primary font (`<Family>-<Weight>.{otf,ttf,woff,woff2}`), so a new
theme that supplies its own font files just needs them dropped into
`assets/fonts/` before re-running.

If the new theme changes the **primary font family**, also re-run
`python3 .codex/skills/slide/scripts/dev/build_font_metrics.py` (after
updating its `FONT_FAMILY`/`WEIGHT_FILES` for the new OTFs) so the PPTX
exporter's glyph-advance cache (`svg_to_pptx/font_metrics.json`) matches.
Until it is rebuilt the exporter detects the mismatch and falls back to
heuristic text measurement with a `[WARN]` — safe, but text boxes get
the older, looser sizing.

If the validator rejects your draft, fix the specific field(s) it flags
and re-run — the script is idempotent.
