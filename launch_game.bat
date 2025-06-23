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

REM Check if pygame is installed
python -c "import pygame" >nul 2>&1
if errorlevel 1 (
    echo ❌ Pygame is not installed
    echo Installing pygame...
    pip install pygame
    if errorlevel 1 (
        echo ❌ Failed to install pygame
        pause
        exit /b 1
    )
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