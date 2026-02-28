import pytest


async def test_login_ok(client, db_session):
    resp = await client.post(
        "/auth/login",
        data={"username": "admin", "password": "admin"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert body["force_change_password"] is True


async def test_login_wrong_password(client):
    resp = await client.post(
        "/auth/login",
        data={"username": "admin", "password": "wrong"},
    )
    assert resp.status_code == 401


async def test_login_unknown_user(client):
    resp = await client.post(
        "/auth/login",
        data={"username": "nobody", "password": "x"},
    )
    assert resp.status_code == 401


async def test_change_password_ok(client, admin_token):
    resp = await client.post(
        "/auth/change-password",
        json={"current_password": "admin", "new_password": "newpass123"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 204


async def test_change_password_wrong_current(client, admin_token):
    resp = await client.post(
        "/auth/change-password",
        json={"current_password": "wrong", "new_password": "newpass123"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 400


async def test_change_password_clears_force_flag(client, admin_token, db_session):
    from models import User

    await client.post(
        "/auth/change-password",
        json={"current_password": "admin", "new_password": "newpass123"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    db_session.expire_all()
    admin = db_session.query(User).filter(User.username == "admin").first()
    assert admin.force_change_password is False


async def test_change_password_unauthenticated(client):
    resp = await client.post(
        "/auth/change-password",
        json={"current_password": "admin", "new_password": "new"},
    )
    assert resp.status_code == 401
