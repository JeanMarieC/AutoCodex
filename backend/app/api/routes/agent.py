"""Agent pipeline SSE endpoint.

`GET /api/agent/stream?make=&model=&year=` runs the ingestion graph and streams
IngestionEvents as Server-Sent Events. A final named `complete` event tells the
browser's EventSource to close (instead of auto-reconnecting).
"""

from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter, Query
from sse_starlette.sse import EventSourceResponse

from app.agent.state import Car
from app.auth.security import decode_token
from app.db import repo
from app.services.ingestion import run_ingestion

router = APIRouter(tags=["agent"])


@router.get("/agent/stream")
async def agent_stream(
    make: str = Query(...),
    model: str = Query(...),
    year: str = Query(...),
    # EventSource can't send headers, so the JWT comes through the query string.
    token: str | None = Query(default=None),
    # Accepted for forward-compat with the UI's retry button; resuming mid-graph
    # needs checkpointing, so for now a retry re-runs the pipeline.
    from_step: int | None = Query(default=None),
) -> EventSourceResponse:
    car = Car(make=make, model=model, year=year)
    email = repo.resolve_email(decode_token(token) if token else None)

    async def event_generator():
        manuals: list[dict] = []
        completed = False
        async for event in run_ingestion(car):
            if event.get("type") == "manuals":
                manuals = event["manuals"]
            elif event.get("type") == "complete":
                completed = True
            yield {"data": json.dumps(event)}

        # On success, persist the car + its manuals to the user's garage.
        if completed:
            try:
                await asyncio.to_thread(repo.save_car_with_manuals, email, car, manuals)
            except Exception:
                pass
        yield {"event": "complete", "data": "{}"}

    return EventSourceResponse(event_generator())
