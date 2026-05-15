#!/usr/bin/env bash
# Venv-aware python launcher for /slide skill scripts.
#
# Resolves the project root (slide-svg/), picks .venv/bin/python3 if it exists,
# and falls back to system python3 otherwise. This lets the skill run scripts
# right after `python3 -m venv .venv && pip install -r requirements.txt` —
# without the user having to `source .venv/bin/activate` in every new shell.
#
# Usage (drop-in replacement for `python3`):
#   .claude/skills/slide/scripts/_py.sh path/to/script.py [args...]
#   .claude/skills/slide/scripts/_py.sh -c "import …"

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# scripts/_py.sh → walk up 4 levels to reach slide-svg/
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"

if [ -x "$PROJECT_ROOT/.venv/bin/python3" ]; then
  exec "$PROJECT_ROOT/.venv/bin/python3" "$@"
fi

exec python3 "$@"
