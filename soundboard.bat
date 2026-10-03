@echo off
rem Soundboard LPD8 - Adolfo Rosas (GitHub: @ahrsml) - MIT License
title Soundboard LPD8
cd /d "%~dp0"

rem First run: create the virtual environment and install dependencies
if not exist ".venv\Scripts\python.exe" (
    echo Creating virtual environment...
    py -3 -m venv .venv || goto :error
    ".venv\Scripts\python.exe" -m pip install -q -r requirements.txt || goto :error
)

".venv\Scripts\python.exe" soundboard.py %*
echo.
pause
exit /b

:error
echo.
echo Setup failed. Make sure Python 3.8+ is installed (https://www.python.org).
pause
exit /b 1
