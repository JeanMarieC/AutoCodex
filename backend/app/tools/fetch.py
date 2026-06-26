"""Fetch tool — download a selected manual to disk and verify it's a real PDF.

Handling per source:
  • direct .pdf URLs (common on Archive.org) → downloaded as-is
  • ManualsLib viewer pages (/manual/…) → best-effort: rewrite to the /download/
    endpoint and try; ManualsLib's real flow is JS-driven, so this often falls
    back gracefully rather than succeeding
  • anything else → tried directly

Every failure is non-fatal: it returns FetchedManual(ok=False, error=…) so the
pipeline keeps moving. `simulated_fetch` is used in keyless/stub mode to avoid
hitting the network with fake URLs.
"""

from __future__ import annotations

import re
from pathlib import Path

import httpx

from app.agent.state import Car
from app.config import get_settings
from app.tools.models import FetchedManual, SelectedManual

_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "manual"


def car_dir_slug(car: Car) -> str:
    """Folder name for a car's downloaded manuals."""
    return car.id


def _pdf_url(url: str) -> str:
    """Best-effort rewrite of a candidate URL to a likely direct PDF."""
    if url.lower().endswith(".pdf"):
        return url
    if "manualslib.com/manual/" in url:
        return url.replace("/manual/", "/download/")
    return url


def _looks_like_pdf(content_type: str, body: bytes) -> bool:
    return "application/pdf" in content_type.lower() or body[:5].startswith(b"%PDF")


async def fetch_manual(manual: SelectedManual, car_slug: str) -> FetchedManual:
    dest_dir = Path(get_settings().manuals_dir) / car_slug
    timeout = get_settings().fetch_timeout_seconds
    url = _pdf_url(manual.url)

    try:
        async with httpx.AsyncClient(
            follow_redirects=True, timeout=timeout, headers={"User-Agent": _UA}
        ) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            body = resp.content
            if not _looks_like_pdf(resp.headers.get("content-type", ""), body):
                return FetchedManual(
                    name=manual.name,
                    kind=manual.kind,
                    url=manual.url,
                    source=manual.source,
                    ok=False,
                    error="Response was not a PDF (likely a viewer page).",
                )

        dest_dir.mkdir(parents=True, exist_ok=True)
        path = dest_dir / f"{_slug(manual.name)}.pdf"
        path.write_bytes(body)
        return FetchedManual(
            name=manual.name,
            kind=manual.kind,
            url=manual.url,
            source=manual.source,
            ok=True,
            path=str(path),
            size_bytes=len(body),
        )
    except Exception as exc:
        return FetchedManual(
            name=manual.name,
            kind=manual.kind,
            url=manual.url,
            source=manual.source,
            ok=False,
            error=f"{type(exc).__name__}: {exc}"[:200],
        )


def simulated_fetch(manual: SelectedManual) -> FetchedManual:
    """Keyless/stub mode: pretend the download succeeded (no network call)."""
    return FetchedManual(
        name=manual.name,
        kind=manual.kind,
        url=manual.url,
        source=manual.source,
        ok=True,
        path=None,
        size_bytes=None,
    )
