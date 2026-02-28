import asyncio
import io

import pytest


@pytest.fixture
def sender_token(regular_user):
    from auth import create_access_token
    return create_access_token({"sub": str(regular_user.id)})


@pytest.fixture
def receiver(db_session):
    from auth import hash_password
    from models import User

    u = User(
        username="receiver",
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


async def _upload(client, sender_token, receiver_id, content=b"hello", filename="test.txt"):
    return await client.post(
        "/files/upload",
        files={"file": (filename, io.BytesIO(content), "application/octet-stream")},
        data={
            "receiver_id": str(receiver_id),
            "original_filename": filename,
            "part_number": "1",
            "total_parts": "1",
        },
        headers={"Authorization": f"Bearer {sender_token}"},
    )


async def test_upload_file(client, sender_token, receiver, tmp_storage):
    resp = await _upload(client, sender_token, receiver.id)
    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == "pending"
    # File must exist on disk
    stored = tmp_storage / body["stored_filename"]
    assert stored.exists()


async def test_upload_creates_directory(client, sender_token, receiver, tmp_storage):
    resp = await _upload(client, sender_token, receiver.id)
    assert resp.status_code == 201
    file_id = resp.json()["id"]
    assert (tmp_storage / str(file_id)).is_dir()


async def test_upload_unknown_receiver(client, sender_token):
    resp = await _upload(client, sender_token, receiver_id=99999)
    assert resp.status_code == 404


async def test_list_pending_as_receiver(client, sender_token, receiver, receiver_token, tmp_storage):
    await _upload(client, sender_token, receiver.id)
    resp = await client.get(
        "/files/pending",
        headers={"Authorization": f"Bearer {receiver_token}"},
    )
    assert resp.status_code == 200
    assert len(resp.json()) == 1


async def test_list_pending_as_sender(client, sender_token, receiver, tmp_storage):
    await _upload(client, sender_token, receiver.id)
    resp = await client.get(
        "/files/pending",
        headers={"Authorization": f"Bearer {sender_token}"},
    )
    assert resp.status_code == 200
    assert resp.json() == []


async def test_download_as_receiver(client, sender_token, receiver, receiver_token, tmp_storage):
    content = b"file content here"
    resp = await _upload(client, sender_token, receiver.id, content=content)
    file_id = resp.json()["id"]

    dl = await client.get(
        f"/files/{file_id}/part/1",
        headers={"Authorization": f"Bearer {receiver_token}"},
    )
    assert dl.status_code == 200
    assert dl.content == content


async def test_download_as_wrong_user(client, sender_token, receiver, tmp_storage):
    resp = await _upload(client, sender_token, receiver.id)
    file_id = resp.json()["id"]

    # sender is not receiver and not admin
    dl = await client.get(
        f"/files/{file_id}/part/1",
        headers={"Authorization": f"Bearer {sender_token}"},
    )
    assert dl.status_code == 403


async def test_download_not_found(client, receiver_token):
    dl = await client.get(
        "/files/99999/part/1",
        headers={"Authorization": f"Bearer {receiver_token}"},
    )
    assert dl.status_code == 404


async def test_ack_marks_delivered(client, sender_token, receiver, receiver_token, tmp_storage, db_session):
    from models import PendingFile

    resp = await _upload(client, sender_token, receiver.id)
    file_id = resp.json()["id"]

    ack = await client.post(
        f"/files/{file_id}/ack",
        headers={"Authorization": f"Bearer {receiver_token}"},
    )
    assert ack.status_code == 204

    db_session.expire_all()
    record = db_session.get(PendingFile, file_id)
    assert record.status == "delivered"


async def test_ack_deletes_disk_file(client, sender_token, receiver, receiver_token, tmp_storage):
    resp = await _upload(client, sender_token, receiver.id)
    file_id = resp.json()["id"]
    dir_path = tmp_storage / str(file_id)
    assert dir_path.exists()

    await client.post(
        f"/files/{file_id}/ack",
        headers={"Authorization": f"Bearer {receiver_token}"},
    )
    # Give background task time to run
    await asyncio.sleep(0.1)
    assert not dir_path.exists()


async def test_ack_wrong_user(client, sender_token, receiver, tmp_storage):
    resp = await _upload(client, sender_token, receiver.id)
    file_id = resp.json()["id"]

    ack = await client.post(
        f"/files/{file_id}/ack",
        headers={"Authorization": f"Bearer {sender_token}"},
    )
    assert ack.status_code == 403


async def test_download_as_admin(client, sender_token, receiver, admin_token, tmp_storage):
    content = b"admin can see this"
    resp = await _upload(client, sender_token, receiver.id, content=content)
    file_id = resp.json()["id"]

    dl = await client.get(
        f"/files/{file_id}/part/1",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert dl.status_code == 200
    assert dl.content == content
