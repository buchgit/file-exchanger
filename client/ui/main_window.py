from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QHBoxLayout, QLabel, QLineEdit,
    QMainWindow, QMenuBar, QMessageBox, QPushButton,
    QStatusBar, QTabWidget, QVBoxLayout, QWidget,
)

from api import ApiClient, ApiWorker
import config
from ui.inbox_widget import InboxWidget
from ui.send_widget import SendWidget
from ui.admin_widget import AdminWidget
from ws_thread import WsThread


class MainWindow(QMainWindow):
    logout_requested = pyqtSignal()

    def __init__(self, token: str, user_info: dict, api_client: ApiClient):
        super().__init__()
        self._token = token
        self._user_info = user_info
        self._api = api_client
        self._ws: WsThread | None = None
        self._workers: list[ApiWorker] = []

        self.setWindowTitle(f"File Exchanger — {user_info['username']}")
        self.setMinimumSize(800, 500)

        self._build_ui()
        self._build_menu()
        self._start_ws()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        self._tabs = QTabWidget()

        self._inbox = InboxWidget(self._api, self._token)
        self._inbox.request_logout.connect(self._handle_401)

        self._send = SendWidget(self._api, self._token, self._user_info.get("id", 0))
        self._send.request_logout.connect(self._handle_401)

        self._tabs.addTab(self._inbox, "Inbox")
        self._tabs.addTab(self._send, "Send")

        if self._user_info.get("is_admin"):
            self._admin = AdminWidget(self._api, self._token, self._user_info.get("id", 0))
            self._admin.request_logout.connect(self._handle_401)
            self._tabs.addTab(self._admin, "Admin")
        else:
            self._admin = None

        self.setCentralWidget(self._tabs)

        # Status bar
        self._ws_status_label = QLabel("WS: connecting…")
        status_bar = QStatusBar()
        status_bar.addPermanentWidget(self._ws_status_label)
        self.setStatusBar(status_bar)

    def _build_menu(self) -> None:
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")

        change_pw_action = file_menu.addAction("Change Password")
        change_pw_action.triggered.connect(self._on_change_password)

        file_menu.addSeparator()

        logout_action = file_menu.addAction("Log Out")
        logout_action.triggered.connect(self._on_logout)

        quit_action = file_menu.addAction("Quit")
        quit_action.triggered.connect(self._on_quit)

    # ------------------------------------------------------------------
    # WebSocket
    # ------------------------------------------------------------------

    def _start_ws(self) -> None:
        self._ws = WsThread(self._token)
        self._ws.new_file.connect(self._on_new_file)
        self._ws.connected.connect(lambda: self._ws_status_label.setText("WS: connected"))
        self._ws.disconnected.connect(lambda: self._ws_status_label.setText("WS: reconnecting…"))
        self._ws.error.connect(lambda msg: self._ws_status_label.setText(f"WS: {msg[:60]}"))
        self._ws.start()

    def _stop_ws(self) -> None:
        if self._ws is not None:
            self._ws.stop()
            self._ws = None

    def _on_new_file(self, data: dict) -> None:
        self._inbox._on_new_file_notification(data)

    # ------------------------------------------------------------------
    # Menu slots
    # ------------------------------------------------------------------

    def _on_change_password(self) -> None:
        dlg = _ChangePasswordDialog(self._api, self._token, parent=self)
        dlg.exec()

    def _on_logout(self) -> None:
        self._stop_ws()
        config.clear_session()
        self.hide()
        self.logout_requested.emit()

    def _on_quit(self) -> None:
        self._stop_ws()
        from PyQt6.QtWidgets import QApplication
        QApplication.quit()

    # ------------------------------------------------------------------
    # 401 handler
    # ------------------------------------------------------------------

    def _handle_401(self) -> None:
        self._stop_ws()
        config.clear_session()
        self.hide()
        self.logout_requested.emit()

    # ------------------------------------------------------------------
    # Close event
    # ------------------------------------------------------------------

    def closeEvent(self, event) -> None:
        if self._ws is not None:
            self._ws.stop()
            self._ws.wait(3000)
        event.accept()


# ---------------------------------------------------------------------------
# Change-password dialog (used from menu)
# ---------------------------------------------------------------------------

class _ChangePasswordDialog(QDialog):
    def __init__(self, api: ApiClient, token: str, parent=None):
        super().__init__(parent)
        self._api = api
        self._token = token
        self._workers: list = []

        self.setWindowTitle("Change Password")
        self.setMinimumWidth(320)

        form = QFormLayout()
        self._current = QLineEdit()
        self._current.setEchoMode(QLineEdit.EchoMode.Password)
        self._new_pw = QLineEdit()
        self._new_pw.setEchoMode(QLineEdit.EchoMode.Password)
        self._confirm = QLineEdit()
        self._confirm.setEchoMode(QLineEdit.EchoMode.Password)
        form.addRow("Current:", self._current)
        form.addRow("New:", self._new_pw)
        form.addRow("Confirm:", self._confirm)

        self._btn = QPushButton("Change")
        self._btn.clicked.connect(self._on_change)
        self._status = QLabel("")
        self._status.setWordWrap(True)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(self._btn)

        vbox = QVBoxLayout(self)
        vbox.addLayout(form)
        vbox.addLayout(btn_row)
        vbox.addWidget(self._status)

    def _on_change(self) -> None:
        current = self._current.text()
        new_pw = self._new_pw.text()
        confirm = self._confirm.text()
        if not current or not new_pw:
            self._status.setText("All fields are required.")
            return
        if new_pw != confirm:
            self._status.setText("New passwords do not match.")
            return

        self._btn.setEnabled(False)
        self._status.setText("Changing…")

        w = ApiWorker(self._api.change_password, self._token, current, new_pw)
        self._workers.append(w)
        w.result.connect(self._on_result)
        w.error.connect(self._on_error)
        w.finished.connect(lambda: self._workers.remove(w) if w in self._workers else None)
        w.start()

    def _on_result(self, _) -> None:
        QMessageBox.information(self, "Success", "Password changed successfully.")
        self.accept()

    def _on_error(self, code: int, detail: str) -> None:
        self._btn.setEnabled(True)
        self._status.setText(f"Error {code}: {detail}" if code else f"Network error: {detail}")
