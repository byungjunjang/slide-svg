# PPT Master Toolset

This directory contains user-facing scripts for conversion, project setup, SVG processing, and export.

AI image generation is handled by the bundled `/codex-image` skill (Codex CLI OAuth → `gpt-image-2`); it lives in `.claude/skills/codex-image/` rather than under `scripts/`.

## Directory Layout

- Top-level `scripts/`: runnable entry scripts
- `scripts/source_to_md/`: source-document → Markdown converters (`pdf_to_md.py`, `doc_to_md.py`, `ppt_to_md.py`, `web_to_md.py`, `web_to_md.cjs`)
- `scripts/template_import/`: internal PPTX reference-preparation helpers used by `pptx_template_import.py`
- `scripts/svg_finalize/`: internal post-processing helpers used by `finalize_svg.py`
- `scripts/docs/`: topic-focused script documentation

## Quick Start

Typical end-to-end workflow:

```bash
./scripts/_py.sh scripts/source_to_md/pdf_to_md.py <file.pdf>
# or
./scripts/_py.sh scripts/source_to_md/ppt_to_md.py <deck.pptx>
./scripts/_py.sh scripts/project_manager.py init <project_name> --format ppt169
./scripts/_py.sh scripts/project_manager.py import-sources <project_path> <source_files...> --move
./scripts/_py.sh scripts/total_md_split.py <project_path>
./scripts/_py.sh scripts/finalize_svg.py <project_path>
./scripts/_py.sh scripts/svg_to_pptx.py <project_path> -s final
```

Repository update:

```bash
./scripts/_py.sh scripts/dev/update_repo.py
```

## Script Index

| Area | Primary scripts | Documentation |
|------|-----------------|---------------|
| Conversion | `source_to_md/pdf_to_md.py`, `source_to_md/doc_to_md.py`, `source_to_md/ppt_to_md.py`, `source_to_md/web_to_md.py`, `source_to_md/web_to_md.cjs` | [docs/conversion.md](./docs/conversion.md) |
| Project management | `project_manager.py`, `error_helper.py`, `pptx_template_import.py` | [docs/project.md](./docs/project.md) |
| SVG pipeline | `finalize_svg.py`, `svg_to_pptx.py`, `total_md_split.py`, `svg_quality_checker.py` | [docs/svg-pipeline.md](./docs/svg-pipeline.md) |
| Image tools | `analyze_images.py` (size/aspect inspection only — generation is `/codex-image`) | — |
| Dev / maintenance utilities | `dev/update_repo.py`, `dev/batch_validate.py`, `dev/generate_examples_index.py`, `dev/svg_position_calculator.py`, `dev/rotate_images.py`, `dev/pptx_animations.py` | [dev/README.md](./dev/README.md) |
| Troubleshooting | validation, preview, export, dependency issues | [docs/troubleshooting.md](./docs/troubleshooting.md) |

## High-Frequency Commands

Conversion:

```bash
./scripts/_py.sh scripts/source_to_md/pdf_to_md.py <file.pdf>
./scripts/_py.sh scripts/source_to_md/ppt_to_md.py <deck.pptx>
./scripts/_py.sh scripts/source_to_md/doc_to_md.py <file.docx>
./scripts/_py.sh scripts/source_to_md/web_to_md.py <url>
```

Project setup:

```bash
./scripts/_py.sh scripts/project_manager.py init <project_name> --format ppt169
./scripts/_py.sh scripts/project_manager.py import-sources <project_path> <source_files...> --move
./scripts/_py.sh scripts/project_manager.py validate <project_path>
```

Template source import:

```bash
./scripts/_py.sh scripts/pptx_template_import.py <template.pptx>
./scripts/_py.sh scripts/pptx_template_import.py <template.pptx> --manifest-only
```

Post-processing and export:

```bash
./scripts/_py.sh scripts/total_md_split.py <project_path>
./scripts/_py.sh scripts/finalize_svg.py <project_path>
./scripts/_py.sh scripts/svg_to_pptx.py <project_path> -s final
```

Image inspection (size/aspect for layout planning):

```bash
./scripts/_py.sh scripts/analyze_images.py <project_path>/images
```

(For AI image generation, use the `/codex-image` slash command — see `.claude/skills/codex-image/README.md`.)

Repository update:

```bash
./scripts/_py.sh scripts/dev/update_repo.py
./scripts/_py.sh scripts/dev/update_repo.py --skip-pip
```

## Recommendations

- Keep one user-facing entry point per workflow at the top level of `scripts/`
- Move provider-specific or helper internals into subdirectories
- Prefer the unified entry points `project_manager.py` and `finalize_svg.py`
- Prefer `svg_final/` over `svg_output/` when exporting

## Related Docs

- [Conversion Tools](./docs/conversion.md)
- [Project Tools](./docs/project.md)
- [SVG Pipeline Tools](./docs/svg-pipeline.md)
- [Troubleshooting](./docs/troubleshooting.md)
- [AGENTS Guide](../../../AGENTS.md)

_Last updated: 2026-04-09_
