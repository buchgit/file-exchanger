"""
File Exchanger - Modern UI Launcher

This launcher uses the new modern card-based interface design
instead of the default glassmorphism style.

Usage:
    python main_modern.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure the client directory is on sys.path
sys.path.insert(0, str(Path(__file__).parent))

from PyQt6.QtWidgets import QApplication, QMessageBox

import config
from api import ApiClient
from ui.login_dialog import LoginDialog
from ui.modern_main_window import MainWindow


def _show_server_config_error() -> None:
    QMessageBox.critical(
        None,
        "Server Address Is Not Configured",
        config.server_config_help_text(),
    )


def main() -> None:
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Clean modern look

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
    dialog.login_successful.connect(
        lambda t, u: result.update(token=t, user=u)
    )
    if not dialog.exec() or not result:
        return None, None
    return result["token"], result["user"]


def _resolve_user_info(api: ApiClient, token: str, user_info: dict) -> dict:
    """If user_info has no id, fetch it from /users/me or list_users."""
    if user_info.get("id") is not None:
        return user_info

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

    try:
        users = api.list_users(token)
        for u in users:
            if u.username == user_info.get("username"):
                return {"id": u.id, "username": u.username, "is_admin": u.is_admin}
    except Exception:
        pass

    return user_info


def _show_main(app: QApplication, api: ApiClient, token: str, user_info: dict) -> None:
    win = MainWindow(token, user_info, api)

    def on_logout() -> None:
        win.hide()
        new_token, new_user = _do_login(api)
        if new_token is None:
            app.quit()
            return
        new_user = _resolve_user_info(api, new_token, new_user)
        config.save_session(
            new_token,
            new_user["id"],
            new_user["username"],
            new_user["is_admin"],
        )
        _show_main(app, api, new_token, new_user)

    win.logout_requested.connect(on_logout)
    win.show()


if __name__ == "__main__":
    main()
