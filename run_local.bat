@echo off
setlocal

REM Windows one-click launcher for local dashboard
set "PY=python"
where %PY% >nul 2>&1
if errorlevel 1 (
  echo [ERROR] python not found in PATH.
  echo Install Python and reopen PowerShell/CMD.
  exit /b 1
)

set "SCRIPT=%~dp0run_local.py"
if exist "%SCRIPT%" (
  %PY% "%SCRIPT%"
  exit /b %errorlevel%
)

set "NESTED=%~dp0GPT\run_local.py"
if exist "%NESTED%" (
  %PY% "%NESTED%"
  exit /b %errorlevel%
)

echo [ERROR] run_local.py not found.
echo Tried:
echo   %SCRIPT%
echo   %NESTED%
echo.
echo Hint: If you cloned into a nested folder, run this .bat from repo root.
exit /b 1
