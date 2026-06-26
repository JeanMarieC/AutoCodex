"""Chat endpoint — STUB.

Returns a canned, citation-bearing answer so the chat UI works against the real
backend. The actual RAG answer (Claude + retrieved chunks) is wired in Phase 2.2
and 2.5; this just keeps the contract live.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.schemas.chat import ChatRequest, ChatResponse, Citation

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    car = req.car
    text = (
        f"(Preview) Once the manuals for your {car.make} {car.model} are indexed, "
        "I'll answer this from the source. Real retrieval-augmented answers come "
        "online in the next sub-phases."
    )
    return ChatResponse(
        text=text,
        citations=[Citation(tag="Workshop Manual", ref="General · Specs")],
    )
