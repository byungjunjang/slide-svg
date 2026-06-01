#!/usr/bin/env python3
"""CLI entry point for the svg_to_pptx package.

Bootstraps sys.path so the colocated `svg_to_pptx/` package resolves when this
script is run by absolute path from any cwd (the documented workflow does
`python3 .codex/skills/slide/scripts/svg_to_pptx.py <project_path> -s final`
from the project root). Without the path insert, Python wouldn't find the
package because the cwd-based import roots wouldn't include this directory.

If the entry point is ever moved or the call style changes to `python3 -m
svg_to_pptx`, this file becomes redundant — until then it earns its keep.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from svg_to_pptx import main

if __name__ == '__main__':
    main()
