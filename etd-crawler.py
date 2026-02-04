from flask import Flask, request, render_template_string, send_file, redirect, url_for
import requests
import os
import fitz  # PyMuPDF for PDF parsing
import threading
import time
import re
from datetime import datetime
import json
import urllib.parse

app = Flask(__name__)
BASE_URL = "http://etd.intranet.lib.ugm/home/detail_pencarian_downloadfiles/"
SESSION_COOKIE = "98bd8iuo8b0ifo9vsneg5b30cd3gtgjv"  # Change if needed

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
            print(f"Loaded {len(crawled_pdfs)} entries from database")
        except Exception as e:
            print(f"Error loading database: {e}")
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
        print(f"Error extracting title: {e}")
        return "Error Extracting Title"

def crawl_pdfs(start_id, end_id):
    global crawl_status
    
    crawl_status["is_running"] = True
    crawl_status["current_id"] = start_id
    crawl_status["total_found"] = 0
    crawl_status["start_time"] = time.time()
    crawl_status["end_id"] = end_id
    
    # Create temporary directory for downloads
    temp_dir = os.path.join("temp_downloads")
    os.makedirs(temp_dir, exist_ok=True)
    
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
                temp_path = os.path.join(temp_dir, filename)
                
                # Temporarily save the file to extract the title
                with open(temp_path, 'wb') as f:
                    f.write(r.content)
                
                # Extract PDF title
                title = extract_pdf_title(temp_path)
                
                # Delete the temporary file
                try:
                    os.remove(temp_path)
                except Exception as e:
                    print(f"Error deleting temporary file: {e}")
                
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
                    
                print(f"Found document {doc_id}: {title} (metadata only)")
            
            # Be nice to the server - don't hammer it
            time.sleep(1)
            
        except Exception as e:
            print(f"Error processing document {doc_id}: {e}")
    
    # Final save
    save_crawl_database()
    
    # Cleanup temp directory if it's empty
    try:
        os.rmdir(temp_dir)  # Only removes if empty
    except:
        pass
        
    crawl_status["is_running"] = False
    print(f"Crawl completed. Found {crawl_status['total_found']} documents.")
    
@app.route('/')
def index():
    return redirect(url_for('ugm_search'))

@app.route('/ugm', methods=['GET', 'POST'])
def ugm_search():
    result = None
    if request.method == 'POST':
        doc_id = request.form.get('doc_id')
        if doc_id:
            headers = {'Cookie': f'ugmfw_session={SESSION_COOKIE}'}
            url = f"{BASE_URL}{doc_id}"
            r = requests.get(url, headers=headers)
            
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
                    print(f"Error deleting temporary file: {e}")
                
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
                
                search_link = f"https://www.google.com/search?q={urllib.parse.quote(title)}"
                download_link = f"{BASE_URL}{doc_id}"
                result = f"""✅ Found: <a href='{download_link}' target='_blank'>{filename}</a><br>
                         Title: {title}<br>
                         <a href='{search_link}' target='_blank'>Search this title on Google</a>"""
            else:
                result = "❌ No PDF found or access denied."
    
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>UGM ETD PDF Finder</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }
            .container { max-width: 900px; margin: 0 auto; }
            h2 { color: #333; }
            form { margin: 20px 0; }
            input[type="text"], input[type="number"] { padding: 8px; width: 200px; }
            input[type="submit"] { padding: 8px 15px; background: #4CAF50; color: white; border: none; cursor: pointer; }
            .result { margin: 20px 0; padding: 15px; background: #f9f9f9; border-left: 5px solid #4CAF50; }
            .tabs { overflow: hidden; border: 1px solid #ccc; background-color: #f1f1f1; }
            .tabs button { background-color: inherit; float: left; border: none; outline: none; cursor: pointer; padding: 10px 16px; }
            .tabs button:hover { background-color: #ddd; }
            .tabs button.active { background-color: #ccc; }
            .tabcontent { display: none; padding: 20px; border: 1px solid #ccc; border-top: none; }
            .visible { display: block; }
            table { width: 100%; border-collapse: collapse; }
            table, th, td { border: 1px solid #ddd; }
            th, td { padding: 8px; text-align: left; }
            tr:nth-child(even) { background-color: #f2f2f2; }
            th { background-color: #4CAF50; color: white; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>UGM ETD PDF Finder and Crawler</h2>
            
            <div class="tabs">
                <button class="tablinks active" onclick="openTab(event, 'Search')">Search by ID</button>
                <button class="tablinks" onclick="openTab(event, 'Crawler')">Crawler</button>
                <button class="tablinks" onclick="openTab(event, 'Database')">PDF Database</button>
            </div>
            
            <div id="Search" class="tabcontent visible">
                <h3>Find PDF by Document ID</h3>
                <form method="post">
                    <input type="text" name="doc_id" placeholder="Enter doc ID (e.g., 624012)" required>
                    <input type="submit" value="Check PDF">
                </form>
                {% if result %}
                    <div class="result">
                        {{ result|safe }}
                    </div>
                {% endif %}
            </div>
            
            <div id="Crawler" class="tabcontent">
                <h3>PDF Crawler</h3>
                <p>Systematically check for PDFs in a range of IDs.</p>
                <form action="/ugm/crawl" method="post">
                    <div>
                        <label for="start_id">Start ID:</label>
                        <input type="number" id="start_id" name="start_id" value="1" min="1" required>
                    </div>
                    <div>
                        <label for="end_id">End ID:</label>
                        <input type="number" id="end_id" name="end_id" value="1000" min="1" max="9999999" required>
                    </div>
                    <input type="submit" value="Start Crawling">
                </form>
                
                {% if crawl_active %}
                <div class="result">
                    <h4>Crawl Status:</h4>
                    <p>Currently scanning IDs: {{ current_id }} / {{ end_id }}</p>
                    <p>Documents found: {{ total_found }}</p>
                    <p>Running time: {{ running_time }}</p>
                </div>
                {% endif %}
            </div>
            
            <div id="Database" class="tabcontent">
                <h3>PDF Database</h3>
                <p>Search through found PDFs:</p>
                <form action="/ugm/database" method="get">
                    <input type="text" name="search" placeholder="Search by title..." value="{{ search_term }}">
                    <input type="submit" value="Search">
                </form>
                
                {% if pdf_count > 0 %}
                <p>Showing {{ showing_count }} of {{ pdf_count }} documents</p>
                <table>
                    <tr>
                        <th>ID</th>
                        <th>Title</th>
                        <th>Actions</th>
                    </tr>
                    {% for pdf in pdfs %}
                    <tr>
                        <td>{{ pdf.id }}</td>
                        <td>{{ pdf.title }}</td>
                        <td>
                            <a href="/ugm/download/{{ pdf.filename }}">Download</a> |
                            <a href="https://www.google.com/search?q={{ pdf.title|urlencode }}" target="_blank">Search</a>
                        </td>
                    </tr>
                    {% endfor %}
                </table>
                {% else %}
                <p>No PDFs found in database. Use the crawler to find some!</p>
                {% endif %}
            </div>
        </div>
        
        <script>
        function openTab(evt, tabName) {
            var i, tabcontent, tablinks;
            tabcontent = document.getElementsByClassName("tabcontent");
            for (i = 0; i < tabcontent.length; i++) {
                tabcontent[i].className = tabcontent[i].className.replace(" visible", "");
            }
            tablinks = document.getElementsByClassName("tablinks");
            for (i = 0; i < tablinks.length; i++) {
                tablinks[i].className = tablinks[i].className.replace(" active", "");
            }
            document.getElementById(tabName).className += " visible";
            evt.currentTarget.className += " active";
        }
        </script>
    </body>
    </html>
    """, result=result, crawl_active=crawl_status["is_running"], 
         current_id=crawl_status["current_id"], 
         end_id=crawl_status["end_id"],
         total_found=crawl_status["total_found"],
         running_time="N/A" if not crawl_status["start_time"] else f"{int(time.time() - crawl_status['start_time'])} seconds",
         pdf_count=len(crawled_pdfs),
         pdfs=[],
         showing_count=0,
         search_term="")

@app.route('/ugm/download/<doc_id>')
def download_file(doc_id):
    if doc_id in crawled_pdfs:
        # Redirect user to the original source URL
        return redirect(f"{BASE_URL}{doc_id}")
    else:
        return "Document not found in database.", 404

@app.route('/ugm/crawl', methods=['POST'])
def start_crawl():
    if not crawl_status["is_running"]:
        start_id = int(request.form.get('start_id', 1))
        end_id = int(request.form.get('end_id', 1000))
        
        # Start crawling in a separate thread
        thread = threading.Thread(target=crawl_pdfs, args=(start_id, end_id))
        thread.daemon = True
        thread.start()
        
    return redirect(url_for('ugm_search'))
@app.route('/ugm/database')
def database():
    search_term = request.args.get('search', '').lower()
    
    if search_term:
        filtered_pdfs = [
            pdf_data for pdf_id, pdf_data in crawled_pdfs.items()
            if search_term in pdf_data["title"].lower()
        ]
    else:
        filtered_pdfs = list(crawled_pdfs.values())
    
    # Sort by ID
    filtered_pdfs.sort(key=lambda x: int(x["id"]))
    
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>UGM ETD PDF Database</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }
            .container { max-width: 900px; margin: 0 auto; }
            h2 { color: #333; }
            form { margin: 20px 0; }
            input[type="text"] { padding: 8px; width: 300px; }
            input[type="submit"] { padding: 8px 15px; background: #4CAF50; color: white; border: none; cursor: pointer; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            table, th, td { border: 1px solid #ddd; }
            th, td { padding: 8px; text-align: left; }
            tr:nth-child(even) { background-color: #f2f2f2; }
            th { background-color: #4CAF50; color: white; }
            .nav { margin: 20px 0; }
            .nav a { padding: 8px 16px; background: #ddd; text-decoration: none; color: black; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>UGM ETD PDF Database</h2>
            <div class="nav">
                <a href="/ugm">Back to Main Page</a>
            </div>
            
            <form action="/ugm/database" method="get">
                <input type="text" name="search" placeholder="Search by title..." value="{{ search_term }}">
                <input type="submit" value="Search">
            </form>
            
            <p>Showing {{ showing_count }} of {{ pdf_count }} documents</p>
            
            {% if pdfs %}
            <table>
                <tr>
                    <th>ID</th>
                    <th>Title</th>
                    <th>Date Added</th>
                    <th>Actions</th>
                </tr>
                {% for pdf in pdfs %}
                <tr>
                    <td>{{ pdf.id }}</td>
                    <td>{{ pdf.title }}</td>
                    <td>{{ pdf.date }}</td>
                    <td>
                        <a href="{{ base_url }}{{ pdf.id }}" target="_blank">Download</a> |
                        <a href="https://www.google.com/search?q={{ pdf.title|urlencode }}" target="_blank">Search</a>
                    </td>
                </tr>
                {% endfor %}
            </table>
            {% else %}
            <p>No PDFs found matching your search criteria.</p>
            {% endif %}
        </div>
    </body>
    </html>
    """, pdfs=filtered_pdfs, showing_count=len(filtered_pdfs), 
         pdf_count=len(crawled_pdfs), search_term=search_term, base_url=BASE_URL)

if __name__ == '__main__':
    load_crawl_database()
    app.run(debug=True, host='0.0.0.0', port=1234)