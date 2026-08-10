@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\test.ps1"
set "DEUTSCHFLOW_EXIT=%ERRORLEVEL%"
echo.
if not "%DEUTSCHFLOW_EXIT%"=="0" echo One or more checks failed. Review the output above.
pause
exit /b %DEUTSCHFLOW_EXIT%
