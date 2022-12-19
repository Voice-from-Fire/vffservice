from app.service import app
from app.ops.user import remove_user, get_user_by_name
from fastapi.testclient import TestClient

import pytest

client = TestClient(app)


def test_upload_file(test_wav, auth, user):
    with open(test_wav, "rb") as f:
        files = {"file": f}
        r = client.post("/samples", files=files, headers=auth)
        assert r.status_code == 200
        sample_id = r.json()
        assert isinstance(sample_id, int)

    r = client.get("/samples", headers=auth)
    assert r.status_code == 200

    samples = r.json()
    assert len(samples) == 1
    assert samples[0]["id"] == sample_id
    assert samples[0]["duration"] == pytest.approx(0.42)
    assert samples[0]["owner"] == user.id

    r = client.get(f"/samples/{sample_id}/audio", headers=auth)
    assert r.status_code == 200
    with open(test_wav, "rb") as f:
        assert r.content == f.read()


# def test_download_sample(auth, sample):
#     r = client.get(f"/samples/{sample}", headers=auth)
#     assert r.status_code == 200
