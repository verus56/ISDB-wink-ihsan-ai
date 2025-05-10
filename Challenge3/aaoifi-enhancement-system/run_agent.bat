@echo off
echo AAOIFI Enhancement System
echo ========================
echo.

REM Check if Python is installed
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.7 or higher and try again
    pause
    exit /b 1
)

echo Installing required packages...
python -m pip install -r requirements.txt

echo.
echo Testing PDF loading...
python test_pdf_loading.py

echo.
echo Starting the agent...
python run_agent.py

pause
