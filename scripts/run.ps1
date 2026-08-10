$ErrorActionPreference = "Stop"
$Repository = Split-Path -Parent $PSScriptRoot
Set-Location $Repository

function Stop-WithMessage([string]$Message) {
    Write-Host "ERROR: $Message" -ForegroundColor Red
    exit 1
}

$VenvPython = Join-Path $Repository ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $VenvPython)) {
    Stop-WithMessage "DeutschFlow is not set up yet. Double-click SETUP.bat first."
}
if (-not (Test-Path -LiteralPath (Join-Path $Repository "node_modules"))) {
    Stop-WithMessage "Extension dependencies are missing. Double-click SETUP.bat again."
}
$Npm = Get-Command npm.cmd -ErrorAction SilentlyContinue
if (-not $Npm) {
    Stop-WithMessage "npm was not found. Install Node.js 24 LTS (24.15 or later), then run SETUP.bat again."
}

Write-Host "Building the browser extension..."
& $Npm.Source run build
if ($LASTEXITCODE -ne 0) { Stop-WithMessage "The extension build failed." }

$ExtensionPath = Join-Path $Repository "apps\extension\dist"
Write-Host ""
Write-Host "DeutschFlow is ready for the browser." -ForegroundColor Green
Write-Host "Extension folder: $ExtensionPath"
Write-Host ""
Write-Host "If it is not loaded yet:"
Write-Host "  1. Open chrome://extensions or opera://extensions."
Write-Host "  2. Enable Developer mode and choose Load unpacked."
Write-Host "  3. Select the extension folder shown above."
Write-Host "  4. Open DeutschFlow Settings and pair with this local service."
Write-Host ""
Write-Host "The local service is starting at http://127.0.0.1:8765."
Write-Host "Keep this window open while using DeutschFlow. Press Ctrl+C to stop."
Write-Host ""
& $VenvPython -m deutschflow.main
if ($LASTEXITCODE -ne 0) { Stop-WithMessage "The local service stopped with an error." }
