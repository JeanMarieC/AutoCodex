"""Phase 2.3 — search / validate / fetch tools.

External services (Tavily, HTTP) are mocked, so tests are deterministic and
offline.
"""

import httpx

from app.agent.state import Car
from app.config import get_settings
from app.tools import search as search_mod
from app.tools.fetch import fetch_manual, simulated_fetch
from app.tools.models import Candidate, SelectedManual
from app.tools.search import search_manuals
from app.tools.validate import select_manuals

CAR = Car(make="Mercedes-Benz", model="C200", year="1998")


# ── search (fallback + scoping) ──────────────────────────────────────


async def test_search_fallback_returns_stub_candidates():
    cands = await search_manuals(CAR)
    assert len(cands) == 2
    assert {c.source for c in cands} == {"manualslib", "archive"}


async def test_search_fallback_no_manual_vehicle_is_empty():
    cands = await search_manuals(Car(make="Toyota", model="Hilux", year="2009"))
    assert cands == []


async def test_search_maps_and_scopes_tavily_results(monkeypatch):
    class _FakeTavily:
        def __init__(self, *a, **k):
            pass

        async def search(self, **kwargs):
            assert kwargs["include_domains"] == ["manualslib.com", "archive.org"]
            return {
                "results": [
                    {
                        "title": "Mercedes C200 Owner's Manual",
                        "url": "https://www.manualslib.com/manual/123/c200.html",
                        "content": "owner manual",
                        "score": 0.9,
                    },
                    {
                        "title": "C200 Workshop Manual",
                        "url": "https://archive.org/details/c200-workshop",
                        "content": "service",
                        "score": 0.8,
                    },
                ]
            }

    monkeypatch.setattr(search_mod, "tavily_available", lambda: True)
    monkeypatch.setattr(search_mod, "AsyncTavilyClient", _FakeTavily)

    cands = await search_manuals(CAR)
    assert [c.source for c in cands] == ["manualslib", "archive"]
    assert cands[0].score == 0.9


# ── validate (selection + sufficiency) ───────────────────────────────


def test_select_picks_owner_and_workshop():
    candidates = [
        Candidate(title="C200 Owner's Manual 1998", url="https://x/o.pdf",
                  source="manualslib", score=0.9),
        Candidate(title="C200 Workshop Service Manual", url="https://x/w.pdf",
                  source="archive", score=0.8),
    ]
    selected, sufficient = select_manuals(CAR, candidates)
    assert sufficient
    assert {m.kind for m in selected} == {"owner", "workshop"}


def test_select_empty_candidates_is_insufficient():
    selected, sufficient = select_manuals(CAR, [])
    assert selected == [] and sufficient is False


# ── fetch (download + validation) ────────────────────────────────────


def _mock_httpx(monkeypatch, body: bytes, content_type: str):
    class _Resp:
        content = body
        headers = {"content-type": content_type}

        def raise_for_status(self):
            pass

    class _Client:
        def __init__(self, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *exc):
            return False

        async def get(self, url):
            return _Resp()

    monkeypatch.setattr(httpx, "AsyncClient", _Client)


MANUAL = SelectedManual(
    name="Owner's Manual", kind="owner",
    url="https://archive.org/x/owner.pdf", source="archive", meta="1998 · Archive.org",
)


async def test_fetch_saves_valid_pdf(monkeypatch, tmp_path):
    monkeypatch.setattr(get_settings(), "manuals_dir", str(tmp_path))
    _mock_httpx(monkeypatch, b"%PDF-1.7\n...bytes...", "application/pdf")

    result = await fetch_manual(MANUAL, "merc-c200-1998")
    assert result.ok and result.path is not None
    assert result.size_bytes and result.size_bytes > 0


async def test_fetch_rejects_non_pdf(monkeypatch, tmp_path):
    monkeypatch.setattr(get_settings(), "manuals_dir", str(tmp_path))
    _mock_httpx(monkeypatch, b"<html>viewer page</html>", "text/html")

    result = await fetch_manual(MANUAL, "merc-c200-1998")
    assert result.ok is False
    assert "not a PDF" in (result.error or "")


def test_simulated_fetch_is_ok_without_network():
    result = simulated_fetch(MANUAL)
    assert result.ok and result.path is None
