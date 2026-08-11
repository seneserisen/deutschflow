param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("Start", "Stop", "Status")]
    [string]$Action
)

$ErrorActionPreference = "Stop"
$Repository = Split-Path -Parent $PSScriptRoot
$Runtime = Join-Path $Repository ".runtime"
$PidFile = Join-Path $Runtime "deutschflow.pid"
$OutputLog = Join-Path $Runtime "deutschflow.log"
$ErrorLog = Join-Path $Runtime "deutschflow-error.log"
$Server = Join-Path $Repository ".venv\Scripts\deutschflow-server.exe"
$HealthUrl = "http://127.0.0.1:43131/api/v1/health"

function Get-DeutschFlowProcess {
    if (-not (Test-Path -LiteralPath $PidFile)) { return $null }
    $savedPid = (Get-Content -LiteralPath $PidFile -Raw -ErrorAction SilentlyContinue).Trim()
    if ($savedPid -notmatch '^\d+$') { Remove-Item -LiteralPath $PidFile -Force -ErrorAction SilentlyContinue; return $null }
    $process = Get-CimInstance Win32_Process -Filter "ProcessId = $savedPid" -ErrorAction SilentlyContinue
    if (-not $process -or $process.CommandLine -notlike "*deutschflow-server*") {
        Remove-Item -LiteralPath $PidFile -Force -ErrorAction SilentlyContinue
        return $null
    }
    return $process
}

function Test-DeutschFlowHealth {
    try {
        $health = Invoke-RestMethod -Uri $HealthUrl -TimeoutSec 2
        return $health.status -eq "ok" -and $health.application -eq "deutschflow"
    } catch { return $false }
}

New-Item -ItemType Directory -Path $Runtime -Force | Out-Null
switch ($Action) {
    "Status" {
        if ((Get-DeutschFlowProcess) -and (Test-DeutschFlowHealth)) {
            Write-Host "DeutschFlow is running at http://127.0.0.1:43131." -ForegroundColor Green
        } else {
            Write-Host "DeutschFlow is stopped." -ForegroundColor Yellow
        }
        exit 0
    }
    "Stop" {
        $process = Get-DeutschFlowProcess
        if (-not $process) { Write-Host "DeutschFlow is already stopped." -ForegroundColor Yellow; exit 0 }
        & taskkill.exe /PID $process.ProcessId /T /F | Out-Null
        Remove-Item -LiteralPath $PidFile -Force -ErrorAction SilentlyContinue
        Write-Host "DeutschFlow stopped." -ForegroundColor Green
        exit 0
    }
}

if (-not (Test-Path -LiteralPath $Server)) { throw "DeutschFlow is not set up. Run SETUP.bat first." }
if (Get-DeutschFlowProcess) { Write-Host "DeutschFlow is already running." -ForegroundColor Green; exit 0 }
if (Test-NetConnection -ComputerName 127.0.0.1 -Port 43131 -InformationLevel Quiet -WarningAction SilentlyContinue) {
    throw "Port 43131 belongs to another application. DeutschFlow was not started."
}

Set-Location -LiteralPath $Repository
$npm = Get-Command npm.cmd -ErrorAction SilentlyContinue
if (-not $npm) { throw "npm was not found. Run DOCTOR.bat." }
& $npm.Source run build
if ($LASTEXITCODE -ne 0) { throw "The browser extension build failed." }

Remove-Item -LiteralPath $OutputLog, $ErrorLog -Force -ErrorAction SilentlyContinue
$env:DEUTSCHFLOW_PORT = "43131"
$process = Start-Process -FilePath $Server -WorkingDirectory $Repository -WindowStyle Hidden `
    -RedirectStandardOutput $OutputLog -RedirectStandardError $ErrorLog -PassThru
Set-Content -LiteralPath $PidFile -Value $process.Id -NoNewline

$deadline = (Get-Date).AddSeconds(30)
while ((Get-Date) -lt $deadline) {
    if (Test-DeutschFlowHealth) {
        Write-Host "DeutschFlow is ready at http://127.0.0.1:43131." -ForegroundColor Green
        Write-Host "Extension folder: $Repository\apps\extension\dist"
        exit 0
    }
    if (-not (Get-DeutschFlowProcess)) { break }
    Start-Sleep -Milliseconds 400
}
throw "DeutschFlow did not become ready. Review $ErrorLog."
