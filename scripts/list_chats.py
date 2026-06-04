from telethon import TelegramClient
from config import API_ID, API_HASH, SESSION_NAME
import asyncio

async def main():
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

    await client.start()

    print("\n=== CHATS ===\n")

    async for dialog in client.iter_dialogs():
        print(f"{dialog.id} | {dialog.name}")

    await client.disconnect()

asyncio.run(main())
