# 🖥️ ETD UGM Crawler Bot - Server Setup Guide

## 🎯 Overview
This guide shows you how to run the ETD UGM Crawler Telegram Bot as a background server on your PC.

## 📋 Prerequisites
- Python 3.8+ installed
- Telegram Bot Token from @BotFather
- Stable internet connection
- PC that can run 24/7 (optional but recommended)

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Bot Token
Edit `telegram_bot.py` and set your bot token:
```python
BOT_TOKEN = "your_actual_bot_token_here"
```

### 3. Start the Server

#### Windows:
```bash
# Double-click or run:
start_bot_server.bat
```

#### Linux/Mac:
```bash
# Make executable and run:
chmod +x start_bot_server.sh
./start_bot_server.sh
```

#### Manual Start:
```bash
python run_bot_server.py
```

## 🔧 Running as a Service

### Windows (Task Scheduler)
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger to "At startup"
4. Action: Start a program
5. Program: `python.exe`
6. Arguments: `run_bot_server.py`
7. Start in: Your bot directory

### Linux (Systemd Service)
1. Copy `etd-bot.service` to `/etc/systemd/system/`
2. Edit the service file with your paths:
```bash
sudo nano /etc/systemd/system/etd-bot.service
```
3. Update paths in the service file:
   - `User=your_username`
   - `WorkingDirectory=/path/to/your/bot/directory`
   - `ExecStart=/usr/bin/python3 /path/to/your/bot/directory/run_bot_server.py`

4. Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable etd-bot.service
sudo systemctl start etd-bot.service
```

5. Check status:
```bash
sudo systemctl status etd-bot.service
```

## 📊 Monitoring

### Log Files
- **Main log**: `bot_server.log`
- **System logs**: Check systemd journal (Linux) or Event Viewer (Windows)

### Check Bot Status
```bash
# Linux
sudo systemctl status etd-bot.service
sudo journalctl -u etd-bot.service -f

# Windows
# Check Task Manager or Event Viewer
```

### Bot Commands (via Telegram)
- `/status` - Check crawling status
- `/database` - View found PDFs
- `/help` - Show all commands

## 🔄 Auto-Restart

### Linux (Systemd)
The service file includes auto-restart:
```ini
Restart=always
RestartSec=10
```

### Windows (Task Scheduler)
Set the task to restart on failure in Task Scheduler.

## 🛡️ Security Considerations

### Firewall
- Ensure your PC can make outbound HTTPS connections
- No inbound ports need to be opened (bot uses webhooks)

### Bot Token Security
- Keep your bot token secure
- Don't share it publicly
- Consider using environment variables

### File Permissions
```bash
# Linux - Secure the bot files
chmod 600 telegram_bot.py
chmod 644 *.log
```

## 📱 Usage Examples

Once running, users can interact with your bot:

```
/search 624012          # Search for specific PDF
/crawl 1 100           # Crawl PDFs from ID 1 to 100
/status                # Check current status
/database              # View found PDFs
```

## 🔧 Troubleshooting

### Bot Not Responding
1. Check if the server is running
2. Verify bot token is correct
3. Check internet connection
4. Review logs for errors

### Server Won't Start
1. Check Python installation
2. Verify all dependencies are installed
3. Check file permissions
4. Review error messages in console

### High CPU/Memory Usage
1. Check crawling progress
2. Monitor database size
3. Consider limiting crawl ranges
4. Restart server if needed

## 📈 Performance Tips

### Optimize for 24/7 Operation
- Use SSD storage for better performance
- Monitor disk space (database grows over time)
- Set up log rotation
- Consider using a VPS for better uptime

### Database Management
- Database is automatically saved
- Consider periodic backups
- Monitor file size growth

## 🔄 Updates

To update the bot:
1. Stop the service
2. Update the code
3. Restart the service

```bash
# Linux
sudo systemctl stop etd-bot.service
# Update code
sudo systemctl start etd-bot.service
```

## 📞 Support

### Logs Location
- **Application logs**: `bot_server.log`
- **System logs**: System journal (Linux) or Event Viewer (Windows)

### Common Issues
1. **Bot token invalid**: Check token in @BotFather
2. **Network errors**: Check internet connection
3. **Permission denied**: Check file permissions
4. **Service won't start**: Check systemd logs

---

**Your ETD UGM Crawler Bot is now running as a server! 🚀**

Users can now access it 24/7 through Telegram, and it will automatically crawl and search PDFs from the UGM ETD system.