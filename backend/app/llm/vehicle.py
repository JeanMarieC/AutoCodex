"""LLM-assisted vehicle identification used by the parse node.

Replaces the Phase 2.1 hardcoded "chassis W202" stub with a real one-line
identification from Gemini. Falls back to a plain label when no key is set or
the call fails, so the pipeline never stalls.
"""

from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from app.agent.pacing import step_pause
from app.agent.state import Car
from app.llm.client import get_chat_model, llm_available

_SYSTEM = (
    "You identify vehicles for a car-manual assistant. Given a make, model and "
    "year, reply with ONE short line naming the chassis code / generation and "
    "engine family if you know them. Start with 'Identified '. No more than 90 "
    "characters. If unsure, just restate the vehicle."
)


async def identify_vehicle(car: Car) -> str:
    """One-line vehicle identification for the progress feed."""
    default = f"Identified {car.label}"
    if not llm_available():
        await step_pause()
        return default
    try:
        model = get_chat_model()
        resp = await model.ainvoke(
            [
                SystemMessage(content=_SYSTEM),
                HumanMessage(content=f"{car.make} {car.model} {car.year}"),
            ]
        )
        line = str(resp.content).strip().splitlines()[0].strip()
        return line or default
    except Exception:
        return default
