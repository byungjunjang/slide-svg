#!/usr/bin/env bash
# Venv-aware, cross-platform python launcher for /slide skill scripts.
#
# Resolves the project root (slide-svg/) and runs the project's virtualenv
# interpreter if present, else a system interpreter. Handles BOTH layouts:
#   - POSIX  (macOS/Linux):  .venv/bin/python3
#   - Windows (Git Bash):    .venv/Scripts/python.exe
# and skips the non-functional Microsoft Store python stub (the WindowsApps
# alias that hangs / opens the Store instead of running Python).
#
# This lets the skill run scripts right after creating a venv —
#   POSIX:    python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
#   Windows:  py -3 -m venv .venv  && .venv/Scripts/pip install -r requirements.txt
# without the user having to activate the venv in every new shell.
#
# Usage (drop-in replacement for `python3`):
#   .claude/skills/slide/scripts/_py.sh path/to/script.py [args...]
#   .claude/skills/slide/scripts/_py.sh -c "import …"

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# scripts/_py.sh → walk up 4 levels to reach slide-svg/
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"

# 1) Project virtualenv — Windows layout first, then POSIX. Use -f as well as
#    -x because Git Bash does not always report the executable bit on .exe.
for VENV_PY in \
  "$PROJECT_ROOT/.venv/Scripts/python.exe" \
  "$PROJECT_ROOT/.venv/bin/python3" \
  "$PROJECT_ROOT/.venv/bin/python"; do
  if [ -x "$VENV_PY" ] || [ -f "$VENV_PY" ]; then
    exec "$VENV_PY" "$@"
  fi
done

# 2) System interpreter, skipping the Microsoft Store stub. The stub lives
#    under ...\WindowsApps\ and is a launcher alias, not a real interpreter:
#    invoking it hangs or pops the Store. command -v "finds" it, so we must
#    inspect the resolved path and reject it.
for CAND in python3 python; do
  CAND_PATH="$(command -v "$CAND" 2>/dev/null || true)"
  [ -n "$CAND_PATH" ] || continue
  case "$CAND_PATH" in
    *WindowsApps*|*Microsoft/WindowsApps*) continue ;;
  esac
  exec "$CAND" "$@"
done

# 3) Windows py launcher (PEP 397) — resolves a real Python even when only the
#    Store stub is on PATH for python/python3.
if command -v py >/dev/null 2>&1; then
  exec py -3 "$@"
fi

# 4) Nothing usable — fail loudly with a fix, instead of silently running a stub.
{
  echo "[_py.sh] No usable Python interpreter found."
  echo "  Create a project venv at: $PROJECT_ROOT/.venv"
  echo "    Windows:      py -3 -m venv .venv"
  echo "                  .venv/Scripts/pip install -r .claude/skills/slide/requirements.txt"
  echo "    macOS/Linux:  python3 -m venv .venv"
  echo "                  .venv/bin/pip install -r .claude/skills/slide/requirements.txt"
  echo "  (On Windows, install real Python from python.org or 'winget install Python.Python.3.12'"
  echo "   — the Microsoft Store 'python'/'python3' aliases are stubs and are skipped.)"
} >&2
exit 1
