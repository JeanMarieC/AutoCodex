"""Validation node — rank candidates and decide if coverage is good enough.

Demonstrates the two non-linear paths:
  • retry      — coverage insufficient and retries remain → loop back to search
  • graceful   — retries exhausted → emit failed/error, pipeline ends cleanly

Stub failure trigger: a vehicle with no manual in our (fake) corpus, mirroring
the frontend's "Toyota Hilux" example. Real scoring lands in Phase 2.3.
"""

from app.agent.events import emit_error, emit_step
from app.agent.pacing import step_pause
from app.agent.state import AgentState, ManualRef
from app.agent.steps import ACTIVE_DETAIL, MAX_VALIDATION_RETRIES, VALIDATION_FAIL_DETAIL

NO_MANUAL_MODELS = ("hilux",)


async def validate(state: AgentState) -> dict:
    car = state["car"]
    retries = state.get("retries", 0)
    emit_step("validate", "active", ACTIVE_DETAIL["validate"])
    await step_pause()

    has_coverage = not any(m in car.model.lower() for m in NO_MANUAL_MODELS)

    if has_coverage:
        selected = [
            ManualRef(name="Owner's Manual", meta=f"{car.year} · 312 pp"),
            ManualRef(name="Workshop Manual", meta="W202 · 300 pp"),
        ]
        emit_step("validate", "done", "Ranked by relevance — 2 official manuals selected")
        return {"selected": selected, "failed": False}

    if retries < MAX_VALIDATION_RETRIES:
        # Retry path: broaden and try again (handled by the conditional edge).
        return {"retries": retries + 1}

    # Graceful failure path.
    emit_step("validate", "failed", VALIDATION_FAIL_DETAIL)
    emit_error("validate", VALIDATION_FAIL_DETAIL)
    return {"failed": True, "error": VALIDATION_FAIL_DETAIL}
