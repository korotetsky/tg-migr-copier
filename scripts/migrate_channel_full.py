from telethon import TelegramClient
from telethon.errors import FloodWaitError
from telethon.tl.types import MessageMediaWebPage
try:
    from config import API_ID, API_HASH, MAIN_SESSION_NAME, OLD_CHANNEL_ID, NEW_GROUP_ID, CHANNEL_TOPIC_ID
except ModuleNotFoundError:
    raise SystemExit("config.py not found. Copy config.example.py to config.py and fill real values.")
import asyncio
import json
import os


DELAY_SECONDS = 3
PROGRESS_FILE = "progress_channel.json"


def load_progress():
    if not os.path.exists(PROGRESS_FILE):
        return {"done_ids": []}
    with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_progress(progress):
    tmp = PROGRESS_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)
    os.replace(tmp, PROGRESS_FILE)


async def sender_name(msg):
    sender = await msg.get_sender()
    if not sender:
        return "невідомо"

    name_parts = []
    if getattr(sender, "first_name", None):
        name_parts.append(sender.first_name)
    if getattr(sender, "last_name", None):
        name_parts.append(sender.last_name)

    name = " ".join(name_parts) or getattr(sender, "title", None) or "невідомо"
    username = getattr(sender, "username", None)

    if username:
        return f"{name} (@{username})"
    return name


async def build_header(msg):
    author = await sender_name(msg)
    date = msg.date.strftime("%Y-%m-%d %H:%M:%S UTC")
    original_text = msg.message or ""

    header = (
        f"📅 {date}\n"
        f"👤 Автор: {author}\n\n"
    )

    return header + original_text


async def main():
    client = TelegramClient(MAIN_SESSION_NAME, API_ID, API_HASH)
    await client.start()

    source = await client.get_entity(OLD_CHANNEL_ID)
    target = await client.get_entity(NEW_GROUP_ID)

    progress = load_progress()
    done_ids = set(progress.get("done_ids", []))

    messages = []
    async for msg in client.iter_messages(source, limit=None):
        if msg.action:
            continue
        if msg.id in done_ids:
            continue
        messages.append(msg)

    messages.reverse()

    print(f"Already done: {len(done_ids)}")
    print(f"To send now: {len(messages)}")

    for i, msg in enumerate(messages, start=1):
        text = await build_header(msg)

        try:
            if msg.media and not isinstance(msg.media, MessageMediaWebPage):
                await client.send_file(
                    target,
                    msg.media,
                    caption=text[:1024],
                    reply_to=CHANNEL_TOPIC_ID
                )

                if len(text) > 1024:
                    await client.send_message(
                        target,
                        text[1024:],
                        reply_to=CHANNEL_TOPIC_ID
                    )
            else:
                await client.send_message(
                    target,
                    text or "[empty message]",
                    reply_to=CHANNEL_TOPIC_ID
                )

            done_ids.add(msg.id)
            progress["done_ids"] = sorted(done_ids)
            save_progress(progress)

            print(f"OK {i}/{len(messages)} | old_id={msg.id}")
            await asyncio.sleep(DELAY_SECONDS)

        except FloodWaitError as e:
            print(f"FloodWait: sleeping {e.seconds} seconds")
            await asyncio.sleep(e.seconds + 5)

        except KeyboardInterrupt:
            print("Stopped by user")
            break

        except Exception as e:
            print(f"ERROR old_id={msg.id}: {type(e).__name__}: {e}")

    await client.disconnect()


asyncio.run(main())
