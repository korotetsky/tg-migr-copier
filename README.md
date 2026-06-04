# tg-migr-copier

Telegram toolkit for:

- one-time migration of a Telegram channel into a forum topic;
- one-time migration of a Telegram group into a forum topic;
- continuous shadow mirroring from a source group into a target forum topic.

The project uses Telethon and runs as a systemd service.

## Repository structure

.
├── config.example.py
├── install.sh
├── requirements.txt
├── README.md
├── scripts/
│   ├── list_chats.py
│   ├── migrate_channel_full.py
│   ├── migrate_group_full.py
│   └── mirror_group.py
└── systemd/
    └── tg-mirror.service

## Runtime path

Default deployment path on the server:

/root/scripts/tg_migrator

The systemd service expects this path.

If you deploy elsewhere, edit:

systemd/tg-mirror.service

and update:

- WorkingDirectory
- ExecStart

## Configuration

Copy:

config.example.py

to:

config.py

and fill real values:

- API_ID
- API_HASH
- source channel/group IDs
- target group ID
- topic IDs
- ignored bot usernames

config.py is intentionally excluded from Git.

## Config Tool

The project includes an interactive configuration utility:

python config_tool.py

Features:

- show current configuration;
- validate configuration;
- set channel/group IDs;
- set forum topic IDs;
- add ignored bot usernames;
- remove ignored bot usernames.

Command line mode:

python config_tool.py show

python config_tool.py validate

python config_tool.py set GROUP_TOPIC_ID 4

python config_tool.py add-bot example_bot

python config_tool.py remove-bot example_bot

## Installation

Run as root:

./install.sh

The installer will:

- create /root/scripts/tg_migrator
- copy scripts
- copy config.example.py
- create config.py if it does not exist
- create Python virtual environment
- install dependencies
- install systemd service
- enable autostart

The installer does not start the service automatically.

## Python dependencies

Stored in:

requirements.txt

Manual install:

pip install -r requirements.txt

## Telegram sessions

Session files are NOT stored in Git.

Typical files:

- main_account.session
- mirror_account.session

Restore them from backup or create new sessions by authorizing Telegram accounts.

## Runtime state

The live mirror uses:

mirror_state.json

This file stores the last copied source message ID.

Before starting the mirror on a restored server, either restore this file from backup or create it manually with the correct last_copied_id.

Example:

{
  "last_copied_id": 528
}

## Systemd service

Service file in repository:

systemd/tg-mirror.service

Installed service path:

/etc/systemd/system/tg-mirror.service

Default runtime path:

/root/scripts/tg_migrator

If you deploy to another directory, update in the service file:

- WorkingDirectory
- ExecStart

## Service management

Status:

systemctl status tg-mirror

Start:

systemctl start tg-mirror

Stop:

systemctl stop tg-mirror

Restart:

systemctl restart tg-mirror

Live logs:

journalctl -u tg-mirror -f

Last 100 log lines:

journalctl -u tg-mirror -n 100

## Files excluded from Git

Never commit:

- config.py
- *.session
- *.session-journal
- mirror_state.json
- progress_channel.json
- progress_group.json
- venv/
- __pycache__/
- .DS_Store

These files contain secrets, Telegram sessions, runtime state or local environment data.

## Recovery workflow

1. Clone this repository.
2. Run ./install.sh as root.
3. Fill /root/scripts/tg_migrator/config.py.
4. Restore Telegram session files from private backup or authorize accounts again.
5. Restore or create mirror_state.json.
6. Start the service:

systemctl start tg-mirror

7. Check status:

systemctl status tg-mirror
