$ErrorActionPreference = "Continue"
$Repository = Split-Path -Parent $PSScriptRoot
$Failures = 0

function Show-Check([string]$Name, [string]$State, [string]$Detail, [ConsoleColor]$Color) {
    Write-Host (("{0,-25} {1,-7} {2}" -f $Name, $State, $Detail)) -ForegroundColor $Color
}
function Fail-Check([string]$Name, [string]$Detail) {
    $script:Failures += 1
    Show-Check $Name "ERROR" $Detail Red
}

Write-Host "DeutschFlow environment check"
Write-Host "Repository: $Repository"
Write-Host ""

$Python = Get-Command python.exe -ErrorAction SilentlyContinue
if ($Python) {
    $VersionText = (& $Python.Source --version 2>&1 | Out-String).Trim()
    try { $Version = [version](($VersionText -replace '^Python\s+', '').Trim()) } catch { $Version = [version]'0.0' }
    if ($Version -ge [version]'3.12') { Show-Check "Python" "OK" $VersionText Green }
    else { Fail-Check "Python" "Python 3.12 or later is required; found $VersionText." }
} else {
    Fail-Check "Python" "Not found. Install Python 3.12+ and enable Add Python to PATH."
}

$Node = Get-Command node.exe -ErrorAction SilentlyContinue
if ($Node) {
    $NodeText = (& $Node.Source --version).Trim()
    $NodeVersion = [version]$NodeText.TrimStart('v')
    $NodeSupported = (($NodeVersion.Major -eq 24 -and $NodeVersion -ge [version]'24.15.0') -or $NodeVersion.Major -ge 26)
    if ($NodeSupported) { Show-Check "Node.js" "OK" $NodeText Green }
    else { Fail-Check "Node.js" "Node.js 24.15+ in the Node 24 line, or Node.js 26+, is required; found $NodeText." }
} else { Fail-Check "Node.js" "Not found. Install Node.js 24 LTS (24.15 or later)." }

$Npm = Get-Command npm.cmd -ErrorAction SilentlyContinue
if ($Npm) { Show-Check "npm" "OK" (& $Npm.Source --version).Trim() Green }
else { Fail-Check "npm" "Not found. It is normally installed with Node.js." }

$VenvPython = Join-Path $Repository ".venv\Scripts\python.exe"
$DependencyLock = Join-Path $Repository "requirements-dev.lock"
if (Test-Path -LiteralPath $DependencyLock) {
    Show-Check "Python dependency lock" "OK" "requirements-dev.lock" Green
} else { Fail-Check "Python dependency lock" "Missing. Restore requirements-dev.lock from Git." }

if (Test-Path -LiteralPath $VenvPython) {
    Show-Check "Virtual environment" "OK" ".venv" Green
    & $VenvPython -c "from importlib.metadata import version; import deutschflow, fastapi, sqlalchemy, uvicorn; assert version('httpx2')" 2>$null
    if ($LASTEXITCODE -eq 0) { Show-Check "Python package" "OK" "DeutschFlow and runtime dependencies import correctly." Green }
    else { Fail-Check "Python package" "Dependencies are incomplete. Run SETUP.bat again." }
} else {
    Fail-Check "Virtual environment" "Missing. Run SETUP.bat."
}

if (Test-Path -LiteralPath (Join-Path $Repository "node_modules")) {
    Show-Check "Extension dependencies" "OK" "node_modules exists." Green
} else { Fail-Check "Extension dependencies" "Missing. Run SETUP.bat." }

$Manifest = Join-Path $Repository "apps\extension\dist\manifest.json"
if (Test-Path -LiteralPath $Manifest) { Show-Check "Extension build" "OK" $Manifest Green }
else { Fail-Check "Extension build" "Missing. Run SETUP.bat or RUN.bat." }

$Artifacts = Join-Path $Repository "artifacts"
try {
    $Probe = Join-Path $Artifacts ".doctor-write-test"
    [IO.File]::WriteAllText($Probe, "ok")
    Remove-Item -LiteralPath $Probe -Force
    Show-Check "Artifacts directory" "OK" "Writable." Green
} catch { Fail-Check "Artifacts directory" "Not writable: $($_.Exception.Message)" }

$Git = Get-Command git.exe -ErrorAction SilentlyContinue
if ($Git) {
    & $Git.Source -C $Repository rev-parse --is-inside-work-tree *> $null
    if ($LASTEXITCODE -eq 0) {
        Show-Check "Git repository" "OK" "Local repository detected." Green
        $Branch = (& $Git.Source -C $Repository branch --show-current 2>$null | Out-String).Trim()
        Show-Check "Git branch" "OK" $(if ($Branch) { $Branch } else { "No branch name yet." }) Green
        $Remote = (& $Git.Source -C $Repository remote get-url origin 2>$null | Out-String).Trim()
        if ($LASTEXITCODE -eq 0 -and $Remote) { Show-Check "Git remote" "OK" $Remote Green }
        else { Show-Check "Git remote" "WARN" "No origin configured; add one deliberately when ready." Yellow }
    } else { Fail-Check "Git repository" "This folder is not a Git working tree." }
} else { Show-Check "Git" "WARN" "Git was not found; runtime use still works." Yellow }

try {
    $Health = Invoke-RestMethod -Uri "http://127.0.0.1:8765/api/v1/health" -TimeoutSec 2
    Show-Check "Local service" "OK" "Running (version $($Health.version))." Green
} catch { Show-Check "Local service" "INFO" "Not running. RUN.bat starts it." Cyan }

Write-Host ""
if ($Failures -gt 0) {
    Write-Host "$Failures required check(s) failed. Fix the ERROR items, then run DOCTOR.bat again." -ForegroundColor Red
    exit 1
}
Write-Host "All required environment checks passed." -ForegroundColor Green
exit 0
