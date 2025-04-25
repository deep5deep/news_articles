import smtplib
from email.message import EmailMessage
import os
from datetime import datetime

def send_email(folder):
    sender = os.getenv('EMAIL_SENDER')
    password = os.getenv('EMAIL_PASSWORD')
    receiver = os.getenv('EMAIL_RECEIVER')

    msg = EmailMessage()
    msg['Subject'] = 'Daily News Articles'
    msg['From'] = sender
    msg['To'] = receiver
    msg.set_content("Attached are today's news articles.")

    for file_name in os.listdir(folder):
        file_path = os.path.join(folder, file_name)
        if os.path.isfile(file_path):
            with open(file_path, 'rb') as f:
                data = f.read()
                msg.add_attachment(data, maintype='application', subtype='octet-stream', filename=file_name)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(sender, password)
        smtp.send_message(msg)

if __name__ == '__main__':
    today = datetime.now().strftime('%d-%m-%Y')
    send_email(today)
