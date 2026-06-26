"""Search tool — find candidate manuals via Tavily, scoped to the two sources
we trust (ManualsLib + Archive.org).

Without a TAVILY_API_KEY it falls back to deterministic stub candidates so the
pipeline still runs end-to-end (and the frontend's "no manual" demo vehicle
still fails). Real search activates the moment a key is present.
"""

from __future__ import annotations

from urllib.parse import urlparse

import httpx
from tavily import AsyncTavilyClient

from app.agent.state import Car
from app.config import get_settings
from app.tools.models import Candidate, Source

INCLUDE_DOMAINS = ["manualslib.com", "archive.org"]
_UA = "Mozilla/5.0 (compatible; ManualAI/1.0)"

# Vehicles with no manual in our (stub) corpus — keeps the keyless demo's
# failure path working. Ignored once real search is enabled.
_STUB_NO_MANUAL = ("hilux",)


def tavily_available() -> bool:
    return bool(get_settings().tavily_api_key)


def _archive_enabled() -> bool:
    return get_settings().archive_search_enabled


async def _search_archive(car: Car) -> list[Candidate]:
    """Query Archive.org's free search API directly for the vehicle's manual."""
    query = f'({car.make} {car.model} manual) AND mediatype:texts'
    params = [
        ("q", query),
        ("fl[]", "identifier"),
        ("fl[]", "title"),
        ("rows", "15"),
        ("output", "json"),
    ]
    async with httpx.AsyncClient(timeout=20, headers={"User-Agent": _UA}) as client:
        res = await client.get(
            "https://archive.org/advancedsearch.php", params=params  # type: ignore[arg-type]
        )
        docs = res.json().get("response", {}).get("docs", [])

    make_l, model_l = car.make.lower(), car.model.lower()
    out: list[Candidate] = []
    for d in docs:
        ident = d.get("identifier")
        if not ident:
            continue
        raw_title = d.get("title") or ident
        title = raw_title if isinstance(raw_title, str) else " ".join(map(str, raw_title))
        # Relevance filter — keep results that actually name the make or model.
        if make_l not in title.lower() and model_l not in title.lower():
            continue
        out.append(
            Candidate(
                title=title[:200],
                url=f"https://archive.org/details/{ident}",
                source="archive",
                snippet="Archive.org",
                score=0.7,
            )
        )
    return out


def _source_of(url: str) -> Source:
    host = urlparse(url).netloc.lower()
    if "manualslib" in host:
        return "manualslib"
    if "archive.org" in host:
        return "archive"
    return "other"


def _query(car: Car) -> str:
    return f'{car.make} {car.model} {car.year} owner\'s manual OR workshop service manual'


async def _search_tavily(car: Car) -> list[Candidate]:
    client = AsyncTavilyClient(api_key=get_settings().tavily_api_key)
    res = await client.search(
        query=_query(car),
        search_depth="advanced",
        include_domains=INCLUDE_DOMAINS,
        max_results=10,
    )
    candidates: list[Candidate] = []
    for hit in res.get("results", []):
        url = hit.get("url", "")
        if not url:
            continue
        candidates.append(
            Candidate(
                title=hit.get("title", "").strip() or url,
                url=url,
                source=_source_of(url),
                snippet=hit.get("content", "")[:300],
                score=float(hit.get("score", 0.0)),
            )
        )
    return candidates


def _stub_candidates(car: Car) -> list[Candidate]:
    if any(m in car.model.lower() for m in _STUB_NO_MANUAL):
        return []
    base = f"{car.make} {car.model} {car.year}"
    return [
        Candidate(
            title=f"{base} Owner's Manual",
            url=f"https://www.manualslib.com/manual/000000/{car.make}-{car.model}.html",
            source="manualslib",
            snippet="Owner's manual (stub candidate — set TAVILY_API_KEY for real search).",
            score=0.9,
        ),
        Candidate(
            title=f"{base} Workshop Manual",
            url=f"https://archive.org/details/{car.make}-{car.model}-workshop",
            source="archive",
            snippet="Workshop/service manual (stub candidate).",
            score=0.85,
        ),
    ]


async def search_manuals(car: Car) -> list[Candidate]:
    """Return candidate manuals, combining Archive.org (free) + Tavily (if keyed).

    Archive.org results are real, downloadable PDFs and need no key. Tavily adds
    ManualsLib coverage when a key is present. Falls back to stub candidates only
    when neither source returns anything.
    """
    results: list[Candidate] = []

    if _archive_enabled():
        try:
            results += await _search_archive(car)
        except Exception:
            pass

    if tavily_available():
        try:
            results += await _search_tavily(car)
        except Exception:
            pass

    if not results:
        return _stub_candidates(car)

    # De-duplicate by URL, preserving order (archive-first).
    seen: set[str] = set()
    unique: list[Candidate] = []
    for c in results:
        if c.url in seen:
            continue
        seen.add(c.url)
        unique.append(c)
    return unique
