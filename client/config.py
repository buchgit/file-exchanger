import json
import os
import sys
from pathlib import Path
from typing import Mapping


ENV_FILE_NAME = ".env"
HOST_KEY = "FILE_EXCHANGER_HOST"
IP_KEYS = ("FILE_EXCHANGER_SERVER_IP", "FILE_EXCHANGER_IP")
PORT_KEYS = ("FILE_EXCHANGER_SERVER_PORT", "FILE_EXCHANGER_PORT")
DEFAULT_PORT = "8000"


def _candidate_env_files() -> list[Path]:
    candidates: list[Path] = []
    if getattr(sys, "frozen", False):
        candidates.append(Path(sys.executable).resolve().parent / ENV_FILE_NAME)
    candidates.append(Path.cwd() / ENV_FILE_NAME)
    candidates.append(Path(__file__).resolve().parent / ENV_FILE_NAME)

    # Keep order and remove duplicates on case-insensitive filesystems.
    deduped: list[Path] = []
    seen: set[str] = set()
    for env_file in candidates:
        key = str(env_file).lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(env_file)
    return deduped


def _parse_env_text(text: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        result[key.strip()] = value.strip()
    return result


def _load_env_file() -> tuple[dict[str, str], Path | None]:
    """Read key=value pairs from the first existing .env file."""
    for env_file in _candidate_env_files():
        if not env_file.exists():
            continue
        for encoding in ("utf-8-sig", "cp1251"):
            try:
                return _parse_env_text(env_file.read_text(encoding=encoding)), env_file
            except UnicodeDecodeError:
                continue
    return {}, None


def _first_non_empty(values: Mapping[str, str], keys: tuple[str, ...]) -> str:
    for key in keys:
        value = values.get(key, "")
        if value and value.strip():
            return value.strip()
    return ""


def _normalize_host(raw_value: str | None) -> str:
    if not raw_value:
        return ""
    host = raw_value.strip().strip('"').strip("'")
    if not host:
        return ""
    host = host.removeprefix("http://").removeprefix("https://").rstrip("/")
    if not host:
        return ""
    if ":" not in host:
        host = f"{host}:{DEFAULT_PORT}"
    return host


def _host_from_ip_port(values: Mapping[str, str]) -> str:
    ip = _first_non_empty(values, IP_KEYS)
    if not ip:
        return ""
    port = _first_non_empty(values, PORT_KEYS) or DEFAULT_PORT
    return f"{ip}:{port}"


def _resolve_server_host(env_data: dict[str, str]) -> str:
    for candidate in (
        os.environ.get(HOST_KEY),
        env_data.get(HOST_KEY),
        _host_from_ip_port(os.environ),
        _host_from_ip_port(env_data),
    ):
        host = _normalize_host(candidate)
        if host:
            return host
    return ""


_env, _loaded_env_path = _load_env_file()

SERVER_HOST = _resolve_server_host(_env)
BASE_URL = f"http://{SERVER_HOST}" if SERVER_HOST else ""
WS_URL = f"ws://{SERVER_HOST}/ws" if SERVER_HOST else ""

SESSION_FILE = Path.home() / ".file_exchanger/session.json"

CHUNK_SIZE = 256 * 1024
PING_INTERVAL_SEC = 30
WS_RECONNECT_DELAY_SEC = 5


def server_is_configured() -> bool:
    return bool(SERVER_HOST)


def preferred_env_file() -> Path:
    """Return the main .env path where users should configure server host."""
    return _candidate_env_files()[0]


def server_config_help_text() -> str:
    env_path = preferred_env_file()
    return (
        "Server address is not configured.\n\n"
        f"Create/edit file:\n{env_path}\n\n"
        "Add one of these options:\n"
        "FILE_EXCHANGER_HOST=192.168.1.100:8000\n"
        "or FILE_EXCHANGER_SERVER_IP=192.168.1.100\n"
    )


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
        json.dumps(
            {
                "token": token,
                "user_id": user_id,
                "username": username,
                "is_admin": is_admin,
            }
        )
    )


def clear_session() -> None:
    try:
        SESSION_FILE.unlink()
    except FileNotFoundError:
        pass
