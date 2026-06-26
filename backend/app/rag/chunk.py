"""Chunking — split extracted pages into retrievable, metadata-tagged chunks.

Uses LangChain's RecursiveCharacterTextSplitter (paragraph → line → word
boundaries). Each chunk keeps its page and section so answers in Phase 2.5 can
cite an exact location.
"""

from __future__ import annotations

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import get_settings
from app.rag.models import Chunk, Page
from app.tools.models import ManualKind, Source


def _splitter() -> RecursiveCharacterTextSplitter:
    s = get_settings()
    return RecursiveCharacterTextSplitter(
        chunk_size=s.chunk_size,
        chunk_overlap=s.chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )


def chunk_pages(
    pages: list[Page],
    *,
    car_id: str,
    manual_name: str,
    manual_type: ManualKind,
    source: Source,
) -> list[Chunk]:
    splitter = _splitter()
    chunks: list[Chunk] = []
    for page in pages:
        if not page.text:
            continue
        for piece in splitter.split_text(page.text):
            piece = piece.strip()
            if not piece:
                continue
            chunks.append(
                Chunk(
                    text=piece,
                    car_id=car_id,
                    manual_name=manual_name,
                    manual_type=manual_type,
                    source=source,
                    page=page.number,
                    section=page.section,
                    chunk_index=len(chunks),
                )
            )
    return chunks
