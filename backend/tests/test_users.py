from app.service import app, create_user, deactivate_user
from sqlalchemy.orm import Session
from app.ops.user import get_user_by_id, remove_user, get_user_by_name
from app.db.models import AuditLog, EventType, Sample, User, Role
from fastapi.testclient import TestClient
import random
import string
import json
from app.schemas.user import UserCreate
from userutils import UserService

from tests.conftest import auth, db_session, user

client = TestClient(app)


def test_invalid_login(db_session):
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
        assert (
            db_session.query(AuditLog)
            .filter(AuditLog.user == user_id, AuditLog.event == EventType.user_new)
            .count()
            == 1
        )
    finally:
        if user_id is not None:
            remove_user(db_session, user_id)
    assert get_user_by_name(db_session, username) is None
    assert (
        db_session.query(AuditLog)
        .filter(AuditLog.user == user_id, AuditLog.event == EventType.user_deleted)
        .count()
        == 1
    )


def test_deactivate_user_not_auth(db_session, users: UserService, auth):
    user = users.new_user()
    user2 = users.new_user()
    assert user.active

    r = client.patch(
        f"/users/{user.id}/deactivate",
        headers=auth,
    )

    assert r.status_code == 403


def test_deactivate_user_admin(db_session, users: UserService, auth):
    user = users.new_user()
    user2 = users.new_user()
    db_session.add(Sample(owner=user.id, duration=10))
    db_session.add(Sample(owner=user.id, duration=20))
    db_session.add(Sample(owner=user2.id, duration=10))
    db_session.commit()
    assert db_session.query(Sample).filter(Sample.owner == user.id).count() == 2
    _admin, admin_auth = users.new_user(role=Role.admin, auth=True)

    r = client.patch(f"/users/{user.id}/deactivate", headers=admin_auth)

    assert r.status_code == 200
    assert db_session.query(Sample).filter(Sample.owner == user.id).count() == 0
    assert (
        db_session.query(User).filter(User.id == user.id, User.active == False).count()
        == 1
    )
    assert (
        db_session.query(User).filter(User.id == user.id, User.active == True).count()
        == 0
    )
    assert (
        db_session.query(AuditLog)
        .filter(AuditLog.event == EventType.user_deactivated, AuditLog.user == user.id)
        .count()
        == 1
    )

    # deactivation of non-existing user
    r = client.patch(f"/users/{999}/deactivate", headers=admin_auth)
    assert r.status_code == 404

    # admin is deactivated themselves
    r = client.patch(f"/users/{_admin.id}/deactivate", headers=admin_auth)
    assert r.status_code == 403


def test_update_role_by_admin(db_session, users: UserService):
    user = users.new_user()
    assert db_session.query(User).filter(User.role == Role.uploader).count() == 1
    _admin, admin_auth = users.new_user(role=Role.admin, auth=True)
    r = client.patch(
        "/users/role_update", json={"id": user.id, "role": "admin"}, headers=admin_auth
    )
    assert r.status_code == 200
    assert (
        db_session.query(User)
        .filter(User.id == user.id, User.role == Role.admin)
        .count()
        == 1
    )
    assert (
        db_session.query(AuditLog)
        .filter(AuditLog.event == EventType.user_role_updated, AuditLog.user == user.id)
        .count()
        == 1
    )


def test_update_role_admin_itself(db_session, users: UserService):
    _admin, admin_auth = users.new_user(role=Role.admin, auth=True)
    r = client.patch(
        "/users/role_update",
        json={"id": _admin.id, "role": "uploader"},
        headers=admin_auth,
    )
    assert r.status_code == 403


def test_update_role_by_uploader(db_session, users: UserService, auth):
    user = users.new_user()
    r = client.patch(
        "/users/role_update", json={"id": user.id, "role": "admin"}, headers=auth
    )
    assert r.status_code == 403


def test_update_role_not_found(db_session, users: UserService):
    user = users.new_user()
    assert db_session.query(User).filter(User.role == Role.uploader).count() == 1
    _admin, admin_auth = users.new_user(role=Role.admin, auth=True)
    r = client.patch(
        "/users/role_update", json={"id": 999, "role": "admin"}, headers=admin_auth
    )
    assert r.status_code == 404


def test_authaccess(auth):
    r = client.get("/samples")
    assert r.status_code == 401
    r = client.get("/samples", headers=auth)
    assert r.status_code == 200
