#!/bin/bash

# ETD UGM Crawler Telegram Bot Server Startup Script

echo "========================================"
echo " ETD UGM Crawler Telegram Bot Server"
echo "========================================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8+ and try again"
    exit 1
fi

# Check if requirements are installed
if ! python3 -c "import telegram" &> /dev/null; then
    echo "Installing required packages..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install requirements"
        exit 1
    fi
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Start the bot server
echo "Starting bot server..."
echo "Press Ctrl+C to stop the server"
echo "Logs will be saved to bot_server.log"
echo

python3 run_bot_server.py

echo
echo "Bot server stopped."