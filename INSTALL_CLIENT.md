# Client Installation Instructions for LLM Agents

## Target environment
- OS: Windows 10/11, Ubuntu 24.04, or macOS 12+
- Python 3.10 or newer required
- The server must already be running and accessible (see INSTALL_SERVER.md)

## Prerequisites check

```bash
# Check Python version (must be 3.10+)
python --version        # Windows
python3 --version       # Linux/macOS
# Expected: Python 3.10.x or newer

# Check pip
python -m pip --version
# Expected: pip 23.x.x or newer
```

If Python is not installed:
- **Windows:** download from https://www.python.org/downloads/ — check "Add Python to PATH" during install
- **Ubuntu:** `sudo apt update && sudo apt install -y python3 python3-pip python3-venv`
- **macOS:** `brew install python`

## Step 1 — Clone the repository

```bash
git clone https://github.com/buchgit/file-exchanger.git
cd file-exchanger
```

If git is not available:
- **Windows:** download ZIP from https://github.com/buchgit/file-exchanger/archive/refs/heads/master.zip and extract
- **Ubuntu:** `sudo apt install -y git`
- **macOS:** `xcode-select --install`

## Step 2 — Install system dependencies (Linux only)

On Ubuntu/Debian, PyQt6 requires additional system libraries:

```bash
sudo apt update
sudo apt install -y \
    libgl1 libglib2.0-0 libxcb-cursor0 \
    libxcb-icccm4 libxcb-image0 libxcb-keysyms1 \
    libxcb-render-util0 libxcb-xinerama0 libxkbcommon-x11-0 \
    libdbus-1-3 libxcb-shape0
```

Skip this step on Windows and macOS.

## Step 3 — Create Python virtual environment

```bash
cd file-exchanger/client

# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

Verify activation:
```bash
python --version
# Expected: Python 3.10+ (from venv)
which python    # Linux/macOS — should point inside venv/
where python    # Windows — should point inside venv\
```

## Step 4 — Install Python dependencies

```bash
pip install -r requirements.txt
```

Expected: installs PyQt6, requests, websocket-client without errors. Exit code: 0.

Verify:
```bash
pip show PyQt6 requests websocket-client
# Expected: shows Name and Version for each package
```

If PyQt6 fails on Linux with "Failed building wheel":
```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

## Step 5 — Configure server address

The `.env` file must be created inside the `client/` directory (next to `main.py`).

Copy the example config file from within `client/`:

```bash
# Windows (cmd)
copy .env.example .env

# Windows (PowerShell)
Copy-Item .env.example .env

# Linux/macOS
cp .env.example .env
```

Edit `client/.env` and set your server address:

```
FILE_EXCHANGER_HOST=<SERVER_IP>:<PORT>
```

Example:
```
FILE_EXCHANGER_HOST=192.168.1.100:8000
```

The `.env` file is gitignored and will not be committed to the repository.

Priority order for server address (highest to lowest):
1. `FILE_EXCHANGER_HOST` environment variable
2. `FILE_EXCHANGER_HOST` value in `client/.env`
3. Default: `localhost:8000`

## Step 6 — Verify server connectivity

Before launching the client, confirm the server is reachable:

```bash
# Windows (PowerShell)
Invoke-WebRequest -Uri "http://<SERVER_IP>:8000/health" -UseBasicParsing
# Expected: StatusCode 200, Content {"status":"ok"}

# Linux/macOS
curl -s http://<SERVER_IP>:8000/health
# Expected: {"status":"ok"}
```

If the server is not reachable:
- Check that the server is running (see INSTALL_SERVER.md)
- Check firewall on the server: `ufw status`
- Check that the IP and port in `.env` are correct

## Step 7 — Run the client

```bash
# Make sure the virtual environment is activated, then:
python main.py
```

Expected: a login window appears.

If the window does not appear on Linux (no display):
```bash
echo $DISPLAY
# Must not be empty. If running over SSH, use: ssh -X user@host
```

## Step 8 — First login

1. Enter `admin` as username and `admin` as password
2. A "Change Password" form will appear — this is mandatory on first login
3. After changing the password the main window opens with tabs: **Inbox**, **Send**, **Admin**
4. Status bar at the bottom should show **"WS: connected"**

## Session persistence and server switching

After a successful login, the session token is saved to:
- **Windows:** `C:\Users\<username>\.file_exchanger\session.json`
- **Linux/macOS:** `~/.file_exchanger/session.json`

On the next launch the client restores the session automatically — no login required.

> **When switching servers:** the saved session token is bound to the server
> it was issued by. If you change `FILE_EXCHANGER_HOST` in `.env` to point
> to a different server, the old token will be rejected and the login dialog
> will appear automatically. This is expected behaviour, not an error.
> Simply log in with credentials valid on the new server.

To force a fresh login, delete the session file:
```bash
# Windows
del "%USERPROFILE%\.file_exchanger\session.json"

# Linux/macOS
rm ~/.file_exchanger/session.json
```

## Uninstalling

```bash
# Deactivate venv
deactivate

# Delete the project directory
rm -rf file-exchanger          # Linux/macOS
rmdir /s /q file-exchanger     # Windows

# Delete saved session
rm -rf ~/.file_exchanger       # Linux/macOS
rmdir /s /q "%USERPROFILE%\.file_exchanger"   # Windows
```

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| `python main.py` — `ModuleNotFoundError: PyQt6` | venv not activated or install failed | Activate venv and re-run `pip install -r requirements.txt` |
| Login window appears after server change | Session token from old server is invalid | Expected — just log in with new server credentials |
| Login window appears but login fails | Wrong server address | Check `client/.env`, verify with `curl` |
| `WS: reconnecting…` in status bar | WebSocket can't connect | Check port 8000 is open on server; check `.env` address |
| Blank window / no widgets visible | Missing Qt system libs on Linux | Re-run Step 2 system dependencies |
| `qt.qpa.plugin: could not load xcb` | Missing xcb libs on Linux | `sudo apt install -y libxcb-cursor0 libxcb-icccm4` |
