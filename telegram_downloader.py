from telethon.sessions import StringSession
from telethon import TelegramClient, events
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest
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
        'files': [
            {
                'source_format': 'INDIAN EXPRESS HD Delhi {date}.pdf',
                'target_format': 'Indian_Express_{date}.pdf',
                'date_format': '%d~%m~%Y',
                'target_date_format': '%d-%m-%Y'
            },
            {
                'source_format': 'INDIAN EXPRESS UPSC IAS EDITION HD {date}.pdf',
                'target_format': 'Indian_Express_UPSC_{date}.pdf',
                'date_format': '%d~%m~%Y',
                'target_date_format': '%d-%m-%Y'
            }
        ],
        'type': 'newspaper'
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
        'files': [
            # Commented out the old Hindu UPSC channel
            # {
            #     'source_format': 'THE HINDU UPSC IAS EDITION HD {date}.pdf',
            #     'target_format': 'The_Hindu_UPSC_{date}.pdf',
            #     'date_format': '%d~%m~%Y',
            #     'target_date_format': '%d-%m-%Y'
            # },
            {
                'source_format': 'TH Delhi {date}.pdf',
                'target_format': 'The_Hindu_Delhi_{date}.pdf',
                'date_format': '%d--%m',
                'target_date_format': '%d-%m-%Y'
            }
        ],
        'type': 'newspaper'
    },
    # Using the full invite link for the private channel as mentioned in the prompt
    {
        'username': 'https://t.me/+Bu7senHpQdhlODg1',
        'files': [
            {
                'source_format': 'THE HINDU UPSC IAS EDITION HD {date}.pdf',
                'target_format': 'The_Hindu_UPSC_{date}.pdf',
                'date_format': '%d~%m~%Y',
                'target_date_format': '%d-%m-%Y'
            }
        ],
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
            # Try with the original date format first
            date_str = today.strftime(pattern['date_format'])
            expected_text = pattern['text_pattern'].format(date=date_str)
            target_filename = pattern['target_format'].format(
                date=today.strftime(pattern['target_date_format'])
            )
            
            logger.info(f"Checking {channel['username']} for: {expected_text}")
            found = False
            
            async for message in client.iter_messages(channel['username'], limit=50):
                if message.text and expected_text in message.text and message.media:
                    success = await download_file(client, message, target_filename, 'highlights')
                    if success:
                        found = True
                        break
                await asyncio.sleep(0.5)
            
            # If not found, try alternative date formats (removing leading zeros)
            if not found and '/' in pattern['date_format']:
                # Generate all possible date format variations
                alt_date_formats = []
                
                # Original format (e.g., "02/05/2025")
                orig_date = today.strftime(pattern['date_format'])
                parts = orig_date.split('/')
                
                if len(parts) > 1:
                    # Format 1: Day without leading zero (e.g., "2/05/2025")
                    if parts[0].startswith('0'):
                        new_parts = parts.copy()
                        new_parts[0] = parts[0][1:]
                        alt_date_formats.append('/'.join(new_parts))
                    
                    # Format 2: Month without leading zero (e.g., "02/5/2025")
                    if len(parts) > 1 and parts[1].startswith('0'):
                        new_parts = parts.copy()
                        new_parts[1] = parts[1][1:]
                        alt_date_formats.append('/'.join(new_parts))
                    
                    # Format 3: Both day and month without leading zeros (e.g., "2/5/2025")
                    if parts[0].startswith('0') and parts[1].startswith('0'):
                        new_parts = parts.copy()
                        new_parts[0] = parts[0][1:]
                        new_parts[1] = parts[1][1:]
                        alt_date_formats.append('/'.join(new_parts))
                
                # Try each alternative date format
                for alt_date in alt_date_formats:
                    alt_expected_text = pattern['text_pattern'].format(date=alt_date)
                    logger.info(f"Retrying with alternative date format: {alt_expected_text}")
                    
                    found_with_alt = False
                    async for message in client.iter_messages(channel['username'], limit=50):
                        if message.text and alt_expected_text in message.text and message.media:
                            success = await download_file(client, message, target_filename, 'highlights')
                            if success:
                                found_with_alt = True
                                found = True
                                break
                        await asyncio.sleep(0.5)
                    
                    if found_with_alt:
                        break
    except Exception as e:
        logger.error(f"Error checking highlights in {channel['username']}: {e}")

async def check_newspaper_channel(client, channel):
    try:
        today = datetime.now()
        found_any = False
        file_confs = channel.get('files')
        if not file_confs:
            # Support single-file config for backward compatibility
            file_confs = [{
                'source_format': channel['source_format'],
                'target_format': channel['target_format'],
                'date_format': channel['date_format'],
                'target_date_format': channel['target_date_format']
            }]
        
        # For private channels with invite links, let's verify we can access it
        if channel['username'].startswith('https://t.me/+'):
            try:
                # Try to get recent messages to verify access
                logger.info(f"Verifying access to private channel {channel['username']} before searching for files")
                messages = []
                file_list = []
                
                # List up to 200 available files in the channel for debugging
                logger.info(f"Listing available files in channel {channel['username']}...")
                async for msg in client.iter_messages(channel['username'], limit=200):
                    messages.append(msg)
                    if msg.file and hasattr(msg.file, 'name') and msg.file.name:
                        file_list.append(msg.file.name)
                        logger.info(f"Found file in channel: {msg.file.name}")
                
                if not messages:
                    logger.warning(f"Could access the channel {channel['username']} but no messages found. This might be an access issue.")
                    return False
                else:
                    logger.info(f"Successfully accessed private channel {channel['username']} and found {len(messages)} messages")
                    if file_list:
                        logger.info(f"Available files in channel: {file_list}")
                    else:
                        logger.warning(f"No files found in the messages we checked in {channel['username']}")
            except Exception as channel_access_err:
                logger.error(f"Failed to access private channel {channel['username']}: {channel_access_err}")
                logger.error("This might be due to not being a member of the channel or an invalid invite link")
                return False
                
        for file_conf in file_confs:
            source_date = today.strftime(file_conf['date_format'])
            target_date = today.strftime(file_conf['target_date_format'])
            source_filename = file_conf['source_format'].format(date=source_date)
            target_filename = file_conf['target_format'].format(date=target_date)
            
            # Special handling for The Hindu to try both with and without space
            alternate_source_filename = None
            if '@the_hindu_newspaper_free_pdf' in channel['username']:
                if ' {date}' in file_conf['source_format']:
                    # Create alternate filename without space
                    alternate_format = file_conf['source_format'].replace(' {date}', '{date}')
                    alternate_source_filename = alternate_format.format(date=source_date)
                elif '{date}' in file_conf['source_format']:
                    # Create alternate filename with space
                    alternate_format = file_conf['source_format'].replace('{date}', ' {date}')
                    alternate_source_filename = alternate_format.format(date=source_date)
            
            # Check if the file we're looking for is in the file_list already found
            if file_list and any(f.lower() == source_filename.lower() for f in file_list):
                logger.info(f"The file {source_filename} was found in the initial channel scan. Attempting direct download...")
                # Try to find the message with this file and download it
                try:
                    async for msg in client.iter_messages(channel['username'], limit=100):
                        if msg.file and hasattr(msg.file, 'name') and msg.file.name and msg.file.name.lower() == source_filename.lower():
                            logger.info(f"Found the exact file in channel: {msg.file.name}")
                            success = await download_file(client, msg, target_filename, 'newspaper')
                            if success:
                                found_any = True
                                found_file = True
                                break
                    
                    if found_file:
                        logger.info(f"Successfully downloaded {source_filename} directly")
                        continue  # Skip to next file
                except Exception as direct_err:
                    logger.error(f"Error attempting direct download of {source_filename}: {direct_err}")
            
            logger.info(f"Checking {channel['username']} for: {source_filename}")
            if alternate_source_filename:
                logger.info(f"Will also check alternative format: {alternate_source_filename}")
                
            found_file = False
            
            # Implement manual pagination to check more messages
            offset_id = 0
            message_count = 0
            max_messages = 200  # Check up to 200 messages
            
            while message_count < max_messages:
                messages = await client.get_messages(channel['username'], limit=50, offset_id=offset_id)
                if not messages:
                    logger.info(f"No more messages found after checking {message_count} messages")
                    break
                
                for message in messages:
                    message_count += 1
                    
                    # Skip messages without files
                    if not message.file:
                        continue
                        
                    # Skip files without name attribute
                    if not hasattr(message.file, 'name') or not message.file.name:
                        continue
                        
                    # Log every filename to help with debugging
                    logger.info(f"File found during search: {message.file.name}")
                    
                    # Check for primary format match
                    if message.file.name.lower() == source_filename.lower():
                        logger.info(f"Found file with primary format: {message.file.name}")
                        success = await download_file(client, message, target_filename, 'newspaper')
                        if success:
                            found_any = True
                            found_file = True
                            break
                    
                    # Check for alternate format match if available
                    if alternate_source_filename and message.file.name.lower() == alternate_source_filename.lower():
                        logger.info(f"Found file with alternate format: {message.file.name}")
                        success = await download_file(client, message, target_filename, 'newspaper')
                        if success:
                            found_any = True
                            found_file = True
                            break
                    
                    # For private channels, try a more flexible matching approach
                    if channel['username'].startswith('https://t.me/+'):
                        # Check if filename contains the essential components (exact match failed)
                        filename_parts = source_filename.lower().replace('.pdf', '').split()
                        file_name_lower = message.file.name.lower()
                        
                        # Check if all important parts are in the filename (like "HINDU", "UPSC", "HD", etc.)
                        all_parts_match = all(part in file_name_lower for part in filename_parts if len(part) > 1)
                        
                        # Check for date components in the filename
                        date_parts = source_date.split('~')
                        date_matches = all(date_part in file_name_lower for date_part in date_parts)
                        
                        if all_parts_match and date_matches:
                            logger.info(f"Found file with flexible matching: {message.file.name}")
                            logger.info(f"  - Looking for: {source_filename}")
                            success = await download_file(client, message, target_filename, 'newspaper')
                            if success:
                                found_any = True
                                found_file = True
                                break
                        elif all_parts_match:  # Log partial matches for debugging
                            logger.info(f"Found partial match (keywords match but date doesn't): {message.file.name}")
                        
                if found_file:
                    break
                        
                # Update offset_id for pagination if messages exist
                if messages:
                    offset_id = messages[-1].id
                
                await asyncio.sleep(0.5)
            
            # If the file was not found with the original date format, try alternative formats
            if not found_file:
                alt_date_formats = []
                
                # Handle tilde format (dd~mm~yyyy)
                if '~' in file_conf['date_format']:
                    # Parse the original date
                    parts = source_date.split('~')
                    if len(parts) >= 3:
                        # Format 1: Day without leading zero
                        if parts[0].startswith('0'):
                            new_parts = parts.copy()
                            new_parts[0] = parts[0][1:]  # Remove leading zero from day
                            alt_date_formats.append('~'.join(new_parts))
                        
                        # Format 2: Month without leading zero
                        if parts[1].startswith('0'):
                            new_parts = parts.copy()
                            new_parts[1] = parts[1][1:]  # Remove leading zero from month
                            alt_date_formats.append('~'.join(new_parts))
                        
                        # Format 3: Both day and month without leading zeros
                        if parts[0].startswith('0') and parts[1].startswith('0'):
                            new_parts = parts.copy()
                            new_parts[0] = parts[0][1:]  # Remove leading zero from day
                            new_parts[1] = parts[1][1:]  # Remove leading zero from month
                            alt_date_formats.append('~'.join(new_parts))
                
                # Handle double-hyphen format (dd--mm)
                elif '--' in file_conf['date_format']:
                    # Parse the original date
                    parts = source_date.split('--')
                    if len(parts) >= 2:
                        # Format 1: Day without leading zero
                        if parts[0].startswith('0'):
                            new_parts = parts.copy()
                            new_parts[0] = parts[0][1:]  # Remove leading zero from day
                            alt_date_formats.append('--'.join(new_parts))
                        
                        # Format 2: Month without leading zero
                        if parts[1].startswith('0'):
                            new_parts = parts.copy()
                            new_parts[1] = parts[1][1:]  # Remove leading zero from month
                            alt_date_formats.append('--'.join(new_parts))
                        
                        # Format 3: Both day and month without leading zeros
                        if parts[0].startswith('0') and parts[1].startswith('0'):
                            new_parts = parts.copy()
                            new_parts[0] = parts[0][1:]  # Remove leading zero from day
                            new_parts[1] = parts[1][1:]  # Remove leading zero from month
                            alt_date_formats.append('--'.join(new_parts))
                
                # Try each alternative date format
                for alt_date in alt_date_formats:
                    alt_source_filename = file_conf['source_format'].format(date=alt_date)
                    logger.info(f"Trying alternative date format: {alt_source_filename}")
                    
                    async for message in client.iter_messages(channel['username'], limit=50):
                        if (message.file and 
                            hasattr(message.file, 'name') and 
                            message.file.name and
                            message.file.name.lower() == alt_source_filename.lower()):
                            
                            logger.info(f"Found file with alternative date format: {message.file.name}")
                            success = await download_file(client, message, target_filename, 'newspaper')
                            if success:
                                found_any = True
                                found_file = True
                                break
                        await asyncio.sleep(0.5)
                    
                    if found_file:
                        break
            
            if not found_file:
                logger.info(f"File not found in {channel['username']} with any date format: {source_filename}")
                if alternate_source_filename:
                    logger.info(f"Also tried alternate format: {alternate_source_filename}")
                
                # Last resort: try a very loose match for private channels (just look for Hindu + UPSC + date)
                if not found_file and channel['username'].startswith('https://t.me/+'):
                    logger.info(f"Trying last resort loose matching for {channel['username']}")
                    
                    # Extract key keywords from filename
                    key_parts = []
                    if "HINDU" in source_filename.upper():
                        key_parts.append("hindu")
                    if "UPSC" in source_filename.upper():
                        key_parts.append("upsc")
                    if "EXPRESS" in source_filename.upper():
                        key_parts.append("express")
                        
                    # Get just the date digits
                    date_digits = []
                    for part in source_date.split('~'):
                        if part.isdigit():
                            date_digits.append(part.lstrip('0') if part.startswith('0') else part)
                    
                    logger.info(f"Looking for loose match with keywords: {key_parts} and date digits: {date_digits}")
                    
                    # Manual pagination for last resort search
                    offset_id = 0
                    message_count = 0
                    max_messages = 100  # Check up to 100 messages
                    
                    while message_count < max_messages and not found_file:
                        messages = await client.get_messages(channel['username'], limit=50, offset_id=offset_id)
                        if not messages:
                            logger.info(f"No more messages found during last resort search after checking {message_count} messages")
                            break
                        
                        for message in messages:
                            message_count += 1
                            
                            # Skip messages without files or without name attribute
                            if not message.file or not hasattr(message.file, 'name') or not message.file.name:
                                continue
                                
                            file_name_lower = message.file.name.lower()
                            
                            # Log all PDF files for debugging
                            if file_name_lower.endswith('.pdf'):
                                logger.info(f"Last resort checking: {message.file.name}")
                                
                                # Check which keywords match
                                matching_keys = [part for part in key_parts if part in file_name_lower]
                                matching_dates = [digit for digit in date_digits if digit in file_name_lower]
                                
                                if matching_keys and matching_dates:
                                    logger.info(f"Potential match - Keys: {matching_keys}, Dates: {matching_dates}")
                                
                                # Must match all key parts (publication name, edition)
                                if all(part in file_name_lower for part in key_parts):
                                    # Must match at least one date part
                                    date_match = any(digit in file_name_lower for digit in date_digits if len(digit) > 0)
                                    
                                    if date_match and file_name_lower.endswith('.pdf'):
                                        logger.info(f"Found file with very loose matching: {message.file.name}")
                                        success = await download_file(client, message, target_filename, 'newspaper')
                                        if success:
                                            found_any = True
                                            found_file = True
                                            break
                        
                        if found_file:
                            break
                            
                        # Update offset_id for pagination if messages exist
                        if messages:
                            offset_id = messages[-1].id
                        
                        await asyncio.sleep(0.5)
                    
        return found_any
    except Exception as e:
        logger.error(f"Error checking {channel['username']}: {e}")
        return False


async def join_private_channels(client):
    """Joins private channels using their invite links before attempting to download"""
    for channel in channels:
        if channel['username'].startswith('https://t.me/+'):
            try:
                logger.info(f"Attempting to join private channel: {channel['username']}")
                # Extract the hash from the invite link
                channel_hash = channel['username'].split('+', 1)[1]
                
                # Try to join using ImportChatInviteRequest
                try:
                    await client(ImportChatInviteRequest(channel_hash))
                    logger.info(f"Successfully joined private channel using invite hash: {channel['username']}")
                except Exception as invite_err:
                    logger.warning(f"Couldn't join using invite hash, trying direct URL: {invite_err}")
                    # Try to join using the full URL as a fallback
                    try:
                        await client(JoinChannelRequest(channel['username']))
                        logger.info(f"Successfully joined private channel using full URL: {channel['username']}")
                    except Exception as url_err:
                        logger.error(f"Failed to join using full URL: {url_err}")
                        raise
                
                # Add a delay after joining to ensure it takes effect
                await asyncio.sleep(2)
                logger.info(f"Successfully joined private channel: {channel['username']}")
            except Exception as e:
                logger.error(f"Failed to join private channel {channel['username']}: {e}")

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
            
            # Join any private channels first
            await join_private_channels(client)
            
            # Verify channel access
            for channel in channels:
                try:
                    channel_entity = None
                    try:
                        # Try to get the channel entity to verify access
                        channel_entity = await client.get_entity(channel['username'])
                        logger.info(f"Successfully verified access to channel: {channel['username']}")
                    except Exception as access_err:
                        logger.error(f"Failed to verify access to channel {channel['username']}: {access_err}")
                    
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
