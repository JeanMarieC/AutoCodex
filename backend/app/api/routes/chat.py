"""Chat endpoint — RAG answers via Gemini, grounded in retrieved manual chunks.

Retrieves the top-k excerpts from the car's vector collection and passes them to
the LLM, which answers ONLY from them and cites page/section. Falls back to a
general-knowledge answer (no citations) when nothing is indexed or no key is set.
"""

from __future__ import annotations

import asyncio

from fastapi import APIRouter, Depends

from app.api.schemas.chat import ChatRequest, ChatResponse, Citation
from app.auth.deps import optional_email
from app.db import repo
from app.llm.rag import answer_question
from app.rag.store import embeddings_available, retrieve

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, email: str = Depends(optional_email)) -> ChatResponse:
    context = []
    if embeddings_available():
        try:
            context = await asyncio.to_thread(retrieve, req.car, req.message)
        except Exception:
            context = []  # no collection yet / retrieval error → general answer

    answer = await answer_question(req.car, req.message, context)
    citations = [Citation(tag=c.tag, ref=c.ref) for c in answer.citations] or None

    # Persist the turn to the car's per-user chat history.
    try:
        await asyncio.to_thread(
            repo.record_chat,
            email,
            req.car,
            req.message,
            answer.text,
            [c.model_dump() for c in citations] if citations else None,
        )
    except Exception:
        pass

    return ChatResponse(text=answer.text, citations=citations)
