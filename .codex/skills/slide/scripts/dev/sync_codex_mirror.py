#!/usr/bin/env python3
"""Generate the .codex/skills mirror from the canonical .codex/skills tree.

.codex/skills is the single source of truth. .codex/skills is a generated
artifact: a byte-for-byte copy, except the literal path token ".codex/skills"
is rewritten to ".codex/skills" inside text files so Codex copies host-correct
invocation commands. Re-run after editing anything under .codex/skills.

Usage:
    python3 .codex/skills/slide/scripts/dev/sync_codex_mirror.py          # regenerate
    python3 .codex/skills/slide/scripts/dev/sync_codex_mirror.py --check  # exit 1 if stale
"""
from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from pathlib import Path

# dev/sync_codex_mirror.py: parents[0]=dev [1]=scripts [2]=slide [3]=skills [4]=.claude [5]=repo
REPO_ROOT = Path(__file__).resolve().parents[5]
SRC = REPO_ROOT / ".claude" / "skills"
DST = REPO_ROOT / ".codex" / "skills"

TEXT_SUFFIXES = {".md", ".py", ".sh", ".json", ".txt", ".svg", ".cfg",
                 ".toml", ".yml", ".yaml", ".ini"}
EXCLUDE_NAMES = {"__pycache__", ".DS_Store"}
OLD_TOKEN = ".claude" + "/skills"
NEW_TOKEN = ".codex" + "/skills"


def _iter_files(root: Path):
    if not root.exists():
        return
    for p in sorted(root.rglob("*")):
        rel = p.relative_to(root)
        if any(part in EXCLUDE_NAMES for part in rel.parts):
            continue
        if p.suffix == ".pyc":
            continue
        if p.is_file():
            yield p


def _transform_bytes(path: Path, data: bytes) -> bytes:
    if path.suffix.lower() in TEXT_SUFFIXES:
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            return data
        return text.replace(OLD_TOKEN, NEW_TOKEN).encode("utf-8")
    return data


def build_mirror(dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    for src_file in _iter_files(SRC):
        rel = src_file.relative_to(SRC)
        out = dst / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(_transform_bytes(src_file, src_file.read_bytes()))


def _stale_files(mirror: Path, fresh: Path) -> list[str]:
    a = {p.relative_to(mirror) for p in _iter_files(mirror)}
    b = {p.relative_to(fresh) for p in _iter_files(fresh)}
    out = []
    for rel in sorted(a | b):
        fa, fb = mirror / rel, fresh / rel
        if not fa.exists() or not fb.exists() or fa.read_bytes() != fb.read_bytes():
            out.append(str(rel))
    return out


def check() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        fresh = Path(tmp) / "skills"
        build_mirror(fresh)
        stale = _stale_files(DST, fresh)
    if stale:
        sys.stderr.write("[sync_codex_mirror] .codex/skills is STALE:\n")
        for rel in stale[:40]:
            sys.stderr.write(f"  - {rel}\n")
        if len(stale) > 40:
            sys.stderr.write(f"  ... and {len(stale) - 40} more\n")
        sys.stderr.write("  Fix: python3 .codex/skills/slide/scripts/dev/sync_codex_mirror.py\n")
        return 1
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate/verify the .codex/skills mirror.")
    ap.add_argument("--check", action="store_true",
                    help="Exit 1 if the mirror is stale; do not write.")
    args = ap.parse_args()
    if args.check:
        return check()
    build_mirror(DST)
    print(f"[sync_codex_mirror] regenerated {DST} from {SRC}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
