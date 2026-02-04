import os
import json
import time
import requests
import fitz  # PyMuPDF
from datetime import datetime
import threading
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import logging

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # Replace with your bot token
BASE_URL = "http://etd.intranet.lib.ugm/home/detail_pencarian_downloadfiles/"
SESSION_COOKIE = "98bd8iuo8b0ifo9vsneg5b30cd3gtgjv"

# Database to store crawled PDFs
CRAWL_DB_FILE = "crawled_pdfs.json"
crawled_pdfs = {}
crawl_status = {
    "is_running": False,
    "current_id": 0,
    "total_found": 0,
    "start_time": 0,
    "end_id": 0
}

def load_crawl_database():
    global crawled_pdfs
    if os.path.exists(CRAWL_DB_FILE):
        try:
            with open(CRAWL_DB_FILE, 'r', encoding='utf-8') as f:
                crawled_pdfs = json.load(f)
            logger.info(f"Loaded {len(crawled_pdfs)} entries from database")
        except Exception as e:
            logger.error(f"Error loading database: {e}")
            crawled_pdfs = {}
    else:
        crawled_pdfs = {}

def save_crawl_database():
    with open(CRAWL_DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(crawled_pdfs, f, ensure_ascii=False, indent=2)

def extract_pdf_title(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        first_page = doc.load_page(0)
        
        # Try getting text in blocks which might preserve formatting better
        text_blocks = first_page.get_text("blocks")
        
        # If we have blocks, the first substantial block is likely the title
        if text_blocks and len(text_blocks) > 0:
            for block in text_blocks:
                if isinstance(block, tuple) and len(block) >= 4:
                    candidate = block[4].strip()
                    if candidate and len(candidate) > 5:  # Assuming title is at least 5 chars
                        doc.close()
                        return candidate
        
        # Fallback to regular text extraction
        text = first_page.get_text("text").strip()
        
        # Look for potential title by getting first non-empty lines
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Combine first few lines that might form the title (usually within first 5 lines)
        potential_title = ' '.join(lines[:3])
        
        doc.close()
        
        # If we have something substantial, return it
        if potential_title and len(potential_title) > 5:
            return potential_title
            
        # If nothing works, return a placeholder
        return "Unknown Title"
    except Exception as e:
        logger.error(f"Error extracting title: {e}")
        return "Error Extracting Title"

def search_pdf_by_id(doc_id):
    """Search for a PDF by document ID"""
    try:
        headers = {'Cookie': f'ugmfw_session={SESSION_COOKIE}'}
        url = f"{BASE_URL}{doc_id}"
        r = requests.get(url, headers=headers, timeout=10)
        
        if 'attachment; filename=' in r.headers.get('Content-Disposition', ''):
            filename = r.headers['Content-Disposition'].split('filename=')[1].strip('"')
            
            # Create a temporary directory
            temp_dir = os.path.join("temp_downloads")
            os.makedirs(temp_dir, exist_ok=True)
            temp_path = os.path.join(temp_dir, filename)
            
            # Temporarily save for title extraction
            with open(temp_path, 'wb') as f:
                f.write(r.content)
            
            # Extract PDF title
            title = extract_pdf_title(temp_path)
            
            # Delete the file after getting the title
            try:
                os.remove(temp_path)
            except Exception as e:
                logger.error(f"Error deleting temporary file: {e}")
            
            # Try to remove temp directory if empty
            try:
                os.rmdir(temp_dir)
            except:
                pass
            
            # Store in our database
            crawled_pdfs[str(doc_id)] = {
                "id": doc_id,
                "filename": filename,
                "title": title,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "direct_url": url
            }
            save_crawl_database()
            
            return {
                "found": True,
                "filename": filename,
                "title": title,
                "download_url": url,
                "size": len(r.content)
            }
        else:
            return {"found": False, "message": "No PDF found or access denied"}
    except Exception as e:
        return {"found": False, "message": f"Error: {str(e)}"}

def crawl_pdfs(start_id, end_id, progress_callback=None):
    """Crawl PDFs in a range of IDs"""
    global crawl_status
    
    crawl_status["is_running"] = True
    crawl_status["current_id"] = start_id
    crawl_status["total_found"] = 0
    crawl_status["start_time"] = time.time()
    crawl_status["end_id"] = end_id
    
    headers = {'Cookie': f'ugmfw_session={SESSION_COOKIE}'}
    
    for doc_id in range(start_id, end_id + 1):
        # Update current ID in status
        crawl_status["current_id"] = doc_id
        
        # Skip if already crawled
        if str(doc_id) in crawled_pdfs:
            continue
            
        try:
            url = f"{BASE_URL}{doc_id}"
            r = requests.get(url, headers=headers, timeout=10)
            
            if 'attachment; filename=' in r.headers.get('Content-Disposition', ''):
                filename = r.headers['Content-Disposition'].split('filename=')[1].strip('"')
                
                # Create a temporary directory
                temp_dir = os.path.join("temp_downloads")
                os.makedirs(temp_dir, exist_ok=True)
                temp_path = os.path.join(temp_dir, filename)
                
                # Temporarily save for title extraction
                with open(temp_path, 'wb') as f:
                    f.write(r.content)
                
                # Extract PDF title
                title = extract_pdf_title(temp_path)
                
                # Delete the file after getting the title
                try:
                    os.remove(temp_path)
                except Exception as e:
                    logger.error(f"Error deleting temporary file: {e}")
                
                # Store in our database
                crawled_pdfs[str(doc_id)] = {
                    "id": doc_id,
                    "filename": filename,
                    "title": title,
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "direct_url": url
                }
                
                crawl_status["total_found"] += 1
                
                # Save database periodically
                if crawl_status["total_found"] % 10 == 0:
                    save_crawl_database()
                
                # Call progress callback if provided
                if progress_callback:
                    progress_callback(doc_id, crawl_status["total_found"], title)
                
                logger.info(f"Found document {doc_id}: {title}")
            
            # Be nice to the server - don't hammer it
            time.sleep(1)
            
        except Exception as e:
            logger.error(f"Error processing document {doc_id}: {e}")
    
    # Final save
    save_crawl_database()
    
    # Cleanup temp directory if it's empty
    try:
        os.rmdir("temp_downloads")
    except:
        pass
        
    crawl_status["is_running"] = False
    logger.info(f"Crawl completed. Found {crawl_status['total_found']} documents.")

# Telegram Bot Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    welcome_message = """
🤖 **ETD UGM Crawler Bot**

Selamat datang! Bot ini membantu Anda mencari dan mengunduh PDF dari ETD UGM.

**Perintah yang tersedia:**
/search [ID] - Cari PDF berdasarkan ID dokumen
/crawl [start] [end] - Crawl PDF dalam rentang ID
/status - Lihat status crawling
/database - Lihat database PDF yang ditemukan
/help - Tampilkan bantuan

**Contoh:**
/search 624012
/crawl 1 100
"""
    
    keyboard = [
        [InlineKeyboardButton("🔍 Cari PDF", callback_data="search")],
        [InlineKeyboardButton("🕷️ Mulai Crawl", callback_data="crawl")],
        [InlineKeyboardButton("📊 Status", callback_data="status")],
        [InlineKeyboardButton("📚 Database", callback_data="database")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_message, reply_markup=reply_markup, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    help_text = """
📖 **Bantuan ETD UGM Crawler Bot**

**Perintah:**
• `/search [ID]` - Cari PDF berdasarkan ID dokumen
• `/crawl [start] [end]` - Crawl PDF dalam rentang ID
• `/status` - Lihat status crawling saat ini
• `/database` - Lihat database PDF yang ditemukan
• `/help` - Tampilkan bantuan ini

**Contoh penggunaan:**
• `/search 624012` - Cari PDF dengan ID 624012
• `/crawl 1 100` - Crawl PDF dari ID 1 sampai 100
• `/status` - Lihat progress crawling

**Catatan:**
• Crawling membutuhkan waktu, mohon bersabar
• Database disimpan otomatis
• Server UGM memiliki rate limit, jadi ada delay antar request
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /search command"""
    if not context.args:
        await update.message.reply_text("❌ Mohon berikan ID dokumen.\nContoh: /search 624012")
        return
    
    try:
        doc_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ ID dokumen harus berupa angka.")
        return
    
    # Send searching message
    searching_msg = await update.message.reply_text(f"🔍 Mencari PDF dengan ID {doc_id}...")
    
    # Search for PDF
    result = search_pdf_by_id(doc_id)
    
    if result["found"]:
        message = f"""
✅ **PDF Ditemukan!**

📄 **Judul:** {result['title']}
📁 **File:** {result['filename']}
📏 **Ukuran:** {result['size']:,} bytes
🔗 **Download:** [Klik di sini]({result['download_url']})

ID: {doc_id}
"""
        keyboard = [
            [InlineKeyboardButton("📥 Download PDF", url=result['download_url'])]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await searching_msg.edit_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await searching_msg.edit_text(f"❌ {result['message']}")

async def crawl_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /crawl command"""
    if crawl_status["is_running"]:
        await update.message.reply_text("⚠️ Crawling sedang berjalan. Tunggu hingga selesai.")
        return
    
    if len(context.args) != 2:
        await update.message.reply_text("❌ Mohon berikan range ID.\nContoh: /crawl 1 100")
        return
    
    try:
        start_id = int(context.args[0])
        end_id = int(context.args[1])
    except ValueError:
        await update.message.reply_text("❌ ID harus berupa angka.")
        return
    
    if start_id > end_id:
        await update.message.reply_text("❌ ID awal harus lebih kecil dari ID akhir.")
        return
    
    if end_id - start_id > 1000:
        await update.message.reply_text("❌ Range terlalu besar. Maksimal 1000 ID per crawling.")
        return
    
    # Start crawling
    crawl_msg = await update.message.reply_text(f"🕷️ Memulai crawling dari ID {start_id} sampai {end_id}...")
    
    def progress_callback(current_id, total_found, title):
        # This will be called from the crawling thread
        pass
    
    # Start crawling in a separate thread
    def crawl_thread():
        crawl_pdfs(start_id, end_id, progress_callback)
    
    thread = threading.Thread(target=crawl_thread)
    thread.daemon = True
    thread.start()
    
    # Monitor progress
    while crawl_status["is_running"]:
        current_id = crawl_status["current_id"]
        total_found = crawl_status["total_found"]
        elapsed = int(time.time() - crawl_status["start_time"])
        
        progress_msg = f"""
🕷️ **Crawling in Progress...**

📊 **Progress:** {current_id}/{end_id}
✅ **Ditemukan:** {total_found} PDF
⏱️ **Waktu:** {elapsed}s
🔄 **Status:** Sedang berjalan...
"""
        await crawl_msg.edit_text(progress_msg, parse_mode='Markdown')
        time.sleep(5)
    
    # Final status
    final_total = crawl_status["total_found"]
    final_elapsed = int(time.time() - crawl_status["start_time"])
    
    final_msg = f"""
✅ **Crawling Selesai!**

📊 **Total ditemukan:** {final_total} PDF
⏱️ **Waktu total:** {final_elapsed}s
📚 **Database:** {len(crawled_pdfs)} total PDF

Gunakan /database untuk melihat hasil.
"""
    await crawl_msg.edit_text(final_msg, parse_mode='Markdown')

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command"""
    if crawl_status["is_running"]:
        current_id = crawl_status["current_id"]
        end_id = crawl_status["end_id"]
        total_found = crawl_status["total_found"]
        elapsed = int(time.time() - crawl_status["start_time"])
        
        status_msg = f"""
🔄 **Crawling Sedang Berjalan**

📊 **Progress:** {current_id}/{end_id}
✅ **Ditemukan:** {total_found} PDF
⏱️ **Waktu:** {elapsed}s
"""
    else:
        status_msg = f"""
📊 **Status Bot**

🔄 **Crawling:** Tidak aktif
📚 **Database:** {len(crawled_pdfs)} PDF tersimpan
"""
    
    await update.message.reply_text(status_msg, parse_mode='Markdown')

async def database_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /database command"""
    if not crawled_pdfs:
        await update.message.reply_text("📚 Database kosong. Gunakan /crawl untuk mencari PDF.")
        return
    
    # Show first 10 entries
    message = "📚 **Database PDF (10 terbaru):**\n\n"
    
    # Sort by ID and get last 10
    sorted_pdfs = sorted(crawled_pdfs.values(), key=lambda x: int(x["id"]), reverse=True)[:10]
    
    for pdf in sorted_pdfs:
        message += f"📄 **{pdf['title'][:50]}...**\n"
        message += f"   ID: {pdf['id']} | {pdf['date']}\n\n"
    
    if len(crawled_pdfs) > 10:
        message += f"... dan {len(crawled_pdfs) - 10} PDF lainnya"
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "search":
        await query.edit_message_text("🔍 **Cari PDF**\n\nKetik: /search [ID]\nContoh: /search 624012", parse_mode='Markdown')
    elif query.data == "crawl":
        await query.edit_message_text("🕷️ **Mulai Crawl**\n\nKetik: /crawl [start] [end]\nContoh: /crawl 1 100", parse_mode='Markdown')
    elif query.data == "status":
        await status_command(update, context)
    elif query.data == "database":
        await database_command(update, context)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular text messages"""
    text = update.message.text
    
    # Check if it's a number (potential document ID)
    if text.isdigit():
        doc_id = int(text)
        await search_command(update, context)
    else:
        await update.message.reply_text("❓ Tidak mengerti. Gunakan /help untuk melihat perintah yang tersedia.")

def main():
    """Start the bot."""
    # Load database
    load_crawl_database()
    
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("search", search_command))
    application.add_handler(CommandHandler("crawl", crawl_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("database", database_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Run the bot
    print("🤖 ETD UGM Crawler Bot is starting...")
    print("📚 Database loaded with", len(crawled_pdfs), "entries")
    application.run_polling()

if __name__ == '__main__':
    main()