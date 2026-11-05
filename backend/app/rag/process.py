"""Turn fetched manuals into metadata-tagged chunks.

Only **real, successfully downloaded** PDFs are processed — entries without a
local file are skipped. The pipeline never fabricates manual content; if nothing
real was fetched, ingestion fails and the user is asked to upload a PDF.
Returns the chunks (for embedding) plus per-manual summaries (for the UI).
"""

from __future__ import annotations

from pathlib import Path

from app.agent.state import Car
from app.config import get_settings
from app.rag.chunk import chunk_pages
from app.rag.extract import extract_pages
from app.rag.models import Chunk, ManualSummary
from app.tools.models import FetchedManual


def process_pdf_file(
    car: Car, path: str, name: str, kind: str, source: str = "upload"
) -> tuple[list[Chunk], ManualSummary]:
    """Extract + chunk a single PDF (e.g. a user upload)."""
    pages = extract_pages(path)
    chunks = chunk_pages(
        pages, car_id=car.id, manual_name=name, manual_type=kind, source=source  # type: ignore[arg-type]
    )
    summary = ManualSummary(
        name=name, kind=kind, source=source, pages=len(pages), chunk_count=len(chunks)  # type: ignore[arg-type]
    )
    return chunks, summary


def _is_substantial(pages: list, total_chars: int) -> bool:
    """A real manual is large; stub/landing-page PDFs are tiny. Require both a
    minimum page count and a minimum amount of extractable text."""
    s = get_settings()
    return len(pages) >= s.min_manual_pages and total_chars >= s.min_manual_chars


def process_manuals(
    car: Car, fetched: list[dict]
) -> tuple[list[Chunk], list[ManualSummary]]:
    all_chunks: list[Chunk] = []
    summaries: list[ManualSummary] = []

    for raw in fetched:
        fm = FetchedManual(**raw)
        if not (fm.ok and fm.path and Path(fm.path).exists()):
            continue  # no real file → skip (never fabricate one)

        pages = extract_pages(fm.path)
        total_chars = sum(len(p.text) for p in pages)
        # Quality gate — discard stub/landing-page or scanned-but-empty PDFs so
        # their non-manual text never reaches the index. Uploads skip this path.
        if not _is_substantial(pages, total_chars):
            continue

        chunks = chunk_pages(
            pages,
            car_id=car.id,
            manual_name=fm.name,
            manual_type=fm.kind,
            source=fm.source,
        )
        all_chunks.extend(chunks)
        summaries.append(
            ManualSummary(
                name=fm.name,
                kind=fm.kind,
                source=fm.source,
                pages=len(pages),
                chunk_count=len(chunks),
            )
        )

    return all_chunks, summaries
