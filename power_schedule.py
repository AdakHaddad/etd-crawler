#!/usr/bin/env python3
"""
Power Schedule Manager for ETD Bot
Automatically manages computer power and bot startup
"""

import schedule
import time
import subprocess
import os
import logging
from datetime import datetime
import platform

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('power_schedule.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PowerScheduler:
    def __init__(self):
        self.system = platform.system()
        self.bot_running = False
        
    def wake_computer(self):
        """Wake up the computer (if sleeping)"""
        try:
            if self.system == "Windows":
                # Wake up Windows computer
                subprocess.run(["powercfg", "/devicequery", "wake_armed"], check=True)
                logger.info("Computer wake command sent")
            elif self.system == "Linux":
                # Wake up Linux computer
                subprocess.run(["sudo", "rtcwake", "-m", "on", "-t", str(int(time.time()) + 60)], check=True)
                logger.info("Computer wake command sent")
            elif self.system == "Darwin":  # macOS
                # Wake up macOS computer
                subprocess.run(["caffeinate", "-u", "-t", "1"], check=True)
                logger.info("Computer wake command sent")
        except Exception as e:
            logger.error(f"Failed to wake computer: {e}")
    
    def start_bot(self):
        """Start the ETD bot server"""
        try:
            logger.info("Starting ETD Bot server...")
            
            if self.system == "Windows":
                # Start bot on Windows
                subprocess.Popen([
                    "cmd", "/c", "start", "/min", "ETD Bot Server", 
                    os.path.join(os.getcwd(), "start_bot_server.bat")
                ])
            else:
                # Start bot on Linux/Mac
                subprocess.Popen([
                    "python3", os.path.join(os.getcwd(), "run_bot_server.py")
                ])
            
            self.bot_running = True
            logger.info("ETD Bot server started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start bot: {e}")
    
    def stop_bot(self):
        """Stop the ETD bot server"""
        try:
            logger.info("Stopping ETD Bot server...")
            
            if self.system == "Windows":
                # Stop bot on Windows
                subprocess.run(["taskkill", "/f", "/im", "python.exe"], capture_output=True)
            else:
                # Stop bot on Linux/Mac
                subprocess.run(["pkill", "-f", "run_bot_server.py"], capture_output=True)
            
            self.bot_running = False
            logger.info("ETD Bot server stopped")
            
        except Exception as e:
            logger.error(f"Failed to stop bot: {e}")
    
    def schedule_events(self):
        """Schedule all power and bot events"""
        
        # Schedule bot startup at 7 PM daily
        schedule.every().day.at("19:00").do(self.start_bot)
        
        # Schedule bot shutdown at 11 PM daily (optional)
        schedule.every().day.at("23:00").do(self.stop_bot)
        
        # Schedule computer wake at 6:55 PM (5 minutes before bot starts)
        schedule.every().day.at("18:55").do(self.wake_computer)
        
        logger.info("Power schedule configured:")
        logger.info("- Computer wake: 6:55 PM")
        logger.info("- Bot start: 7:00 PM")
        logger.info("- Bot stop: 11:00 PM")
    
    def run_scheduler(self):
        """Run the power scheduler"""
        logger.info("Power Scheduler started")
        logger.info(f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.schedule_events()
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("Power Scheduler stopped by user")
        except Exception as e:
            logger.error(f"Power Scheduler error: {e}")

def main():
    """Main entry point"""
    print("=" * 60)
    print("🕰️  ETD Bot Power Scheduler")
    print("=" * 60)
    print("This will automatically:")
    print("- Wake computer at 6:55 PM")
    print("- Start bot at 7:00 PM")
    print("- Stop bot at 11:00 PM")
    print("=" * 60)
    
    scheduler = PowerScheduler()
    scheduler.run_scheduler()

if __name__ == "__main__":
    main()