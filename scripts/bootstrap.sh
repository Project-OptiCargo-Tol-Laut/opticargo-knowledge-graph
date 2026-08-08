#!/usr/bin/env sh
set -eu
repository="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
shared="$(dirname -- "$repository")/opticargo-shared"
python -m pip install --upgrade pip build hatchling
python -m pip install "$shared"
python -m pip install -e "$repository[dev]"
python "$repository/scripts/smoke_shared.py"
python "$repository/scripts/smoke_structure.py"
