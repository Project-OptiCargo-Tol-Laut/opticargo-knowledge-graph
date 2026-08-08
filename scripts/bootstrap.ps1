$ErrorActionPreference = "Stop"
$Repository = Split-Path -Parent $PSScriptRoot
$Shared = Join-Path (Split-Path -Parent $Repository) "opticargo-shared"
python -m pip install --upgrade pip build hatchling
python -m pip install $Shared
python -m pip install -e "$Repository[dev]"
python (Join-Path $PSScriptRoot "smoke_shared.py")
python (Join-Path $PSScriptRoot "smoke_structure.py")
