"""Preset catalog helpers for the theme-init skill.

The catalog stores validated theme snapshots so themes can be kept and
re-activated without re-extracting from a design guide:

    .claude/skills/slide/assets/design-systems/
    ├── active.json              ← {"active": "<name>"} pointer (catalog SSOT)
    ├── README.md                ← auto-generated catalog (render_presets_readme.py)
    └── <preset>/theme.json      ← pristine theme snapshot (pre font-fallback injection)

Invariant: catalog folder name == theme.json["name"] == templates/layouts/<name>/.
`save_preset` enforces the first equality; the layouts directory is created by
render_layouts.py keyed on the same name field, so the chain holds.

`references/theme-active.json` stays the render-time SSOT every downstream
script reads — the catalog only governs what `init_theme.py --activate` copies
into it. Used by init_theme.py; importable directly in tests.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
DEFAULT_PRESETS_ROOT = SCRIPTS.parents[1] / "slide" / "assets" / "design-systems"

_NAME_RE = re.compile(r"^[a-z][a-z0-9-]*$")

_ACTIVE_COMMENT = (
    "활성 테마 카탈로그 포인터(SSOT). init_theme.py --activate <preset>이 갱신하며, "
    "references/theme-active.json은 이 프리셋의 렌더 작업 사본이다. "
    "직접 바꾸지 말고 --activate를 쓸 것."
)


def presets_root() -> Path:
    return DEFAULT_PRESETS_ROOT


def preset_theme_path(root: Path, name: str) -> Path:
    return Path(root) / name / "theme.json"


def list_presets(root: Path) -> list[str]:
    root = Path(root)
    if not root.is_dir():
        return []
    return sorted(
        sub.name for sub in root.iterdir()
        if sub.is_dir() and (sub / "theme.json").is_file()
    )


def read_active(root: Path) -> str | None:
    try:
        data = json.loads((Path(root) / "active.json").read_text(encoding="utf-8"))
        return data.get("active")
    except (OSError, json.JSONDecodeError):
        return None


def set_active(root: Path, name: str) -> Path:
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    out = root / "active.json"
    out.write_text(
        json.dumps({"active": name, "_comment": _ACTIVE_COMMENT},
                   ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return out


def save_preset(root: Path, theme: dict) -> Path:
    """Snapshot a complete theme dict into the catalog as <name>/theme.json.

    Overwrites an existing snapshot of the same name unconditionally — the
    name comes from the theme itself, so a same-name save is by definition a
    re-bake of that preset, never an accidental collision.
    """
    name = theme.get("name")
    if not isinstance(name, str) or not _NAME_RE.match(name):
        raise ValueError(f"theme has no valid 'name' (lowercase-kebab): {name!r}")
    out = preset_theme_path(root, name)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(theme, ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8")
    return out


def check_no_set_active_preflight(root: Path) -> str:
    """Validate that --no-set-active can restore the previous theme afterwards.

    Called BEFORE any write (fill / render) happens, so a failure leaves the
    working tree untouched. Returns the previous active preset name. Raises
    ValueError when the previous active theme is unknown or not in the
    catalog — the caller should suggest `--register-current` first.

    (The new theme's name is not known yet at this point; the caller handles
    the new-name == previous-name case after the fill step.)
    """
    prev = read_active(root)
    if prev is None:
        raise ValueError(
            "--no-set-active requires an existing active.json pointer to restore; "
            "run `init_theme.py --register-current` first to register the current theme."
        )
    if not preset_theme_path(root, prev).is_file():
        raise ValueError(
            f"--no-set-active cannot restore '{prev}': not in the catalog ({root}/{prev}/theme.json missing); "
            "run `init_theme.py --register-current` while it is still active, then retry."
        )
    return prev
