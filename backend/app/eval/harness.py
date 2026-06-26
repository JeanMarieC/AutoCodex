"""Evaluation harness — runs the labeled set and aggregates metrics.

Retrieval and answering are injectable so the harness is testable offline; by
default they use the real vector store + Gemini.
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from app.agent.state import Car
from app.eval.dataset import EVAL_CAR, EVAL_ITEMS, EvalItem
from app.eval.metrics import judge_faithfulness, keyword_recall, retrieval_hit
from app.llm.rag import ContextChunk, GroundedAnswer, answer_question
from app.rag.store import retrieve

RetrieveFn = Callable[[Car, str], list[ContextChunk]]
AnswerFn = Callable[[Car, str, list[ContextChunk]], Awaitable[GroundedAnswer]]


@dataclass
class EvalResult:
    question: str
    retrieval_hit: bool
    keyword_recall: float
    faithfulness: float | None


@dataclass
class EvalReport:
    results: list[EvalResult]
    retrieval_accuracy: float
    avg_keyword_recall: float
    avg_faithfulness: float | None


async def run_eval(
    *,
    items: list[EvalItem] | None = None,
    retrieve_fn: RetrieveFn = retrieve,
    answer_fn: AnswerFn = answer_question,
    judge: bool = True,
    delay: float = 0.0,
) -> EvalReport:
    """Run the labeled set. `delay` paces calls to respect free-tier rate limits."""
    items = items or EVAL_ITEMS
    results: list[EvalResult] = []

    for i, item in enumerate(items):
        if delay and i:
            await asyncio.sleep(delay)
        contexts = retrieve_fn(EVAL_CAR, item.question)
        answer = await answer_fn(EVAL_CAR, item.question, contexts)
        results.append(
            EvalResult(
                question=item.question,
                retrieval_hit=retrieval_hit(contexts, item.expected_section),
                keyword_recall=keyword_recall(answer.text, item.expected_keywords),
                faithfulness=judge_faithfulness(answer.text, contexts) if judge else None,
            )
        )

    n = len(results)
    faiths = [r.faithfulness for r in results if r.faithfulness is not None]
    return EvalReport(
        results=results,
        retrieval_accuracy=sum(r.retrieval_hit for r in results) / n if n else 0.0,
        avg_keyword_recall=sum(r.keyword_recall for r in results) / n if n else 0.0,
        avg_faithfulness=(sum(faiths) / len(faiths)) if faiths else None,
    )


def format_report(report: EvalReport) -> str:
    lines = ["", "Question                                          hit   recall  faith", "-" * 72]
    for r in report.results:
        faith = "  -  " if r.faithfulness is None else f"{r.faithfulness:.2f}"
        lines.append(
            f"{r.question[:48]:<48} {'Y' if r.retrieval_hit else 'N':^5} "
            f"{r.keyword_recall:>5.2f}  {faith:>5}"
        )
    faith = "n/a (LLM off)" if report.avg_faithfulness is None else f"{report.avg_faithfulness:.0%}"
    lines += [
        "-" * 72,
        f"Retrieval accuracy : {report.retrieval_accuracy:.0%}",
        f"Answer correctness : {report.avg_keyword_recall:.0%}  (keyword recall)",
        f"Answer faithfulness: {faith}",
        "",
    ]
    return "\n".join(lines)
