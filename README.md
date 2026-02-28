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

## Getting Started

### Server

```bash
cd server
pip install -r requirements.txt
uvicorn main:app --reload
```

Server runs at `http://localhost:8000`. Default admin credentials: `admin` / `admin`.

### Client

```bash
cd client
pip install -r requirements.txt
python main.py
```

### Run Tests

```bash
cd server
pytest
```

All 34 tests should pass.

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
