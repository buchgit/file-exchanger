#!/bin/bash
# Deploy script for File Exchanger Server on Ubuntu 24
# Run as root: bash deploy.sh

set -e

APP_DIR=/opt/file-exchanger

echo "=== Installing system dependencies ==="
apt update
apt install -y python3 python3-pip python3-venv git

echo "=== Cloning / updating repository ==="
if [ -d "$APP_DIR/.git" ]; then
    cd "$APP_DIR"
    git pull
else
    git clone https://github.com/buchgit/file-exchanger.git "$APP_DIR"
    cd "$APP_DIR"
fi

echo "=== Setting up Python virtual environment ==="
python3 -m venv "$APP_DIR/venv"
"$APP_DIR/venv/bin/pip" install --upgrade pip
"$APP_DIR/venv/bin/pip" install -r "$APP_DIR/server/requirements.txt"

echo "=== Creating storage directory ==="
mkdir -p "$APP_DIR/server/storage"
chown -R www-data:www-data "$APP_DIR"

echo "=== Installing systemd service ==="
cp "$APP_DIR/server/file-exchanger.service" /etc/systemd/system/
systemctl daemon-reload
systemctl enable file-exchanger
systemctl restart file-exchanger

echo "=== Configuring firewall ==="
ufw allow 8000/tcp
ufw --force enable

echo ""
echo "=== Done! ==="
systemctl status file-exchanger --no-pager
echo ""
echo "Server running at http://$(curl -s ifconfig.me):8000"
