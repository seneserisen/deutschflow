@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\setup.ps1"
set "DEUTSCHFLOW_EXIT=%ERRORLEVEL%"
echo.
if not "%DEUTSCHFLOW_EXIT%"=="0" echo Setup did not complete. Read the message above, then run SETUP.bat again.
pause
exit /b %DEUTSCHFLOW_EXIT%
