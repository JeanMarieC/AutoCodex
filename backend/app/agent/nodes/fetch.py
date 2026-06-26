"""Fetch node — download the selected manuals via the fetch tool.

Downloads the top-N relevant candidates **in parallel** whenever a real search
source is active (Archive.org is free, so this is the normal case). We keep every
PDF that downloads successfully — retrieval ranks across all of them per
question. If **no real PDF** could be downloaded, the step fails — we never
fabricate a manual; the user is prompted to upload one.
"""

import asyncio

from app.agent.events import emit_error, emit_step
from app.agent.state import AgentState
from app.agent.steps import ACTIVE_DETAIL
from app.config import get_settings
from app.tools.fetch import car_dir_slug, fetch_manual, simulated_fetch
from app.tools.models import FetchedManual, SelectedManual
from app.tools.search import tavily_available

_FETCH_FAIL = (
    "Couldn't download a usable manual for this vehicle from our sources. "
    "Upload the manual PDF to continue."
)


async def fetch(state: AgentState) -> dict:
    car = state["car"]
    selected = [SelectedManual(**m) for m in state.get("selected", [])]
    emit_step("fetch", "active", ACTIVE_DETAIL["fetch"])

    real_search = tavily_available() or get_settings().archive_search_enabled
    results: list[FetchedManual]
    if real_search:
        slug = car_dir_slug(car)
        results = list(await asyncio.gather(*(fetch_manual(m, slug) for m in selected)))
    else:
        results = [simulated_fetch(m) for m in selected]

    downloaded = [r for r in results if r.ok and r.path]
    if not downloaded:
        emit_step("fetch", "failed", _FETCH_FAIL)
        emit_error("fetch", _FETCH_FAIL)
        return {"fetched": [], "failed": True}

    emit_step("fetch", "done", f"{len(downloaded)} of {len(results)} PDFs retrieved")
    return {"fetched": [r.model_dump() for r in downloaded]}
