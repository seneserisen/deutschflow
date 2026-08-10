$ErrorActionPreference = "Stop"
$Repository = Split-Path -Parent $PSScriptRoot
& "$Repository\.venv\Scripts\python.exe" -m deutschflow.main

