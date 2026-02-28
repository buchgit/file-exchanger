from __future__ import annotations

import json
import threading

import websocket
from PyQt6.QtCore import QThread, pyqtSignal

from config import WS_URL, PING_INTERVAL_SEC, WS_RECONNECT_DELAY_SEC


class WsThread(QThread):
    new_file = pyqtSignal(dict)
    connected = pyqtSignal()
    disconnected = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, token: str, ws_url: str = WS_URL):
        super().__init__()
        self._ws_url = ws_url
        self._lock = threading.Lock()
        self._token = token
        self._stop_event = threading.Event()
        self._ws: websocket.WebSocketApp | None = None

    def update_token(self, token: str) -> None:
        with self._lock:
            self._token = token

    def stop(self) -> None:
        self._stop_event.set()
        with self._lock:
            ws = self._ws
        if ws is not None:
            try:
                ws.close()
            except Exception:
                pass

    def run(self) -> None:
        while not self._stop_event.is_set():
            with self._lock:
                token = self._token
            url = f"{self._ws_url}?token={token}"

            wsa = websocket.WebSocketApp(
                url,
                on_open=self._on_open,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close,
            )

            with self._lock:
                self._ws = wsa

            wsa.run_forever(ping_interval=PING_INTERVAL_SEC, ping_timeout=10)

            with self._lock:
                self._ws = None

            if not self._stop_event.is_set():
                self._stop_event.wait(WS_RECONNECT_DELAY_SEC)

    def _on_open(self, ws) -> None:
        self.connected.emit()

    def _on_message(self, ws, msg: str) -> None:
        if msg == "pong":
            return
        try:
            data = json.loads(msg)
        except Exception:
            return
        if data.get("event") == "new_file":
            self.new_file.emit(data)

    def _on_error(self, ws, err) -> None:
        self.error.emit(str(err))

    def _on_close(self, ws, code, msg) -> None:
        self.disconnected.emit()
