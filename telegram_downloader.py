from telethon.sessions import StringSession
from telethon import TelegramClient, events
import asyncio
import os
from datetime import datetime
import logging
from telethon.errors import TimeoutError
import json

# Accept an override directory from environment variable, otherwise use default
base_dir = os.getenv('GITHUB_WORKSPACE', '.')  # Use workspace directory or default to current directory
today_str = datetime.now().strftime('%d-%m-%Y')
output_dir_override = os.getenv('OUTPUT_DIR')  # Get override from env if set

if output_dir_override:
    dated_dir = os.path.join(base_dir, output_dir_override)
else:
    dated_dir = os.path.join(base_dir, today_str)

os.makedirs(dated_dir, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# API credentials
api_id = 20197798
api_hash = '109f16378f64be336b43eb678ea487df'

# Channel and file configurations
channels = [
    {
        'username': '@csaccoep',
        'files': [
            {
                'source_format': 'INDIAN EXPRESS HD Delhi {date}.pdf',
                'target_format': 'Indian_Express_{date}.pdf',
                'date_format': '%d~%m~%Y',
                'target_date_format': '%d-%m-%Y',
                'name': 'Indian Express'
            },
            {
                'source_format': 'INDIAN EXPRESS UPSC IAS EDITION HD {date}.pdf',
                'target_format': 'Indian_Express_UPSC_{date}.pdf',
                'date_format': '%d~%m~%Y',
                'target_date_format': '%d-%m-%Y',
                'name': 'Indian Express UPSC'
            }
        ],
        'type': 'newspaper',
        'name': 'Indian Express Channel'
    },
    # International Edition:
    # {
    #     'username': '@thevishwakalyansewarth',
    #     'source_format': 'NEWS {date}.pdf',
    #     'target_format': 'The_Hindu_{date}.pdf',
    #     'date_format': '%d-%m-%Y',
    #     'target_date_format': '%d-%m-%Y',
    #     'type': 'newspaper'
    # },
    {
        'username': '@the_hindu_newspaper_free_pdf',
        'source_format': 'THE HINDU UPSC IAS EDITION HD{date}.pdf',
        'target_format': 'The_Hindu_{date}.pdf',
        'date_format': '%d~%m~%Y',
        'target_date_format': '%d-%m-%Y',
        'type': 'newspaper',
        'name': 'The Hindu'
    },
    {
        'username': '@vajiramandraviofficial',
        'type': 'highlights',
        'name': 'Highlights',
        'patterns': [
            {
                'text_pattern': '#ToBeReadVajiram in The Indian Express: {date}\n(Delhi edition e-paper)',
                'target_format': 'Indian_Express_{date}.jpg',
                'date_format': '%d/%m/%Y',
                'target_date_format': '%d-%m-%Y'
            },
            {
                'text_pattern': '#ToBeReadVajiram in The Hindu: {date}\n(Delhi edition e-paper)',
                'target_format': 'The_Hindu_{date}.jpg',
                'date_format': '%d/%m/%Y',
                'target_date_format': '%d-%m-%Y'
            }
        ]
    }
]

# Count of expected newspapers (excluding highlights)
EXPECTED_NEWSPAPER_COUNT = 3  # Indian Express, Indian Express UPSC, and The Hindu

async def download_file(client, message, target_filename, file_type, timeout=600):
    try:
        if message.file:
            save_path = os.path.join(dated_dir, target_filename)
            
            async def progress_callback(current, total):
                percentage = (current/total)*100
                if percentage % 10 == 0:
                    logger.info(f'Downloaded: {current}/{total} bytes ({percentage:.1f}%)')
            
            await asyncio.wait_for(
                client.download_media(
                    message,
                    save_path,
                    progress_callback=progress_callback
                ),
                timeout=timeout
            )
            logger.info(f"Downloaded: {target_filename}")
            return True
    except TimeoutError:
        logger.error(f"Download timed out for {target_filename}")
    except Exception as e:
        logger.error(f"Error downloading {target_filename}: {e}")
    return False

async def check_highlights_channel(client, channel):
    try:
        today = datetime.now()
        for pattern in channel['patterns']:
            date_str = today.strftime(pattern['date_format'])
            expected_text = pattern['text_pattern'].format(date=date_str)
            target_filename = pattern['target_format'].format(
                date=today.strftime(pattern['target_date_format'])
            )
            
            logger.info(f"Checking {channel['username']} for: {expected_text}")
            
            async for message in client.iter_messages(channel['username'], limit=50):
                if message.text and expected_text in message.text and message.media:
                    await download_file(client, message, target_filename, 'highlights')
                await asyncio.sleep(0.5)
        return True  # Return True as highlights are optional
    except Exception as e:
        logger.error(f"Error checking highlights in {channel['username']}: {e}")
        return False

async def check_newspaper_channel(client, channel):
    try:
        today = datetime.now()
        found_newspapers = set()
        file_confs = channel.get('files')
        if not file_confs:
            # Support single-file config for backward compatibility
            file_confs = [{
                'source_format': channel['source_format'],
                'target_format': channel['target_format'],
                'date_format': channel['date_format'],
                'target_date_format': channel['target_date_format'],
                'name': channel['name']
            }]
        for file_conf in file_confs:
            source_date = today.strftime(file_conf['date_format'])
            target_date = today.strftime(file_conf['target_date_format'])
            source_filename = file_conf['source_format'].format(date=source_date)
            target_filename = file_conf['target_format'].format(date=target_date)
            logger.info(f"Checking {channel['username']} for: {source_filename}")
            async for message in client.iter_messages(channel['username'], limit=50):
                if (message.file and 
                    hasattr(message.file, 'name') and 
                    message.file.name and 
                    message.file.name.lower() == source_filename.lower()):
                    if await download_file(client, message, target_filename, 'newspaper'):
                        found_newspapers.add(file_conf.get('name', target_filename))
                    break
                await asyncio.sleep(0.5)
            else:
                logger.info(f"File not found in {channel['username']}: {source_filename}")
        return found_newspapers
    except Exception as e:
        logger.error(f"Error checking {channel['username']}: {e}")
        return set()

def count_downloaded_newspapers():
    """Count how many unique newspapers we've downloaded"""
    newspapers = set()
    
    for file in os.listdir(dated_dir):
        if file.startswith("Indian_Express_") and file.endswith(".pdf") and not file.startswith("Indian_Express_UPSC_"):
            newspapers.add("Indian Express")
        elif file.startswith("Indian_Express_UPSC_") and file.endswith(".pdf"):
            newspapers.add("Indian Express UPSC")
        elif file.startswith("The_Hindu_") and file.endswith(".pdf"):
            newspapers.add("The Hindu")
    
    return len(newspapers), newspapers

async def main():
    try:
        # Try getting session string from environment variable (for remote execution)
        session_string = os.environ.get('TELEGRAM_SESSION_STRING')
        
        if session_string:
            # Remote execution using session string
            client = TelegramClient(StringSession(session_string), api_id, api_hash)
        else:
            # Local execution using file-based session
            client = TelegramClient('news_session', api_id, api_hash)
        
        newspaper_results = {}
        found_newspapers = set()
        
        async with client:
            logger.info("Starting Telegram client...")
            me = await client.get_me()
            logger.info(f"Successfully connected as {me.username}")
            
            for channel in channels:
                try:
                    if channel['type'] == 'highlights':
                        result = await asyncio.wait_for(check_highlights_channel(client, channel), timeout=300)
                        newspaper_results[channel['name']] = result
                    else:
                        result = await asyncio.wait_for(check_newspaper_channel(client, channel), timeout=300)
                        found_newspapers.update(result)
                        newspaper_results[channel['name']] = len(result) > 0
                except asyncio.TimeoutError:
                    logger.error(f"Timeout checking {channel['username']}")
                    newspaper_results[channel['name']] = False
            
            logger.info("All channels checked")
        
        # Count actual newspaper files downloaded
        newspaper_count, downloaded_papers = count_downloaded_newspapers()
        logger.info(f"Downloaded {newspaper_count}/{EXPECTED_NEWSPAPER_COUNT} newspapers: {', '.join(downloaded_papers)}")
        
        # Create a status file that the workflow can check
        status = {
            "newspaper_count": newspaper_count,
            "expected_count": EXPECTED_NEWSPAPER_COUNT,
            "all_newspapers_downloaded": newspaper_count >= EXPECTED_NEWSPAPER_COUNT,
            "downloaded_newspapers": list(downloaded_papers),
            "details": newspaper_results
        }
        
        with open(os.path.join(dated_dir, "download_status.json"), "w") as f:
            json.dump(status, f, indent=2)
            
        # Return success status based on newspaper count for GitHub workflow
        if newspaper_count < EXPECTED_NEWSPAPER_COUNT:
            missing_papers = EXPECTED_NEWSPAPER_COUNT - newspaper_count
            logger.warning(f"Not all newspapers downloaded ({newspaper_count}/{EXPECTED_NEWSPAPER_COUNT}). Missing {missing_papers} newspaper(s).")
            return 1
        return 0
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
        return 1

if __name__ == '__main__':
    try:
        exit_code = asyncio.run(main())
        exit(exit_code)  # Return non-zero exit code if not all newspapers were downloaded
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        exit(1)
