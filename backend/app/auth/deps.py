"""Auth dependencies — resolve the request's user email from a Bearer token.

`optional_email` falls back to the shared guest user (so the app works without
login); `require_email` 401s when there's no valid token.
"""

from __future__ import annotations

from fastapi import Header, HTTPException

from app.auth.security import decode_token
from app.db import repo


def _email_from_header(authorization: str | None) -> str | None:
    if authorization and authorization.lower().startswith("bearer "):
        return decode_token(authorization[7:])
    return None


def optional_email(authorization: str | None = Header(default=None)) -> str:
    return _email_from_header(authorization) or repo.DEFAULT_EMAIL


def require_email(authorization: str | None = Header(default=None)) -> str:
    email = _email_from_header(authorization)
    if not email:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return email
