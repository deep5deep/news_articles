import smtplib
import os
import glob
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import formatdate
from email import encoders
from datetime import datetime
import pytz
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Allow folder override via environment variable
base_dir = os.getenv('GITHUB_WORKSPACE', '.')  # Use workspace directory or current
date_str = datetime.now().strftime('%d-%m-%Y')
folder_override = os.getenv('EMAIL_FOLDER')
subject_prefix = os.getenv('EMAIL_SUBJECT_PREFIX', '')  # Default to empty string if not set

if folder_override:
    dated_dir = os.path.join(base_dir, folder_override)
else:
    dated_dir = os.path.join(base_dir, date_str)

# Email settings
email_sender = os.environ.get('EMAIL_SENDER')
email_password = os.environ.get('EMAIL_PASSWORD')
email_receiver = os.environ.get('EMAIL_RECEIVER')
additional_receivers_str = os.environ.get('ADDITIONAL_EMAIL_RECEIVERS', '')
additional_receivers = [email.strip() for email in additional_receivers_str.split(',') if email.strip()]

# Current date in Dublin timezone
dublin_tz = pytz.timezone('Europe/Dublin')
dublin_time = datetime.now(dublin_tz)
dublin_date_str = dublin_time.strftime('%d %B %Y')

# Get retry count for email subject
retry_count = os.environ.get('RETRY_COUNT', '0')
retry_text = f" (Retry #{retry_count})" if retry_count and retry_count != '0' else ""

def send_email_with_attachments():
    try:
        # Count PDFs in directory
        pdf_files = glob.glob(os.path.join(dated_dir, "*.pdf"))
        pdf_count = len(pdf_files)
        
        # Create email
        msg = MIMEMultipart()
        msg['From'] = email_sender
        msg['To'] = email_receiver
        
        # Add today's date with retry info in the subject
        msg['Subject'] = f"{subject_prefix}Daily Newspapers - {dublin_date_str}{retry_text}"
        msg['Date'] = formatdate(localtime=True)
        
        # Body text
        body = f"Attached are {pdf_count} newspaper PDFs for {dublin_date_str}."
        msg.attach(MIMEText(body, 'plain'))
        
        # Attach all PDF files from the dated directory
        for pdf_file in pdf_files:
            filename = os.path.basename(pdf_file)
            attachment = open(pdf_file, "rb")
            
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f"attachment; filename={filename}")
            
            msg.attach(part)
            attachment.close()
        
        # Connect to SMTP server (using Gmail)
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email_sender, email_password)
        
        # Send email to primary recipient
        server.send_message(msg)
        logger.info(f"Email with {pdf_count} newspapers sent to {email_receiver}")
        
        # Send to additional recipients if provided
        if additional_receivers:
            for additional_receiver in additional_receivers:
                msg.replace_header('To', additional_receiver)
                server.send_message(msg)
                logger.info(f"Email also sent to {additional_receiver}")
        
        server.quit()
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False

if __name__ == '__main__':
    success = send_email_with_attachments()
    exit(0 if success else 1)
