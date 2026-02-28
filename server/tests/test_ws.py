import asyncio
import io
import threading

import pytest
from starlette.testclient import TestClient


async def test_connect_valid_token(test_app, admin_token):
    connected = threading.Event()
    error = []

    def _run():
        try:
            with TestClient(test_app) as tc:
                with tc.websocket_connect(f"/ws?token={admin_token}") as ws:
                    connected.set()
        except Exception as e:
            error.append(e)
            connected.set()

    t = threading.Thread(target=_run, daemon=True)
    t.start()
    connected.wait(timeout=5)
    t.join(timeout=2)
    assert not error, f"WS connection failed: {error}"


async def test_connect_no_token(test_app):
    errors = []

    def _run():
        try:
            with TestClient(test_app) as tc:
                with tc.websocket_connect("/ws") as ws:
                    ws.receive_text()
        except Exception as e:
            errors.append(e)

    t = threading.Thread(target=_run, daemon=True)
    t.start()
    t.join(timeout=5)
    assert errors


async def test_connect_invalid_token(test_app):
    errors = []

    def _run():
        try:
            with TestClient(test_app) as tc:
                with tc.websocket_connect("/ws?token=bad.token.here") as ws:
                    ws.receive_text()
        except Exception as e:
            errors.append(e)

    t = threading.Thread(target=_run, daemon=True)
    t.start()
    t.join(timeout=5)
    assert errors


async def test_ping_pong(test_app, admin_token):
    result = []

    def _run():
        try:
            with TestClient(test_app) as tc:
                with tc.websocket_connect(f"/ws?token={admin_token}") as ws:
                    ws.send_text("ping")
                    msg = ws.receive_text()
                    result.append(msg)
        except Exception as e:
            result.append(f"ERROR: {e}")

    t = threading.Thread(target=_run, daemon=True)
    t.start()
    t.join(timeout=5)
    assert result == ["pong"]


async def test_upload_triggers_new_file_notification(
    test_app, sender_token, receiver, receiver_token, tmp_storage
):
    """Upload a file and verify the receiver gets a new_file WS notification.

    Both WS connection and upload use the SAME TestClient so they share one
    event loop — asyncio.create_task in the upload handler fires correctly.
    """
    notification = []
    connected = threading.Event()

    def _run_all():
        with TestClient(test_app) as tc:
            def ws_thread():
                try:
                    with tc.websocket_connect(f"/ws?token={receiver_token}") as ws:
                        connected.set()
                        msg = ws.receive_json()
                        notification.append(msg)
                except Exception as e:
                    notification.append({"error": str(e)})
                    connected.set()

            wst = threading.Thread(target=ws_thread, daemon=True)
            wst.start()
            connected.wait(timeout=5)

            # Upload via the same TestClient (same event loop → task fires correctly)
            tc.post(
                "/files/upload",
                files={"file": ("n.txt", io.BytesIO(b"data"), "application/octet-stream")},
                data={
                    "receiver_id": str(receiver.id),
                    "original_filename": "n.txt",
                    "part_number": "1",
                    "total_parts": "1",
                },
                headers={"Authorization": f"Bearer {sender_token}"},
            )

            wst.join(timeout=5)

    await asyncio.to_thread(_run_all)

    assert notification, "No WS notification received"
    assert notification[0].get("event") == "new_file"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sender_token(regular_user):
    from auth import create_access_token
    return create_access_token({"sub": str(regular_user.id)})


@pytest.fixture
def receiver(db_session):
    from auth import hash_password
    from models import User

    u = User(
        username="ws_receiver",
        password_hash=hash_password("recv"),
        is_admin=False,
        force_change_password=False,
    )
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)
    return u


@pytest.fixture
def receiver_token(receiver):
    from auth import create_access_token
    return create_access_token({"sub": str(receiver.id)})
