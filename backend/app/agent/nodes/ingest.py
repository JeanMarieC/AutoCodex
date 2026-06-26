"""Ingestion node — chunk, embed, build the vector index. Stub only; real
PyMuPDF/pdfplumber extraction + chunking + Chroma indexing arrive in 2.4–2.5.

On success it emits the indexed manuals and a `complete` event, which is what
flips the frontend from the progress screen into chat.
"""

from app.agent.events import emit_complete, emit_manuals, emit_step
from app.agent.pacing import step_pause
from app.agent.state import AgentState
from app.agent.steps import ACTIVE_DETAIL


async def ingest(state: AgentState) -> dict:
    car = state["car"]
    manuals = state.get("selected", [])

    emit_step("ingest", "active", ACTIVE_DETAIL["ingest"])
    await step_pause()
    emit_step("ingest", "done", "1,438 chunks embedded · index ready")

    emit_manuals(manuals)
    greeting = (
        f"Your {car.make} {car.model} ({car.year}) is indexed and ready. "
        "I've read the Owner's and Workshop manuals — ask me anything about "
        "maintenance, fluids, warning lights or repair procedures."
    )
    emit_complete(greeting)
    return {"chunk_count": 1438, "greeting": greeting}
