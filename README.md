# File Exchanger

A client-server application for secure file exchange between users.

## Stack

- **Server:** Python, FastAPI, SQLAlchemy, SQLite, WebSockets
- **Client:** Python, PyQt6, requests, websocket-client

## Project Structure

```
file_exchanger/
├── server/                       # FastAPI backend
│   ├── main.py
│   ├── auth.py
│   ├── models.py
│   ├── database.py
│   ├── connection_manager.py
│   ├── config.py
│   ├── routes/
│   │   ├── auth.py               # POST /auth/login, /auth/change-password
│   │   ├── users.py              # CRUD /users/
│   │   ├── files.py              # Upload, download, ack /files/
│   │   └── ws.py                 # WebSocket /ws
│   ├── file-exchanger.service    # systemd unit file
│   ├── deploy.sh                 # Ubuntu 24 deploy script
│   ├── tests/                    # 34 pytest tests
│   └── requirements.txt
└── client/                       # PyQt6 desktop client
    ├── main.py
    ├── api.py                    # ApiClient + ApiWorker
    ├── ws_thread.py              # WebSocket thread with auto-reconnect
    ├── config.py                 # Constants + session persistence
    ├── .env.example              # Server address template (copy to .env)
    ├── ui/
    │   ├── login_dialog.py       # Login + forced password change
    │   ├── main_window.py        # Main window with tabs
    │   ├── inbox_widget.py       # Incoming files
    │   ├── send_widget.py        # Send files
    │   └── admin_widget.py       # User management (admin only)
    └── requirements.txt
```

## Features

- JWT authentication with forced password change on first login
- Send files to other users with part/multipart support and comments
- Real-time notifications via WebSocket when a new file arrives
- Download and acknowledge received files
- Admin panel: create and delete users
- Session persistence — no re-login after restart

## Detailed installation guides

- **[INSTALL_SERVER.md](INSTALL_SERVER.md)** — deploy server on Ubuntu 24 (for LLM agents and sysadmins)
- **[INSTALL_CLIENT.md](INSTALL_CLIENT.md)** — install client on Windows / Linux / macOS (for LLM agents and end users)

---

## Server — Quick Start

### Local (development)

```bash
cd server
python -m venv venv

# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Remote (Ubuntu 24, one command)

SSH into the server and run:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/buchgit/file-exchanger/master/server/deploy.sh)
```

The script installs dependencies, creates a systemd service, and opens port 8000.

### Verify

```bash
curl http://<SERVER_IP>:8000/health
# Expected: {"status":"ok"}
```

**Default admin credentials:** `admin` / `admin` (forced password change on first login)

### Run tests

```bash
cd server && pytest
# Expected: 34 passed
```

---

## Client — Quick Start

```bash
cd client
python -m venv venv

# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

pip install -r requirements.txt
```

### Configure server address

```bash
# Windows
copy .env.example .env
# Linux/macOS
cp .env.example .env
```

Edit `client/.env`:

```
FILE_EXCHANGER_HOST=<SERVER_IP>:8000
```

The `.env` file is gitignored. Priority order (highest to lowest):
1. `FILE_EXCHANGER_HOST` environment variable
2. `FILE_EXCHANGER_HOST` in `client/.env`
3. Default: `localhost:8000`

### Run

```bash
python main.py
```

---

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/login` | Login (form-encoded) |
| POST | `/auth/change-password` | Change password |
| GET | `/users/` | List all users |
| POST | `/users/` | Create user (admin) |
| DELETE | `/users/{id}` | Delete user (admin) |
| POST | `/files/upload` | Upload file |
| GET | `/files/pending` | List pending files |
| GET | `/files/{id}/part/{n}` | Download file part |
| POST | `/files/{id}/ack` | Acknowledge receipt |
| WS | `/ws?token=...` | Real-time notifications |
