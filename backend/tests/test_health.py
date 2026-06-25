from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health() -> None:
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok", "version": "0.1.0"}


def test_root() -> None:
    res = client.get("/api")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"
