@echo off
echo Runic Lands Menu Music Generator
echo This will create new menu music sections with proper musical notes.
echo.

echo Installing required package (numpy)...
python -m pip install numpy --quiet
if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to install numpy. Please install it manually:
    echo python -m pip install numpy
    pause
    exit /b 1
)

echo.
echo Generating menu music sections...
python generate_menu_music.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Error: Failed to generate menu music.
    pause
    exit /b 1
)

echo.
echo Menu music generation complete!
echo The new audio files have been saved in the assets/audio directory.
pause 