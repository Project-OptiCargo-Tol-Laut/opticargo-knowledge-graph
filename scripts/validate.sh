#!/usr/bin/env sh
set -eu
repository="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$repository"
python -m ruff check src tests scripts
python -m compileall -q src tests scripts
python -m pytest -q
python -m pip check
python scripts/smoke_structure.py
python scripts/smoke_shared.py
