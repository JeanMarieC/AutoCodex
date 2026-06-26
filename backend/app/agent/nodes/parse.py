"""Input node — normalize the vehicle. (Real normalization in later phases.)"""

from app.agent.events import emit_step
from app.agent.pacing import step_pause
from app.agent.state import AgentState
from app.agent.steps import ACTIVE_DETAIL


async def parse(state: AgentState) -> dict:
    car = state["car"]
    emit_step("parse", "active", ACTIVE_DETAIL["parse"])
    await step_pause()
    emit_step("parse", "done", f"Identified {car.label} · chassis W202 generation")
    return {"retries": state.get("retries", 0)}
