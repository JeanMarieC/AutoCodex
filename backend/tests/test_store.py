"""Phase 2.5 — vector store index/retrieve + the closed RAG loop in chat.

Uses an in-memory Chroma client and deterministic fake embeddings, so tests are
offline and never call the embeddings API.
"""

import chromadb
import pytest
from chromadb.config import Settings as ChromaSettings
from fastapi.testclient import TestClient
from langchain_core.embeddings import DeterministicFakeEmbedding

from app.agent.state import Car
from app.api.routes import chat as chat_route
from app.llm import rag
from app.llm.rag import Citation, ContextChunk, GroundedAnswer
from app.main import app
from app.rag import store
from app.rag.models import Chunk

CAR_A = Car(make="Mercedes-Benz", model="C200", year="1998")
CAR_B = Car(make="BMW", model="320i", year="2012")
client = TestClient(app)


@pytest.fixture
def vstore(monkeypatch):
    chroma = chromadb.EphemeralClient(ChromaSettings(anonymized_telemetry=False))
    monkeypatch.setattr(store, "_client", lambda: chroma)
    monkeypatch.setattr(store, "_embeddings", lambda: DeterministicFakeEmbedding(size=64))
    monkeypatch.setattr(store, "embeddings_available", lambda: True)
    return chroma


def _chunks() -> list[Chunk]:
    rows = [
        ("Use SAE 5W-40 fully synthetic oil; capacity 5.5 litres.", "Engine Oil", 124),
        ("Recommended cold tire pressures are on the door pillar.", None, 2),
    ]
    return [
        Chunk(text=t, car_id=CAR_A.id, manual_name="Owner's Manual", manual_type="owner",
              source="archive", page=p, section=sec, chunk_index=i)
        for i, (t, sec, p) in enumerate(rows)
    ]


def test_index_and_retrieve_roundtrip(vstore):
    store.index_chunks(CAR_A, _chunks())
    results = store.retrieve(CAR_A, "what oil should I use?", k=5)

    assert len(results) == 2
    assert all(isinstance(r, ContextChunk) for r in results)
    refs = {r.ref for r in results}
    assert "Engine Oil" in refs   # section used when present
    assert "p.2" in refs          # falls back to page number


def test_retrieval_is_scoped_per_car(vstore):
    store.index_chunks(CAR_A, _chunks())
    # CAR_B has its own (empty) collection.
    assert store.retrieve(CAR_B, "oil", k=5) == []


def test_reindex_replaces_without_duplicates(vstore):
    store.index_chunks(CAR_A, _chunks())
    store.index_chunks(CAR_A, _chunks())
    count = vstore.get_collection(f"car-{CAR_A.id}").count()
    assert count == 2


# ── closed RAG loop in the chat route ────────────────────────────────


class _FakeStructured:
    async def ainvoke(self, _messages):
        return GroundedAnswer(
            text="Use 5W-40.",
            citations=[Citation(tag="Owner's Manual", ref="p.124")],
        )


def test_chat_grounds_in_retrieved_context(monkeypatch):
    calls = {}

    def fake_retrieve(car, message, *a, **k):
        calls["retrieved"] = (car.id, message)
        return [ContextChunk(manual="Owner's Manual", ref="p.124", text="5W-40, 5.5L")]

    monkeypatch.setattr(chat_route, "embeddings_available", lambda: True)
    monkeypatch.setattr(chat_route, "retrieve", fake_retrieve)
    monkeypatch.setattr(rag, "llm_available", lambda: True)
    monkeypatch.setattr(rag, "structured_model", lambda _schema: _FakeStructured())

    res = client.post(
        "/api/chat",
        json={"car": CAR_A.model_dump(), "message": "What oil?"},
    )
    assert res.status_code == 200
    assert calls["retrieved"][0] == CAR_A.id          # retrieval happened, scoped
    assert res.json()["citations"][0]["tag"] == "Owner's Manual"
