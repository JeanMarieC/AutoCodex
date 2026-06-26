"""Fetch node — download the selected manuals via the fetch tool.

Real HTTP download when search is live (Tavily key present); a no-network
simulated fetch in keyless/stub mode so the demo stays fast and offline.
Download failures are non-fatal — ingestion proceeds with whatever arrived.
"""

from app.agent.events import emit_step
from app.agent.state import AgentState
from app.agent.steps import ACTIVE_DETAIL
from app.tools.fetch import car_dir_slug, fetch_manual, simulated_fetch
from app.tools.models import FetchedManual, SelectedManual
from app.tools.search import tavily_available


async def fetch(state: AgentState) -> dict:
    car = state["car"]
    selected = [SelectedManual(**m) for m in state.get("selected", [])]
    emit_step("fetch", "active", ACTIVE_DETAIL["fetch"])

    results: list[FetchedManual]
    if tavily_available():
        slug = car_dir_slug(car)
        results = [await fetch_manual(m, slug) for m in selected]
    else:
        results = [simulated_fetch(m) for m in selected]

    ok = sum(1 for r in results if r.ok)
    emit_step("fetch", "done", f"{ok} of {len(results)} PDFs retrieved")
    return {"fetched": [r.model_dump() for r in results]}
