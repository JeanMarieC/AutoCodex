"""RAG answer generation.

`answer_question` is the function the chat endpoint calls. It uses Gemini's
function-calling (via LangChain `with_structured_output`) to return a typed
{text, citations} object rather than free-form text — so the UI always gets
clean citation chips.

The `context` parameter is the retrieval slot: in Phase 2.5 the vector store
will pass the manual chunks it found. Until then it's empty and the model
answers from general automotive knowledge (and returns no citations, so we never
fabricate sources).
"""

from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from app.agent.state import Car
from app.llm.client import llm_available, structured_model


class ContextChunk(BaseModel):
    """One retrieved manual excerpt (populated by the vector store in 2.5)."""

    manual: str          # e.g. "Owner's Manual"
    ref: str             # e.g. "p.124" or "Engine · Lubrication"
    text: str


class Citation(BaseModel):
    tag: str = Field(description="The manual the fact came from, e.g. 'Owner's Manual'")
    ref: str = Field(description="Page or section within that manual, e.g. 'p.124'")


class GroundedAnswer(BaseModel):
    text: str = Field(description="The answer, in clear prose.")
    citations: list[Citation] = Field(
        default_factory=list,
        description="Sources used. Empty when no manual excerpts were provided.",
    )


def _system_prompt(car: Car, context: list[ContextChunk]) -> str:
    base = (
        f"You are AutoCodex, an expert assistant for a {car.make} {car.model} "
        f"({car.year}). Answer the owner's maintenance and repair questions "
        "clearly and practically."
    )
    if context:
        return (
            base
            + "\n\nAnswer ONLY from the manual excerpts below. If they do not "
            "cover the question, say you can't confirm it from the manuals. Cite "
            "every excerpt you rely on (tag = manual name, ref = page/section).\n\n"
            + "\n\n".join(f"[{c.manual} · {c.ref}]\n{c.text}" for c in context)
        )
    return (
        base
        + "\n\nThe vehicle's manuals are not yet indexed, so answer from general "
        "automotive knowledge. Be helpful but note when something should be "
        "verified against the printed manual. Return an EMPTY citations list — "
        "do not invent sources."
    )


def _citations_from_context(context: list[ContextChunk]) -> list[Citation]:
    seen: set[tuple[str, str]] = set()
    out: list[Citation] = []
    for c in context:
        key = (c.manual, c.ref)
        if key in seen:
            continue
        seen.add(key)
        out.append(Citation(tag=c.manual, ref=c.ref))
        if len(out) >= 3:
            break
    return out


def _fallback(car: Car) -> GroundedAnswer:
    return GroundedAnswer(
        text=(
            f"The language model isn't configured yet, so I can't answer about "
            f"your {car.make} {car.model} live. Add GOOGLE_API_KEY to backend/.env "
            "to enable real answers."
        ),
        citations=[],
    )


async def answer_question(
    car: Car,
    question: str,
    context: list[ContextChunk] | None = None,
) -> GroundedAnswer:
    if not llm_available():
        return _fallback(car)

    context = context or []
    model = structured_model(GroundedAnswer)
    messages = [
        SystemMessage(content=_system_prompt(car, context)),
        HumanMessage(content=question),
    ]
    try:
        result = await model.ainvoke(messages)
        # with_structured_output usually returns the Pydantic instance; tolerate
        # a plain dict too.
        if isinstance(result, GroundedAnswer):
            answer = result
        elif isinstance(result, dict):
            answer = GroundedAnswer(**result)
        else:
            answer = GroundedAnswer.model_validate(result)

        # Smaller local models often answer from the context but leave citations
        # empty. Since the answer was built from these excerpts, attribute them.
        if context and not answer.citations:
            answer.citations = _citations_from_context(context)
        return answer
    except Exception:
        # Never let an LLM/network hiccup 500 the chat endpoint.
        return GroundedAnswer(
            text="I hit a problem reaching the language model. Please try again.",
            citations=[],
        )
