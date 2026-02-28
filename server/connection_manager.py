import asyncio
from typing import Dict, Set

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self._connections: Dict[int, Set[WebSocket]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, user_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self._connections.setdefault(user_id, set()).add(websocket)

    async def disconnect(self, user_id: int, websocket: WebSocket) -> None:
        async with self._lock:
            sockets = self._connections.get(user_id, set())
            sockets.discard(websocket)
            if not sockets:
                self._connections.pop(user_id, None)

    async def send_to_user(self, user_id: int, message: dict) -> None:
        async with self._lock:
            sockets = set(self._connections.get(user_id, set()))
        # Send outside the lock to prevent deadlocks
        dead: list[WebSocket] = []
        for ws in sockets:
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        # Clean up dead connections
        if dead:
            async with self._lock:
                bucket = self._connections.get(user_id, set())
                for ws in dead:
                    bucket.discard(ws)
                if not bucket:
                    self._connections.pop(user_id, None)


manager = ConnectionManager()
