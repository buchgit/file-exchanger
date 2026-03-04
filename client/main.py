from __future__ import annotations

import sys
import traceback
from pathlib import Path

# Ensure the client directory is on sys.path so sibling imports work
sys.path.insert(0, str(Path(__file__).parent))

from PyQt6.QtWidgets import QApplication, QMessageBox

import config
from api import ApiClient
from ui.login_dialog import LoginDialog
from ui.main_window import MainWindow


def _write_crash_log(exc: BaseException) -> Path | None:
    """Persist unexpected startup/runtime errors for packaged EXE diagnostics."""
    try:
        log_dir = Path.home() / ".file_exchanger"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "client_crash.log"
        with log_file.open("a", encoding="utf-8") as fh:
            fh.write("\n=== FileExchanger crash ===\n")
            fh.write("Python executable: " + sys.executable + "\n")
            fh.write("Working directory: " + str(Path.cwd()) + "\n")
            fh.write("Traceback:\n")
            fh.write("".join(traceback.format_exception(type(exc), exc, exc.__traceback__)))
        return log_file
    except Exception:
        return None


def _show_server_config_error() -> None:
    QMessageBox.critical(
        None,
        "Server Address Is Not Configured",
        config.server_config_help_text(),
    )


def main() -> None:
    app = QApplication(sys.argv)

    if not config.server_is_configured():
        _show_server_config_error()
        sys.exit(1)

    api = ApiClient()

    # ------------------------------------------------------------------
    # Try session restore (sync, before event loop)
    # ------------------------------------------------------------------
    token: str | None = None
    user_info: dict | None = None

    session = config.load_session()
    if session:
        try:
            u = api.get_user(session["token"], session["user_id"])
            token = session["token"]
            user_info = {
                "id": u.id,
                "username": u.username,
                "is_admin": u.is_admin,
            }
        except Exception:
            config.clear_session()

    # ------------------------------------------------------------------
    # Login if no valid session
    # ------------------------------------------------------------------
    if token is None:
        token, user_info = _do_login(api)
        if token is None:
            sys.exit(0)
        # If user_info has no id yet (login dialog only has username),
        # fetch proper user info now
        user_info = _resolve_user_info(api, token, user_info)
        config.save_session(
            token,
            user_info["id"],
            user_info["username"],
            user_info["is_admin"],
        )

    # ------------------------------------------------------------------
    # Show main window
    # ------------------------------------------------------------------
    _show_main(app, api, token, user_info)
    sys.exit(app.exec())


def _do_login(api: ApiClient) -> tuple[str | None, dict | None]:
    """Show login dialog; return (token, user_info) or (None, None)."""
    result: dict = {}

    dialog = LoginDialog(api)
    dialog.login_successful.connect(lambda t, u: result.update(token=t, user=u))
    if not dialog.exec() or not result:
        return None, None
    return result["token"], result["user"]


def _resolve_user_info(api: ApiClient, token: str, user_info: dict) -> dict:
    """If user_info has no id, fetch it from /users/me or list_users."""
    if user_info.get("id") is not None:
        return user_info

    # Try /users/me first.
    try:
        import requests

        resp = requests.get(
            f"{config.BASE_URL}/users/me",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        if resp.ok:
            data = resp.json()
            return {
                "id": data["id"],
                "username": data["username"],
                "is_admin": bool(data.get("is_admin", False)),
            }
    except Exception:
        pass

    # Fallback for compatibility: parse raw /users response
    # without requiring all modern fields.
    try:
        import requests

        resp = requests.get(
            f"{config.BASE_URL}/users/",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        if resp.ok and isinstance(resp.json(), list):
            for user in resp.json():
                if user.get("username") == user_info.get("username"):
                    return {
                        "id": user.get("id"),
                        "username": user.get("username", user_info.get("username", "")),
                        "is_admin": bool(user.get("is_admin", False)),
                    }
    except Exception:
        pass

    # Last fallback: typed client list.
    try:
        for user in api.list_users(token):
            if user.username == user_info.get("username"):
                return {
                    "id": user.id,
                    "username": user.username,
                    "is_admin": user.is_admin,
                }
    except Exception:
        pass
    return user_info


def _show_main(app: QApplication, api: ApiClient, token: str, user_info: dict) -> None:
    win = MainWindow(token, user_info, api)
    _keep_window_reference(app, win)

    def on_logout() -> None:
        win.hide()
        new_token, new_user = _do_login(api)
        if new_token is None:
            # Do not terminate abruptly if re-login is canceled.
            # Keep current window visible so the user can continue or retry.
            win.show()
            return
        new_user = _resolve_user_info(api, new_token, new_user)
        config.save_session(
            new_token,
            new_user["id"],
            new_user["username"],
            new_user["is_admin"],
        )
        win.close()
        _show_main(app, api, new_token, new_user)

    win.logout_requested.connect(on_logout)
    win.show()


def _keep_window_reference(app: QApplication, win: MainWindow) -> None:
    # Prevent Python GC from destroying the top-level window unexpectedly.
    windows = getattr(app, "_file_exchanger_windows", None)
    if windows is None:
        windows = []
        setattr(app, "_file_exchanger_windows", windows)
    windows.append(win)

    def _drop_reference(_=None) -> None:
        tracked = getattr(app, "_file_exchanger_windows", [])
        if win in tracked:
            tracked.remove(win)

    win.destroyed.connect(_drop_reference)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        _write_crash_log(exc)
        raise
