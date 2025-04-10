@echo off
cd /d "%~dp0"
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
) else (
    echo Virtual environment not found. Please set up the game first.
    pause
    exit /b 1
)
python main.py
if errorlevel 1 (
    echo Game crashed. Please check the error message above.
    pause
) 