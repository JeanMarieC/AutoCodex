"""Manual upload — PDF → process → (embed) → recorded on the car."""

from fastapi.testclient import TestClient

from app.agent.state import Car
from app.auth.security import create_access_token
from app.main import app
from app.rag.sample import generate_sample_pdf

client = TestClient(app)
CAR = Car(make="BMW", model="320i", year="2012")


def _pdf_bytes(tmp_path) -> bytes:
    path = generate_sample_pdf(tmp_path / "u.pdf", CAR, "Owner's Manual", "owner")
    return open(path, "rb").read()


def _form():
    return {"make": CAR.make, "model": CAR.model, "year": CAR.year,
            "name": "Owner's Manual", "kind": "owner"}


def test_upload_processes_and_records(tmp_path):
    pdf = _pdf_bytes(tmp_path)
    res = client.post(
        "/api/manuals/upload",
        data=_form(),
        files={"file": ("manual.pdf", pdf, "application/pdf")},
        headers={"Authorization": f"Bearer {create_access_token('uploader@test')}"},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["chunk_count"] > 0
    assert "indexed your" in body["greeting"]

    # The uploaded manual is recorded on the user's car.
    cars = client.get(
        "/api/cars", headers={"Authorization": f"Bearer {create_access_token('uploader@test')}"}
    ).json()
    assert cars[0]["car_key"] == CAR.id
    assert cars[0]["manuals"][0]["name"] == "Owner's Manual"


def test_upload_rejects_non_pdf(tmp_path):
    res = client.post(
        "/api/manuals/upload",
        data=_form(),
        files={"file": ("note.txt", b"not a pdf", "text/plain")},
    )
    assert res.status_code == 400
