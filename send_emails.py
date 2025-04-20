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

# Set up logging
log_file = os.path.join(logs_dir, 'email_log.txt')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

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

def create_ssl_context():
    """Create a secure SSL context with appropriate settings."""
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    return context

def connect_to_smtp(server, port, username, password, max_retries=3, retry_delay=5):
    """Attempt to connect to SMTP server with retry mechanism."""
    context = create_ssl_context()
    
    for attempt in range(max_retries):
        try:
            logging.info(f"Attempting to connect to {server} on port {port} (attempt {attempt + 1}/{max_retries})")
            
            if port == 465:
                # SSL connection
                server = smtplib.SMTP_SSL(server, port, context=context, timeout=60)
            else:
                # STARTTLS connection
                server = smtplib.SMTP(server, port, timeout=60)
                server.set_debuglevel(1)  # Enable debug logging
                server.ehlo()
                if port == 587:  # Special handling for webmail on port 587
                    server.starttls(context=context)
                    server.ehlo()
                server.login(username, password)
            
            logging.info(f"Successfully connected to {server} on port {port}")
            return server
            
        except (smtplib.SMTPException, ssl.SSLError, ConnectionError) as e:
            logging.error(f"Connection attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                logging.info(f"Waiting {retry_delay} seconds before retrying...")
                time.sleep(retry_delay)
            else:
                raise Exception(f"Failed to connect to SMTP server after {max_retries} attempts: {str(e)}")

def send_emails_to_clients(subject, body):
    # Email configuration
    sender_email = "samanta@knygospigiau.lt"
    password = "KEo3D+9bIf.-"
    smtp_server = "mail.knygospigiau.lt"
    smtp_port = 465  # Using SMTPS (implicit SSL)
    
    # Create SSL context
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    
    try:
        # Read email addresses from file
        email_list_path = os.path.join(data_dir, 'email_list.txt')
        with open(email_list_path, 'r', encoding='utf-8') as f:
            email_addresses = [line.strip() for line in f if line.strip()]
        
        logger.info(f"Rasta {len(email_addresses)} el. pašto adresų")
        
        # Connect to SMTP server
        with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
            server.login(sender_email, password)
            logger.info("Sėkmingai prisijungta prie SMTP serverio")
            
            # Send emails
            successful_sends = 0
            for email in email_addresses:
                try:
                    # Create message
                    msg = MIMEMultipart()
                    msg['From'] = sender_email
                    msg['To'] = email
                    msg['Subject'] = subject
                    
                    # Add signature to the body
                    full_body = body + get_email_signature(use_html=True)
                    msg.attach(MIMEText(full_body, 'html'))
                    
                    # Send email
                    server.send_message(msg)
                    successful_sends += 1
                    logger.info(f"Laiškas sėkmingai išsiųstas į {email}")
                    time.sleep(1)  # Small delay between sends
                    
                except Exception as e:
                    logger.error(f"Klaida siunčiant laišką į {email}: {str(e)}")
                    continue
            
            logger.info(f"Baigtas laiškų siuntimas. Sėkmingai išsiųsta: {successful_sends} iš {len(email_addresses)}")
            
    except FileNotFoundError:
        logger.error(f"Nerastas el. pašto adresų sąrašo failas: {email_list_path}")
        raise
    except Exception as e:
        logger.error(f"Klaida siunčiant laiškus: {str(e)}")
        raise

# For running from terminal
if __name__ == "__main__":
    subject = "Test from terminal"
    body = """<p>Hello,</p>
<p>This is a test email.</p>
<p>Thank you for reading our newsletter!</p>"""
    send_emails_to_clients(subject, body)
