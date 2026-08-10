$ErrorActionPreference = "Stop"
$Repository = Split-Path -Parent $PSScriptRoot
Set-Location $Repository
npm run dev:extension

