from __future__ import annotations

import dataclasses
import os

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox, QFileDialog, QFormLayout, QHBoxLayout,
    QLabel, QLineEdit, QMessageBox, QProgressBar,
    QPushButton, QSpinBox, QTextEdit, QVBoxLayout, QWidget,
    QScrollArea, QFrame,
)

from api import ApiClient, ApiError, ApiWorker
from ui.modern_style import MODERN_STYLESHEET


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
        self.setStyleSheet(MODERN_STYLESHEET)

        self._build_ui()
        self._load_users()

    def showEvent(self, event):
        super().showEvent(event)
        self._load_users()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(24)

        # Header
        title = QLabel("📤 Send File")
        title.setObjectName("headerLabel")
        layout.addWidget(title)

        # Main content card
        card = QWidget()
        card.setObjectName("cardWidget")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 24, 24, 24)
        card_layout.setSpacing(20)

        # Recipient selection
        recipient_group = self._build_recipient_section()
        card_layout.addLayout(recipient_group)

        # File selection
        file_group = self._build_file_section()
        card_layout.addLayout(file_group)

        # Part selection
        part_group = self._build_part_section()
        card_layout.addLayout(part_group)

        # Comment
        comment_group = self._build_comment_section()
        card_layout.addLayout(comment_group)

        # Progress
        self._progress = QProgressBar()
        self._progress.setObjectName("successProgress")
        self._progress.setFixedHeight(8)
        self._progress.setVisible(False)
        card_layout.addWidget(self._progress)

        # Status
        self._status_label = QLabel("")
        self._status_label.setObjectName("statusLabel")
        card_layout.addWidget(self._status_label)

        # Send button
        self._send_btn = QPushButton("📤 Send File")
        self._send_btn.setObjectName("successBtn")
        self._send_btn.setFixedHeight(50)
        self._send_btn.clicked.connect(self._on_send)
        card_layout.addWidget(self._send_btn)

        layout.addWidget(card)
        layout.addStretch()

    def _build_recipient_section(self) -> QVBoxLayout:
        section = QVBoxLayout()
        section.setSpacing(8)

        label = QLabel("Recipient")
        label.setStyleSheet("font-weight: 600; font-size: 14px; color: #1e293b;")

        self._receiver_combo = QComboBox()
        self._receiver_combo.setFixedHeight(44)
        self._receiver_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self._refresh_users_btn = QPushButton("⟳ Refresh")
        self._refresh_users_btn.setObjectName("secondaryBtn")
        self._refresh_users_btn.setFixedHeight(44)
        self._refresh_users_btn.clicked.connect(self._load_users)

        row_layout = QHBoxLayout()
        row_layout.setSpacing(12)
        row_layout.addWidget(self._receiver_combo, 1)
        row_layout.addWidget(self._refresh_users_btn)

        section.addWidget(label)
        section.addLayout(row_layout)

        return section

    def _build_file_section(self) -> QVBoxLayout:
        section = QVBoxLayout()
        section.setSpacing(8)

        label = QLabel("File")
        label.setStyleSheet("font-weight: 600; font-size: 14px; color: #1e293b;")

        self._file_edit = QLineEdit()
        self._file_edit.setReadOnly(True)
        self._file_edit.setFixedHeight(44)
        self._file_edit.setPlaceholderText("No file selected")

        self._browse_btn = QPushButton("📁 Browse")
        self._browse_btn.setObjectName("secondaryBtn")
        self._browse_btn.setFixedHeight(44)
        self._browse_btn.clicked.connect(self._on_browse)

        self._file_size_label = QLabel("")
        self._file_size_label.setStyleSheet("font-size: 13px; color: #64748b;")

        row_layout = QHBoxLayout()
        row_layout.setSpacing(12)
        row_layout.addWidget(self._file_edit, 1)
        row_layout.addWidget(self._browse_btn)

        section.addWidget(label)
        section.addLayout(row_layout)
        section.addWidget(self._file_size_label)

        return section

    def _build_part_section(self) -> QHBoxLayout:
        section = QHBoxLayout()
        section.setSpacing(16)

        # Part number
        part_widget = QWidget()
        part_layout = QVBoxLayout(part_widget)
        part_layout.setContentsMargins(0, 0, 0, 0)
        part_layout.setSpacing(8)

        part_label = QLabel("Part Number")
        part_label.setStyleSheet("font-weight: 600; font-size: 14px; color: #1e293b;")

        self._part_spin = QSpinBox()
        self._part_spin.setMinimum(1)
        self._part_spin.setValue(1)
        self._part_spin.setFixedHeight(44)
        self._part_spin.setStyleSheet("font-size: 14px;")

        part_layout.addWidget(part_label)
        part_layout.addWidget(self._part_spin)

        # Total parts
        total_widget = QWidget()
        total_layout = QVBoxLayout(total_widget)
        total_layout.setContentsMargins(0, 0, 0, 0)
        total_layout.setSpacing(8)

        total_label = QLabel("Total Parts")
        total_label.setStyleSheet("font-weight: 600; font-size: 14px; color: #1e293b;")

        self._total_spin = QSpinBox()
        self._total_spin.setMinimum(1)
        self._total_spin.setValue(1)
        self._total_spin.setFixedHeight(44)
        self._total_spin.setStyleSheet("font-size: 14px;")

        total_layout.addWidget(total_label)
        total_layout.addWidget(self._total_spin)

        self._part_spin.valueChanged.connect(self._sync_part_constraints)
        self._total_spin.valueChanged.connect(self._sync_part_constraints)

        section.addWidget(part_widget)
        section.addWidget(total_widget)
        section.addStretch()

        return section

    def _build_comment_section(self) -> QVBoxLayout:
        section = QVBoxLayout()
        section.setSpacing(8)

        label = QLabel("Comment (optional)")
        label.setStyleSheet("font-weight: 600; font-size: 14px; color: #1e293b;")

        self._comment_edit = QTextEdit()
        self._comment_edit.setMaximumHeight(100)
        self._comment_edit.setPlaceholderText("Add a message to accompany this file...")
        self._comment_edit.setStyleSheet("""
            QTextEdit {
                font-size: 14px;
            }
        """)

        section.addWidget(label)
        section.addWidget(self._comment_edit)

        return section

    def _sync_part_constraints(self) -> None:
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
        self._refresh_users_btn.setEnabled(False)
        w = self._run_worker(self._api.list_users, self._token)
        w.result.connect(self._on_users_result)
        w.error.connect(self._on_users_error)
        w.finished.connect(lambda: self._refresh_users_btn.setEnabled(True))
        w.start()

    def _on_users_result(self, users: list) -> None:
        self._receiver_combo.clear()
        has_users = False
        for user in users:
            if user.id != self._current_user_id:
                self._receiver_combo.addItem(
                    f"👤 {user.username}",
                    userData=user.id
                )
                has_users = True

        if not has_users:
            self._receiver_combo.addItem("No recipients available", userData=None)

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
            self._file_size_label.setText(f"📦 {self._human_size(size)}")
            self._status_label.setText("")

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
            self._status_label.setText("⚠ Please select a file")
            self._status_label.setStyleSheet("color: #f59e0b; font-weight: 500;")
            return

        receiver_id = self._receiver_combo.currentData()
        if receiver_id is None:
            self._status_label.setText("⚠ Please select a recipient")
            self._status_label.setStyleSheet("color: #f59e0b; font-weight: 500;")
            return

        original_filename = os.path.basename(self._selected_file)
        part_number = self._part_spin.value()
        total_parts = self._total_spin.value()
        comment = self._comment_edit.toPlainText().strip()

        self._set_enabled(False)
        self._progress.setRange(0, 0)
        self._progress.setVisible(True)
        self._status_label.setText("Uploading...")
        self._status_label.setStyleSheet("color: #64748b;")

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
        self._refresh_users_btn.setEnabled(enabled)
        self._part_spin.setEnabled(enabled)
        self._total_spin.setEnabled(enabled)
        self._comment_edit.setEnabled(enabled)
        self._browse_btn.setEnabled(enabled)

    def _on_upload_finished(self, result: dict) -> None:
        self._progress.setVisible(False)
        self._set_enabled(True)
        self._status_label.setText(f"✓ Sent successfully! File ID: {result.get('id')}")
        self._status_label.setStyleSheet("color: #10b981; font-weight: 500;")

        # Reset form
        self._file_edit.clear()
        self._file_size_label.clear()
        self._comment_edit.clear()
        self._selected_file = None

    def _on_upload_error(self, code: int, detail: str) -> None:
        self._progress.setVisible(False)
        self._set_enabled(True)
        if code == 401:
            self.request_logout.emit()
        elif code >= 500:
            self._status_label.setText(f"✗ Server error: {detail}")
            self._status_label.setStyleSheet("color: #ef4444; font-weight: 500;")
            QMessageBox.critical(self, "Upload Error", f"Server error: {detail}")
        else:
            msg = f"Error {code}: {detail}" if code else f"Network error: {detail}"
            self._status_label.setText(f"✗ {msg}")
            self._status_label.setStyleSheet("color: #ef4444; font-weight: 500;")
            QMessageBox.warning(self, "Upload Error", msg)
