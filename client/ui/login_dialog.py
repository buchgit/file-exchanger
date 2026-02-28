from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QStackedWidget, QVBoxLayout, QWidget,
)

from api import ApiClient, ApiError, ApiWorker


class LoginDialog(QDialog):
    login_successful = pyqtSignal(str, dict)

    def __init__(self, api: ApiClient, parent=None):
        super().__init__(parent)
        self._api = api
        self._workers: list[ApiWorker] = []
        self._token: str | None = None

        self.setWindowTitle("File Exchanger — Login")
        self.setMinimumWidth(360)

        self._stack = QStackedWidget()
        self._stack.addWidget(self._build_login_page())
        self._stack.addWidget(self._build_change_pw_page())

        layout = QVBoxLayout(self)
        layout.addWidget(self._stack)
        self.setLayout(layout)

    # ------------------------------------------------------------------
    # Page builders
    # ------------------------------------------------------------------

    def _build_login_page(self) -> QWidget:
        page = QWidget()
        vbox = QVBoxLayout(page)

        self._username_edit = QLineEdit()
        self._password_edit = QLineEdit()
        self._password_edit.setEchoMode(QLineEdit.EchoMode.Password)

        self._login_btn = QPushButton("Log In")
        self._login_btn.setDefault(True)
        self._login_btn.clicked.connect(self._on_login_clicked)
        self._username_edit.returnPressed.connect(self._on_login_clicked)
        self._password_edit.returnPressed.connect(self._on_login_clicked)

        self._status_label = QLabel("")
        self._status_label.setStyleSheet("color: red;")
        self._status_label.setWordWrap(True)

        vbox.addWidget(QLabel("Username:"))
        vbox.addWidget(self._username_edit)
        vbox.addWidget(QLabel("Password:"))
        vbox.addWidget(self._password_edit)
        vbox.addWidget(self._login_btn)
        vbox.addWidget(self._status_label)
        vbox.addStretch()
        return page

    def _build_change_pw_page(self) -> QWidget:
        page = QWidget()

        info = QLabel("Your password must be changed before continuing.")
        info.setWordWrap(True)

        form = QFormLayout()
        self._current_password_edit = QLineEdit()
        self._current_password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self._new_password_edit = QLineEdit()
        self._new_password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self._confirm_password_edit = QLineEdit()
        self._confirm_password_edit.setEchoMode(QLineEdit.EchoMode.Password)

        form.addRow("Current password:", self._current_password_edit)
        form.addRow("New password:", self._new_password_edit)
        form.addRow("Confirm password:", self._confirm_password_edit)

        self._change_btn = QPushButton("Change Password")
        self._change_btn.clicked.connect(self._on_change_clicked)
        self._confirm_password_edit.returnPressed.connect(self._on_change_clicked)

        self._pw_status_label = QLabel("")
        self._pw_status_label.setStyleSheet("color: red;")
        self._pw_status_label.setWordWrap(True)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(self._change_btn)

        vbox = QVBoxLayout(page)
        vbox.addWidget(info)
        vbox.addLayout(form)
        vbox.addLayout(btn_row)
        vbox.addWidget(self._pw_status_label)
        return page

    # ------------------------------------------------------------------
    # Worker helper
    # ------------------------------------------------------------------

    def _run_worker(self, fn, *args) -> ApiWorker:
        w = ApiWorker(fn, *args)
        self._workers.append(w)
        w.finished.connect(lambda: self._workers.remove(w) if w in self._workers else None)
        return w

    # ------------------------------------------------------------------
    # Login page slots
    # ------------------------------------------------------------------

    def _on_login_clicked(self) -> None:
        username = self._username_edit.text().strip()
        password = self._password_edit.text()
        if not username or not password:
            self._status_label.setText("Username and password are required.")
            return

        self._set_login_enabled(False)
        self._status_label.setText("Logging in…")

        w = self._run_worker(self._api.login, username, password)
        w.result.connect(self._on_login_result)
        w.error.connect(self._on_login_error)
        w.start()

    def _set_login_enabled(self, enabled: bool) -> None:
        self._username_edit.setEnabled(enabled)
        self._password_edit.setEnabled(enabled)
        self._login_btn.setEnabled(enabled)

    def _on_login_result(self, result) -> None:
        self._token = result.access_token
        username = self._username_edit.text().strip()

        if result.force_change_password:
            self._status_label.setText("")
            self._set_login_enabled(True)
            self._stack.setCurrentIndex(1)
        else:
            # We need user info — emit with placeholder; main.py will call get_user
            user_info = {"id": None, "username": username, "is_admin": False}
            self.login_successful.emit(self._token, user_info)
            self.accept()

    def _on_login_error(self, code: int, detail: str) -> None:
        self._set_login_enabled(True)
        self._status_label.setText(f"Error {code}: {detail}" if code else f"Network error: {detail}")

    # ------------------------------------------------------------------
    # Change-password page slots
    # ------------------------------------------------------------------

    def _on_change_clicked(self) -> None:
        current = self._current_password_edit.text()
        new_pw = self._new_password_edit.text()
        confirm = self._confirm_password_edit.text()

        if not current or not new_pw:
            self._pw_status_label.setText("All fields are required.")
            return
        if new_pw != confirm:
            self._pw_status_label.setText("New passwords do not match.")
            return

        self._change_btn.setEnabled(False)
        self._pw_status_label.setText("Changing password…")

        w = self._run_worker(self._api.change_password, self._token, current, new_pw)
        w.result.connect(self._on_change_result)
        w.error.connect(self._on_change_error)
        w.start()

    def _on_change_result(self, _) -> None:
        username = self._username_edit.text().strip()
        user_info = {"id": None, "username": username, "is_admin": False}
        self.login_successful.emit(self._token, user_info)
        self.accept()

    def _on_change_error(self, code: int, detail: str) -> None:
        self._change_btn.setEnabled(True)
        self._pw_status_label.setText(f"Error {code}: {detail}" if code else f"Network error: {detail}")
