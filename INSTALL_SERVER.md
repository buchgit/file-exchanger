# Server Installation Instructions for LLM Agents

## Target environment
- OS: Ubuntu 24.04 LTS
- Access: SSH root or sudo user
- Required open port: 8000 (TCP)

## Prerequisites check

Run the following commands to verify the environment before starting:

```bash
# Check OS version
lsb_release -a
# Expected output contains: Ubuntu 24.04

# Check Python version (must be 3.10+)
python3 --version
# Expected: Python 3.12.x

# Check git
git --version
# Expected: git version 2.x.x

# Check available disk space (need at least 500 MB)
df -h /
```

## Step 1 — Install system packages

```bash
apt update && apt install -y python3 python3-pip python3-venv git curl
```

Expected: packages install without errors. Exit code: 0.

## Step 2 — Clone the repository

```bash
git clone https://github.com/buchgit/file-exchanger.git /opt/file-exchanger
```

Expected: directory `/opt/file-exchanger` is created with `server/` and `client/` subdirectories.

Verify:
```bash
ls /opt/file-exchanger/server/
# Expected output includes: main.py requirements.txt routes/ tests/
```

## Step 3 — Create Python virtual environment

```bash
python3 -m venv /opt/file-exchanger/venv
```

Verify:
```bash
/opt/file-exchanger/venv/bin/python --version
# Expected: Python 3.12.x
```

## Step 4 — Install Python dependencies

```bash
/opt/file-exchanger/venv/bin/pip install --upgrade pip
/opt/file-exchanger/venv/bin/pip install -r /opt/file-exchanger/server/requirements.txt
```

Expected: all packages install without errors. Exit code: 0.

Verify:
```bash
/opt/file-exchanger/venv/bin/pip show fastapi uvicorn sqlalchemy
# Expected: shows Name, Version, Location for each package
```

## Step 5 — Create storage directory and set permissions

```bash
mkdir -p /opt/file-exchanger/server/storage
chown -R www-data:www-data /opt/file-exchanger
chmod -R 750 /opt/file-exchanger
```

## Step 6 — Configure environment (optional)

Create `/opt/file-exchanger/server/.env` to override defaults:

```bash
cat > /opt/file-exchanger/server/.env <<EOF
SECRET_KEY=replace-with-a-long-random-string
STORAGE_PATH=./storage
DATABASE_URL=sqlite:///./file_exchanger.db
EOF
```

To generate a secure SECRET_KEY:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

## Step 7 — Install systemd service

```bash
cp /opt/file-exchanger/server/file-exchanger.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable file-exchanger
systemctl start file-exchanger
```

Verify the service is running:
```bash
systemctl is-active file-exchanger
# Expected output: active

systemctl status file-exchanger --no-pager
# Expected: Active: active (running)
```

## Step 8 — Configure firewall

```bash
ufw allow 8000/tcp
ufw --force enable
ufw status
# Expected: 8000/tcp  ALLOW  Anywhere
```

## Step 9 — Verify the server responds

```bash
curl -s http://localhost:8000/health
# Expected: {"status":"ok"}

# From external machine (replace IP with actual server IP):
curl -s http://<SERVER_IP>:8000/health
# Expected: {"status":"ok"}
```

## Step 10 — Check initial admin account

```bash
curl -s -X POST http://localhost:8000/auth/login \
  -d "username=admin&password=admin"
# Expected: JSON with access_token and "force_change_password": true
```

If step 10 returns 401, the database may already have a changed admin password — that is normal.

## Updating the server

```bash
cd /opt/file-exchanger
git pull
systemctl restart file-exchanger
systemctl is-active file-exchanger
# Expected: active
```

## Viewing logs

```bash
journalctl -u file-exchanger -n 50 --no-pager
# Live logs:
journalctl -u file-exchanger -f
```

## Uninstalling

```bash
systemctl stop file-exchanger
systemctl disable file-exchanger
rm /etc/systemd/system/file-exchanger.service
systemctl daemon-reload
rm -rf /opt/file-exchanger
ufw delete allow 8000/tcp
```

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| `systemctl start` fails | Port 8000 already in use | `lsof -i :8000` then kill the process |
| `curl localhost:8000/health` — connection refused | Service not running | `journalctl -u file-exchanger -n 20` to see the error |
| 403 on file operations | Storage dir wrong owner | `chown -R www-data:www-data /opt/file-exchanger/server/storage` |
| Can't connect from internet | Firewall blocking | `ufw allow 8000/tcp` and check cloud provider security groups |
