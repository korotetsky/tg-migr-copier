#!/usr/bin/env bash

set -e

APP_DIR="/root/scripts/tg_migrator"

echo "== tg-migr-copier installer =="

if [ "$EUID" -ne 0 ]; then
    echo "Run as root"
    exit 1
fi

mkdir -p "$APP_DIR"

echo "Copying scripts..."
cp scripts/*.py "$APP_DIR/"

echo "Copying config example..."
cp config.example.py "$APP_DIR/"

if [ ! -f "$APP_DIR/config.py" ]; then
    cp "$APP_DIR/config.example.py" "$APP_DIR/config.py"
fi

echo "Copying requirements..."
cp requirements.txt "$APP_DIR/"

echo "Creating virtualenv..."
python3 -m venv "$APP_DIR/venv"

echo "Installing dependencies..."
"$APP_DIR/venv/bin/pip" install --upgrade pip
"$APP_DIR/venv/bin/pip" install -r "$APP_DIR/requirements.txt"

echo "Installing systemd service..."
cp systemd/tg-mirror.service /etc/systemd/system/tg-mirror.service

systemctl daemon-reload
systemctl enable tg-mirror

echo
echo "Installation complete."
echo
echo "Next steps:"
echo "1. Edit $APP_DIR/config.py"
echo "2. Restore or create Telegram sessions"
echo "3. Restore mirror_state.json if needed"
echo "4. Start service:"
echo "   systemctl start tg-mirror"
echo
echo "Check status:"
echo "   systemctl status tg-mirror"
