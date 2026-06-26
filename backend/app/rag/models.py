"""Document-processing data models."""

from __future__ import annotations

from pydantic import BaseModel

from app.tools.models import ManualKind, Source


class Page(BaseModel):
    """One extracted PDF page."""

    number: int                 # 1-based page number
    text: str
    section: str | None = None  # nearest table-of-contents heading, if any


class Chunk(BaseModel):
    """A retrievable text chunk plus the metadata we filter/cite on."""

    text: str
    # Metadata (also stored on the vector in Phase 2.5):
    car_id: str
    manual_name: str
    manual_type: ManualKind
    source: Source
    page: int
    section: str | None = None
    chunk_index: int = 0

    def metadata(self) -> dict:
        return {
            "car_id": self.car_id,
            "manual_name": self.manual_name,
            "manual_type": self.manual_type,
            "source": self.source,
            "page": self.page,
            "section": self.section or "",
            "chunk_index": self.chunk_index,
        }


class ManualSummary(BaseModel):
    """Per-manual rollup used for the UI 'manuals indexed' chips."""

    name: str
    kind: ManualKind
    source: Source
    pages: int
    chunk_count: int

    @property
    def meta(self) -> str:
        from app.tools.validate import _SOURCE_LABEL

        return f"{self.pages} pp · {_SOURCE_LABEL.get(self.source, 'Web')}"
