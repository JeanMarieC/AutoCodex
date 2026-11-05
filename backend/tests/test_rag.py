"""Phase 2.4 — PDF extraction, chunking, and the processing orchestrator.

Uses a generated sample PDF as the input fixture, so tests are self-contained
and offline.
"""

import pymupdf

from app.agent.state import Car
from app.config import get_settings
from app.rag.chunk import chunk_pages
from app.rag.extract import extract_pages
from app.rag.process import process_manuals
from app.rag.sample import generate_sample_pdf

CAR = Car(make="Mercedes-Benz", model="C200", year="1998")


def _relax_quality_gate(monkeypatch):
    """Let the small sample PDFs through the size gate for pipeline tests."""
    s = get_settings()
    monkeypatch.setattr(s, "min_manual_pages", 1)
    monkeypatch.setattr(s, "min_manual_chars", 1)


def test_extract_pages_with_sections(tmp_path):
    pdf = generate_sample_pdf(tmp_path / "owner.pdf", CAR, "Owner's Manual", "owner")
    pages = extract_pages(pdf)

    assert len(pages) == 4
    assert all(p.text for p in pages)
    # The TOC drives per-page sections.
    assert pages[0].section == "Engine Oil"
    assert "synthetic" in pages[0].text.lower()


def test_chunk_pages_tags_metadata(tmp_path):
    pdf = generate_sample_pdf(tmp_path / "workshop.pdf", CAR, "Workshop Manual", "workshop")
    pages = extract_pages(pdf)
    chunks = chunk_pages(
        pages,
        car_id=CAR.id,
        manual_name="Workshop Manual",
        manual_type="workshop",
        source="archive",
    )

    assert chunks
    c = chunks[0]
    assert c.car_id == "mercedes-benz-c200-1998"
    assert c.manual_type == "workshop"
    assert c.page >= 1
    assert c.section  # carried from the page
    md = c.metadata()
    assert md["car_id"] == CAR.id and md["manual_name"] == "Workshop Manual"


def test_process_manuals_skips_unfetched():
    # No real file → skipped entirely (never fabricates a sample manual).
    fetched = [
        {"name": "Owner's Manual", "kind": "owner", "url": "x", "source": "manualslib",
         "ok": True, "path": None},
        {"name": "Workshop Manual", "kind": "workshop", "url": "y", "source": "archive",
         "ok": False, "path": None},
    ]
    chunks, summaries = process_manuals(CAR, fetched)
    assert chunks == [] and summaries == []


def test_process_manuals_reads_real_pdf(tmp_path, monkeypatch):
    _relax_quality_gate(monkeypatch)
    pdf = generate_sample_pdf(tmp_path / "real.pdf", CAR, "Owner's Manual", "owner")
    fetched = [
        {"name": "Owner's Manual", "kind": "owner", "url": "x", "source": "archive",
         "ok": True, "path": pdf},
    ]
    chunks, summaries = process_manuals(CAR, fetched)
    assert summaries[0].pages == 4 and chunks


def test_process_manuals_drops_stub_pdf(tmp_path):
    """A tiny 1-page 'manual' (e.g. an Archive.org catalog page) is discarded by
    the quality gate so its non-manual text never reaches the index."""
    stub = tmp_path / "stub.pdf"
    doc = pymupdf.open()
    doc.new_page().insert_text((72, 72), "Civic catalog listing — see details.")
    doc.save(str(stub))
    doc.close()

    fetched = [
        {"name": "Owner's Manual", "kind": "owner", "url": "x", "source": "archive",
         "ok": True, "path": str(stub)},
    ]
    chunks, summaries = process_manuals(CAR, fetched)
    assert chunks == [] and summaries == []
