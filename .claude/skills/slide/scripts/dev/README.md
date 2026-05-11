# scripts/dev/ — Maintenance & Dev Utilities

These scripts are **not part of the active `/slide` pipeline**. They are kept as developer / maintenance utilities and are not invoked by `SKILL.md`. Moved here from `scripts/` to clarify scope; left in the tree (rather than deleted) so authors can still reach for them when needed.

| Script | Purpose |
|--------|---------|
| `update_repo.py` | Pull latest changes and sync `requirements.txt` via pip when it changes. |
| `batch_validate.py` | Run validation across multiple projects at once (developer utility). |
| `generate_examples_index.py` | Regenerate the README index for `examples/` (only used after adding new example projects). |
| `svg_position_calculator.py` | Geometry / position-calculation helpers used during template authoring (debug aid). |
| `rotate_images.py` | Bulk-rotate images by EXIF orientation (one-off normalization tool). |
| `pptx_animations.py` | Apply animation hints to an exported PPTX (post-export experiment, not in the standard export path). |

If something in this folder ends up needed by the main `/slide` pipeline, **promote it back to `scripts/`** and add it to `SKILL.md`. Don't reach into `dev/` from the documented workflow.
