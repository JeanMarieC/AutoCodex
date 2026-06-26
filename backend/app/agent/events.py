"""Ingestion events — the SSE wire contract consumed by the frontend.

A discriminated union (matching `IngestionEvent` in frontend/src/types). Nodes
push these through LangGraph's custom stream writer; the SSE route serializes
them to the client.
"""

from __future__ import annotations

from typing import Annotated, Literal

from langgraph.config import get_stream_writer
from pydantic import BaseModel, Field

from app.agent.state import ManualRef
from app.agent.steps import StepId

StepStatus = Literal["pending", "active", "done", "failed"]


class StepEvent(BaseModel):
    type: Literal["step"] = "step"
    step: StepId
    status: StepStatus
    detail: str


class ManualsEvent(BaseModel):
    type: Literal["manuals"] = "manuals"
    manuals: list[ManualRef]


class CompleteEvent(BaseModel):
    type: Literal["complete"] = "complete"
    greeting: str


class ErrorEvent(BaseModel):
    type: Literal["error"] = "error"
    step: StepId
    message: str


IngestionEvent = Annotated[
    StepEvent | ManualsEvent | CompleteEvent | ErrorEvent,
    Field(discriminator="type"),
]


def _emit(event: BaseModel) -> None:
    """Push one event to the active stream. No-op outside a streaming run
    (e.g. unit tests using .invoke()), so nodes can emit unconditionally."""
    writer = get_stream_writer()
    if writer is not None:
        writer(event.model_dump())


def emit_step(step: StepId, status: StepStatus, detail: str) -> None:
    _emit(StepEvent(step=step, status=status, detail=detail))


def emit_manuals(manuals: list[ManualRef]) -> None:
    _emit(ManualsEvent(manuals=manuals))


def emit_complete(greeting: str) -> None:
    _emit(CompleteEvent(greeting=greeting))


def emit_error(step: StepId, message: str) -> None:
    _emit(ErrorEvent(step=step, message=message))
