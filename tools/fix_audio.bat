@echo off
echo Running Runic Lands Audio File Fixer...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python is not installed or not in the PATH.
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Try to install required packages
echo Installing required packages...
pip install numpy >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Warning: Could not install numpy package.
    echo Some features may not work correctly.
)

REM Run the audio fixer script
echo.
python fix_audio_files.py

echo.
echo Audio fixing process completed!
pause 