"""Manual upload — user supplies a PDF when none could be fetched.

Saves the PDF, runs it through the same extract → chunk → embed pipeline, adds
it to the car's vector collection, and records the manual on the user's car.
"""

from __future__ import annotations

import asyncio
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from app.agent.state import Car
from app.api.schemas.manuals import UploadResponse
from app.auth.deps import optional_email
from app.config import get_settings
from app.db import repo
from app.rag.models import ManualSummary
from app.rag.process import process_pdf_file
from app.rag.store import add_to_index, embeddings_available
from app.tools.fetch import car_dir_slug

router = APIRouter(tags=["manuals"])

_MAX_BYTES = 30 * 1024 * 1024  # 30 MB


def _save_and_index(car: Car, data: bytes, name: str, kind: str) -> tuple[ManualSummary, int]:
    dest = Path(get_settings().manuals_dir) / car_dir_slug(car)
    dest.mkdir(parents=True, exist_ok=True)
    path = dest / f"uploaded-{name.lower().replace(' ', '-')}.pdf"
    path.write_bytes(data)

    chunks, summary = process_pdf_file(car, str(path), name, kind)
    embedded = add_to_index(car, chunks) if embeddings_available() else 0
    return summary, embedded


@router.post("/manuals/upload", response_model=UploadResponse)
async def upload_manual(
    make: str = Form(...),
    model: str = Form(...),
    year: str = Form(...),
    name: str = Form("Owner's Manual"),
    kind: str = Form("owner"),
    file: UploadFile = File(...),
    email: str = Depends(optional_email),
) -> UploadResponse:
    data = await file.read()
    if len(data) > _MAX_BYTES:
        raise HTTPException(status_code=413, detail="File too large (max 30 MB).")
    if not (data[:5].startswith(b"%PDF") or (file.content_type or "").endswith("pdf")):
        raise HTTPException(status_code=400, detail="Please upload a PDF file.")

    car = Car(make=make, model=model, year=year)
    summary, embedded = await asyncio.to_thread(_save_and_index, car, data, name, kind)

    # Record the manual on the user's car.
    await asyncio.to_thread(repo.add_manual, email, car, summary.name, summary.meta)

    return UploadResponse(
        name=summary.name,
        meta=summary.meta,
        chunk_count=summary.chunk_count,
        embedded=bool(embedded),
        greeting=(
            f"Got it — I've indexed your {name} for the {car.make} {car.model} "
            f"({car.year}). Ask me anything about it."
        ),
    )
