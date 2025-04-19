import smtplib
import ssl
import sys
import os
import logging
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Get the application directory
if getattr(sys, 'frozen', False):
    # Running as a bundled app
    if sys.platform == 'darwin':
        # For macOS app bundle, we need to use the MacOS directory
        application_path = os.path.dirname(sys.executable)
    else:
        application_path = os.path.dirname(sys.executable)
else:
    # Running as a script
    application_path = os.path.dirname(os.path.abspath(__file__))

# Create necessary directories
data_dir = os.path.join(application_path, 'data')
logs_dir = os.path.join(application_path, 'logs')
os.makedirs(data_dir, exist_ok=True)
os.makedirs(logs_dir, exist_ok=True)

# Set up logging to file and console
log_file = os.path.join(logs_dir, 'email_log.txt')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8', mode='w'),  # Use 'w' mode to clear the file
        logging.StreamHandler()
    ]
)

# Function to generate email signature
def get_email_signature(use_html=False):
    if use_html:
        return """
        <br><br>
        <div style="font-family: Arial, sans-serif; font-size: 14px;">
            <p>--</p>
            <p>Pagarbiai,</p>
            <p><strong>Samanta</strong><br>
            Administratorė</p>
            <p>Bažnyčių g. 3, Tauragė<br>
            <a href="https://www.knygospigiau.lt">www.knygospigiau.lt</a></p>
        </div>
        """
    else:
        return """
--
Pagarbiai,

Samanta
Administratorė

Bažnyčių g. 3, Tauragė
www.knygospigiau.lt
        """

# Function to send one email
def send_email(sender_email, recipient_email, subject, body, smtp_server, smtp_port, username, password, use_html=True):
    try:
        logging.info(f"Ruošiamas laiškas adresatui: {recipient_email}")
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = recipient_email

        # Add HTML signature to the body
        full_body = body + get_email_signature(use_html=True)

        # Attach both HTML and plain text versions
        msg.attach(MIMEText(full_body, 'html', 'utf-8'))
        msg.attach(MIMEText(full_body, 'plain', 'utf-8'))

        logging.info(f"Jungiamasi prie SMTP serverio: {smtp_server}:{smtp_port}")
        
        # Send via SMTP
        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, smtp_port, timeout=30) as server:
            logging.info("Pradedama TLS sesija...")
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            
            logging.info("Bandoma prisijungti prie serverio...")
            server.login(username, password)
            
            logging.info(f"Siunčiamas laiškas į {recipient_email}")
            server.send_message(msg)
            logging.info(f"✅ Laiškas išsiųstas: {recipient_email}")

    except smtplib.SMTPAuthenticationError:
        logging.error("❌ Autentifikavimo klaida – patikrink vartotojo vardą/slaptažodį.")
        raise
    except smtplib.SMTPException as e:
        logging.error(f"❌ SMTP klaida ({recipient_email}): {str(e)}")
        raise
    except Exception as e:
        logging.error(f"❌ Kita klaida ({recipient_email}): {str(e)}")
        raise

# Send to all clients
def send_emails_to_clients(subject, body):
    # Clear the log file at the start of sending
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write('')
    
    smtp_server = "mail.versloidejos.lt"
    smtp_port = 587
    sender_email = "info@versloidejos.lt"
    username = sender_email
    password = "^j19Yv4w2"
    use_html = True

    emails_per_hour = 30
    sleep_duration = (3600 / emails_per_hour) + 5  # 125s

    # Nuskaito el. paštų adresus iš failo
    email_list_path = os.path.join(data_dir, 'email_list.txt')
    try:
        logging.info(f"Bandoma atidaryti el. paštų sąrašą: {email_list_path}")
        with open(email_list_path, 'r', encoding='utf-8') as f:
            email_list = [line.strip() for line in f if line.strip()]
            logging.info(f"Rasta {len(email_list)} el. pašto adresų")
    except FileNotFoundError:
        logging.error(f"❌ email_list.txt nerastas! Ieškota: {email_list_path}")
        raise FileNotFoundError(f"email_list.txt nerastas! Ieškota: {email_list_path}")

    if not email_list:
        logging.error("❌ El. paštų adresų failas tuščias!")
        raise ValueError("El. paštų adresų failas tuščias!")

    # Siunčia laiškus
    total_sent = 0
    for email in email_list:
        try:
            send_email(sender_email, email, subject, body, smtp_server, smtp_port, username, password, use_html)
            total_sent += 1
            logging.info(f"Išsiųsta laiškų: {total_sent}/{len(email_list)}")
            if total_sent < len(email_list):
                logging.info(f"Laukiama {sleep_duration} sekundžių prieš siunčiant kitą laišką...")
                time.sleep(sleep_duration)
        except Exception as e:
            logging.error(f"❌ Klaida siunčiant laišką {email}: {str(e)}")
            continue

# Paleidimui iš terminalo
if __name__ == "__main__":
    subject = "Testas iš terminalo"
    body = """<p>Laba diena,</p>
<p>Pranešame, kad visą balandžio mėnesį vyksta akcija – knygos pigiau!</p>
<p>Ačiū, kad skaitote mūsų naujienlaiškį. Jei turite klausimų, kreipkitės!</p>"""
    send_emails_to_clients(subject, body)
