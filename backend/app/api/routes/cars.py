"""Garage + chat-history endpoints (scoped to the authenticated user / guest)."""

from __future__ import annotations

import asyncio

from fastapi import APIRouter, Depends

from app.api.schemas.cars import CarOut, MessageOut
from app.auth.deps import optional_email
from app.db import repo

router = APIRouter(tags=["garage"])


@router.get("/cars", response_model=list[CarOut])
async def get_cars(email: str = Depends(optional_email)) -> list[dict]:
    return await asyncio.to_thread(repo.list_cars, email)


@router.get("/cars/{car_key}/messages", response_model=list[MessageOut])
async def get_messages(car_key: str, email: str = Depends(optional_email)) -> list[dict]:
    return await asyncio.to_thread(repo.list_messages, email, car_key)
