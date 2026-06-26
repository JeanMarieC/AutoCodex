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

    @property
    def id(self) -> str:
        """Stable slug used for collections, folders and chunk metadata."""
        import re

        raw = f"{self.make}-{self.model}-{self.year}".lower()
        return re.sub(r"[^a-z0-9]+", "-", raw).strip("-")


class ManualRef(BaseModel):
    name: str
    meta: str


class AgentState(TypedDict, total=False):
    """LangGraph state. `total=False` so nodes return partial updates."""

    car: Car

    # Search → Validation  (dicts: tool models serialized via .model_dump())
    candidates: list[dict]          # Candidate hits from search
    selected: list[dict]            # SelectedManual entries that passed validation
    retries: int                    # validation retry counter

    # Fetch → Ingestion
    fetched: list[dict]             # FetchedManual download results
    chunk_count: int                # chunks embedded (stub until 2.4)

    # Outcome
    failed: bool
    error: str | None
    greeting: str
