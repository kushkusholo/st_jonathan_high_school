@echo off
REM St. Jonathan High School Chatbot Launcher
REM This script sets up and runs the chatbot on Windows

echo.
echo ========================================
echo ST. JONATHAN HIGH SCHOOL CHATBOT
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo [✓] Python found

REM Check if virtual environment exists
if not exist "venv\" (
    echo [!] Creating virtual environment...
    python -m venv venv
    echo [✓] Virtual environment created
)

REM Activate virtual environment
echo [!] Activating virtual environment...
call venv\Scripts\activate.bat

REM Install requirements
echo [!] Installing dependencies...
pip install -r requirements.txt >nul
echo [✓] Dependencies installed

REM Run the Flask app
echo.
echo ========================================
echo Starting chatbot server...
echo ========================================
echo.
echo Open your browser and go to:
echo    http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.
echo ========================================
echo.

python app.py

pause
