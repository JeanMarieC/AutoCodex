"""Turn fetched manuals into metadata-tagged chunks.

For each fetched manual: extract pages → chunk → tag. If a real PDF isn't
available (download failed, or keyless stub mode), a sample PDF is generated so
processing still produces real chunks. Returns the chunks (for embedding in
Phase 2.5) plus per-manual summaries (for the UI).
"""

from __future__ import annotations

import re
from pathlib import Path

from app.agent.state import Car
from app.config import get_settings
from app.rag.chunk import chunk_pages
from app.rag.extract import extract_pages
from app.rag.models import Chunk, ManualSummary
from app.rag.sample import generate_sample_pdf
from app.tools.models import FetchedManual


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "manual"


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


def process_manuals(
    car: Car, fetched: list[dict]
) -> tuple[list[Chunk], list[ManualSummary]]:
    base_dir = Path(get_settings().manuals_dir) / car.id
    all_chunks: list[Chunk] = []
    summaries: list[ManualSummary] = []

    for raw in fetched:
        fm = FetchedManual(**raw)
        path = fm.path if (fm.ok and fm.path and Path(fm.path).exists()) else None
        if path is None:
            path = generate_sample_pdf(
                base_dir / f"sample-{_slug(fm.name)}.pdf", car, fm.name, fm.kind
            )

        pages = extract_pages(path)
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
