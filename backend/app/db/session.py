"""Database engine + session factory.

Sync SQLAlchemy: SQLite for local dev (default), Postgres in Docker. The repo
layer opens its own short-lived sessions and is invoked from async routes via
asyncio.to_thread, so the event loop is never blocked. `init_db` creates tables
(fine for dev; production would use Alembic migrations).
"""

from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import get_settings

_url = get_settings().database_url
_connect_args = {"check_same_thread": False} if _url.startswith("sqlite") else {}

engine = create_engine(_url, connect_args=_connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def init_db() -> None:
    # Import models so they register on Base.metadata before create_all.
    from app.db import models  # noqa: F401
    from app.db.base import Base

    Base.metadata.create_all(bind=engine)
