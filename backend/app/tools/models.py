"""Data passed between the search → validate → fetch tools."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

ManualKind = Literal["owner", "workshop", "unknown"]
Source = Literal["manualslib", "archive", "upload", "other"]


class Candidate(BaseModel):
    """One search hit for a possible manual."""

    title: str
    url: str
    source: Source
    snippet: str = ""
    score: float = 0.0  # relevance score from the search provider (0..1)


class SelectedManual(BaseModel):
    """A candidate that passed validation and will be fetched."""

    name: str          # UI label, e.g. "Owner's Manual"
    kind: ManualKind
    url: str
    source: Source
    meta: str          # short descriptor, e.g. "1998 · ManualsLib"


class FetchedManual(BaseModel):
    """Result of trying to download a selected manual."""

    name: str
    kind: ManualKind = "unknown"
    url: str
    source: Source
    ok: bool
    path: str | None = None       # local file path when the PDF was saved
    size_bytes: int | None = None
    error: str | None = None
