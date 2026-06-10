#!/usr/bin/env python3
"""Regenerate <presets_root>/README.md as a markdown catalog of every preset.

Reads each subfolder's `theme.json`, extracts identity fields, and writes a
single index file. Run as a post-step from init_theme.py, or standalone:

    python3 render_presets_readme.py [--presets-root <path>]

The README is fully owned by this script — direct edits are clobbered on
the next run. The header carries a disclaimer to that effect.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
DEFAULT_PRESETS_ROOT = SCRIPTS.parents[1] / "slide" / "assets" / "design-systems"


def _load_theme(theme_path: Path) -> dict | None:
    try:
        return json.loads(theme_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _active_preset(presets_root: Path) -> str | None:
    """Read the active-preset SSOT (active.json) if present."""
    try:
        data = json.loads((presets_root / "active.json").read_text(encoding="utf-8"))
        return data.get("active")
    except (OSError, json.JSONDecodeError):
        return None


def _row(name: str, theme: dict, active: str | None) -> str:
    display = theme.get("display_name", name)
    description = (theme.get("description") or "").replace("|", "\\|")
    accent = theme.get("colors", {}).get("accent", "—")
    mark = "●" if name == active else ""
    return f"| {mark} | `{name}` | {display} | {description} | {accent} |"


def render_readme(presets_root: Path) -> Path:
    presets_root = Path(presets_root)
    if not presets_root.is_dir():
        raise FileNotFoundError(f"presets_root does not exist: {presets_root}")

    active = _active_preset(presets_root)
    rows: list[str] = []
    for sub in sorted(presets_root.iterdir()):
        if not sub.is_dir():
            continue
        theme = _load_theme(sub / "theme.json")
        if theme is None:
            continue
        rows.append(_row(sub.name, theme, active))

    body = [
        "# 사용 가능한 디자인 시스템 (테마 카탈로그)",
        "",
        "_이 파일은 `theme-init`이 자동 생성합니다. 직접 편집하지 마세요 — 다음 실행 시 덮어씁니다._",
        "",
        f"활성 프리셋(●): **{active or '(active.json 없음 — theme-active.json 그대로 사용)'}** "
        "— `references/theme-active.json`이 이 프리셋의 렌더 작업 사본입니다.",
        "",
        "| 활성 | 프리셋 | 표시명 | 설명 | 액센트 |",
        "|---|---|---|---|---|",
    ]
    body.extend(rows if rows else ["| | _(no presets found)_ |  |  |  |"])
    body.append("")
    body.append("전환: `python3 .codex/skills/theme-init/scripts/init_theme.py --activate <preset>` "
                "(전역 참조 문서를 해당 테마로 결정적 재렌더 — LLM 불필요)")
    body.append("")

    out = presets_root / "README.md"
    out.write_text("\n".join(body), encoding="utf-8")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--presets-root", type=Path, default=DEFAULT_PRESETS_ROOT)
    args = ap.parse_args()

    out = render_readme(args.presets_root)
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
