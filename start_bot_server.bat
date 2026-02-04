@echo off
title ETD UGM Crawler Bot Server
echo ========================================
echo  ETD UGM Crawler Telegram Bot Server
echo ========================================
echo.
echo Starting bot server...
echo Press Ctrl+C to stop the server
echo Logs will be saved to bot_server.log
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check if requirements are installed
python -c "import telegram" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install requirements
        pause
        exit /b 1
    )
)

REM Start the bot server
python run_bot_server.py

echo.
echo Bot server stopped.
pause