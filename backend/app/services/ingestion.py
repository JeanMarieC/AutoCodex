"""Runs the ingestion graph and surfaces the events nodes emit.

Thin wrapper over LangGraph's custom stream so the API layer doesn't depend on
graph internals.
"""

from __future__ import annotations

from collections.abc import AsyncIterator

from app.agent.graph import get_graph
from app.agent.state import Car


async def run_ingestion(car: Car) -> AsyncIterator[dict]:
    """Yield each IngestionEvent (as a dict) as the pipeline advances."""
    graph = get_graph()
    initial = {"car": car, "retries": 0}
    async for event in graph.astream(initial, stream_mode="custom"):
        yield event
