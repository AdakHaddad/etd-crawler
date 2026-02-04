#!/usr/bin/env python3
"""
ETD UGM Crawler Telegram Bot Server
Run this as a background service on your PC
"""

import os
import sys
import signal
import logging
import time
from datetime import datetime
import threading
from telegram_bot import main as bot_main

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot_server.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class BotServer:
    def __init__(self):
        self.running = False
        self.bot_thread = None
        
    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}. Shutting down gracefully...")
        self.stop()
        
    def start(self):
        """Start the bot server"""
        if self.running:
            logger.warning("Bot server is already running!")
            return
            
        logger.info("🤖 Starting ETD UGM Crawler Bot Server...")
        self.running = True
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        try:
            # Start the bot in the main thread
            bot_main()
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt. Shutting down...")
        except Exception as e:
            logger.error(f"Bot server error: {e}")
        finally:
            self.stop()
            
    def stop(self):
        """Stop the bot server"""
        if not self.running:
            return
            
        logger.info("🛑 Stopping bot server...")
        self.running = False
        
        # Give some time for cleanup
        time.sleep(2)
        logger.info("✅ Bot server stopped.")

def main():
    """Main entry point"""
    print("=" * 60)
    print("🤖 ETD UGM Crawler Telegram Bot Server")
    print("=" * 60)
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("📝 Logs will be saved to: bot_server.log")
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 60)
    
    # Check if bot token is configured
    try:
        from telegram_bot import BOT_TOKEN
        if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
            print("❌ ERROR: Bot token not configured!")
            print("Please edit telegram_bot.py and set your BOT_TOKEN")
            sys.exit(1)
    except ImportError:
        print("❌ ERROR: Cannot import telegram_bot.py")
        print("Make sure telegram_bot.py is in the same directory")
        sys.exit(1)
    
    # Start the server
    server = BotServer()
    server.start()

if __name__ == "__main__":
    main()