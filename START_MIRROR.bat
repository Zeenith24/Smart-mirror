@echo off
REM ─────────────────────────────────────────────────────────────
REM  Magic Mirror AI — Windows Auto-Start Script
REM  Double-click this, or add it to Task Scheduler / Startup folder
REM ─────────────────────────────────────────────────────────────

REM Change this to wherever you put the mirror_ai folder:
set MIRROR_DIR=%~dp0

cd /d "%MIRROR_DIR%"

echo ============================================================
echo   MAGIC MIRROR AI - STARTING UP
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10+ from python.org
    pause
    exit /b 1
)

REM Check if main.py exists
if not exist main.py (
    echo ERROR: main.py not found in %MIRROR_DIR%
    echo Please make sure you're running this from the mirror_ai folder
    pause
    exit /b 1
)

REM Check if requirements are installed
echo Checking dependencies...
python -c "import cv2, yaml, numpy, pyttsx3, pygame" >nul 2>&1
if errorlevel 1 (
    echo.
    echo WARNING: Some dependencies are missing
    echo Installing required packages...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo ERROR: Failed to install dependencies
        echo Please run manually: pip install -r requirements.txt
        pause
        exit /b 1
    )
)

echo.
echo Starting Magic Mirror AI...
echo Log file: logs\mirror.log
echo Press Ctrl+C to stop
echo.
echo ============================================================
echo.

:RESTART
python main.py

REM Check if it was a clean exit (Ctrl+C) or a crash
if errorlevel 1 (
    echo.
    echo ============================================================
    echo   Mirror crashed! Check logs\mirror.log for errors
    echo ============================================================
    echo.
    echo Common issues:
    echo   - "No module named 'edge_tts'" : Run: pip install edge-tts
    echo   - Camera error                 : Check webcam is plugged in
    echo   - Microphone error             : Check mic in Windows Sound settings
    echo.
    echo Restarting in 10 seconds...
    echo Press Ctrl+C to cancel
    timeout /t 10 /nobreak >nul
    goto RESTART
) else (
    echo.
    echo Mirror stopped cleanly. Goodbye!
    pause
)