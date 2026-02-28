from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox, QFormLayout, QGroupBox, QHBoxLayout,
    QLabel, QLineEdit, QMessageBox, QPushButton,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

from api import ApiClient, ApiError, ApiWorker


class AdminWidget(QWidget):
    request_logout = pyqtSignal()

    COL_ID = 0
    COL_USERNAME = 1
    COL_ADMIN = 2
    COL_FORCE_PW = 3
    COL_CREATED = 4
    COL_DELETE = 5

    def __init__(self, api: ApiClient, token: str, current_user_id: int):
        super().__init__()
        self._api = api
        self._token = token
        self._current_user_id = current_user_id
        self._workers: list[ApiWorker] = []

        self._build_ui()
        self._refresh_users()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        # ---- Users group ----
        users_group = QGroupBox("Users")
        users_vbox = QVBoxLayout(users_group)

        self._table = QTableWidget(0, 6)
        self._table.setHorizontalHeaderLabels(
            ["ID", "Username", "Admin", "Force PW", "Created", "Delete"]
        )
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.verticalHeader().setVisible(False)
        self._table.horizontalHeader().setStretchLastSection(False)
        users_vbox.addWidget(self._table)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self._refresh_users)
        users_vbox.addWidget(refresh_btn)

        layout.addWidget(users_group)

        # ---- Create User group ----
        create_group = QGroupBox("Create User")
        create_form = QFormLayout(create_group)

        self._new_username = QLineEdit()
        self._new_password = QLineEdit()
        self._new_password.setEchoMode(QLineEdit.EchoMode.Password)
        self._is_admin_check = QCheckBox("Admin")

        create_form.addRow("Username:", self._new_username)
        create_form.addRow("Password:", self._new_password)
        create_form.addRow("", self._is_admin_check)

        self._create_btn = QPushButton("Create")
        self._create_btn.clicked.connect(self._on_create_clicked)
        self._create_status = QLabel("")
        self._create_status.setWordWrap(True)

        create_form.addRow(self._create_btn)
        create_form.addRow(self._create_status)

        layout.addWidget(create_group)

    # ------------------------------------------------------------------
    # Worker helper
    # ------------------------------------------------------------------

    def _run_worker(self, fn, *args) -> ApiWorker:
        w = ApiWorker(fn, *args)
        self._workers.append(w)
        w.finished.connect(lambda: self._workers.remove(w) if w in self._workers else None)
        return w

    # ------------------------------------------------------------------
    # Refresh users
    # ------------------------------------------------------------------

    def _refresh_users(self) -> None:
        w = self._run_worker(self._api.list_users, self._token)
        w.result.connect(self._on_users_result)
        w.error.connect(self._on_users_error)
        w.start()

    def _on_users_result(self, users: list) -> None:
        self._table.setRowCount(0)
        for user in users:
            self._add_user_row(user)
        self._table.resizeColumnsToContents()

    def _on_users_error(self, code: int, detail: str) -> None:
        if code == 401:
            self.request_logout.emit()
        else:
            QMessageBox.warning(self, "Error", f"Failed to load users: {detail}")

    def _add_user_row(self, user) -> None:
        row = self._table.rowCount()
        self._table.insertRow(row)

        self._table.setItem(row, self.COL_ID, QTableWidgetItem(str(user.id)))
        self._table.setItem(row, self.COL_USERNAME, QTableWidgetItem(user.username))
        self._table.setItem(row, self.COL_ADMIN, QTableWidgetItem("Yes" if user.is_admin else "No"))
        self._table.setItem(row, self.COL_FORCE_PW, QTableWidgetItem("Yes" if user.force_change_password else "No"))
        self._table.setItem(row, self.COL_CREATED, QTableWidgetItem(user.created_at[:19]))

        del_btn = QPushButton("Delete")
        if user.id == self._current_user_id:
            del_btn.setEnabled(False)
        else:
            del_btn.clicked.connect(
                lambda checked, uid=user.id, uname=user.username:
                    self._on_delete_clicked(uid, uname)
            )
        self._table.setCellWidget(row, self.COL_DELETE, del_btn)

    # ------------------------------------------------------------------
    # Delete user
    # ------------------------------------------------------------------

    def _on_delete_clicked(self, user_id: int, username: str) -> None:
        reply = QMessageBox.question(
            self,
            "Delete User",
            f"Delete user '{username}'? This cannot be undone.",
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        w = self._run_worker(self._api.delete_user, self._token, user_id)
        w.result.connect(lambda _: self._refresh_users())
        w.error.connect(self._on_delete_error)
        w.start()

    def _on_delete_error(self, code: int, detail: str) -> None:
        if code == 401:
            self.request_logout.emit()
        elif code >= 500:
            QMessageBox.critical(self, "Delete Error", f"Server error: {detail}")
        else:
            QMessageBox.warning(self, "Delete Error", f"Error {code}: {detail}" if code else detail)

    # ------------------------------------------------------------------
    # Create user
    # ------------------------------------------------------------------

    def _on_create_clicked(self) -> None:
        username = self._new_username.text().strip()
        password = self._new_password.text()
        is_admin = self._is_admin_check.isChecked()

        if not username or not password:
            self._create_status.setText("Username and password are required.")
            return

        self._create_btn.setEnabled(False)
        self._create_status.setText("Creating…")

        w = self._run_worker(self._api.create_user, self._token, username, password, is_admin)
        w.result.connect(self._on_create_result)
        w.error.connect(self._on_create_error)
        w.start()

    def _on_create_result(self, user) -> None:
        self._create_btn.setEnabled(True)
        self._create_status.setText(f"User '{user.username}' created (ID {user.id}).")
        self._new_username.clear()
        self._new_password.clear()
        self._is_admin_check.setChecked(False)
        self._refresh_users()

    def _on_create_error(self, code: int, detail: str) -> None:
        self._create_btn.setEnabled(True)
        if code == 401:
            self.request_logout.emit()
        elif code == 409:
            QMessageBox.warning(self, "Conflict", detail)
        elif code >= 500:
            QMessageBox.critical(self, "Create Error", f"Server error: {detail}")
        else:
            msg = f"Error {code}: {detail}" if code else f"Network error: {detail}"
            self._create_status.setText(msg)
