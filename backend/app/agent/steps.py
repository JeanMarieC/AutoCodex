"""The 5 pipeline steps and their human-readable status lines.

Kept in sync with the frontend's STEP_DEFS so progress text matches whether the
UI runs against mocks or this backend. The `done`/`fail` text is filled in by
the nodes (real tools will supply real numbers in later phases).
"""

from __future__ import annotations

from typing import Literal

StepId = Literal["parse", "search", "validate", "fetch", "ingest"]

STEP_ORDER: list[StepId] = ["parse", "search", "validate", "fetch", "ingest"]

# Status line shown while a step is actively working.
ACTIVE_DETAIL: dict[StepId, str] = {
    "parse": "Normalizing make, model and production year…",
    "search": "Querying ManualsLib and Archive.org for matching manuals…",
    "validate": "Scoring candidates by edition, language and completeness…",
    "fetch": "Downloading PDFs and verifying checksums…",
    "ingest": "Chunking pages, embedding and building the vector index…",
}

# Label per step (mirrors the UI).
STEP_LABEL: dict[StepId, str] = {
    "parse": "Parsing vehicle",
    "search": "Searching sources",
    "validate": "Validating & ranking results",
    "fetch": "Fetching manual PDF",
    "ingest": "Ingesting & indexing",
}

VALIDATION_FAIL_DETAIL = (
    "No candidate scored above the reliability threshold for this exact model year."
)

MAX_VALIDATION_RETRIES = 1
