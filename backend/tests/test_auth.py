"""Auth — signup, login, current user."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _creds(email="auth@test.com", password="hunter2"):
    return {"email": email, "password": password}


def test_signup_returns_token():
    res = client.post("/api/auth/signup", json=_creds("new@test.com"))
    assert res.status_code == 200
    body = res.json()
    assert body["email"] == "new@test.com"
    assert body["access_token"]


def test_duplicate_signup_conflicts():
    client.post("/api/auth/signup", json=_creds("dup@test.com"))
    res = client.post("/api/auth/signup", json=_creds("dup@test.com"))
    assert res.status_code == 409


def test_login_flow_and_me():
    client.post("/api/auth/signup", json=_creds("login@test.com", "secret123"))

    bad = client.post("/api/auth/login", json=_creds("login@test.com", "wrongpass"))
    assert bad.status_code == 401

    res = client.post("/api/auth/login", json=_creds("login@test.com", "secret123"))
    assert res.status_code == 200
    token = res.json()["access_token"]

    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["email"] == "login@test.com"


def test_me_requires_auth():
    assert client.get("/api/auth/me").status_code == 401


def test_short_password_rejected():
    res = client.post("/api/auth/signup", json={"email": "x@test.com", "password": "123"})
    assert res.status_code == 422
