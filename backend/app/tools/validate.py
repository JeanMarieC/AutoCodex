"""Validation tool — rank candidates and pick the manuals to fetch.

Deterministic heuristic scoring (no LLM, so ingestion stays fast and free):
classify each hit as owner's vs workshop, score it by source trust, year match
and title signals, then take the top-N most relevant. We index several manuals
per car and let retrieval rank chunks per question — so coverage is broad while
precision stays in retrieval's hands. "Sufficient" coverage means at least one
candidate scored above threshold.
"""

from __future__ import annotations

import re

from app.agent.state import Car
from app.config import get_settings
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
    # Archive.org is the only source we can actually download from, so rank ALL
    # archive candidates above ManualsLib — we want the fetchable slots filled.
    if c.source == "archive":
        score += 1.0
    elif c.source == "manualslib":
        score += 0.1
    if car.year and car.year in c.title:
        score += 0.15
    if "manual" in c.title.lower():
        score += 0.1
    if kind != "unknown":
        score += 0.1
    return score


def _clean_title(title: str) -> str:
    title = re.sub(r"\s+", " ", title).strip()
    return (title[:70] + "…") if len(title) > 71 else title


_YEAR_TOLERANCE = 3  # keep manuals within this many years of the target


def _year_relevant(car: Car, title: str) -> bool:
    """Drop manuals whose title clearly names a different generation/year.

    Titles with no year pass (generic). Titles with a year are kept only if some
    year is within tolerance of the target — so a 2004 query won't index a 1991
    or 2023 manual.
    """
    if not car.year.isdigit():
        return True
    target = int(car.year)
    years = [int(y) for y in re.findall(r"(?:19|20)\d{2}", title)]
    if not years:
        return True
    return any(abs(y - target) <= _YEAR_TOLERANCE for y in years)


def select_manuals(car: Car, candidates: list[Candidate]) -> tuple[list[SelectedManual], bool]:
    """Return (top-N selected manuals, coverage-is-sufficient).

    Picks the most relevant candidates (up to `max_manuals`) above the score
    threshold, deduped by URL. We fetch/index all of them and let the vector
    store rank chunks per question.
    """
    if not candidates:
        return [], False

    max_n = get_settings().max_manuals
    scored = sorted(
        ((_score(car, c, _classify(c.title)), _classify(c.title), c) for c in candidates),
        key=lambda x: x[0],
        reverse=True,
    )

    selected: list[SelectedManual] = []
    seen_urls: set[str] = set()
    for score, kind, c in scored:
        if score < _SCORE_THRESHOLD or c.url in seen_urls:
            continue
        if not _year_relevant(car, c.title):
            continue
        seen_urls.add(c.url)
        selected.append(
            SelectedManual(
                name=_clean_title(c.title),
                kind=kind,
                url=c.url,
                source=c.source,
                meta=f"{car.year} · {_SOURCE_LABEL[c.source]}",
            )
        )
        if len(selected) >= max_n:
            break

    return selected, len(selected) > 0
