"""Input node — identify the vehicle via the LLM (with a plain-label fallback)."""

from app.agent.events import emit_step
from app.agent.state import AgentState
from app.agent.steps import ACTIVE_DETAIL
from app.llm.vehicle import identify_vehicle


async def parse(state: AgentState) -> dict:
    car = state["car"]
    emit_step("parse", "active", ACTIVE_DETAIL["parse"])
    detail = await identify_vehicle(car)
    emit_step("parse", "done", detail)
    return {"retries": state.get("retries", 0)}
