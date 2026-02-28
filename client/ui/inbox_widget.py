from __future__ import annotations

from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QFileDialog, QHBoxLayout, QLabel, QMessageBox,
    QProgressBar, QPushButton, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget,
)

from api import ApiClient, ApiError, ApiWorker


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


class InboxWidget(QWidget):
    request_logout = pyqtSignal()

    # column indices
    COL_ID = 0
    COL_SENDER = 1
    COL_FILENAME = 2
    COL_PARTS = 3
    COL_COMMENT = 4
    COL_RECEIVED = 5
    COL_DOWNLOAD = 6
    COL_ACK = 7

    def __init__(self, api: ApiClient, token: str):
        super().__init__()
        self._api = api
        self._token = token
        self._workers: list = []
        self._download_workers: list[DownloadWorker] = []

        self._build_ui()
        self._refresh()

    def _build_ui(self) -> None:
        # Top bar
        top = QHBoxLayout()
        title = QLabel("<b>Inbox — Pending Files</b>")
        self._refresh_btn = QPushButton("Refresh")
        self._refresh_btn.clicked.connect(self._refresh)
        top.addWidget(title)
        top.addStretch()
        top.addWidget(self._refresh_btn)

        # Table
        self._table = QTableWidget(0, 8)
        self._table.setHorizontalHeaderLabels(
            ["ID", "Sender", "Filename", "Parts", "Comment", "Received", "Download", "Ack"]
        )
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.horizontalHeader().setStretchLastSection(False)
        self._table.verticalHeader().setVisible(False)

        # Bottom
        self._download_progress = QProgressBar()
        self._download_progress.setVisible(False)
        self._status_label = QLabel("")

        layout = QVBoxLayout(self)
        layout.addLayout(top)
        layout.addWidget(self._table)
        layout.addWidget(self._download_progress)
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
        self._status_label.setText("Loading…")
        w = self._run_worker(self._api.list_pending, self._token)
        w.result.connect(self._on_pending_result)
        w.error.connect(self._on_pending_error)
        w.finished.connect(lambda: self._refresh_btn.setEnabled(True))
        w.start()

    def _on_pending_result(self, files: list) -> None:
        self._status_label.setText(f"{len(files)} pending file(s).")
        self._table.setRowCount(0)
        for f in files:
            self._add_row(f)
        self._table.resizeColumnsToContents()

    def _on_pending_error(self, code: int, detail: str) -> None:
        if code == 401:
            self.request_logout.emit()
        else:
            self._status_label.setText(f"Error: {detail}")

    def _add_row(self, f) -> None:
        row = self._table.rowCount()
        self._table.insertRow(row)

        self._table.setItem(row, self.COL_ID, QTableWidgetItem(str(f.id)))
        self._table.setItem(row, self.COL_SENDER, QTableWidgetItem(str(f.sender_id)))
        self._table.setItem(row, self.COL_FILENAME, QTableWidgetItem(f.original_filename))
        self._table.setItem(
            row, self.COL_PARTS,
            QTableWidgetItem(f"{f.part_number}/{f.total_parts}")
        )
        self._table.setItem(row, self.COL_COMMENT, QTableWidgetItem(f.comment or ""))
        self._table.setItem(row, self.COL_RECEIVED, QTableWidgetItem(f.created_at[:19]))

        # Download button
        dl_btn = QPushButton("Download")
        dl_btn.clicked.connect(
            lambda checked, fid=f.id, pn=f.part_number, fn=f.original_filename:
                self._on_download_clicked(fid, pn, fn)
        )
        self._table.setCellWidget(row, self.COL_DOWNLOAD, dl_btn)

        # Ack button
        ack_btn = QPushButton("Acknowledge")
        ack_btn.clicked.connect(
            lambda checked, fid=f.id, r=row: self._on_ack_clicked(fid, r)
        )
        self._table.setCellWidget(row, self.COL_ACK, ack_btn)

    # ------------------------------------------------------------------
    # WS notification
    # ------------------------------------------------------------------

    def _on_new_file_notification(self, data: dict) -> None:
        self._status_label.setText("New file received — refreshing…")
        self._refresh()

    # ------------------------------------------------------------------
    # Download
    # ------------------------------------------------------------------

    def _on_download_clicked(self, file_id: int, part_n: int, filename: str) -> None:
        dest, _ = QFileDialog.getSaveFileName(self, "Save File", filename)
        if not dest:
            return

        self._download_progress.setValue(0)
        self._download_progress.setVisible(True)
        self._download_progress.setRange(0, 0)  # indeterminate until we know size
        self._status_label.setText("Downloading…")

        worker = DownloadWorker(self._api, self._token, file_id, part_n, dest)
        self._download_workers.append(worker)
        worker.progress.connect(lambda n: None)  # could track bytes
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
        self._download_progress.setVisible(False)
        self._status_label.setText(f"Downloaded to: {path}")

    def _on_download_error(self, code: int, detail: str) -> None:
        self._download_progress.setVisible(False)
        if code == 401:
            self.request_logout.emit()
        else:
            level = QMessageBox.critical if code >= 500 else QMessageBox.warning
            level(self, "Download Error", f"Error {code}: {detail}" if code else detail)

    # ------------------------------------------------------------------
    # Ack
    # ------------------------------------------------------------------

    def _on_ack_clicked(self, file_id: int, row: int) -> None:
        reply = QMessageBox.question(
            self,
            "Acknowledge File",
            f"Acknowledge file ID {file_id}? This will mark it as received.",
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        w = self._run_worker(self._api.ack_file, self._token, file_id)
        w.result.connect(lambda _: self._on_ack_result(file_id))
        w.error.connect(self._on_ack_error)
        w.start()

    def _on_ack_result(self, file_id: int) -> None:
        # Find and remove the row with this file_id
        for row in range(self._table.rowCount()):
            item = self._table.item(row, self.COL_ID)
            if item and item.text() == str(file_id):
                self._table.removeRow(row)
                break
        count = self._table.rowCount()
        self._status_label.setText(f"Acknowledged. {count} pending file(s).")

    def _on_ack_error(self, code: int, detail: str) -> None:
        if code == 401:
            self.request_logout.emit()
        else:
            level = QMessageBox.critical if code >= 500 else QMessageBox.warning
            level(self, "Ack Error", f"Error {code}: {detail}" if code else detail)
