from telethon.sync import TelegramClient
from telethon.sessions import StringSession

api_id = 20197798
api_hash = '109f16378f64be336b43eb678ea487df'

with TelegramClient(StringSession(), api_id, api_hash) as client:
    print("Your session string is:")
    print(client.session.save())
