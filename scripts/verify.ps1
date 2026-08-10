$ErrorActionPreference = "Stop"
$Repository = Split-Path -Parent $PSScriptRoot
Set-Location $Repository
& ".\.venv\Scripts\ruff.exe" check apps/server
& ".\.venv\Scripts\python.exe" -c "from importlib.metadata import version; assert version('httpx2')"
& ".\.venv\Scripts\python.exe" -m pip check
& ".\.venv\Scripts\python.exe" -m pytest apps/server/tests
npm run verify:extension
npm audit --audit-level=high
$manifest = Get-Content -Raw -LiteralPath "apps\extension\dist\manifest.json" | ConvertFrom-Json
if ($manifest.manifest_version -ne 3) { throw "Built manifest is not Manifest V3" }
& ".\.venv\Scripts\python.exe" -c "from deutschflow.main import app; assert app.title == 'DeutschFlow local API'"
Write-Output "DeutschFlow verification passed."
