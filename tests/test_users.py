from app.service import app
from app.ops.user import remove_user, get_user_by_name
from fastapi.testclient import TestClient
import random
import string

client = TestClient(app)


def test_invalid_login():
    r = client.post(
        "/auth/token", json={"username": "non-existent", "password": "pass"}
    )
    assert r.status_code == 422


def test_create_user(db_session):
    password = "".join(random.choice(string.ascii_letters) for i in range(5))
    username = "testusernew" + "".join(
        random.choice(string.ascii_letters) for i in range(5)
    )
    assert get_user_by_name(db_session, username) is None
    r = client.post(
        "/users",
        json={"name": username, "password": password},
    )
    assert r.status_code == 200
    user_id = r.json()["id"]
    try:
        assert isinstance(user_id, int)
        assert r.json()["name"] == username
        assert get_user_by_name(db_session, username).id == user_id
    finally:
        if user_id is not None:
            remove_user(db_session, user_id)
    assert get_user_by_name(db_session, username) is None


def test_no_authaccess():
    r = client.get("/audio")
    assert r.status_code == 401


def test_authaccess(auth):
    r = client.get("/audio", headers=auth)
    assert r.status_code == 200
