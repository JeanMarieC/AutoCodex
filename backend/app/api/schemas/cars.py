"""Schemas for the garage / history endpoints."""

from __future__ import annotations

from pydantic import BaseModel

from app.api.schemas.chat import Citation


class ManualOut(BaseModel):
    name: str
    meta: str


class CarOut(BaseModel):
    car_key: str
    make: str
    model: str
    year: str
    manuals: list[ManualOut]


class MessageOut(BaseModel):
    role: str
    text: str
    citations: list[Citation] | None = None
