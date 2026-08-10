$ErrorActionPreference = "Stop"
$Repository = Split-Path -Parent $PSScriptRoot
$Verification = Join-Path $PSScriptRoot "verify.ps1"

if (-not (Test-Path -LiteralPath (Join-Path $Repository ".venv\Scripts\python.exe"))) {
    Write-Host "ERROR: DeutschFlow is not set up yet. Double-click SETUP.bat first." -ForegroundColor Red
    exit 1
}

& $Verification
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
