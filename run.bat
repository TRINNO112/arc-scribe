@echo off
TITLE Arc Scribe - Web Novel Enactment Studio
cd /d "%~dp0"

echo ========================================================
echo        ARC SCRIBE - NOVEL ENACTMENT STUDIO
echo ========================================================
echo.

IF NOT EXIST ".venv\Scripts\python.exe" (
    echo [!] Virtual environment not found. Creating .venv...
    python -m venv .venv
    call .venv\Scripts\activate.bat
    pip install -r requirements.txt
) ELSE (
    call .venv\Scripts\activate.bat
)

echo [*] Starting Arc Scribe Server...
echo [*] Open http://localhost:8000 on this PC
echo [*] Or open http://[YOUR-LOCAL-IP]:8000 on your smartphone!
echo.

python main.py

pause
