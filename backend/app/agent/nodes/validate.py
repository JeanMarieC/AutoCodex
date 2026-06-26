"""Validation node — rank/select candidates via the validation tool.

Keeps the two non-linear paths from 2.1:
  • retry      — no acceptable manuals yet and retries remain → loop to search
  • graceful   — retries exhausted → emit failed/error, pipeline ends cleanly
"""

from app.agent.events import emit_error, emit_step
from app.agent.state import AgentState
from app.agent.steps import ACTIVE_DETAIL, MAX_VALIDATION_RETRIES, VALIDATION_FAIL_DETAIL
from app.tools.models import Candidate
from app.tools.validate import select_manuals


async def validate(state: AgentState) -> dict:
    car = state["car"]
    retries = state.get("retries", 0)
    candidates = [Candidate(**c) for c in state.get("candidates", [])]
    emit_step("validate", "active", ACTIVE_DETAIL["validate"])

    selected, sufficient = select_manuals(car, candidates)

    if sufficient:
        emit_step(
            "validate",
            "done",
            f"Ranked by relevance — {len(selected)} official manual"
            f"{'s' if len(selected) != 1 else ''} selected",
        )
        return {"selected": [m.model_dump() for m in selected], "failed": False}

    if retries < MAX_VALIDATION_RETRIES:
        return {"retries": retries + 1}  # → conditional edge loops back to search

    emit_step("validate", "failed", VALIDATION_FAIL_DETAIL)
    emit_error("validate", VALIDATION_FAIL_DETAIL)
    return {"failed": True, "error": VALIDATION_FAIL_DETAIL}
