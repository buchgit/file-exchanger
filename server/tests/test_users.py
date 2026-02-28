import pytest


async def test_list_users_authenticated(client, user_token):
    resp = await client.get(
        "/users/", headers={"Authorization": f"Bearer {user_token}"}
    )
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


async def test_list_users_unauthenticated(client):
    resp = await client.get("/users/")
    assert resp.status_code == 401


async def test_create_user_as_admin(client, admin_token):
    resp = await client.post(
        "/users/",
        json={"username": "newuser", "password": "pass123"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["username"] == "newuser"
    assert body["force_change_password"] is True


async def test_create_user_duplicate_username(client, admin_token):
    await client.post(
        "/users/",
        json={"username": "dupeuser", "password": "pass"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    resp = await client.post(
        "/users/",
        json={"username": "dupeuser", "password": "pass2"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 409


async def test_create_user_non_admin(client, user_token):
    resp = await client.post(
        "/users/",
        json={"username": "x", "password": "y"},
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert resp.status_code == 403


async def test_get_user_by_id(client, user_token, regular_user):
    resp = await client.get(
        f"/users/{regular_user.id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["username"] == regular_user.username


async def test_get_user_not_found(client, user_token):
    resp = await client.get(
        "/users/99999",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert resp.status_code == 404


async def test_delete_user_as_admin(client, admin_token, regular_user):
    resp = await client.delete(
        f"/users/{regular_user.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 204


async def test_delete_self(client, admin_token, db_session):
    from models import User

    admin = db_session.query(User).filter(User.is_admin == True).first()
    resp = await client.delete(
        f"/users/{admin.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 400


async def test_delete_non_admin(client, user_token, db_session):
    from models import User

    admin = db_session.query(User).filter(User.is_admin == True).first()
    resp = await client.delete(
        f"/users/{admin.id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert resp.status_code == 403
