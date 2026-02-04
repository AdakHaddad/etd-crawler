@echo off
title ETD Bot Auto Startup Setup
echo ========================================
echo  ETD Bot Auto Startup Setup (7 PM)
echo ========================================
echo.

REM Create a scheduled task to wake computer and start bot
echo Creating scheduled task for 7 PM startup...

schtasks /create /tn "ETD Bot Auto Start" /tr "cmd /c start /min \"ETD Bot Server\" \"%~dp0start_bot_server.bat\"" /sc daily /st 19:00 /ru "SYSTEM" /f

if %errorlevel% equ 0 (
    echo ✅ Task created successfully!
    echo.
    echo The computer will now:
    echo - Wake up at 7:00 PM daily
    echo - Start the ETD Bot server automatically
    echo.
    echo To modify or delete this task:
    echo - Open Task Scheduler
    echo - Look for "ETD Bot Auto Start"
) else (
    echo ❌ Failed to create task. Please run as Administrator.
    echo.
    echo Manual setup:
    echo 1. Open Task Scheduler
    echo 2. Create Basic Task
    echo 3. Name: "ETD Bot Auto Start"
    echo 4. Trigger: Daily at 7:00 PM
    echo 5. Action: Start program
    echo 6. Program: %~dp0start_bot_server.bat
)

echo.
echo Press any key to continue...
pause >nul