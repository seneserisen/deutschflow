$ErrorActionPreference = "Stop"
$Repository = Split-Path -Parent $PSScriptRoot
Set-Location $Repository

function Stop-WithMessage([string]$Message) {
    Write-Host "ERROR: $Message" -ForegroundColor Red
    exit 1
}

$Python = Get-Command python.exe -ErrorAction SilentlyContinue
if (-not $Python) {
    Stop-WithMessage "Python was not found. Install Python 3.12 or later from python.org, enable 'Add Python to PATH', then run SETUP.bat again."
}

$VersionText = (& $Python.Source --version 2>&1 | Out-String).Trim()
try {
    $PythonVersion = [version](($VersionText -replace '^Python\s+', '').Trim())
} catch {
    Stop-WithMessage "Could not determine the Python version from '$VersionText'."
}
if ($PythonVersion -lt [version]'3.12') {
    Stop-WithMessage "Python 3.12 or later is required; found $PythonVersion."
}

$Npm = Get-Command npm.cmd -ErrorAction SilentlyContinue
if (-not $Npm) {
    Stop-WithMessage "npm was not found. Install Node.js 24 LTS (24.15 or later) from nodejs.org, then run SETUP.bat again."
}
$Node = Get-Command node.exe -ErrorAction SilentlyContinue
if (-not $Node) {
    Stop-WithMessage "Node.js was not found. Install Node.js 24 LTS (24.15 or later) from nodejs.org, then run SETUP.bat again."
}
$NodeVersion = [version]((& $Node.Source --version).Trim().TrimStart('v'))
$NodeSupported = (($NodeVersion.Major -eq 24 -and $NodeVersion -ge [version]'24.15.0') -or $NodeVersion.Major -ge 26)
if (-not $NodeSupported) {
    Stop-WithMessage "Node.js 24.15 or later in the Node 24 line, or Node.js 26+, is required; found $NodeVersion."
}

$VenvPython = Join-Path $Repository ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $VenvPython)) {
    Write-Host "Creating the local Python environment..."
    & $Python.Source -m venv (Join-Path $Repository ".venv")
    if ($LASTEXITCODE -ne 0) { Stop-WithMessage "Python could not create .venv." }
} else {
    Write-Host "Existing .venv detected."
}

Write-Host "Installing locked Python dependencies..."
# httpx2 replaces the legacy httpx distribution used by older checkouts. Both expose the
# same import name, so remove the obsolete distribution before installing the lock.
& $VenvPython -m pip uninstall --yes httpx | Out-Null
& $VenvPython -m pip install --require-hashes -r (Join-Path $Repository "requirements-dev.lock")
if ($LASTEXITCODE -ne 0) { Stop-WithMessage "Locked Python dependencies could not be installed." }
& $VenvPython -m pip install --no-deps -e (Join-Path $Repository "apps\server")
if ($LASTEXITCODE -ne 0) { Stop-WithMessage "DeutschFlow could not be installed into the local environment." }

Write-Host "Installing locked extension dependencies..."
& $Npm.Source ci
if ($LASTEXITCODE -ne 0) { Stop-WithMessage "Node dependencies could not be installed." }

Write-Host "Building the browser extension..."
& $Npm.Source run build
if ($LASTEXITCODE -ne 0) { Stop-WithMessage "The extension build failed." }

Write-Host ""
Write-Host "DeutschFlow setup completed successfully." -ForegroundColor Green
Write-Host "Next: double-click RUN.bat, then follow START_HERE.md to load the extension."
