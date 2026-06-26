"""Phase 2.6 — persistence: saved cars, manual metadata, per-car chat history.

Runs against the isolated temp SQLite DB from conftest. Each test uses a unique
user email so they don't interfere.
"""

from fastapi.testclient import TestClient

from app.agent.state import Car
from app.auth.security import create_access_token
from app.db import repo
from app.main import app

client = TestClient(app)
CAR = Car(make="Mercedes-Benz", model="C200", year="1998")


def _auth(email: str) -> dict:
    return {"Authorization": f"Bearer {create_access_token(email)}"}


def test_save_car_and_list(tmp_path):
    email = "save-car@test"
    repo.save_car_with_manuals(
        email, CAR, [{"name": "Owner's Manual", "meta": "4 pp · ManualsLib"}]
    )
    cars = repo.list_cars(email)
    assert len(cars) == 1
    assert cars[0]["car_key"] == CAR.id
    assert cars[0]["manuals"][0]["name"] == "Owner's Manual"


def test_resave_replaces_manuals():
    email = "resave@test"
    repo.save_car_with_manuals(email, CAR, [{"name": "Owner's Manual", "meta": "a"}])
    repo.save_car_with_manuals(email, CAR, [{"name": "Workshop Manual", "meta": "b"}])
    cars = repo.list_cars(email)
    assert len(cars) == 1
    assert [m["name"] for m in cars[0]["manuals"]] == ["Workshop Manual"]


def test_chat_history_roundtrip():
    email = "history@test"
    repo.record_chat(email, CAR, "What oil?", "Use 5W-40.",
                     [{"tag": "Owner's Manual", "ref": "p.124"}])
    msgs = repo.list_messages(email, CAR.id)
    assert [m["role"] for m in msgs] == ["user", "assistant"]
    assert msgs[1]["citations"][0]["tag"] == "Owner's Manual"


def test_per_user_isolation():
    repo.save_car_with_manuals("alice@test", CAR, [{"name": "Owner's Manual", "meta": "x"}])
    assert repo.list_cars("bob@test") == []


def test_cars_route_scoped_to_token_user():
    repo.save_car_with_manuals("route@test", CAR, [{"name": "Owner's Manual", "meta": "x"}])
    res = client.get("/api/cars", headers=_auth("route@test"))
    assert res.status_code == 200
    assert res.json()[0]["car_key"] == CAR.id

    # A different (empty) user sees nothing.
    assert client.get("/api/cars", headers=_auth("nobody@test")).json() == []


def test_messages_route():
    email = "msgroute@test"
    repo.record_chat(email, CAR, "Hi", "Hello", None)
    res = client.get(f"/api/cars/{CAR.id}/messages", headers=_auth(email))
    assert res.status_code == 200
    assert len(res.json()) == 2
