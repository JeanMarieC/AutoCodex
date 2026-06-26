"""Dashboard-vision response schema."""

from __future__ import annotations

from pydantic import BaseModel

from app.api.schemas.chat import Citation


class DashboardResponse(BaseModel):
    identification: str          # what the vision model saw
    text: str                    # the manual-grounded answer
    citations: list[Citation] | None = None
