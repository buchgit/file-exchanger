from __future__ import annotations

import dataclasses
import os

from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox, QFileDialog, QFormLayout, QHBoxLayout,
    QLabel, QLineEdit, QMessageBox, QProgressBar,
    QPushButton, QSpinBox, QTextEdit, QVBoxLayout, QWidget,
)

from api import ApiClient, ApiError, ApiWorker


class UploadWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(dict)
    error = pyqtSignal(int, str)

    def __init__(
        self,
        api: ApiClient,
        token: str,
        file_path: str,
        receiver_id: int,
        original_filename: str,
        part_number: int,
        total_parts: int,
        comment: str,
    ):
        super().__init__()
        self._api = api
        self._token = token
        self._file_path = file_path
        self._receiver_id = receiver_id
        self._original_filename = original_filename
        self._part_number = part_number
        self._total_parts = total_parts
        self._comment = comment

    def run(self) -> None:
        try:
            result = self._api.upload_part(
                self._token,
                self._file_path,
                self._receiver_id,
                self._original_filename,
                self._part_number,
                self._total_parts,
                self._comment,
                progress_callback=lambda n: self.progress.emit(n),
            )
            self.finished.emit(dataclasses.asdict(result))
        except ApiError as e:
            self.error.emit(e.status_code, e.detail)
        except Exception as e:
            self.error.emit(0, str(e))


class SendWidget(QWidget):
    request_logout = pyqtSignal()

    def __init__(self, api: ApiClient, token: str, current_user_id: int):
        super().__init__()
        self._api = api
        self._token = token
        self._current_user_id = current_user_id
        self._workers: list = []
        self._upload_workers: list[UploadWorker] = []
        self._selected_file: str | None = None

        self._build_ui()
        self._load_users()

    def showEvent(self, event):
        super().showEvent(event)
        self._load_users()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        # To: combobox + refresh
        self._receiver_combo = QComboBox()
        self._refresh_users_btn = QPushButton("↻")
        self._refresh_users_btn.setFixedWidth(28)
        self._refresh_users_btn.setToolTip("Refresh user list")
        self._refresh_users_btn.clicked.connect(self._load_users)
        to_row = QWidget(self)
        to_layout = QHBoxLayout(to_row)
        to_layout.setContentsMargins(0, 0, 0, 0)
        to_layout.addWidget(self._receiver_combo)
        to_layout.addWidget(self._refresh_users_btn)

        # File picker
        self._file_edit = QLineEdit()
        self._file_edit.setReadOnly(True)
        self._file_edit.setPlaceholderText("No file selected")
        self._browse_btn = QPushButton("Browse…")
        self._browse_btn.clicked.connect(self._on_browse)
        file_row = QWidget(self)
        file_layout = QHBoxLayout(file_row)
        file_layout.setContentsMargins(0, 0, 0, 0)
        file_layout.addWidget(self._file_edit)
        file_layout.addWidget(self._browse_btn)

        # Part number
        self._part_spin = QSpinBox()
        self._part_spin.setMinimum(1)
        self._part_spin.setValue(1)
        self._total_spin = QSpinBox()
        self._total_spin.setMinimum(1)
        self._total_spin.setValue(1)
        self._part_spin.valueChanged.connect(self._sync_part_constraints)
        self._total_spin.valueChanged.connect(self._sync_part_constraints)
        part_row = QWidget(self)
        part_layout = QHBoxLayout(part_row)
        part_layout.setContentsMargins(0, 0, 0, 0)
        part_layout.addWidget(self._part_spin)
        part_layout.addWidget(QLabel("of"))
        part_layout.addWidget(self._total_spin)
        part_layout.addStretch()

        # Comment
        self._comment_edit = QTextEdit()
        self._comment_edit.setMaximumHeight(80)
        self._comment_edit.setPlaceholderText("Optional comment…")

        # Send button + progress + status
        self._send_btn = QPushButton("Send")
        self._send_btn.clicked.connect(self._on_send)
        self._progress = QProgressBar()
        self._progress.setVisible(False)
        self._file_size_label = QLabel("")
        self._status_label = QLabel("")

        layout.addWidget(QLabel("To:"))
        layout.addWidget(to_row)
        layout.addWidget(QLabel("File:"))
        layout.addWidget(file_row)
        layout.addWidget(QLabel("Part:"))
        layout.addWidget(part_row)
        layout.addWidget(QLabel("Comment:"))
        layout.addWidget(self._comment_edit)
        layout.addWidget(self._send_btn)
        layout.addWidget(self._progress)
        layout.addWidget(self._file_size_label)
        layout.addWidget(self._status_label)
        layout.addStretch()

    def _sync_part_constraints(self) -> None:
        # part_number cannot exceed total_parts
        total = self._total_spin.value()
        if self._part_spin.value() > total:
            self._part_spin.setValue(total)
        self._part_spin.setMaximum(total)

    # ------------------------------------------------------------------
    # Load users
    # ------------------------------------------------------------------

    def _run_worker(self, fn, *args) -> ApiWorker:
        w = ApiWorker(fn, *args)
        self._workers.append(w)
        w.finished.connect(lambda: self._workers.remove(w) if w in self._workers else None)
        return w

    def _load_users(self) -> None:
        w = self._run_worker(self._api.list_users, self._token)
        w.result.connect(self._on_users_result)
        w.error.connect(self._on_users_error)
        w.start()

    def _on_users_result(self, users: list) -> None:
        self._receiver_combo.clear()
        for user in users:
            if user.id != self._current_user_id:
                self._receiver_combo.addItem(user.username, userData=user.id)

    def _on_users_error(self, code: int, detail: str) -> None:
        if code == 401:
            self.request_logout.emit()
        else:
            self._status_label.setText(f"Failed to load users: {detail}")

    # ------------------------------------------------------------------
    # Browse
    # ------------------------------------------------------------------

    def _on_browse(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Select File")
        if path:
            self._selected_file = path
            self._file_edit.setText(path)
            size = os.path.getsize(path)
            self._file_size_label.setText(f"Size: {self._human_size(size)}")

    def _human_size(self, size: int) -> str:
        for unit in ("B", "KB", "MB", "GB"):
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    # ------------------------------------------------------------------
    # Send
    # ------------------------------------------------------------------

    def _on_send(self) -> None:
        if not self._selected_file:
            self._status_label.setText("Please select a file.")
            return
        if self._receiver_combo.count() == 0:
            self._status_label.setText("No recipients available.")
            return

        receiver_id = self._receiver_combo.currentData()
        if receiver_id is None:
            self._status_label.setText("Please select a recipient.")
            return

        original_filename = os.path.basename(self._selected_file)
        part_number = self._part_spin.value()
        total_parts = self._total_spin.value()
        comment = self._comment_edit.toPlainText().strip()

        self._set_enabled(False)
        self._progress.setRange(0, 0)
        self._progress.setVisible(True)
        self._status_label.setText("Uploading…")

        worker = UploadWorker(
            self._api,
            self._token,
            self._selected_file,
            receiver_id,
            original_filename,
            part_number,
            total_parts,
            comment,
        )
        self._upload_workers.append(worker)
        worker.progress.connect(lambda n: None)
        worker.finished.connect(self._on_upload_finished)
        worker.error.connect(self._on_upload_error)
        worker.finished.connect(
            lambda _: self._upload_workers.remove(worker)
            if worker in self._upload_workers else None
        )
        worker.error.connect(
            lambda c, d: self._upload_workers.remove(worker)
            if worker in self._upload_workers else None
        )
        worker.start()

    def _set_enabled(self, enabled: bool) -> None:
        self._send_btn.setEnabled(enabled)
        self._receiver_combo.setEnabled(enabled)
        self._part_spin.setEnabled(enabled)
        self._total_spin.setEnabled(enabled)
        self._comment_edit.setEnabled(enabled)

    def _on_upload_finished(self, result: dict) -> None:
        self._progress.setVisible(False)
        self._set_enabled(True)
        self._status_label.setText(
            f"Sent successfully! File ID: {result.get('id')}"
        )

    def _on_upload_error(self, code: int, detail: str) -> None:
        self._progress.setVisible(False)
        self._set_enabled(True)
        if code == 401:
            self.request_logout.emit()
        elif code >= 500:
            QMessageBox.critical(self, "Upload Error", f"Server error: {detail}")
        else:
            msg = f"Error {code}: {detail}" if code else f"Network error: {detail}"
            QMessageBox.warning(self, "Upload Error", msg)
        self._status_label.setText("Upload failed.")
