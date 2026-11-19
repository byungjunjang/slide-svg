# Project Tools

Project tools create, validate, and inspect the standard PPT Master workspace.

## `project_manager.py`

Main entry point for project setup and validation.

```bash
./scripts/_py.sh scripts/project_manager.py init <project_name> --format ppt169
./scripts/_py.sh scripts/project_manager.py import-sources <project_path> <source1> [<source2> ...]
./scripts/_py.sh scripts/project_manager.py stage <project_path> <stage> running|done|skipped|failed [--summary S] [--artifact P]... [--confirmation C]
./scripts/_py.sh scripts/project_manager.py validate <project_path>
./scripts/_py.sh scripts/project_manager.py info <project_path>
```

Notes:
- `init` also writes `pipeline_status.json` (`project`, `mode`, empty `stages`); `stage` records one stage in it — `started_at` on its first record, `completed_at` on `done` / `skipped` / `failed`
- Files outside the repo are copied into `sources/` by default
- With `--move`, files outside the repo are moved into `sources/`
- Files already inside the repo are moved into `sources/` by default (with a stderr
  note), to avoid leaving unintended artifacts that could be committed by mistake.
  Pass `--copy` to force a copy for in-repo sources instead.
- `--move` and `--copy` are mutually exclusive.

Common formats:
- `ppt169`
- `ppt43`
- `xiaohongshu`
- `moments`
- `story`
- `banner`
- `a4`

Examples:

```bash
./scripts/_py.sh scripts/project_manager.py init my_presentation --format ppt169
./scripts/_py.sh scripts/project_manager.py validate projects/my_presentation_ppt169_20251116
./scripts/_py.sh scripts/project_manager.py info projects/my_presentation_ppt169_20251116
```

## `project_utils.py`

Shared helper module used by other scripts.

Typical use:

```python
from project_utils import get_project_info, validate_project_structure
```

You can also run it directly for quick checks:

```bash
./scripts/_py.sh scripts/project_utils.py <project_path>
```

## `batch_validate.py`

Batch-check project structure and compliance.

```bash
./scripts/_py.sh scripts/batch_validate.py examples
./scripts/_py.sh scripts/batch_validate.py examples projects
./scripts/_py.sh scripts/batch_validate.py --all
./scripts/_py.sh scripts/batch_validate.py examples --export
```

Use this for repository-wide health checks before release or cleanup.

## `generate_examples_index.py`

Rebuild `examples/README.md` automatically.

```bash
./scripts/_py.sh scripts/generate_examples_index.py
./scripts/_py.sh scripts/generate_examples_index.py examples
```

## `pptx_template_import.py`

Unified PPTX preparation entry point for `/create-template`.

```bash
./scripts/_py.sh scripts/pptx_template_import.py <template.pptx>
./scripts/_py.sh scripts/pptx_template_import.py <template.pptx> -o <output_dir>
./scripts/_py.sh scripts/pptx_template_import.py <template.pptx> --manifest-only
./scripts/_py.sh scripts/pptx_template_import.py <template.pptx> --keep-raw
./scripts/_py.sh scripts/pptx_template_import.py <template.pptx> --skip-manifest
```

Notes:
- Extracts reusable media assets from `ppt/media/`
- Summarizes slide size, theme colors, and font metadata
- Infers background image inheritance across slide, layout, and master
- Generates `manifest.json`, `analysis.md`, `master_layout_refs.json`, `master_layout_analysis.md`, `assets/`, cleaned slide SVGs, and `reference_svg_selection.json`
- Native SVG export is Windows-only because it uses installed Microsoft PowerPoint
- On macOS, the script falls back to exporting PDF via Keynote and then converts PDF pages to SVG
- Writes cleaned SVG files to `svg/` after externalizing inline Base64 image payloads
- Required in `/create-template` whenever the reference source is `.pptx`
- Default output directory is `<pptx_stem>_template_import/`
- Use `--manifest-only` when you explicitly want only the lightweight import output without slide SVG export
- Intended for template reference preparation, not for final 1:1 template delivery

Implementation note:
- Internal helpers for this workflow live under `scripts/template_import/`

## `error_helper.py`

Show standardized fixes for common project errors.

```bash
./scripts/_py.sh scripts/error_helper.py
./scripts/_py.sh scripts/error_helper.py missing_readme
./scripts/_py.sh scripts/error_helper.py missing_readme project_path=my_project
```
