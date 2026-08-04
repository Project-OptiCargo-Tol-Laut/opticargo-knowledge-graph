$ErrorActionPreference = "Stop"
$Repository = Split-Path -Parent $PSScriptRoot
Push-Location $Repository
try {
    python -m ruff check src tests scripts
    python -m compileall -q src tests scripts
    python -m pytest -q
    python -m pip check
    python scripts/smoke_structure.py
    python scripts/smoke_shared.py
} finally {
    Pop-Location
}
