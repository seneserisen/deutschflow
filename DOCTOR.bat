@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\doctor.ps1"
set "DEUTSCHFLOW_EXIT=%ERRORLEVEL%"
echo.
pause
exit /b %DEUTSCHFLOW_EXIT%
