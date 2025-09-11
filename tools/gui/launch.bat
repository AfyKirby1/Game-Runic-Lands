@echo off
echo 🎨 Starting Runic Lands Asset Generator GUI...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Error: Python is not installed or not in the PATH.
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check if we're in the right directory
if not exist "..\..\main.py" (
    echo ❌ Error: Not in the correct directory.
    echo Please run this from the tools\gui\ directory.
    pause
    exit /b 1
)

REM Check for required dependencies
echo 🔍 Checking dependencies...
python -c "import tkinter, PIL, numpy" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Some dependencies are missing
    echo 📦 Installing required packages...
    pip install pillow numpy
    if %ERRORLEVEL% NEQ 0 (
        echo ❌ Failed to install dependencies
        echo 💡 Try running: pip install pillow numpy
        pause
        exit /b 1
    )
    echo ✅ Dependencies installed successfully
)

REM Create assets directory if it doesn't exist
if not exist "..\..\assets" (
    echo 📁 Creating assets directory...
    mkdir "..\..\assets"
    mkdir "..\..\assets\sprites"
    mkdir "..\..\assets\sprites\characters"
    mkdir "..\..\assets\sprites\characters\player"
    mkdir "..\..\assets\sprites\characters\player\png"
    mkdir "..\..\assets\audio"
    mkdir "..\..\assets\audio\menu"
    mkdir "..\..\assets\audio\game"
    echo ✅ Assets directory structure created
)

echo 🚀 Launching Asset Generator GUI...
echo.

REM Launch the GUI
python asset_gui.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Error occurred while running the GUI
    echo Check the error messages above for details
    pause
    exit /b 1
)

echo.
echo ✅ Asset Generator GUI closed successfully
pause
