"""Manual upload response schema."""

from __future__ import annotations

from pydantic import BaseModel


class UploadResponse(BaseModel):
    name: str
    meta: str
    chunk_count: int
    embedded: bool
    greeting: str
