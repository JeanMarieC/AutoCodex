"""Agent pipeline SSE endpoint.

`GET /api/agent/stream?make=&model=&year=` runs the ingestion graph and streams
IngestionEvents as Server-Sent Events. A final named `complete` event tells the
browser's EventSource to close (instead of auto-reconnecting).
"""

from __future__ import annotations

import json

from fastapi import APIRouter, Query
from sse_starlette.sse import EventSourceResponse

from app.agent.state import Car
from app.services.ingestion import run_ingestion

router = APIRouter(tags=["agent"])


@router.get("/agent/stream")
async def agent_stream(
    make: str = Query(...),
    model: str = Query(...),
    year: str = Query(...),
    # Accepted for forward-compat with the UI's retry button; resuming mid-graph
    # needs checkpointing (Phase 2.6), so for now a retry re-runs the pipeline.
    from_step: int | None = Query(default=None),
) -> EventSourceResponse:
    car = Car(make=make, model=model, year=year)

    async def event_generator():
        async for event in run_ingestion(car):
            yield {"data": json.dumps(event)}
        yield {"event": "complete", "data": "{}"}

    return EventSourceResponse(event_generator())
