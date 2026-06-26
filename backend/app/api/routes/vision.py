"""Dashboard warning-light vision endpoint (multimodal RAG).

Photo of a dashboard → local VLM identifies the warning light → that becomes a
question → retrieval + LLM answer it from the car's manual, with citations.
"""

from __future__ import annotations

import asyncio

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from app.agent.state import Car
from app.api.schemas.chat import Citation
from app.api.schemas.vision import DashboardResponse
from app.auth.deps import optional_email
from app.db import repo
from app.llm.rag import answer_question
from app.rag.store import embeddings_available, retrieve
from app.vision.identify import identify_dashboard

router = APIRouter(tags=["vision"])

_MAX_BYTES = 10 * 1024 * 1024
_IMAGE_MAGIC = (b"\xff\xd8\xff", b"\x89PNG", b"RIFF", b"GIF8", b"BM")


def _is_image(data: bytes, content_type: str | None) -> bool:
    if content_type and content_type.startswith("image/"):
        return True
    return any(data.startswith(sig) for sig in _IMAGE_MAGIC)


@router.post("/vision/dashboard", response_model=DashboardResponse)
async def dashboard(
    make: str = Form(...),
    model: str = Form(...),
    year: str = Form(...),
    file: UploadFile = File(...),
    email: str = Depends(optional_email),
) -> DashboardResponse:
    data = await file.read()
    if len(data) > _MAX_BYTES:
        raise HTTPException(status_code=413, detail="Image too large (max 10 MB).")
    if not _is_image(data, file.content_type):
        raise HTTPException(status_code=400, detail="Please upload an image (JPEG/PNG).")

    car = Car(make=make, model=model, year=year)

    try:
        identification = await identify_dashboard(data)
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Vision model unavailable — is Ollama running with the model pulled?",
        ) from None

    question = (
        f"My dashboard is showing this warning light: {identification}. "
        "What does it mean, how serious is it, and what should I do?"
    )

    context = []
    if embeddings_available():
        try:
            context = await asyncio.to_thread(retrieve, car, question)
        except Exception:
            context = []

    answer = await answer_question(car, question, context)
    citations = [Citation(tag=c.tag, ref=c.ref) for c in answer.citations] or None

    try:
        await asyncio.to_thread(
            repo.record_chat,
            email,
            car,
            f"📷 Dashboard light — {identification}",
            answer.text,
            [c.model_dump() for c in citations] if citations else None,
        )
    except Exception:
        pass

    return DashboardResponse(identification=identification, text=answer.text, citations=citations)
