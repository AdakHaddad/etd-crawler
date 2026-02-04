#!/usr/bin/env python3
"""
Complete Auto-Startup Setup for ETD Bot
Sets up automatic computer wake and bot startup at 7 PM
"""

import os
import sys
import subprocess
import platform
from datetime import datetime

def setup_windows_auto_startup():
    """Setup auto-startup for Windows"""
    print("Setting up Windows auto-startup...")
    
    # Create startup script
    startup_script = """@echo off
title ETD Bot Auto Startup
echo Starting ETD Bot at 7 PM...
cd /d "{}"
start /min "ETD Bot Server" start_bot_server.bat
""".format(os.getcwd())
    
    with open("auto_startup.bat", "w") as f:
        f.write(startup_script)
    
    # Create scheduled task
    task_xml = f"""<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <Triggers>
    <CalendarTrigger>
      <StartBoundary>2024-01-01T19:00:00</StartBoundary>
      <Enabled>true</Enabled>
      <ScheduleByDay>
        <DaysInterval>1</DaysInterval>
      </ScheduleByDay>
    </CalendarTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>S-1-5-18</UserId>
      <RunLevel>HighestAvailable</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>false</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>true</WakeToRun>
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>{os.path.join(os.getcwd(), "auto_startup.bat")}</Command>
    </Exec>
  </Actions>
</Task>"""
    
    with open("etd_bot_task.xml", "w") as f:
        f.write(task_xml)
    
    try:
        # Import the task
        subprocess.run([
            "schtasks", "/create", "/tn", "ETD Bot Auto Start", 
            "/xml", "etd_bot_task.xml", "/f"
        ], check=True)
        print("✅ Windows scheduled task created successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to create scheduled task. Please run as Administrator.")
        return False

def setup_linux_auto_startup():
    """Setup auto-startup for Linux"""
    print("Setting up Linux auto-startup...")
    
    # Create systemd timer
    timer_content = f"""[Unit]
Description=ETD Bot Auto Start Timer
Requires=etd-bot.service

[Timer]
OnCalendar=daily
Persistent=true
WakeSystem=true

[Install]
WantedBy=timers.target"""
    
    with open("etd-bot.timer", "w") as f:
        f.write(timer_content)
    
    # Create startup script
    startup_script = f"""#!/bin/bash
# ETD Bot Auto Startup Script
cd "{os.getcwd()}"
python3 run_bot_server.py &
"""
    
    with open("auto_startup.sh", "w") as f:
        f.write(startup_script)
    
    os.chmod("auto_startup.sh", 0o755)
    
    print("✅ Linux auto-startup files created!")
    print("To complete setup:")
    print("1. sudo cp etd-bot.timer /etc/systemd/system/")
    print("2. sudo systemctl enable etd-bot.timer")
    print("3. sudo systemctl start etd-bot.timer")
    
    return True

def setup_mac_auto_startup():
    """Setup auto-startup for macOS"""
    print("Setting up macOS auto-startup...")
    
    # Create launchd plist
    plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.etdbot.autostart</string>
    <key>ProgramArguments</key>
    <array>
        <string>python3</string>
        <string>{os.path.join(os.getcwd(), "run_bot_server.py")}</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>19</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>RunAtLoad</key>
    <false/>
    <key>KeepAlive</key>
    <false/>
</dict>
</plist>"""
    
    with open("com.etdbot.autostart.plist", "w") as f:
        f.write(plist_content)
    
    print("✅ macOS auto-startup file created!")
    print("To complete setup:")
    print("1. cp com.etdbot.autostart.plist ~/Library/LaunchAgents/")
    print("2. launchctl load ~/Library/LaunchAgents/com.etdbot.autostart.plist")
    
    return True

def main():
    """Main setup function"""
    print("=" * 60)
    print("🕰️  ETD Bot Auto-Startup Setup (7 PM)")
    print("=" * 60)
    print(f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("This will set up automatic computer wake and bot startup at 7 PM")
    print("=" * 60)
    
    system = platform.system()
    
    if system == "Windows":
        success = setup_windows_auto_startup()
    elif system == "Linux":
        success = setup_linux_auto_startup()
    elif system == "Darwin":  # macOS
        success = setup_mac_auto_startup()
    else:
        print(f"❌ Unsupported operating system: {system}")
        return
    
    if success:
        print("\n" + "=" * 60)
        print("✅ Auto-startup setup completed!")
        print("=" * 60)
        print("Your computer will now:")
        print("- Wake up at 7:00 PM daily")
        print("- Start the ETD Bot server automatically")
        print("- Run the bot until you stop it")
        print("\nTo test:")
        print("1. Put computer to sleep")
        print("2. Wait until 7 PM")
        print("3. Computer should wake up and start the bot")
        print("\nTo disable:")
        if system == "Windows":
            print("- Open Task Scheduler")
            print("- Delete 'ETD Bot Auto Start' task")
        elif system == "Linux":
            print("- sudo systemctl disable etd-bot.timer")
        elif system == "Darwin":
            print("- launchctl unload ~/Library/LaunchAgents/com.etdbot.autostart.plist")
    else:
        print("\n❌ Setup failed. Please check the error messages above.")

if __name__ == "__main__":
    main()