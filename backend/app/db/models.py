"""ORM models: users, their saved cars, each car's manuals and chat history."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    # Null for guest / chat-created users; set on signup.
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    cars: Mapped[list[SavedCar]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class SavedCar(Base):
    __tablename__ = "saved_cars"
    __table_args__ = (UniqueConstraint("user_id", "car_key", name="uq_user_car"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    car_key: Mapped[str] = mapped_column(String(255), index=True)  # Car.id slug
    make: Mapped[str] = mapped_column(String(120))
    model: Mapped[str] = mapped_column(String(120))
    year: Mapped[str] = mapped_column(String(8))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped[User] = relationship(back_populates="cars")
    manuals: Mapped[list[Manual]] = relationship(
        back_populates="car", cascade="all, delete-orphan"
    )
    messages: Mapped[list[Message]] = relationship(
        back_populates="car", cascade="all, delete-orphan"
    )


class Manual(Base):
    __tablename__ = "manuals"

    id: Mapped[int] = mapped_column(primary_key=True)
    car_id: Mapped[int] = mapped_column(ForeignKey("saved_cars.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(255))
    meta: Mapped[str] = mapped_column(String(255), default="")

    car: Mapped[SavedCar] = relationship(back_populates="manuals")


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    car_id: Mapped[int] = mapped_column(ForeignKey("saved_cars.id", ondelete="CASCADE"), index=True)
    role: Mapped[str] = mapped_column(String(16))  # "user" | "assistant"
    text: Mapped[str] = mapped_column(String)
    citations: Mapped[list | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    car: Mapped[SavedCar] = relationship(back_populates="messages")
