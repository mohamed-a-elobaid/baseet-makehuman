#!/usr/bin/env bash
# Launch MakeHuman with the project venv.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
# shellcheck disable=SC1091
source "$ROOT/.venv/bin/activate"
cd "$ROOT/upstream/makehuman/makehuman"
exec python3 makehuman.py "$@"
