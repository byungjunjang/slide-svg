#!/usr/bin/env python3
"""/slide Step 0: announce the active theme + catalog-drift warning.

Prints the one-line active-theme declaration from references/theme-active.json.
If the preset catalog (assets/design-systems/active.json) exists and its
pointer disagrees with the working copy's name, prints a WARN with the fix —
the working copy stays authoritative for rendering either way. A missing
catalog (e.g. the claude.ai essentials bundle) is silent: not an error.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
THEME_ACTIVE = SKILL / "references" / "theme-active.json"
CATALOG_ACTIVE = SKILL / "assets" / "design-systems" / "active.json"


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except (AttributeError, ValueError):
        pass

    t = json.loads(THEME_ACTIVE.read_text(encoding="utf-8"))
    font = t["typography"]["font-chain"].split(",")[0].strip()
    print(f"[active theme] {t['display_name']} ({t['name']}) — "
          f"accent {t['colors']['accent']}, font {font}")

    if CATALOG_ACTIVE.is_file():
        try:
            pointer = json.loads(CATALOG_ACTIVE.read_text(encoding="utf-8")).get("active")
        except json.JSONDecodeError:
            pointer = None
        if pointer and pointer != t["name"]:
            print(f"[WARN] theme drift: catalog active.json says '{pointer}' but "
                  f"theme-active.json is '{t['name']}'.")
            print(f"       fix: python3 .claude/skills/theme-init/scripts/init_theme.py "
                  f"--activate {pointer}")
            print(f"       (or adopt the working copy: ... init_theme.py --register-current)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
