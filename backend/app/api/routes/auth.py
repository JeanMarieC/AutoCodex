"""Authentication: signup, login, current user."""

from __future__ import annotations

import asyncio

from fastapi import APIRouter, Depends, HTTPException

from app.api.schemas.auth import Credentials, TokenResponse, UserOut
from app.auth.deps import require_email
from app.auth.security import create_access_token, hash_password, verify_password
from app.db import repo

router = APIRouter(tags=["auth"], prefix="/auth")


@router.post("/signup", response_model=TokenResponse)
async def signup(creds: Credentials) -> TokenResponse:
    try:
        await asyncio.to_thread(
            repo.create_user_with_password, creds.email, hash_password(creds.password)
        )
    except ValueError:
        raise HTTPException(status_code=409, detail="Email already registered") from None
    return TokenResponse(access_token=create_access_token(creds.email), email=creds.email)


@router.post("/login", response_model=TokenResponse)
async def login(creds: Credentials) -> TokenResponse:
    password_hash = await asyncio.to_thread(repo.get_password_hash, creds.email)
    if not password_hash or not verify_password(creds.password, password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return TokenResponse(access_token=create_access_token(creds.email), email=creds.email)


@router.get("/me", response_model=UserOut)
async def me(email: str = Depends(require_email)) -> UserOut:
    return UserOut(email=email)
