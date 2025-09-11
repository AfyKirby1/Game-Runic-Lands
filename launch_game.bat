@echo off
echo 🎮 Starting Runic Lands...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://python.org
    pause
    exit /b 1
)

REM Check if all required dependencies are installed
echo 🔍 Checking dependencies...
python -c "import pygame, opensimplex, numpy, scipy, PIL, pytmx, pyscroll" >nul 2>&1
if errorlevel 1 (
    echo ❌ Some dependencies are missing
    echo 📦 Installing all required packages...
    pip install -r docs/requirements.txt
    if errorlevel 1 (
        echo ❌ Failed to install dependencies
        echo 💡 Try running: pip install -r docs/requirements.txt
        pause
        exit /b 1
    )
    echo ✅ Dependencies installed successfully
)

REM Launch the game
echo ✅ Starting Runic Lands...
python main.py

REM Keep window open if there was an error
if errorlevel 1 (
    echo.
    echo ❌ Game exited with an error
    pause
) 