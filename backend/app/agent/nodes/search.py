"""Search node — find candidate manuals. Stub returns fake hits; real Tavily
search scoped to manualslib.com / archive.org arrives in Phase 2.3.
"""

from app.agent.events import emit_step
from app.agent.pacing import step_pause
from app.agent.state import AgentState
from app.agent.steps import ACTIVE_DETAIL


async def search(state: AgentState) -> dict:
    car = state["car"]
    emit_step("search", "active", ACTIVE_DETAIL["search"])
    await step_pause()

    # Stub: pretend we found 7 candidates across 3 sources.
    candidates = [
        {"source": "manualslib", "title": f"{car.make} {car.model} Owner's Manual"},
        {"source": "archive.org", "title": f"{car.make} {car.model} Workshop Manual"},
    ]
    emit_step("search", "done", "7 candidate documents found across 3 sources")
    return {"candidates": candidates}
