import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time

def extract_names_from_html(html_file_path):
    """
    Extract all names from reserved seats in the HTML file
    """
    with open(html_file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Find all names in data-content attributes
    pattern = r"data-content='oleh ([^']+)'"
    names = re.findall(pattern, content)
    
    return names

def create_email_content(name):
    """
    Create personalized email content
    """
    subject = "Layanan Akses PDF Online - Gratis!"
    
    body = f"""Halo Kak {name},

Saya ingin menawarkan layanan akses PDF online yang bisa membantu Kakak mengakses dokumen tanpa perlu datang ke Perpustakaan.

**Layanan yang kami tawarkan:**
- Akses PDF online secara gratis
- Kirim judul atau link karya tulis ke email/DM: 1pordnozama@gmail.com
- Kami bisa bantu kirimkan dokumennya

**Untuk layanan berbayar:**
- Jasa akses PDF: Rp 15.000 / dokumen
- Apakah harga ini masuk akal menurut Kakak?

Silakan hubungi kami jika tertarik dengan layanan ini.

Terima kasih,
Tim Layanan PDF Online

---
Email: 1pordnozama@gmail.com
"""

    return subject, body

def send_email(smtp_server, smtp_port, sender_email, sender_password, recipient_email, subject, body):
    """
    Send email to recipient
    """
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        
        # Add body to email
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # Create SMTP session
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Enable security
        server.login(sender_email, sender_password)
        
        # Send email
        text = msg.as_string()
        server.sendmail(sender_email, recipient_email, text)
        server.quit()
        
        return True, "Email sent successfully"
        
    except Exception as e:
        return False, str(e)

def main():
    # Email configuration
    SMTP_SERVER = "smtp.gmail.com"  # Gmail SMTP server
    SMTP_PORT = 587
    SENDER_EMAIL = "your_email@gmail.com"  # Replace with your email
    SENDER_PASSWORD = "your_app_password"  # Replace with your app password
    
    # Extract names from HTML
    html_file = "email/index.html"
    names = extract_names_from_html(html_file)
    
    print(f"Found {len(names)} names to send emails to:")
    for i, name in enumerate(names, 1):
        print(f"{i:2d}. {name}")
    
    print("\n" + "="*50)
    
    # Ask for confirmation
    confirm = input(f"\nDo you want to send emails to {len(names)} people? (y/n): ")
    if confirm.lower() != 'y':
        print("Email sending cancelled.")
        return
    
    # Email settings
    print("\nEmail Configuration:")
    print("Please update the following in the script:")
    print(f"SENDER_EMAIL = '{SENDER_EMAIL}'")
    print(f"SENDER_PASSWORD = '{SENDER_PASSWORD}'")
    print("\nNote: Use App Password for Gmail, not your regular password")
    
    # For demo purposes, we'll just show what emails would be sent
    print("\n" + "="*50)
    print("EMAIL PREVIEW (First 3 emails):")
    print("="*50)
    
    for i, name in enumerate(names[:3], 1):
        subject, body = create_email_content(name)
        print(f"\nEmail {i} - To: {name}")
        print(f"Subject: {subject}")
        print(f"Body Preview: {body[:200]}...")
        print("-" * 30)
    
    if len(names) > 3:
        print(f"\n... and {len(names) - 3} more emails")
    
    # Save email list to file
    with open("email_recipients.txt", "w", encoding="utf-8") as f:
        f.write("Email Recipients List\n")
        f.write("="*30 + "\n\n")
        for i, name in enumerate(names, 1):
            f.write(f"{i:2d}. {name}\n")
    
    print(f"\nRecipients list saved to 'email_recipients.txt'")
    
    # Instructions for actual sending
    print("\n" + "="*50)
    print("TO ACTUALLY SEND EMAILS:")
    print("="*50)
    print("1. Update SENDER_EMAIL and SENDER_PASSWORD in the script")
    print("2. Uncomment the email sending code below")
    print("3. Run the script again")
    print("\nNote: Gmail requires App Password for SMTP access")
    print("Generate App Password: Google Account > Security > 2-Step Verification > App passwords")

if __name__ == "__main__":
    main()