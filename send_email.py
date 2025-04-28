import smtplib
from email.message import EmailMessage
import os
from datetime import datetime
import pytz

def send_email(folder):
    sender = os.getenv('EMAIL_SENDER')
    password = os.getenv('EMAIL_PASSWORD')
    primary_receiver = os.getenv('EMAIL_RECEIVER')
    
    # Get additional receivers from environment variable
    # Format should be comma-separated email addresses
    additional_receivers = os.getenv('ADDITIONAL_EMAIL_RECEIVERS', '')
    
    # Create a list of all receivers
    all_receivers = [primary_receiver]
    if additional_receivers:
        all_receivers.extend([email.strip() for email in additional_receivers.split(',')])
    
    # Get Dublin time
    dublin_tz = pytz.timezone('Europe/Dublin')
    dublin_time = datetime.now(dublin_tz)
    dublin_time_str = dublin_time.strftime('%d-%m-%Y %H:%M:%S %Z')
    
    msg = EmailMessage()
    msg['Subject'] = f'Daily News Articles - {dublin_time_str} (Dublin Time)'
    msg['From'] = sender
    msg['To'] = ', '.join(all_receivers)
    msg.set_content(f"Attached are today's news articles.\n\nSent at: {dublin_time_str} (Dublin Time)")

    for file_name in os.listdir(folder):
        file_path = os.path.join(folder, file_name)
        if os.path.isfile(file_path):
            with open(file_path, 'rb') as f:
                data = f.read()
                msg.add_attachment(data, maintype='application', subtype='octet-stream', filename=file_name)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(sender, password)
        smtp.send_message(msg)
        print(f"Email sent successfully at {dublin_time_str} (Dublin Time)")

if __name__ == '__main__':
    today = datetime.now().strftime('%d-%m-%Y')
    send_email(today)
