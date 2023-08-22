import datetime

import pytest
from fastapi.testclient import TestClient

from app.db.models import AuditLog, EventType, Label, User
from app.service import app

client = TestClient(app)


def test_upload_file_and_deletes(test_wav, auth, user, db_session):
    with open(test_wav, "rb") as f:
        files = {
            "file": ("test.wav", f, "application/octet-stream"),
            "name": (None, "xx"),
            "language": (None, "en"),
        }
        r = client.post(
            "/samples",
            files=files,
            headers=auth,
        )
        print(r.text)
        assert r.status_code == 200
        sample_id = r.json()
        assert isinstance(sample_id, int)
        assert (
            db_session.query(AuditLog)
            .filter(
                AuditLog.sample == sample_id, AuditLog.event == EventType.sample_new
            )
            .count()
            == 1
        )

        # label
        r = client.post(
            f"/samples/{sample_id}/label",
            json={"status": "ok", "values": [{"label_type": "g", "label_value": 20}]},
            headers=auth,
        )
        assert db_session.query(Label).filter(Label.sample == sample_id).count() == 1

    r = client.get("/samples", headers=auth)
    assert r.status_code == 200

    samples = r.json()
    assert len(samples) == 1
    assert samples[0]["id"] == sample_id
    assert samples[0]["duration"] == pytest.approx(0.418)
    assert samples[0]["owner"] == user.id
    assert samples[0]["language"] == "en"

    r = client.get(f"/sample/{sample_id}/audio", headers=auth)
    assert r.status_code == 200
    assert r.headers["content-type"] == "audio/wav"
    with open(test_wav, "rb") as f:
        assert r.content == f.read()

    r = client.get(f"/sample/{sample_id}/mp3", headers=auth)
    assert r.status_code == 200
    assert r.headers["content-type"] == "audio/mp3"
    assert r.content[:3] == b"ID3"

    r = client.delete(f"/samples/{sample_id}", headers=auth)
    assert r.status_code == 200
    assert db_session.query(Label).filter(Label.sample == sample_id).count() == 0

    r = client.get(f"/sample/{sample_id * 100}/audio", headers=auth)
    assert r.status_code == 404

    r = client.delete(f"/samples/{sample_id}", headers=auth)
    assert r.status_code == 404


def test_next_sample(sample, auth):
    r = client.get("/samples/next", headers=auth)
    assert r.status_code == 200
    r = r.json()
    assert sample == r["id"]
    assert r["duration"] == pytest.approx(0.418)
    assert r["created_at"] is None
    assert r["owner"] is None

    # TODO different result


def test_get_sample(sample: int, user: User, auth):
    r = client.get(f"/samples/{sample}", headers=auth)
    r.raise_for_status()
    r = r.json()
    assert sample == r["id"]
    assert r["duration"] == pytest.approx(0.418)
    assert r["owner"] is user.id
    date = datetime.datetime.fromisoformat(r["created_at"])
    assert (datetime.datetime.utcnow() - date).total_seconds() < 5


def test_get_sample_missing(auth):
    r = client.get("/samples/123456789", headers=auth)
    assert r.status_code == 404
