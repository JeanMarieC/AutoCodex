"""The state that flows through the LangGraph ingestion pipeline.

Stubbed fields (candidates, files, chunk counts) are populated with fake data
in Phase 2.1 and replaced by real tool output in Phases 2.3–2.5.
"""

from __future__ import annotations

from typing import TypedDict

from pydantic import BaseModel


class Car(BaseModel):
    make: str
    model: str
    year: str

    @property
    def label(self) -> str:
        return f"{self.make} {self.model} · {self.year}"


class ManualRef(BaseModel):
    name: str
    meta: str


class AgentState(TypedDict, total=False):
    """LangGraph state. `total=False` so nodes return partial updates."""

    car: Car

    # Search → Validation
    candidates: list[dict]          # raw search hits (stub)
    selected: list[ManualRef]       # manuals that passed validation
    retries: int                    # validation retry counter

    # Fetch → Ingestion
    fetched: list[dict]             # downloaded files (stub)
    chunk_count: int                # chunks embedded (stub)

    # Outcome
    failed: bool
    error: str | None
    greeting: str
