from telethon.sessions import StringSession
from telethon import TelegramClient, events
import asyncio
import os
from datetime import datetime
import logging
from telethon.errors import TimeoutError

base_dir = os.getenv('GITHUB_WORKSPACE', '.')  # Use workspace directory or default to current directory
today_str = datetime.now().strftime('%d-%m-%Y')
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
        'source_format': 'INDIAN EXPRESS HD Delhi {date}.pdf',
        'target_format': 'Indian_Express_{date}.pdf',
        'date_format': '%d~%m~%Y',
        'target_date_format': '%d-%m-%Y',
        'type': 'newspaper'
    },
    {
        'username': '@thevishwakalyansewarth',
        'source_format': 'NEWS {date}.pdf',
        'target_format': 'The_Hindu_{date}.pdf',
        'date_format': '%d-%m-%Y',
        'target_date_format': '%d-%m-%Y',
        'type': 'newspaper'
    },
    {
        'username': '@vajiramandraviofficial',
        'type': 'highlights',
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
    except Exception as e:
        logger.error(f"Error checking highlights in {channel['username']}: {e}")

async def check_newspaper_channel(client, channel):
    try:
        today = datetime.now()
        source_date = today.strftime(channel['date_format'])
        target_date = today.strftime(channel['target_date_format'])
        
        source_filename = channel['source_format'].format(date=source_date)
        target_filename = channel['target_format'].format(date=target_date)
        
        logger.info(f"Checking {channel['username']} for: {source_filename}")
        
        async for message in client.iter_messages(channel['username'], limit=50):
            if (message.file and 
                hasattr(message.file, 'name') and 
                message.file.name and 
                message.file.name.lower() == source_filename.lower()):
                await download_file(client, message, target_filename, 'newspaper')
                return True
            await asyncio.sleep(0.5)
        
        logger.info(f"File not found in {channel['username']}")
        return False
    except Exception as e:
        logger.error(f"Error checking {channel['username']}: {e}")
        return False


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
        
        async with client:
            logger.info("Starting Telegram client...")
            me = await client.get_me()
            logger.info(f"Successfully connected as {me.username}")
            
            for channel in channels:
                try:
                    if channel['type'] == 'highlights':
                        await asyncio.wait_for(check_highlights_channel(client, channel), timeout=300)
                    else:
                        await asyncio.wait_for(check_newspaper_channel(client, channel), timeout=300)
                except asyncio.TimeoutError:
                    logger.error(f"Timeout checking {channel['username']}")
            
            logger.info("All channels checked")
        
    except Exception as e:
        logger.error(f"Error in main: {e}")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
