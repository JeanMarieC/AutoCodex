"""Fetch tool — download a selected manual to disk and verify it's a real PDF.

Handling per source:
  • Archive.org → resolved to a real PDF via the metadata API
    (archive.org/metadata/<id> → file list → archive.org/download/<id>/<file>)
  • direct .pdf URLs → downloaded as-is
  • ManualsLib viewer pages (/manual/…) → best-effort /download/ rewrite;
    ManualsLib's real flow is JS-driven + anti-bot, so this usually falls back
  • anything else → tried directly

Every failure is non-fatal: it returns FetchedManual(ok=False, error=…) so the
pipeline keeps moving. `simulated_fetch` is used in keyless/stub mode to avoid
hitting the network with fake URLs.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from urllib.parse import quote

import httpx

from app.agent.state import Car
from app.config import get_settings
from app.tools.models import FetchedManual, SelectedManual

_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)
_MAX_PDF_BYTES = 80 * 1024 * 1024  # skip absurdly large files


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "manual"


def car_dir_slug(car: Car) -> str:
    """Folder name for a car's downloaded manuals."""
    return car.id


async def _archive_pdf_url(client: httpx.AsyncClient, url: str) -> str | None:
    """Resolve an Archive.org details/download URL to a direct PDF download URL."""
    m = re.search(r"archive\.org/(?:details|download)/([^/?#]+)", url)
    if not m:
        return None
    identifier = m.group(1)
    try:
        meta = (await client.get(f"https://archive.org/metadata/{identifier}")).json()
    except Exception:
        return None
    files = meta.get("files", []) if isinstance(meta, dict) else []
    pdfs = [
        f
        for f in files
        if str(f.get("name", "")).lower().endswith(".pdf")
        or "pdf" in str(f.get("format", "")).lower()
    ]
    if not pdfs:
        return None
    # Prefer the largest PDF under the size cap (usually the full manual).
    pdfs.sort(key=lambda f: int(f.get("size", 0) or 0), reverse=True)
    pick = next((f for f in pdfs if int(f.get("size", 0) or 0) <= _MAX_PDF_BYTES), pdfs[-1])
    return f"https://archive.org/download/{identifier}/{quote(str(pick['name']))}"


async def _resolve_pdf_url(client: httpx.AsyncClient, manual: SelectedManual) -> str | None:
    url = manual.url
    if url.lower().endswith(".pdf"):
        return url
    if manual.source == "archive" or "archive.org" in url:
        resolved = await _archive_pdf_url(client, url)
        if resolved:
            return resolved
    if "manualslib.com/manual/" in url:
        return url.replace("/manual/", "/download/")
    return url


def _looks_like_pdf(content_type: str, body: bytes) -> bool:
    return "application/pdf" in content_type.lower() or body[:5].startswith(b"%PDF")


def _fail(manual: SelectedManual, error: str) -> FetchedManual:
    return FetchedManual(
        name=manual.name, kind=manual.kind, url=manual.url,
        source=manual.source, ok=False, error=error,
    )


async def fetch_manual(manual: SelectedManual, car_slug: str) -> FetchedManual:
    dest_dir = Path(get_settings().manuals_dir) / car_slug
    timeout = get_settings().fetch_timeout_seconds

    try:
        async with httpx.AsyncClient(
            follow_redirects=True, timeout=timeout, headers={"User-Agent": _UA}
        ) as client:
            url = await _resolve_pdf_url(client, manual)
            if not url:
                return _fail(manual, "No direct PDF found for this source.")
            resp = await client.get(url)
            resp.raise_for_status()
            body = resp.content
            if not _looks_like_pdf(resp.headers.get("content-type", ""), body):
                return _fail(manual, "Response was not a PDF (likely a viewer page).")
            if len(body) > _MAX_PDF_BYTES:
                return _fail(manual, "PDF exceeds the size limit.")

        dest_dir.mkdir(parents=True, exist_ok=True)
        # Unique per URL so multiple manuals never overwrite each other.
        uid = hashlib.md5(manual.url.encode()).hexdigest()[:8]
        path = dest_dir / f"{_slug(manual.name)}-{uid}.pdf"
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
        return _fail(manual, f"{type(exc).__name__}: {exc}"[:200])


def simulated_fetch(manual: SelectedManual) -> FetchedManual:
    """Offline mode (no search provider): nothing is actually downloaded."""
    return _fail(manual, "Offline — no search provider configured.")
