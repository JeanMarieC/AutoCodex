"""Phase 2.1 — the ingestion graph flows, fails gracefully, and retries.

Collects the custom-stream events the nodes emit and asserts on the sequence.
"""

import pytest

from app.agent import pacing
from app.agent.graph import build_graph
from app.agent.state import Car


@pytest.fixture(autouse=True)
def _instant(monkeypatch):
    # No artificial delays in tests.
    monkeypatch.setattr(pacing, "DELAY", 0)


async def collect_events(car: Car) -> list[dict]:
    graph = build_graph()
    events: list[dict] = []
    async for event in graph.astream({"car": car, "retries": 0}, stream_mode="custom"):
        events.append(event)
    return events


def step_status(events, step):
    return [e["status"] for e in events if e.get("type") == "step" and e["step"] == step]


async def test_happy_path_reaches_chat():
    events = await collect_events(Car(make="Mercedes-Benz", model="C200", year="1998"))
    types = [e["type"] for e in events]

    # Every step completes, manuals are indexed, and we hand off to chat.
    for s in ("parse", "search", "validate", "fetch", "ingest"):
        assert step_status(events, s) == ["active", "done"], s
    assert "manuals" in types
    assert types[-1] == "complete"

    complete = events[-1]
    assert "C200" in complete["greeting"]
    manuals = next(e for e in events if e["type"] == "manuals")["manuals"]
    assert len(manuals) == 2


async def test_graceful_failure_emits_error():
    events = await collect_events(Car(make="Toyota", model="Hilux", year="2009"))
    types = [e["type"] for e in events]

    assert "failed" in step_status(events, "validate")
    assert "error" in types
    # Pipeline stops before fetch/ingest — no chat handoff.
    assert "manuals" not in types
    assert "complete" not in types
    assert step_status(events, "fetch") == []


async def test_retry_path_runs_search_twice_before_giving_up():
    events = await collect_events(Car(make="Toyota", model="Hilux", year="2009"))

    # Search runs once, then again on the retry loop = two active/done pairs.
    assert step_status(events, "search").count("active") == 2
    # Validation also runs twice; only the final attempt is marked failed.
    assert step_status(events, "validate") == ["active", "active", "failed"]
