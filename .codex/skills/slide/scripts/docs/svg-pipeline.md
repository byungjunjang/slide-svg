# SVG Pipeline Tools

These tools cover post-processing, SVG validation, speaker notes, and PPTX export.

## Recommended Pipeline

Run these steps in order:

```bash
./scripts/_py.sh scripts/total_md_split.py <project_path>
./scripts/_py.sh scripts/finalize_svg.py <project_path>
./scripts/_py.sh scripts/svg_to_pptx.py <project_path> -s final
```

## `finalize_svg.py`

Unified post-processing entry point. This is the preferred way to run SVG cleanup.

It aggregates:
- `embed_icons.py`
- `crop_images.py`
- `fix_image_aspect.py`
- `embed_images.py`
- `flatten_tspan.py`
- `svg_rect_to_path.py`

## `svg_to_pptx.py`

Convert project SVGs into PPTX.

```bash
./scripts/_py.sh scripts/svg_to_pptx.py <project_path> -s final
./scripts/_py.sh scripts/svg_to_pptx.py <project_path> -s final --only native
./scripts/_py.sh scripts/svg_to_pptx.py <project_path> -s final --only legacy
./scripts/_py.sh scripts/svg_to_pptx.py <project_path> -s final --no-notes
./scripts/_py.sh scripts/svg_to_pptx.py <project_path> -s final --no-embed-fonts
./scripts/_py.sh scripts/svg_to_pptx.py <project_path> -t none
./scripts/_py.sh scripts/svg_to_pptx.py <project_path> -s final --auto-advance 3
```

Behavior:
- Default output: timestamped pair in `exports/` — `<project_name>_<timestamp>.pptx` (native editable) + `<project_name>_<timestamp>_svg.pptx` (SVG snapshot)
- Recommended source directory: `svg_final/`
- Speaker notes are embedded automatically unless `--no-notes` is used
- The installed Pretendard TrueType faces the deck uses are embedded (EOT, full fonts) unless `--no-embed-fonts` is used; without an installed static `Pretendard*.ttf` the export skips embedding and prints a `[warn]` line

Dependency:

```bash
pip install python-pptx
```

## `total_md_split.py`

Split `total.md` into per-slide note files.

```bash
./scripts/_py.sh scripts/total_md_split.py <project_path>
./scripts/_py.sh scripts/total_md_split.py <project_path> -o <output_directory>
./scripts/_py.sh scripts/total_md_split.py <project_path> -q
```

Requirements:
- Each section begins with `# `
- Heading text matches the SVG filename
- Sections are separated by `---`

## `svg_quality_checker.py`

Validate SVG technical compliance.

```bash
./scripts/_py.sh scripts/svg_quality_checker.py examples/project/svg_output/01_cover.svg
./scripts/_py.sh scripts/svg_quality_checker.py examples/project/svg_output
./scripts/_py.sh scripts/svg_quality_checker.py examples/project
./scripts/_py.sh scripts/svg_quality_checker.py examples/project --format ppt169
./scripts/_py.sh scripts/svg_quality_checker.py --all examples
./scripts/_py.sh scripts/svg_quality_checker.py examples/project --export
./scripts/_py.sh scripts/svg_quality_checker.py examples/project --all-warnings
./scripts/_py.sh scripts/svg_quality_checker.py examples/project --outline
```

`--outline` prints one `NN | title | .gm` row per page instead of checking — the deck's message line for a flow review (the title is the largest headline-band line with 4+ letters, so a hero number is never the title).

Checks include:
- `viewBox`
- banned elements
- width/height consistency
- line-break structure
- text geometry (warnings): text-box overlap, safe area, and a visible straight stroke running through a text line. Text is measured per run (an inline `<tspan>` at its own font-size) and per line (a `<tspan>` with its own x / y / dy starts a new line)

Each file prints its first 2 warnings; `--all-warnings` lists them all.

## `svg_copy.py`

Guarded copy polish of the text in `svg_output/` (Step 6 deck sweep).

```bash
./scripts/_py.sh scripts/svg_copy.py extract <project_path> -o <project_path>/copy_lines.json
./scripts/_py.sh scripts/svg_copy.py apply <project_path> <edits.json>
```

- `extract` writes every text line per page (`{"07": {"file": ..., "lines": [...]}}`).
- `apply` takes `[{"page": "07", "old": "<exact line>", "new": "<line>"}]`. It refuses an edit that changes a number, a number+unit pair or a Latin word, or whose old line is not exactly one text node on the page; files keep their bytes (line endings) apart from the edit. Report: `<project_path>/copy_polish.json`.

## `render_page.py`

Render one `svg_output` page to a PNG for the Executor's visual self-review (Step 6, after the page check).

```bash
./scripts/_py.sh scripts/render_page.py <project_path>/svg_output/<page>.svg
./scripts/_py.sh scripts/render_page.py <project_path>/svg_output/<page>.svg --width 1280 --out page.png
```

- Draws the page with a headless Chrome / Chromium / Edge (about 1 s per page), so Hangul uses the installed Pretendard; icons are embedded into a copy under `<project_path>/_render/` first. svglib is not used: it draws Hangul as tofu boxes and drops fill opacity.
- No browser, or a failed render: prints `[skip]` and exits 0 — the review is an aid, never a gate. `CHROME_BIN` picks a binary; an empty value disables rendering.

## `svg_position_calculator.py`

Analyze or pre-calculate chart coordinates.

Common commands:

```bash
./scripts/_py.sh scripts/svg_position_calculator.py analyze <svg_file>
./scripts/_py.sh scripts/svg_position_calculator.py interactive
./scripts/_py.sh scripts/svg_position_calculator.py calc bar --data "East:185,South:142"
./scripts/_py.sh scripts/svg_position_calculator.py calc pie --data "A:35,B:25,C:20"
./scripts/_py.sh scripts/svg_position_calculator.py from-json config.json
```

Use this when chart geometry needs to be verified before or after AI generation.

## Advanced Standalone Tools

### `flatten_tspan.py`

```bash
./scripts/_py.sh scripts/svg_finalize/flatten_tspan.py examples/<project>/svg_output
./scripts/_py.sh scripts/svg_finalize/flatten_tspan.py path/to/input.svg path/to/output.svg
```

### `svg_rect_to_path.py`

```bash
./scripts/_py.sh scripts/svg_finalize/svg_rect_to_path.py <project_path>
./scripts/_py.sh scripts/svg_finalize/svg_rect_to_path.py <project_path> -s final
./scripts/_py.sh scripts/svg_finalize/svg_rect_to_path.py path/to/file.svg
```

Use when rounded corners must survive PowerPoint shape conversion.

### `fix_image_aspect.py`

```bash
./scripts/_py.sh scripts/svg_finalize/fix_image_aspect.py path/to/slide.svg
./scripts/_py.sh scripts/svg_finalize/fix_image_aspect.py 01_cover.svg 02_toc.svg
./scripts/_py.sh scripts/svg_finalize/fix_image_aspect.py --dry-run path/to/slide.svg
```

Use when embedded images stretch after PowerPoint shape conversion.

### `embed_icons.py`

```bash
./scripts/_py.sh scripts/svg_finalize/embed_icons.py output.svg
./scripts/_py.sh scripts/svg_finalize/embed_icons.py svg_output/*.svg
./scripts/_py.sh scripts/svg_finalize/embed_icons.py --dry-run svg_output/*.svg
```

Replaces `<use data-icon="chunk/name" .../>`, `<use data-icon="tabler-filled/name" .../>` and `<use data-icon="tabler-outline/name" .../>` placeholders with actual SVG path elements. Use for manual icon embedding checks outside `finalize_svg.py`.

## PPT Compatibility Rules

Use PowerPoint-safe transparency syntax:

| Avoid | Use instead |
|------|-------------|
| `fill=\"rgba(...)\"` | `fill=\"#hex\"` + `fill-opacity` |
| `<g opacity=\"...\">` | Set opacity on each child |
| `<image opacity=\"...\">` | Overlay with a mask layer |

PowerPoint also has trouble with:
- marker-based arrows
- unsupported filters
- direct SVG features not mapped to DrawingML
