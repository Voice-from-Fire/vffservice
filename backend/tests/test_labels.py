from itertools import count
import json
from sqlalchemy import null
from sqlalchemy.orm import Session
from app.service import app
from fastapi.testclient import TestClient

from app.db.models import (
    AudioStatus,
    AuditLog,
    Label,
    LabelType,
    LabelValue,
    Language,
    Role,
    Sample,
    EventType,
)
from app.ops import labels
from app.schemas.user import User
from app.schemas.labels import LabelCreate
from tests.userutils import UserService


client = TestClient(app)

sample_id: int = 888
label_id: int = 999
final_result = {
    "status": "ok",
    "id": 999,
    "creator": 10,
    "sample": 888,
    "values": [{"label_type": "g", "label_value": 10}],
}


def test_is_owner(db_session: Session, auth, users: UserService):
    user: User = users.new_user()
    fill_data(db_session, user.id)

    assert labels.is_owner(db_session, user, sample_id)


def test_get_labels_for_sample_admin(db_session: Session, users: UserService):
    _admin, admin_auth = users.new_user(role=Role.admin, auth=True)
    fill_data(db_session, _admin.id)

    r = client.get(f"/samples/{sample_id}/labels", headers=admin_auth)

    assert r.status_code == 200
    result = r.json()

    assert len(result) == 1
    result = result[0]

    assert isinstance(result["created_at"], str)
    del result["created_at"]

    assert result == final_result


def test_get_labels_for_sample_user(db_session: Session, users: UserService):
    _user, user_auth = users.new_user(role=Role.user, auth=True)
    fill_data(db_session, _user.id)

    r = client.get(f"/samples/{sample_id}/labels", headers=user_auth)

    assert r.status_code == 200
    result = r.json()

    assert len(result) == 1
    result = result[0]

    assert isinstance(result["created_at"], str)
    del result["created_at"]

    assert result == final_result


def test_get_labels_for_sample_unauthorized(
    db_session: Session, auth, users: UserService
):
    user: User = users.new_user()
    fill_data(db_session, user.id)

    r = client.get(f"/samples/{sample_id}/labels", headers=auth)

    assert r.status_code == 403


def test_create_label_and_duplicate_label(
    db_session: Session, auth, users: UserService
):
    assert db_session.query(Label).filter(Label.status == AudioStatus.ok).count() == 0
    user: User = users.new_user()
    db_session.add(
        Sample(id=sample_id, owner=user.id, duration=10, language=Language.en)
    )
    db_session.commit()
    r = client.post(
        f"/samples/{sample_id}/label",
        json={"status": "ok", "values": [{"label_type": "g", "label_value": 20}]},
        headers=auth,
    )

    assert r.status_code == 200
    assert db_session.query(Label).filter(Label.status == AudioStatus.ok).count() == 1
    label: Label = db_session.query(Label).filter(Label.status == AudioStatus.ok).one()
    assert r.text == str(label.id)
    assert (
        db_session.query(AuditLog)
        .filter(AuditLog.label == label.id, AuditLog.event == EventType.label_new)
        .count()
        == 1
    )

    # duplicate label
    r = client.post(
        f"/samples/{sample_id}/label",
        json={"status": "ok", "values": [{"label_type": "g", "label_value": 20}]},
        headers=auth,
    )
    assert r.status_code == 400


def test_delete_labels_for_sample(db_session: Session, auth, users: UserService):
    user: User = users.new_user()
    user2: User = users.new_user()
    sample2_id: int = 800
    fill_data(db_session, user.id)
    fill_data(db_session, user.id, sample2_id, 900)
    db_session.add(create_label(user2.id, sample2_id, 801))
    db_session.commit()
    assert db_session.query(Label).filter(Label.status == AudioStatus.ok).count() == 3

    labels.delete_labels_for_sample(db_session, sample2_id)

    assert db_session.query(Label).filter(Label.sample == sample2_id).count() == 0
    assert db_session.query(Label).filter(Label.sample == sample_id).count() == 1


def fill_data(
    db_session, user_id: int, sample_id: int = sample_id, label_id: int = label_id
):
    db_session.add(
        Sample(id=sample_id, owner=user_id, duration=10, language=Language.cs)
    )
    db_session.commit()
    db_session.add(create_label(user_id, sample_id, label_id))
    db_session.commit()


def create_label(
    user_id: int, sample_id: int = sample_id, label_id: int = label_id
) -> Label:
    return Label(
        id=label_id,
        creator=user_id,
        sample=sample_id,
        status=AudioStatus.ok,
        values=[LabelValue(label_type=LabelType.gender, label_value=10)],
    )
