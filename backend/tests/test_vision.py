"""Dashboard vision endpoint — VLM mocked, so tests are offline/deterministic."""

from fastapi.testclient import TestClient

from app.api.routes import vision as vision_route
from app.llm import rag
from app.llm.rag import Citation, GroundedAnswer
from app.main import app

client = TestClient(app)

# 1x1 PNG.
_PNG = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4"
    "890000000a49444154789c6360000002000154a24f600000000049454e44ae426082"
)


class _FakeStructured:
    async def ainvoke(self, _messages):
        return GroundedAnswer(
            text="That's the coolant temperature warning — stop and let the engine cool.",
            citations=[Citation(tag="Owner's Manual", ref="Warning Lights")],
        )


def _form():
    return {"make": "Honda", "model": "Civic", "year": "2004"}


def test_dashboard_identifies_and_answers(monkeypatch):
    async def fake_identify(_image):
        return "Red coolant-temperature warning light (thermometer in liquid)."

    monkeypatch.setattr(vision_route, "identify_dashboard", fake_identify)
    monkeypatch.setattr(rag, "llm_available", lambda: True)
    monkeypatch.setattr(rag, "structured_model", lambda _s: _FakeStructured())

    res = client.post(
        "/api/vision/dashboard",
        data=_form(),
        files={"file": ("dash.png", _PNG, "image/png")},
    )
    assert res.status_code == 200
    body = res.json()
    assert "coolant" in body["identification"].lower()
    assert "cool" in body["text"].lower()
    assert body["citations"][0]["tag"] == "Owner's Manual"


def test_dashboard_rejects_non_image():
    res = client.post(
        "/api/vision/dashboard",
        data=_form(),
        files={"file": ("note.txt", b"not an image", "text/plain")},
    )
    assert res.status_code == 400


def test_dashboard_vlm_unavailable_returns_503(monkeypatch):
    async def boom(_image):
        raise RuntimeError("ollama down")

    monkeypatch.setattr(vision_route, "identify_dashboard", boom)
    res = client.post(
        "/api/vision/dashboard",
        data=_form(),
        files={"file": ("dash.png", _PNG, "image/png")},
    )
    assert res.status_code == 503
