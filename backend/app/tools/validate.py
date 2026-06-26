"""Validation tool — rank candidates and pick the manuals to fetch.

Deterministic heuristic scoring (no LLM, so ingestion stays fast and free):
classify each hit as owner's vs workshop, score it by source trust, year match
and title signals, then select the best of each kind. "Sufficient" coverage
means at least one trusted manual scored above threshold.
"""

from __future__ import annotations

from app.agent.state import Car
from app.tools.models import Candidate, ManualKind, SelectedManual

_SCORE_THRESHOLD = 0.35

_OWNER_WORDS = ("owner", "operating", "operator", "user")
_WORKSHOP_WORDS = ("workshop", "service", "repair", "maintenance")
_SOURCE_LABEL = {
    "manualslib": "ManualsLib",
    "archive": "Archive.org",
    "upload": "Uploaded",
    "other": "Web",
}


def _classify(title: str) -> ManualKind:
    t = title.lower()
    if any(w in t for w in _WORKSHOP_WORDS):
        return "workshop"
    if any(w in t for w in _OWNER_WORDS):
        return "owner"
    return "unknown"


def _score(car: Car, c: Candidate, kind: ManualKind) -> float:
    score = c.score  # provider relevance (0..1)
    if c.source in ("manualslib", "archive"):
        score += 0.2
    if car.year and car.year in c.title:
        score += 0.15
    if "manual" in c.title.lower():
        score += 0.1
    if kind != "unknown":
        score += 0.1
    return score


def select_manuals(car: Car, candidates: list[Candidate]) -> tuple[list[SelectedManual], bool]:
    """Return (selected manuals, coverage-is-sufficient)."""
    if not candidates:
        return [], False

    scored = sorted(
        ((_score(car, c, _classify(c.title)), _classify(c.title), c) for c in candidates),
        key=lambda x: x[0],
        reverse=True,
    )

    selected: list[SelectedManual] = []
    taken_kinds: set[ManualKind] = set()
    for score, kind, c in scored:
        if score < _SCORE_THRESHOLD:
            continue
        # One manual per kind; "unknown" hits fill remaining slots.
        slot = kind if kind != "unknown" else "owner" if "owner" not in taken_kinds else "workshop"
        if slot in taken_kinds:
            continue
        taken_kinds.add(slot)
        selected.append(
            SelectedManual(
                name="Owner's Manual" if slot == "owner" else "Workshop Manual",
                kind=slot,
                url=c.url,
                source=c.source,
                meta=f"{car.year} · {_SOURCE_LABEL[c.source]}",
            )
        )
        if len(selected) >= 2:
            break

    return selected, len(selected) > 0
