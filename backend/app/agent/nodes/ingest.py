"""Ingestion node — extract & chunk the fetched manuals (Phase 2.4).

Produces real, metadata-tagged chunks and reports real page/chunk counts. The
chunks are embedded into the vector store in Phase 2.5; for now this proves the
document-processing pipeline. On success it emits the indexed manuals and a
`complete` event, which flips the frontend into chat.
"""

import asyncio

from app.agent.events import emit_complete, emit_error, emit_manuals, emit_step
from app.agent.state import AgentState, ManualRef
from app.agent.steps import ACTIVE_DETAIL
from app.rag.process import process_manuals
from app.rag.store import embeddings_available, index_chunks

_NO_TEXT = (
    "The downloaded manual had no extractable text (it may be a scanned image). "
    "Upload a text-based PDF to continue."
)


async def ingest(state: AgentState) -> dict:
    car = state["car"]
    fetched = state.get("fetched", [])

    emit_step("ingest", "active", ACTIVE_DETAIL["ingest"])

    # PDF parsing/chunking and embedding are blocking — run off the event loop.
    chunks, summaries = await asyncio.to_thread(process_manuals, car, fetched)
    if not chunks:
        emit_step("ingest", "failed", _NO_TEXT)
        emit_error("ingest", _NO_TEXT)
        return {"failed": True}
    total_pages = sum(s.pages for s in summaries)

    if embeddings_available():
        try:
            embedded = await asyncio.to_thread(index_chunks, car, chunks)
            detail = f"{embedded:,} chunks embedded across {total_pages} pages · index ready"
        except Exception as exc:
            # Embedding failure (bad model/quota) shouldn't fail the whole run —
            # chat will fall back to general-knowledge answers.
            detail = (
                f"{len(chunks):,} chunks extracted · "
                f"embedding unavailable ({type(exc).__name__})"
            )
    else:
        detail = (
            f"{len(chunks):,} chunks from {total_pages} pages "
            "(embedding disabled — set GOOGLE_API_KEY)"
        )

    emit_step("ingest", "done", detail)
    emit_manuals([ManualRef(name=s.name, meta=s.meta) for s in summaries])

    if len(summaries) <= 2:
        read = " and ".join(s.name for s in summaries)
    else:
        read = f"{len(summaries)} manuals ({total_pages} pages)"
    greeting = (
        f"Your {car.make} {car.model} ({car.year}) is indexed and ready — I've read "
        f"{read}. Ask me anything about maintenance, fluids, warning lights or repairs."
    )
    emit_complete(greeting)
    return {"chunk_count": len(chunks)}
