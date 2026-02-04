import smtplib
import time
import re
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr, make_msgid, formatdate

def parse_contacts_from_file(filename):
    """
    Parse contacts from the reserved_seat_names.txt file
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # This pattern is more robust for various name formats
        pattern = r'([\w\s\.\'-]+)<([^>]+)>'
        matches = re.findall(pattern, content)
        
        contacts = []
        for name, email in matches:
            # Clean up name and email
            name = ' '.join(name.strip().rstrip(',').split())
            email = email.strip()
            contacts.append((name, email))
        
        return contacts
    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found. Please make sure it's in the same directory.")
        return []

def create_email_content(name):
    subject = "Permohonan Izin Bergabung – Proyek Kelompok 9 Pengembangan Aplikasi Web"
    body = f"""Yth. Kak {name},

Assalamualaikum warahmatullahi wabarakatuh,

Perkenalkan, saya Muhammad Muqtada Alhaddad (22/500341/TK/54841), mahasiswa kelas B yang baru bergabung melalui KRS susulan.

Saya diarahkan untuk menghubungi teman-teman dan memohon izin untuk bergabung dengan kelompok 9 pada mata kuliah Pengembangan Aplikasi Web, jika teman-teman berkenan. Saya siap menyesuaikan progres yang sudah ada dan membantu menjalankan tugas di repository proyek.

Terima kasih banyak atas perhatian dan kesediaannya, kami menunggu konfirmasi teman-teman dengan membalas email ini atau melalui WhatsApp di wa.me/6289654630320.

Salam hangat penuh hormat,
Muhammad Muqtada Alhaddad
github.com/adakhaddad
"""
    return subject, body


def send_email(smtp_server, smtp_port, sender_email, sender_password, sender_name, recipient_email, recipient_name, subject, body):
    """
    Send a properly formatted email with headers to avoid spam filters.
    """
    try:
        # Create message
        msg = MIMEMultipart()
        
        # Set "From" header with name and email for a professional look
        msg['From'] = formataddr((sender_name, sender_email))
        msg['To'] = formataddr((recipient_name, recipient_email))
        msg['Subject'] = subject
        
        # Add crucial headers that spam filters look for
        msg['Date'] = formatdate(localtime=True)
        msg['Message-ID'] = make_msgid()
        
        # Add body to email, ensuring UTF-8 encoding
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # Create SMTP session
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Enable security
            server.login(sender_email, sender_password)
            
            # Send email
            server.send_message(msg)
            
        return True, "Email sent successfully"
        
    except smtplib.SMTPException as e:
        return False, f"SMTP Error: {e}"
    except Exception as e:
        return False, str(e)

def main():
    # --- EMAIL CONFIGURATION - UPDATE THESE ---
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    SENDER_EMAIL = "muhammadmuqtada@gmail.com"  # Replace with your Gmail address
    SENDER_PASSWORD = "eqzs csfq zdck kdqn"  # Replace with your 16-character Gmail App Password
    SENDER_NAME = "Muqtada"  # Your name as it appears in emails
    
    CONTACTS_FILE = "reserved_seat_names.txt"
    # ------------------------------------------
    
    contacts = parse_contacts_from_file(CONTACTS_FILE)
    
    if not contacts:
        print("No contacts found or file could not be read. Exiting.")
        return
        
    print(f"Found {len(contacts)} contacts to send emails to.")
    print("-" * 50)
    
    # --- EMAIL PREVIEW ---
    print("\n" + "="*60)
    print("EMAIL PREVIEW:")
    print("="*60)
    
    if contacts:
        preview_name, preview_email = contacts[0]
        subject, body = create_email_content(preview_name)
        print(f"From: {SENDER_NAME} <{SENDER_EMAIL}>")
        print(f"To: {preview_name} <{preview_email}>")
        print(f"Subject: {subject}")
        print("-" * 20)
        print(f"Body:\n{body}")
    
    print("\n" + "="*60)
    
    # --- CONFIRMATION ---
    confirm = input(f"\nDo you want to send emails to {len(contacts)} people? (y/n): ")
    
    if confirm.lower() != 'y':
        print("Email sending cancelled.")
        return
    
    # --- SEND EMAILS ---
    successful = 0
    failed = 0
    
    for i, (name, email) in enumerate(contacts, 1):
        print(f"Sending email {i}/{len(contacts)} to {name}...", end=' ')
        
        subject, body = create_email_content(name)
        
        success, message = send_email(
            SMTP_SERVER, SMTP_PORT, SENDER_EMAIL, SENDER_PASSWORD, SENDER_NAME,
            email, name, subject, body
        )
        
        if success:
            successful += 1
            print(f"✓ Sent")
        else:
            failed += 1
            print(f"✗ Failed: {message}")
        
        # Randomized delay to better simulate human behavior and avoid spam filters
        sleep_time = random.uniform(2, 5)
        time.sleep(sleep_time)
    
    print("\n" + "="*60)
    print(f"Email sending completed!")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")

if __name__ == "__main__":
    main()