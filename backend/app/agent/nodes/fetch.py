"""Fetch node — download & verify the selected PDFs. Stub only; real download
with ManualsLib-viewer handling + fallback arrives in Phase 2.3.
"""

from app.agent.events import emit_step
from app.agent.pacing import step_pause
from app.agent.state import AgentState
from app.agent.steps import ACTIVE_DETAIL


async def fetch(state: AgentState) -> dict:
    emit_step("fetch", "active", ACTIVE_DETAIL["fetch"])
    await step_pause()

    fetched = [{"name": m.name, "pages": 312} for m in state.get("selected", [])]
    emit_step("fetch", "done", "2 PDFs retrieved · 612 pages total")
    return {"fetched": fetched}
