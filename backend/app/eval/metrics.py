"""Evaluation metrics.

  • retrieval_hit     — did retrieval surface the expected manual section?
  • keyword_recall    — does the answer mention the expected facts? (correctness proxy)
  • judge_faithfulness — LLM-as-judge: is the answer fully supported by the
                         retrieved context? (0..1). Requires the LLM; skipped otherwise.
"""

from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from app.llm.client import llm_available, structured_model
from app.llm.rag import ContextChunk


def retrieval_hit(contexts: list[ContextChunk], expected_section: str) -> bool:
    target = expected_section.lower()
    return any((c.ref or "").lower() == target for c in contexts)


def keyword_recall(answer: str, keywords: tuple[str, ...]) -> float:
    if not keywords:
        return 1.0
    text = answer.lower()
    return sum(1 for k in keywords if k.lower() in text) / len(keywords)


class _Judgment(BaseModel):
    score: float = Field(description="0..1: how fully the answer is supported by the context")
    reason: str = ""


_JUDGE_SYSTEM = (
    "You grade RAG answers for faithfulness. Given CONTEXT excerpts and an ANSWER, "
    "return a score from 0 to 1: 1.0 if every claim in the answer is supported by "
    "the context, 0.0 if it is unsupported or contradicted. Judge only support, not "
    "style."
)


def judge_faithfulness(answer: str, contexts: list[ContextChunk]) -> float | None:
    """LLM-as-judge faithfulness in [0,1], or None when the LLM/context is unavailable."""
    if not llm_available() or not contexts:
        return None
    ctx = "\n\n".join(f"[{c.manual} · {c.ref}] {c.text}" for c in contexts)
    model = structured_model(_Judgment)
    try:
        result = model.invoke(
            [
                SystemMessage(content=_JUDGE_SYSTEM),
                HumanMessage(content=f"CONTEXT:\n{ctx}\n\nANSWER:\n{answer}"),
            ]
        )
        judgment = result if isinstance(result, _Judgment) else _Judgment.model_validate(result)
        return max(0.0, min(1.0, float(judgment.score)))
    except Exception:
        return None
