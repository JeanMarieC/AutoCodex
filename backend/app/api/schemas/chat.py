"""Chat request/response schemas."""

from __future__ import annotations

from pydantic import BaseModel

from app.agent.state import Car


class Citation(BaseModel):
    tag: str
    ref: str


class ChatRequest(BaseModel):
    car: Car
    message: str


class ChatResponse(BaseModel):
    role: str = "assistant"
    text: str
    citations: list[Citation] | None = None
