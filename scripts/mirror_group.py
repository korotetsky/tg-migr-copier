from telethon import TelegramClient, events
from telethon.errors import FloodWaitError
try:
    from config import API_ID, API_HASH, MIRROR_SESSION_NAME, OLD_GROUP_ID, NEW_GROUP_ID, GROUP_TOPIC_ID, IGNORED_USERNAMES
except ModuleNotFoundError:
    raise SystemExit("config.py not found. Copy config.example.py to config.py and fill real values.")
import asyncio
import json
import os


STATE_FILE = "mirror_state.json"



def load_state():
    if not os.path.exists(STATE_FILE):
        return {"last_copied_id": 0}
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_state(state):
    tmp = STATE_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    os.replace(tmp, STATE_FILE)


async def sender_name(event):
    sender = await event.get_sender()
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


async def build_text(event):
    author = await sender_name(event)
    date = event.message.date.strftime("%Y-%m-%d %H:%M:%S UTC")
    original_text = event.message.message or ""

    return (
        f"📅 {date}\n"
        f"👤 Автор: {author}\n\n"
        f"{original_text}"
    )


async def main():
    state = load_state()

    client = TelegramClient(MIRROR_SESSION_NAME, API_ID, API_HASH)
    await client.start()

    source = await client.get_entity(OLD_GROUP_ID)
    target = await client.get_entity(NEW_GROUP_ID)

    print("Mirror started")
    print(f"Source: {getattr(source, 'title', OLD_GROUP_ID)}")
    print(f"Target: {getattr(target, 'title', NEW_GROUP_ID)} / topic {GROUP_TOPIC_ID}")
    print(f"Last copied ID: {state.get('last_copied_id', 0)}")

    @client.on(events.NewMessage(chats=source))
    async def handler(event):
        if event.message.action:
            return

        sender = await event.get_sender()
        username = getattr(sender, "username", None)
        if username and username.lower() in IGNORED_USERNAMES:
            print(f"ignored bot @{username} old_id={event.message.id}")
            state["last_copied_id"] = event.message.id
            save_state(state)
            return

        last_id = state.get("last_copied_id", 0)
        if event.message.id <= last_id:
            return

        text = await build_text(event)

        try:
            if event.message.media:
                await client.send_file(
                    target,
                    event.message.media,
                    caption=text[:1024],
                    reply_to=GROUP_TOPIC_ID
                )

                if len(text) > 1024:
                    await client.send_message(
                        target,
                        text[1024:],
                        reply_to=GROUP_TOPIC_ID
                    )
            else:
                await client.send_message(
                    target,
                    text or "[empty message]",
                    reply_to=GROUP_TOPIC_ID
                )

            state["last_copied_id"] = event.message.id
            save_state(state)

            print(f"copied old_id={event.message.id}")

        except FloodWaitError as e:
            print(f"FloodWait: sleeping {e.seconds} seconds")
            await asyncio.sleep(e.seconds + 5)

        except Exception as e:
            print(f"ERROR old_id={event.message.id}: {type(e).__name__}: {e}")

    await client.run_until_disconnected()


asyncio.run(main())
