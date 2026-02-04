# 🤖 ETD UGM Crawler Telegram Bot Setup

## 📋 Prerequisites

1. **Python 3.8+** installed
2. **Telegram Bot Token** from @BotFather
3. **Internet connection**

## 🚀 Quick Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Create Telegram Bot
1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Follow the instructions to create your bot
4. Copy the bot token (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 3. Configure Bot
1. Open `telegram_bot.py`
2. Replace `YOUR_BOT_TOKEN_HERE` with your actual bot token:
```python
BOT_TOKEN = "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
```

### 4. Run the Bot
```bash
python telegram_bot.py
```

## 📱 Bot Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/start` | Start the bot and show main menu | `/start` |
| `/help` | Show help information | `/help` |
| `/search [ID]` | Search PDF by document ID | `/search 624012` |
| `/crawl [start] [end]` | Crawl PDFs in ID range | `/crawl 1 100` |
| `/status` | Show current crawling status | `/status` |
| `/database` | Show database of found PDFs | `/database` |

## 🎯 Features

### ✅ **Search PDF by ID**
- Quick search for specific document
- Shows title, filename, and download link
- Direct download button

### 🕷️ **Crawl PDFs**
- Automated crawling in ID ranges
- Real-time progress updates
- Automatic database storage
- Rate limiting to respect server

### 📊 **Status Monitoring**
- Live crawling progress
- Database statistics
- Time tracking

### 📚 **Database Management**
- View found PDFs
- Search history
- Automatic saving

## 🔧 Configuration

### Bot Settings
```python
BOT_TOKEN = "your_bot_token_here"
BASE_URL = "http://etd.intranet.lib.ugm/home/detail_pencarian_downloadfiles/"
SESSION_COOKIE = "your_session_cookie"
```

### Crawling Limits
- Maximum 1000 IDs per crawl session
- 1 second delay between requests
- Automatic database saving every 10 PDFs

## 🛡️ Security Features

- Input validation for all commands
- Error handling and logging
- Rate limiting protection
- Safe file handling

## 📝 Usage Examples

### Search for a PDF
```
/search 624012
```

### Crawl PDFs from ID 1 to 100
```
/crawl 1 100
```

### Check crawling status
```
/status
```

### View database
```
/database
```

## 🚨 Troubleshooting

### Bot Not Responding
1. Check if bot token is correct
2. Ensure internet connection
3. Check if bot is running

### Crawling Errors
1. Verify session cookie is valid
2. Check UGM server availability
3. Review error logs

### Database Issues
1. Check file permissions
2. Ensure sufficient disk space
3. Verify JSON file integrity

## 📞 Support

For issues or questions:
1. Check the logs in console
2. Verify all dependencies are installed
3. Ensure proper configuration

## 🔄 Updates

The bot automatically:
- Saves progress during crawling
- Updates database in real-time
- Handles errors gracefully
- Provides user feedback

---

**Happy Crawling! 🕷️📚**