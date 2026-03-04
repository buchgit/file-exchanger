from __future__ import annotations

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QFileDialog, QHBoxLayout, QLabel, QMessageBox,
    QProgressBar, QPushButton, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget, QFrame, QScrollArea, QSizePolicy,
)

from api import ApiClient, ApiError, ApiWorker
from ui.modern_style import MODERN_STYLESHEET


class DownloadWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    error = pyqtSignal(int, str)

    def __init__(self, api: ApiClient, token: str, file_id: int, part_n: int, dest_path: str):
        super().__init__()
        self._api = api
        self._token = token
        self._file_id = file_id
        self._part_n = part_n
        self._dest_path = dest_path

    def run(self) -> None:
        try:
            self._api.download_part(
                self._token,
                self._file_id,
                self._part_n,
                self._dest_path,
                progress_callback=lambda n: self.progress.emit(n),
            )
            self.finished.emit(self._dest_path)
        except ApiError as e:
            self.error.emit(e.status_code, e.detail)
        except Exception as e:
            self.error.emit(0, str(e))


class FileCard(QWidget):
    """Modern card widget for displaying a file"""
    download_clicked = pyqtSignal(int, int, str)
    ack_clicked = pyqtSignal(int)

    def __init__(self, file_data, parent=None):
        super().__init__(parent)
        self._file = file_data
        self._build_ui()

    def _build_ui(self) -> None:
        self.setObjectName("cardWidget")
        self.setStyleSheet("""
            QWidget#cardWidget {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 16px;
            }
            QWidget#cardWidget:hover {
                border: 1px solid #2563eb;
                background-color: #f8fafc;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Header row: filename and status
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)

        # File icon
        file_icon = QLabel("📄")
        file_icon.setStyleSheet("font-size: 24px;")
        header_layout.addWidget(file_icon)

        # File info
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(4)

        filename_label = QLabel(self._file.original_filename)
        filename_label.setStyleSheet("font-weight: 600; font-size: 15px; color: #1e293b;")
        filename_label.setWordWrap(True)

        meta_label = QLabel(
            f"From: User #{self._file.sender_id} • "
            f"Part {self._file.part_number}/{self._file.total_parts} • "
            f"Received: {self._file.created_at[:16].replace('T', ' ')}"
        )
        meta_label.setStyleSheet("font-size: 12px; color: #64748b;")

        info_layout.addWidget(filename_label)
        info_layout.addWidget(meta_label)

        header_layout.addWidget(info_widget, 1)

        layout.addLayout(header_layout)

        # Comment (if exists)
        if self._file.comment:
            comment_label = QLabel(f"💬 {self._file.comment}")
            comment_label.setStyleSheet("font-size: 13px; color: #64748b; background: #f1f5f9; padding: 8px 12px; border-radius: 8px;")
            comment_label.setWordWrap(True)
            layout.addWidget(comment_label)

        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        download_btn = QPushButton("⬇ Download")
        download_btn.setObjectName("downloadBtn")
        download_btn.setFixedHeight(40)
        download_btn.clicked.connect(
            lambda: self.download_clicked.emit(
                self._file.id,
                self._file.part_number,
                self._file.original_filename
            )
        )

        ack_btn = QPushButton("✓ Acknowledge")
        ack_btn.setObjectName("ackBtn")
        ack_btn.setFixedHeight(40)
        ack_btn.clicked.connect(lambda: self.ack_clicked.emit(self._file.id))

        button_layout.addWidget(download_btn)
        button_layout.addWidget(ack_btn)
        button_layout.addStretch()

        layout.addLayout(button_layout)


class InboxWidget(QWidget):
    request_logout = pyqtSignal()

    def __init__(self, api: ApiClient, token: str):
        super().__init__()
        self._api = api
        self._token = token
        self._workers: list = []
        self._download_workers: list[DownloadWorker] = []
        self._file_cards: list[FileCard] = []
        self.setStyleSheet(MODERN_STYLESHEET)

        self._build_ui()
        self._refresh()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # Header
        header_layout = QHBoxLayout()
        header_layout.setSpacing(16)

        title = QLabel("📥 Inbox")
        title.setObjectName("headerLabel")

        self._count_badge = QLabel("0 files")
        self._count_badge.setStyleSheet("""
            background-color: #2563eb;
            color: white;
            padding: 6px 14px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 13px;
        """)

        self._refresh_btn = QPushButton("⟳ Refresh")
        self._refresh_btn.setObjectName("secondaryBtn")
        self._refresh_btn.setFixedHeight(40)
        self._refresh_btn.clicked.connect(self._refresh)

        header_layout.addWidget(title)
        header_layout.addWidget(self._count_badge)
        header_layout.addStretch()
        header_layout.addWidget(self._refresh_btn)

        layout.addLayout(header_layout)

        # Scrollable content area
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setStyleSheet("border: none; background: transparent;")

        self._cards_container = QWidget()
        self._cards_layout = QVBoxLayout(self._cards_container)
        self._cards_layout.setContentsMargins(0, 0, 0, 0)
        self._cards_layout.setSpacing(16)
        self._cards_layout.setAlignment(Qt.AlignTop)

        self._scroll.setWidget(self._cards_container)
        layout.addWidget(self._scroll, 1)

        # Empty state
        self._empty_state = QLabel("📭 No pending files\n\nFiles sent to you will appear here")
        self._empty_state.setObjectName("emptyState")
        self._empty_state.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_state.setStyleSheet("""
            font-size: 16px;
            color: #94a3b8;
            padding: 60px 20px;
        """)
        layout.addWidget(self._empty_state)

        # Status bar at bottom
        self._status_label = QLabel("")
        self._status_label.setObjectName("statusLabel")
        layout.addWidget(self._status_label)

    def _run_worker(self, fn, *args) -> ApiWorker:
        w = ApiWorker(fn, *args)
        self._workers.append(w)
        w.finished.connect(lambda: self._workers.remove(w) if w in self._workers else None)
        return w

    # ------------------------------------------------------------------
    # Refresh
    # ------------------------------------------------------------------

    def _refresh(self) -> None:
        self._refresh_btn.setEnabled(False)
        self._refresh_btn.setText("Loading...")
        w = self._run_worker(self._api.list_pending, self._token)
        w.result.connect(self._on_pending_result)
        w.error.connect(self._on_pending_error)
        w.finished.connect(lambda: self._refresh_btn.setEnabled(True))
        w.finished.connect(lambda: self._refresh_btn.setText("⟳ Refresh"))
        w.start()

    def _on_pending_result(self, files: list) -> None:
        # Clear existing cards
        for card in self._file_cards:
            card.deleteLater()
        self._file_cards.clear()

        self._count_badge.setText(f"{len(files)} file{'s' if len(files) != 1 else ''}")

        if not files:
            self._empty_state.setVisible(True)
            self._scroll.setVisible(False)
            self._status_label.setText("No pending files")
            return

        self._empty_state.setVisible(False)
        self._scroll.setVisible(True)

        for f in files:
            card = FileCard(f)
            card.download_clicked.connect(self._on_download_clicked)
            card.ack_clicked.connect(self._on_ack_clicked)
            self._file_cards.append(card)
            self._cards_layout.addWidget(card)

        self._status_label.setText(f"{len(files)} pending file{'s' if len(files) != 1 else ''}")

    def _on_pending_error(self, code: int, detail: str) -> None:
        if code == 401:
            self.request_logout.emit()
        else:
            self._status_label.setText(f"Error: {detail}")
            self._refresh_btn.setText("⟳ Retry")

    # ------------------------------------------------------------------
    # WS notification
    # ------------------------------------------------------------------

    def _on_new_file_notification(self, data: dict) -> None:
        self._status_label.setText("✨ New file received — refreshing...")
        self._refresh()

    # ------------------------------------------------------------------
    # Download
    # ------------------------------------------------------------------

    def _on_download_clicked(self, file_id: int, part_n: int, filename: str) -> None:
        dest, _ = QFileDialog.getSaveFileName(self, "Save File", filename)
        if not dest:
            return

        self._status_label.setText(f"Downloading: {filename}...")

        worker = DownloadWorker(self._api, self._token, file_id, part_n, dest)
        self._download_workers.append(worker)
        worker.finished.connect(self._on_download_finished)
        worker.error.connect(self._on_download_error)
        worker.finished.connect(
            lambda _: self._download_workers.remove(worker)
            if worker in self._download_workers else None
        )
        worker.error.connect(
            lambda c, d: self._download_workers.remove(worker)
            if worker in self._download_workers else None
        )
        worker.start()

    def _on_download_finished(self, path: str) -> None:
        self._status_label.setText(f"✓ Downloaded to: {path}")
        QMessageBox.information(self, "Download Complete", f"File saved to:\n{path}")

    def _on_download_error(self, code: int, detail: str) -> None:
        if code == 401:
            self.request_logout.emit()
        else:
            self._status_label.setText("Download failed")
            level = QMessageBox.critical if code >= 500 else QMessageBox.warning
            level(self, "Download Error", f"Error {code}: {detail}" if code else detail)

    # ------------------------------------------------------------------
    # Ack
    # ------------------------------------------------------------------

    def _on_ack_clicked(self, file_id: int) -> None:
        reply = QMessageBox.question(
            self,
            "Acknowledge File",
            f"Acknowledge receipt of file ID {file_id}?\n\nThis will mark it as received and remove it from your inbox.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        w = self._run_worker(self._api.ack_file, self._token, file_id)
        w.result.connect(lambda _: self._on_ack_result(file_id))
        w.error.connect(self._on_ack_error)
        w.start()

    def _on_ack_result(self, file_id: int) -> None:
        # Find and remove the card with this file_id
        for i, card in enumerate(self._file_cards):
            if card._file.id == file_id:
                card.deleteLater()
                self._file_cards.pop(i)
                break

        count = len(self._file_cards)
        self._count_badge.setText(f"{count} file{'s' if count != 1 else ''}")

        if count == 0:
            self._empty_state.setVisible(True)
            self._scroll.setVisible(False)

        self._status_label.setText("✓ File acknowledged")

    def _on_ack_error(self, code: int, detail: str) -> None:
        if code == 401:
            self.request_logout.emit()
        else:
            self._status_label.setText("Acknowledgement failed")
            level = QMessageBox.critical if code >= 500 else QMessageBox.warning
            level(self, "Error", f"Error {code}: {detail}" if code else detail)
