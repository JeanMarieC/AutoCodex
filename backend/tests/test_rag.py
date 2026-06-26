"""Phase 2.4 — PDF extraction, chunking, and the processing orchestrator.

Uses a generated sample PDF as the input fixture, so tests are self-contained
and offline.
"""

from app.agent.state import Car
from app.rag.chunk import chunk_pages
from app.rag.extract import extract_pages
from app.rag.process import process_manuals
from app.rag.sample import generate_sample_pdf

CAR = Car(make="Mercedes-Benz", model="C200", year="1998")


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


def test_process_manuals_falls_back_to_sample():
    # path=None → orchestrator generates a sample PDF and still produces chunks.
    fetched = [
        {"name": "Owner's Manual", "kind": "owner", "url": "x", "source": "manualslib",
         "ok": True, "path": None},
        {"name": "Workshop Manual", "kind": "workshop", "url": "y", "source": "archive",
         "ok": True, "path": None},
    ]
    chunks, summaries = process_manuals(CAR, fetched)

    assert len(summaries) == 2
    assert all(s.pages > 0 and s.chunk_count > 0 for s in summaries)
    assert len(chunks) == sum(s.chunk_count for s in summaries)
    assert {c.manual_type for c in chunks} == {"owner", "workshop"}
    assert "pp ·" in summaries[0].meta


def test_process_manuals_reads_real_pdf(tmp_path):
    pdf = generate_sample_pdf(tmp_path / "real.pdf", CAR, "Owner's Manual", "owner")
    fetched = [
        {"name": "Owner's Manual", "kind": "owner", "url": "x", "source": "archive",
         "ok": True, "path": pdf},
    ]
    chunks, summaries = process_manuals(CAR, fetched)
    assert summaries[0].pages == 4 and chunks
