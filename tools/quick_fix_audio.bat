@echo off
echo Running Runic Lands Quick Audio Fixer...
echo This will automatically fix the menu music files.
echo.

echo Installing required packages...
python -m pip install numpy --quiet
if %ERRORLEVEL% NEQ 0 (
    echo Warning: Failed to install numpy. The script may not work correctly.
    echo Please install numpy manually by running: python -m pip install numpy
    echo.
    pause
    exit /b 1
)

echo.
python quick_fix_audio.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo An error occurred while running the audio fixer.
    pause
    exit /b 1
)

echo.
echo Quick audio fixing process completed!
echo You can now run the game to test if the menu music plays correctly.
pause 