"""Phase 2.2 — RAG answers + vehicle identification (provider-agnostic).

The model is always mocked or forced-unavailable, so tests are deterministic and
never call a real provider (Gemini or Ollama).
"""

from fastapi.testclient import TestClient

from app.agent.state import Car
from app.llm import rag, vehicle
from app.llm.rag import Citation, GroundedAnswer, answer_question
from app.llm.vehicle import identify_vehicle
from app.main import app

CAR = Car(make="Mercedes-Benz", model="C200", year="1998")
client = TestClient(app)

_ANSWER = GroundedAnswer(
    text="Use SAE 5W-40 fully synthetic.",
    citations=[Citation(tag="Owner's Manual", ref="p.124")],
)


class _FakeStructured:
    """Stands in for a model bound via structured_model()."""

    def __init__(self, result):
        self._result = result

    async def ainvoke(self, _messages):
        return self._result

    def invoke(self, _messages):
        return self._result


class _FakeChat:
    """Plain chat model (used by vehicle identification)."""

    async def ainvoke(self, _messages):
        class _R:
            content = "Identified Mercedes-Benz C200 · W202, M111 engine"

        return _R()


# ── answer_question ──────────────────────────────────────────────────


async def test_answer_fallback_when_unavailable(monkeypatch):
    monkeypatch.setattr(rag, "llm_available", lambda: False)
    ans = await answer_question(CAR, "What oil does it take?")
    assert "isn't configured" in ans.text or "GOOGLE_API_KEY" in ans.text
    assert ans.citations == []


async def test_answer_uses_model_when_available(monkeypatch):
    monkeypatch.setattr(rag, "llm_available", lambda: True)
    monkeypatch.setattr(rag, "structured_model", lambda _schema: _FakeStructured(_ANSWER))
    ans = await answer_question(CAR, "What oil does it take?")
    assert "5W-40" in ans.text
    assert ans.citations[0].tag == "Owner's Manual"


# ── identify_vehicle ─────────────────────────────────────────────────


async def test_identify_vehicle_fallback(monkeypatch):
    monkeypatch.setattr(vehicle, "llm_available", lambda: False)
    assert await identify_vehicle(CAR) == "Identified Mercedes-Benz C200 · 1998"


async def test_identify_vehicle_uses_model(monkeypatch):
    monkeypatch.setattr(vehicle, "llm_available", lambda: True)
    monkeypatch.setattr(vehicle, "get_chat_model", lambda: _FakeChat())
    line = await identify_vehicle(CAR)
    assert line.startswith("Identified") and "W202" in line


# ── /api/chat route ──────────────────────────────────────────────────


def test_chat_route_fallback(monkeypatch):
    monkeypatch.setattr(rag, "llm_available", lambda: False)
    res = client.post("/api/chat", json={"car": CAR.model_dump(), "message": "What oil?"})
    assert res.status_code == 200
    assert res.json()["citations"] is None


def test_chat_route_with_model(monkeypatch):
    monkeypatch.setattr(rag, "llm_available", lambda: True)
    monkeypatch.setattr(rag, "structured_model", lambda _schema: _FakeStructured(_ANSWER))
    res = client.post("/api/chat", json={"car": CAR.model_dump(), "message": "What oil?"})
    assert res.status_code == 200
    assert "5W-40" in res.json()["text"]
    assert res.json()["citations"][0]["tag"] == "Owner's Manual"
