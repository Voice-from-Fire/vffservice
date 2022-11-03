from app.service import app
from fastapi.testclient import TestClient


client = TestClient(app)


def test_login():
    r = client.post(
        "/auth/token", json={"username": "non-existent", "password": "pass"}
    )
    raise Exception("TODO")
