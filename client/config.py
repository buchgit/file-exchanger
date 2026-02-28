import json
import os
from pathlib import Path


def _load_env_file() -> dict:
    """Read key=value pairs from client/.env if it exists."""
    env_file = Path(__file__).parent / ".env"
    result = {}
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                result[key.strip()] = value.strip()
    return result


_env = _load_env_file()

_SERVER_HOST = (
    os.environ.get("FILE_EXCHANGER_HOST")
    or _env.get("FILE_EXCHANGER_HOST")
    or "localhost:8000"
)

BASE_URL = f"http://{_SERVER_HOST}"
WS_URL   = f"ws://{_SERVER_HOST}/ws"

SESSION_FILE = Path.home() / ".file_exchanger/session.json"

CHUNK_SIZE = 256 * 1024
PING_INTERVAL_SEC = 30
WS_RECONNECT_DELAY_SEC = 5


def load_session() -> dict | None:
    try:
        data = json.loads(SESSION_FILE.read_text())
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
