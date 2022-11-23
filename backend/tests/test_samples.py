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
        assert isinstance(r.json(), int)

    r = client.get("/samples", headers=auth)
    assert r.status_code == 200

    samples = r.json()
    assert len(samples) == 1
    assert samples[0]["duration"] == pytest.approx(0.42)
    assert samples[0]["owner"] == user.id


# def test_download_sample(auth, sample):
#     r = client.get(f"/samples/{sample}", headers=auth)
#     assert r.status_code == 200
