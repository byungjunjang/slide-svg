#!/usr/bin/env python3
"""Validate theme-active.json against token-contract.json v1.

Exit 0 on success, 1 on validation failure (errors printed to stderr in a
human-readable list), 2 on setup errors (missing files, missing dependency).

Called by init_theme.py between parse_design_guide.py and the render
scripts so no downstream file is written from an invalid theme.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[2] / "slide"
THEME_INIT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTRACT = THEME_INIT_ROOT / "references" / "token-contract.json"
DEFAULT_THEME = SKILL_ROOT / "references" / "theme-active.json"

# Patterns we recognize and can convert into actionable suggestions instead
# of leaving the user with raw jsonschema regex output. Each entry returns a
# short hint string when the predicate matches, or None to fall through.
_HEX_RE = re.compile(r"^#?([0-9A-Fa-f]+)$")


def _hint_for(err) -> str | None:
    """Return a one-line actionable hint for a jsonschema error, or None.

    The hints target the most frequent agent mistakes when extracting tokens
    from a design guide: lowercase hex, 3-digit shorthand, missing `#`,
    rgba() / hsl() strings, and a few schema-shape mismatches. Hints are
    shown in addition to the raw schema message, never instead of it, so
    nothing is hidden if the heuristic guesses wrong.
    """
    msg = err.message
    val = err.instance

    # Hex-color violations: anything failing the hex pattern under colors.*
    if isinstance(val, str) and "colors" in [str(p) for p in err.absolute_path]:
        m = _HEX_RE.match(val)
        if m:
            digits = m.group(1)
            if not val.startswith("#"):
                return f"hint: hex strings need a leading '#'. Try '#{digits.upper()}'."
            if len(digits) == 3:
                expanded = "".join(c + c for c in digits).upper()
                return f"hint: 3-digit shorthand isn't allowed; expand to 6-digit: '#{expanded}'."
            if len(digits) == 6 and digits != digits.upper():
                return f"hint: contract requires uppercase hex; try '#{digits.upper()}'."
        if val.startswith("rgb(") or val.startswith("rgba("):
            return "hint: contract requires hex (#RRGGBB), not rgb()/rgba(). Convert to hex."
        if val.startswith("hsl(") or val.startswith("hsla("):
            return "hint: contract requires hex (#RRGGBB), not hsl()/hsla(). Convert to hex."

    # Type mismatch on a typeScale leaf (e.g. size given as string "56" instead of 56)
    if "typography" in [str(p) for p in err.absolute_path] and isinstance(val, str):
        if val.replace(".", "", 1).isdigit():
            return f"hint: typography numeric fields must be numbers, not strings. Drop the quotes: {val}."

    # Required-field omission — name the missing key in plain English
    if err.validator == "required" and "is a required property" in msg:
        m = re.search(r"'([^']+)' is a required property", msg)
        if m:
            parent = "/".join(str(p) for p in err.absolute_path) or "<root>"
            return f"hint: add a value for '{m.group(1)}' under {parent}; null is fine if the guide doesn't specify it (fill_theme_defaults will substitute)."

    # additionalProperties: agent invented a field name
    if err.validator == "additionalProperties":
        m = re.search(r"\('([^']+)' was unexpected\)", msg) or re.search(r"Additional properties are not allowed \(([^)]+)\)", msg)
        if m:
            return f"hint: '{m.group(1)}' is not a v1 contract field. Either remove it, or add it to token-contract.json and bump the version."

    return None


def validate(theme: dict, contract: dict) -> list[str]:
    try:
        import jsonschema  # type: ignore
    except ImportError as e:
        raise SystemExit(
            "jsonschema missing. Install with: pip install jsonschema"
        ) from e

    validator = jsonschema.Draft202012Validator(contract)
    errors = []
    for err in sorted(validator.iter_errors(theme), key=lambda e: e.absolute_path):
        path = "/".join(str(p) for p in err.absolute_path) or "<root>"
        line = f"  {path}: {err.message}"
        hint = _hint_for(err)
        if hint:
            line += f"\n      → {hint}"
        errors.append(line)
    return errors


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--theme", type=Path, default=DEFAULT_THEME)
    ap.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    ap.add_argument("--quiet", action="store_true", help="suppress success line")
    args = ap.parse_args()

    if not args.theme.exists():
        print(f"theme not found: {args.theme}", file=sys.stderr)
        return 2
    if not args.contract.exists():
        print(f"contract not found: {args.contract}", file=sys.stderr)
        return 2

    theme = json.loads(args.theme.read_text(encoding="utf-8"))
    contract = json.loads(args.contract.read_text(encoding="utf-8"))

    errors = validate(theme, contract)
    if errors:
        print(f"theme-active.json FAILS the v1 token contract ({len(errors)} error(s)):", file=sys.stderr)
        for e in errors:
            print(e, file=sys.stderr)
        return 1

    if not args.quiet:
        display = theme.get("display_name", theme.get("name", "?"))
        print(f"ok: '{display}' ({theme.get('name', '?')}) conforms to token contract v{theme.get('version', '?')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
