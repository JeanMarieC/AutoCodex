"""PDF text extraction.

PyMuPDF is the primary extractor (fast, good text layer). For each page we also
resolve the nearest table-of-contents heading as its `section`. If a PDF yields
almost no text via PyMuPDF (e.g. an unusual encoding), we retry the whole
document with pdfplumber. Scanned/image-only PDFs (no text layer) are out of
scope — they'd need OCR.
"""

from __future__ import annotations

import pdfplumber
import pymupdf

from app.rag.models import Page

_MIN_DOC_CHARS = 200  # below this, treat PyMuPDF output as a failure and retry


def _section_for_page(toc: list, page_no: int) -> str | None:
    """Nearest TOC heading at or before this page. toc entries: [level, title, page]."""
    section = None
    for _level, title, page in toc:
        if page <= page_no:
            section = title.strip()
        else:
            break
    return section


def _extract_pymupdf(path: str) -> list[Page]:
    doc = pymupdf.open(path)
    try:
        toc = doc.get_toc()  # may be empty
        pages = []
        for i in range(doc.page_count):
            text = doc[i].get_text().strip()
            pages.append(Page(number=i + 1, text=text, section=_section_for_page(toc, i + 1)))
        return pages
    finally:
        doc.close()


def _extract_pdfplumber(path: str) -> list[Page]:
    pages = []
    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages):
            pages.append(Page(number=i + 1, text=(page.extract_text() or "").strip()))
    return pages


def extract_pages(path: str) -> list[Page]:
    """Return one Page per PDF page, with text and (when available) a section."""
    pages = _extract_pymupdf(path)
    if sum(len(p.text) for p in pages) < _MIN_DOC_CHARS:
        try:
            fallback = _extract_pdfplumber(path)
            if sum(len(p.text) for p in fallback) > sum(len(p.text) for p in pages):
                return fallback
        except Exception:
            pass
    return pages
