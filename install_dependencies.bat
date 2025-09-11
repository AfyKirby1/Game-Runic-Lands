@echo off
echo 🎮 Runic Lands - Dependency Installer
echo =====================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://python.org
    pause
    exit /b 1
)

echo ✅ Python found
echo.

REM Install all dependencies
echo 📦 Installing all required packages...
echo This may take a few minutes...
echo.

pip install -r docs/requirements.txt

if errorlevel 1 (
    echo.
    echo ❌ Failed to install some dependencies
    echo 💡 Try running these commands manually:
    echo    pip install pygame>=2.5.0
    echo    pip install opensimplex>=0.4.5
    echo    pip install numpy==2.2.4
    echo    pip install scipy==1.15.2
    echo    pip install pillow==11.1.0
    echo    pip install pytmx==3.32
    echo    pip install pyscroll==2.31
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ All dependencies installed successfully!
echo 🎮 You can now run the game with launch_game.bat
echo.
pause

