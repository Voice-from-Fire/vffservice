from app.service import app
from app.ops.user import remove_user, get_user_by_name
from fastapi.testclient import TestClient
from app.db.models import AuditLog, EventType

import pytest

client = TestClient(app)


def test_upload_file_and_deletes(test_wav, auth, user, db_session):
    with open(test_wav, "rb") as f:
        files = {
            "file": ("test.wav", f, "application/octet-stream"),
            "name": (None, "xx"),
        }
        r = client.post("/samples", files=files, headers=auth)
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

    r = client.get("/samples", headers=auth)
    assert r.status_code == 200

    samples = r.json()
    assert len(samples) == 1
    assert samples[0]["id"] == sample_id
    assert samples[0]["duration"] == pytest.approx(0.418)
    assert samples[0]["owner"] == user.id

    path = samples[0]["audio_files"][0]["path"]
    r = client.get(f"/audio_files/{path}", headers=auth)
    assert r.status_code == 200
    with open(test_wav, "rb") as f:
        assert r.content == f.read()

    r = client.delete(f"/samples/{sample_id}", headers=auth)
    assert r.status_code == 200

    r = client.get(f"/audio_files/{path}xx", headers=auth)
    assert r.status_code == 404

    r = client.delete(f"/samples/{sample_id}", headers=auth)
    assert r.status_code == 404


def test_next_sample(sample, auth):
    r = client.get(f"/samples/next", headers=auth)
    assert r.status_code == 200
    assert sample == r.json()

    # TODO different result
