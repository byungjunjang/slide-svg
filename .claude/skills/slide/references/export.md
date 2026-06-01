# Export Reference

Guide for exporting generated slides from the `slide` skill pipeline to PPTX (and optionally PDF / Google Drive).

---

## Pipeline Position

Export is Step 7 of the skill workflow (see `SKILL.md` §Step 7). It runs **after** all SVGs are generated to `svg_output/` and speaker notes exist at `notes/total.md`. The three sub-commands MUST run one at a time, each in its own bash invocation.

```
svg_output/  ─►  [7.1 split notes]  ─►  notes/*.md
             ─►  [7.2 finalize_svg]  ─►  svg_final/
             ─►  [7.3 svg_to_pptx]   ─►  exports/<project>_<timestamp>.pptx
```

---

## Step 7.1 — Split Speaker Notes

```bash
python3 ${SKILL_DIR}/scripts/total_md_split.py <project_path>
```

Reads `notes/total.md` and writes per-page files into `notes/` (e.g., `01_표지.md`, `02_목차.md`). Each filename matches the corresponding SVG.

---

## Step 7.2 — Finalize SVGs

```bash
python3 ${SKILL_DIR}/scripts/finalize_svg.py <project_path>
```

Runs all SVG post-processing in one pass:

- Embeds icons referenced by `<use data-icon="...">` placeholders from `templates/icons/`
- Crops and embeds `<image href="../images/...">` references
- Flattens text to paths where PowerPoint font substitution would otherwise break layout (Pretendard stays, but any `<text>` with custom kerning or pattern-fill gets flattened)
- Converts rounded rects to `<path d="…">` (preserves rx/ry rendering across PPT renderers)

Output: `<project_path>/svg_final/*.svg`. **Never** use `cp` as a substitute; it skips icon embedding and PPT-safe conversions.

---

## Step 7.3 — Export PPTX

```bash
python3 ${SKILL_DIR}/scripts/svg_to_pptx.py <project_path> -s final
```

Produces two files in `exports/`:

| File | Method | When to use |
|------|--------|-------------|
| `<project>_<timestamp>.pptx` | Native DrawingML (shapes, text, tables remain editable in PowerPoint) | **Default.** Ship this. |
| `<project>_<timestamp>_svg.pptx` | Each slide embedded as an SVG image | Use only if PPT's native conversion mangles a specific visual (fallback) |

Speaker notes from `notes/*.md` are embedded in each slide's notes pane automatically.

### Flags

- `-s final` (required) — read from `svg_final/`, not `svg_output/`. Exporting from `svg_output/` skips post-processing.
- `--only native` — skip the SVG-embedded fallback (produces only the native PPTX)
- `--only legacy` — produce only the SVG-embedded fallback (rarely needed)

**Do not** add other flags.

---

## Design Token → PPTX Color Mapping

The exporter reads the active theme's CSS tokens from the Design Spec and writes them as literal hex into DrawingML. The token → hex values are **not duplicated here** — the single source of truth is the rendered color table in [`design-system.md`](./design-system.md), which `/theme-init` regenerates from `references/theme-active.json` every time the theme changes. Each `--<token>` maps 1:1 to the hex listed there (`--bg`, `--surface`, `--text`, `--accent`, `--accent-soft`, `--accent-ink`, `--border`, `--positive`, `--negative`, `--warning`, …).

> Why no table here: a hardcoded table goes stale the moment `/theme-init` swaps the active theme. `design-system.md` is the rendered source of truth — read the active palette there.

**Drift gate**: if the Strategist recommends any color that is not one of the active theme's tokens in `references/design-system.md`, the generation has drifted — stop and re-check the Design Spec's §III Visual Theme against `references/design-system.md`.

---

## Font Embedding

Pretendard is the active theme's default typeface (see `references/theme-active.json` → `typography`). For PPTX:

1. The SVG Executor writes `font-family="Pretendard"` on all `<text>` elements.
2. `finalize_svg.py` flattens text where fallback would be ambiguous, so the glyph geometry is preserved regardless of what the viewer's system has installed.
3. For recipients who will re-open and edit the PPTX, distribute the font alongside the deck (OTFs are at `assets/fonts/`), or rely on PowerPoint's font substitution (nearest match: Malgun Gothic on Windows / Apple SD Gothic Neo on macOS).

---

## Optional — PDF

The `slide` skill does not currently package a PDF export script. Options:

1. **LibreOffice headless** (recommended if installed):
   ```bash
   soffice --headless --convert-to pdf <project_path>/exports/<file>.pptx --outdir <project_path>/exports/
   ```
2. **PowerPoint / Keynote**: open the PPTX → Export → PDF.
3. **Google Slides**: upload PPTX → File → Download → PDF.

---

## Optional — Google Drive Upload

Not bundled. Use the `gws-drive-upload` skill (already installed globally) with the PPTX path. Example:

```
/gws-drive-upload <project_path>/exports/<file>.pptx
```

---

## Local Preview

Before export, verify SVG rendering:

```bash
python3 -m http.server -d <project_path>/svg_final 8000
# then open http://localhost:8000 in a browser
```

Check: 1280×720 frame fits without overflow, `.gm` line is present on every content slide, monochrome + single accent rule holds.

---

## Troubleshooting

Common export issues and fixes are tracked in the project's GitHub Issues. If a slide renders correctly as SVG but gets mangled in the native PPTX, the `*_svg.pptx` fallback is the escape hatch — ship that, file a fix to `svg_to_pptx.py`.
