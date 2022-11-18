from app.service import app
from app.ops.user import remove_user, get_user_by_name
from fastapi.testclient import TestClient
from conftest import ASSETS_DIRECTORY

import os

client = TestClient(app)


def test_upload_file(test_wav, auth):
    with open(test_wav, "rb") as f:
        files = {"file": f}
        r = client.post("/audio", files=files, headers=auth)
        assert r.status_code == 200
        assert isinstance(r.json(), int)
