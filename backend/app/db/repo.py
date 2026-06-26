"""Persistence operations.

Each function opens its own short-lived Session (thread-safe under
asyncio.to_thread) and returns plain dicts, never live ORM objects.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.agent.state import Car
from app.db.models import Manual, Message, SavedCar, User
from app.db.session import SessionLocal

DEFAULT_EMAIL = "local@demo"


def resolve_email(value: str | None) -> str:
    return (value or DEFAULT_EMAIL).strip().lower()


def _get_or_create_user(s: Session, email: str) -> User:
    user = s.scalar(select(User).where(User.email == email))
    if user is None:
        user = User(email=email)
        s.add(user)
        s.flush()
    return user


def _get_or_create_car(s: Session, user: User, car: Car) -> SavedCar:
    saved = s.scalar(
        select(SavedCar).where(SavedCar.user_id == user.id, SavedCar.car_key == car.id)
    )
    if saved is None:
        saved = SavedCar(
            user_id=user.id, car_key=car.id, make=car.make, model=car.model, year=car.year
        )
        s.add(saved)
        s.flush()
    return saved


def get_password_hash(email: str) -> str | None:
    with SessionLocal() as s:
        user = s.scalar(select(User).where(User.email == resolve_email(email)))
        return user.password_hash if user else None


def create_user_with_password(email: str, password_hash: str) -> None:
    """Create a user with a password. Raises ValueError if email already taken."""
    email = resolve_email(email)
    with SessionLocal() as s:
        existing = s.scalar(select(User).where(User.email == email))
        if existing and existing.password_hash:
            raise ValueError("email already registered")
        if existing:
            existing.password_hash = password_hash  # upgrade a guest/chat user
        else:
            s.add(User(email=email, password_hash=password_hash))
        s.commit()


def add_manual(email: str, car: Car, name: str, meta: str) -> None:
    """Append a single manual (e.g. an upload) to a car without replacing others."""
    with SessionLocal() as s:
        user = _get_or_create_user(s, email)
        saved = _get_or_create_car(s, user, car)
        s.add(Manual(car_id=saved.id, name=name, meta=meta))
        s.commit()


def save_car_with_manuals(email: str, car: Car, manuals: list[dict]) -> None:
    """Persist a saved car and replace its manual metadata (post-ingestion)."""
    with SessionLocal() as s:
        user = _get_or_create_user(s, email)
        saved = _get_or_create_car(s, user, car)
        for m in list(saved.manuals):
            s.delete(m)
        s.flush()
        for man in manuals:
            s.add(Manual(car_id=saved.id, name=man.get("name", ""), meta=man.get("meta", "")))
        s.commit()


def record_chat(
    email: str, car: Car, user_text: str, assistant_text: str, citations: list | None
) -> None:
    """Append a user turn and the assistant reply to a car's history."""
    with SessionLocal() as s:
        user = _get_or_create_user(s, email)
        saved = _get_or_create_car(s, user, car)
        s.add(Message(car_id=saved.id, role="user", text=user_text, citations=None))
        s.add(
            Message(car_id=saved.id, role="assistant", text=assistant_text, citations=citations)
        )
        s.commit()


def list_cars(email: str) -> list[dict]:
    with SessionLocal() as s:
        user = s.scalar(select(User).where(User.email == email))
        if user is None:
            return []
        cars = s.scalars(
            select(SavedCar).where(SavedCar.user_id == user.id).order_by(SavedCar.created_at.desc())
        ).all()
        return [
            {
                "car_key": c.car_key,
                "make": c.make,
                "model": c.model,
                "year": c.year,
                "manuals": [{"name": m.name, "meta": m.meta} for m in c.manuals],
            }
            for c in cars
        ]


def list_messages(email: str, car_key: str) -> list[dict]:
    with SessionLocal() as s:
        user = s.scalar(select(User).where(User.email == email))
        if user is None:
            return []
        saved = s.scalar(
            select(SavedCar).where(SavedCar.user_id == user.id, SavedCar.car_key == car_key)
        )
        if saved is None:
            return []
        msgs = s.scalars(
            select(Message).where(Message.car_id == saved.id).order_by(Message.id)
        ).all()
        return [{"role": m.role, "text": m.text, "citations": m.citations} for m in msgs]
