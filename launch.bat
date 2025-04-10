@echo off
REM Activate your virtual environment if you have one
REM Example: call .venv\Scripts\activate.bat

REM Change directory to the script's location
cd /d "%~dp0"

echo Launching Runic Lands...
python main.py

echo Game execution finished.
pause 