import json
from pathlib import Path

BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000/ws"

SESSION_FILE = Path.home() / ".file_exchanger/session.json"

CHUNK_SIZE = 256 * 1024
PING_INTERVAL_SEC = 30
WS_RECONNECT_DELAY_SEC = 5


def load_session() -> dict | None:
    try:
        data = json.loads(SESSION_FILE.read_text())
        # Validate expected keys
        for key in ("token", "user_id", "username", "is_admin"):
            if key not in data:
                return None
        return data
    except Exception:
        return None


def save_session(token: str, user_id: int, username: str, is_admin: bool) -> None:
    SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)
    SESSION_FILE.write_text(
        json.dumps({"token": token, "user_id": user_id, "username": username, "is_admin": is_admin})
    )


def clear_session() -> None:
    try:
        SESSION_FILE.unlink()
    except FileNotFoundError:
        pass
