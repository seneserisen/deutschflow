@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\run.ps1"
set "DEUTSCHFLOW_EXIT=%ERRORLEVEL%"
echo.
if not "%DEUTSCHFLOW_EXIT%"=="0" echo DeutschFlow did not start. Run DOCTOR.bat for detailed checks.
pause
exit /b %DEUTSCHFLOW_EXIT%
