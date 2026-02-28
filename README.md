# File Exchanger

A client-server application for secure file exchange between users.

## Stack

- **Server:** Python, FastAPI, SQLAlchemy, SQLite, WebSockets
- **Client:** Python, PyQt6, requests, websocket-client

## Project Structure

```
file_exchanger/
├── server/                  # FastAPI backend
│   ├── main.py
│   ├── auth.py
│   ├── models.py
│   ├── database.py
│   ├── connection_manager.py
│   ├── config.py
│   ├── routes/
│   │   ├── auth.py          # POST /auth/login, /auth/change-password
│   │   ├── users.py         # CRUD /users/
│   │   ├── files.py         # Upload, download, ack /files/
│   │   └── ws.py            # WebSocket /ws
│   ├── tests/               # 34 pytest tests
│   └── requirements.txt
└── client/                  # PyQt6 desktop client
    ├── main.py
    ├── api.py               # ApiClient + ApiWorker
    ├── ws_thread.py         # WebSocket thread with auto-reconnect
    ├── config.py            # Constants + session persistence
    ├── ui/
    │   ├── login_dialog.py  # Login + forced password change
    │   ├── main_window.py   # Main window with tabs
    │   ├── inbox_widget.py  # Incoming files
    │   ├── send_widget.py   # Send files
    │   └── admin_widget.py  # User management (admin only)
    └── requirements.txt
```

## Features

- JWT authentication with forced password change on first login
- Send files to other users with part/multipart support and comments
- Real-time notifications via WebSocket when a new file arrives
- Download and acknowledge received files
- Admin panel: create and delete users
- Session persistence — no re-login after restart

---

## Server Installation

### Requirements

- Python 3.10 or newer
- pip

### Step 1 — Install Python

**Windows:**
1. Download installer from https://www.python.org/downloads/
2. Run installer, check **"Add Python to PATH"**
3. Verify: open Command Prompt and run:
   ```
   python --version
   ```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

**macOS:**
```bash
brew install python
```

### Step 2 — Clone the repository

```bash
git clone https://github.com/buchgit/file-exchanger.git
cd file-exchanger
```

### Step 3 — Create virtual environment (recommended)

```bash
cd server
python -m venv venv
```

Activate:
- **Windows:** `venv\Scripts\activate`
- **Linux/macOS:** `source venv/bin/activate`

### Step 4 — Install dependencies

```bash
pip install -r requirements.txt
```

Dependencies installed:
| Package | Version | Purpose |
|---------|---------|---------|
| fastapi | 0.123.9 | Web framework |
| uvicorn | 0.32.0 | ASGI server |
| sqlalchemy | 2.0.36 | ORM / SQLite |
| bcrypt | 4.2.0 | Password hashing |
| python-jose | 3.3.0 | JWT tokens |
| python-multipart | 0.0.12 | File upload support |
| aiofiles | 24.1.0 | Async file I/O |
| pydantic-settings | 2.6.1 | Configuration |

### Step 5 — Configure (optional)

Create a `.env` file in the `server/` directory to override defaults:

```env
SECRET_KEY=your-secret-key-change-in-production
STORAGE_PATH=./storage
DATABASE_URL=sqlite:///./file_exchanger.db
```

If not provided, the server uses built-in defaults.

### Step 6 — Run the server

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The server starts at `http://localhost:8000`.
Swagger UI (API docs) available at `http://localhost:8000/docs`.

**Default admin credentials:** `admin` / `admin`
You will be asked to change the password on first login.

### Step 7 — Run tests (optional)

```bash
pip install pytest pytest-asyncio httpx
pytest
```

All 34 tests should pass.

---

## Client Installation

### Requirements

- Python 3.10 or newer
- Running server (see above)

### Step 1 — Install Python

Same as server Step 1 above.

### Step 2 — Install system dependencies

**Linux only** — PyQt6 requires the following:
```bash
sudo apt update
sudo apt install libgl1 libglib2.0-0 libxcb-cursor0 \
    libxcb-icccm4 libxcb-image0 libxcb-keysyms1 \
    libxcb-render-util0 libxcb-xinerama0 libxkbcommon-x11-0
```

**Windows / macOS:** no extra dependencies needed.

### Step 3 — Navigate to client directory

```bash
cd file-exchanger/client
```

### Step 4 — Create virtual environment (recommended)

```bash
python -m venv venv
```

Activate:
- **Windows:** `venv\Scripts\activate`
- **Linux/macOS:** `source venv/bin/activate`

### Step 5 — Install dependencies

```bash
pip install -r requirements.txt
```

Dependencies installed:
| Package | Version | Purpose |
|---------|---------|---------|
| PyQt6 | ≥ 6.6.0 | GUI framework |
| requests | ≥ 2.32.0 | HTTP API calls |
| websocket-client | ≥ 1.8.0 | WebSocket connection |

### Step 6 — Configure server address (optional)

By default the client connects to `http://localhost:8000`.
To connect to a remote server, edit `client/config.py`:

```python
BASE_URL = "http://your-server-address:8000"
WS_URL  = "ws://your-server-address:8000/ws"
```

### Step 7 — Run the client

```bash
python main.py
```

The login window will appear. Enter your credentials.
On first login you will be prompted to change your password.

### Session persistence

After a successful login, the session token is saved to:
- **Windows:** `C:\Users\<username>\.file_exchanger\session.json`
- **Linux/macOS:** `~/.file_exchanger/session.json`

The next launch will restore the session automatically without prompting for login.

---

## Quick Start (both on the same machine)

```bash
# Terminal 1 — server
cd file-exchanger/server
python -m venv venv && venv\Scripts\activate   # Windows
pip install -r requirements.txt
uvicorn main:app --reload

# Terminal 2 — client
cd file-exchanger/client
python -m venv venv && venv\Scripts\activate   # Windows
pip install -r requirements.txt
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
