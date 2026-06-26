"""Search node — find candidate manuals via the Tavily-backed search tool,
scoped to ManualsLib + Archive.org (with a keyless stub fallback).
"""

from app.agent.events import emit_step
from app.agent.state import AgentState
from app.agent.steps import ACTIVE_DETAIL
from app.tools.search import search_manuals


async def search(state: AgentState) -> dict:
    car = state["car"]
    emit_step("search", "active", ACTIVE_DETAIL["search"])

    candidates = await search_manuals(car)
    n = len(candidates)
    sources = {c.source for c in candidates}
    detail = (
        f"{n} candidate document{'s' if n != 1 else ''} found across {len(sources)} source"
        f"{'s' if len(sources) != 1 else ''}"
        if n
        else "No candidate documents found"
    )
    emit_step("search", "done", detail)
    return {"candidates": [c.model_dump() for c in candidates]}
