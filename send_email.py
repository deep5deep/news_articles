import smtplib
from email.message import EmailMessage
import os
from datetime import datetime
import pytz

def send_email(folder, newspaper_filter=None):
    """
    Send an email with news articles from the specified folder.
    
    Args:
        folder: Path to the folder containing news articles
        newspaper_filter: Filter articles by newspaper name ('indian_express' or 'the_hindu')
                     If None, all articles are sent
    """
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
    
    # Create email based on newspaper type
    msg = EmailMessage()
    if newspaper_filter == 'indian_express':
        msg['Subject'] = f'Indian Express Articles - {dublin_time_str}'
        msg.set_content(f"Attached are today's articles from The Indian Express, including Delhi edition, UPSC edition, and image file.\n\nSent at: {dublin_time_str} (Dublin Time)")
    elif newspaper_filter == 'the_hindu':
        msg['Subject'] = f'The Hindu Articles - {dublin_time_str}'
        msg.set_content(f"Attached are today's articles from The Hindu, including Delhi edition, UPSC edition, and image file.\n\nSent at: {dublin_time_str} (Dublin Time)")
    else:
        msg['Subject'] = f'Daily News Articles - {dublin_time_str}'
        msg.set_content(f"Attached are today's news articles.\n\nSent at: {dublin_time_str} (Dublin Time)")
    
    msg['From'] = sender
    msg['To'] = ', '.join(all_receivers)

    # Counter to keep track of how many files were attached
    attached_files = 0
    
    for file_name in os.listdir(folder):
        # Filter files based on newspaper parameter
        include_file = False
        
        if newspaper_filter == 'indian_express':
            include_file = file_name.lower().startswith('indian_express') or 'indian_express' in file_name.lower()
        elif newspaper_filter == 'the_hindu':
            include_file = file_name.lower().startswith('the_hindu') or 'the_hindu' in file_name.lower()
        else:
            include_file = True  # Include all files if no filter
                
        if include_file:
            file_path = os.path.join(folder, file_name)
            if os.path.isfile(file_path):
                with open(file_path, 'rb') as f:
                    data = f.read()
                    msg.add_attachment(data, maintype='application', subtype='octet-stream', filename=file_name)
                    attached_files += 1
                    print(f"Attached file: {file_name}")
    
    # Only send email if there are attachments
    if attached_files > 0:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender, password)
            smtp.send_message(msg)
            print(f"Email with {attached_files} {newspaper_filter if newspaper_filter else 'news'} articles sent successfully at {dublin_time_str} (Dublin Time)")
    else:
        print(f"No {newspaper_filter if newspaper_filter else 'news'} articles found to send")

if __name__ == '__main__':
    today = datetime.now().strftime('%d-%m-%Y')
    
    # Send separate emails for each newspaper
    send_email(today, 'indian_express')
    send_email(today, 'the_hindu')
