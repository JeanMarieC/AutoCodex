"""Phase 2.7 — evaluation harness logic (offline, fakes for retrieval + LLM)."""

from app.eval.dataset import EVAL_ITEMS
from app.eval.harness import format_report, run_eval
from app.eval.metrics import keyword_recall, retrieval_hit
from app.llm.rag import ContextChunk, GroundedAnswer

_SECTION = {it.question: it.expected_section for it in EVAL_ITEMS}
_KEYWORDS = {it.question: it.expected_keywords for it in EVAL_ITEMS}


def test_metric_units():
    ctx = [ContextChunk(manual="Owner's Manual", ref="Engine Oil", text="...")]
    assert retrieval_hit(ctx, "Engine Oil") is True
    assert retrieval_hit(ctx, "Brake System") is False
    assert keyword_recall("use synthetic oil", ("synthetic", "oil")) == 1.0
    assert keyword_recall("use oil", ("synthetic", "oil")) == 0.5


async def test_run_eval_perfect_scores():
    def fake_retrieve(_car, q):
        return [ContextChunk(manual="Owner's Manual", ref=_SECTION[q], text="ctx")]

    async def fake_answer(_car, q, _ctx):
        return GroundedAnswer(text=" ".join(_KEYWORDS[q]), citations=[])

    report = await run_eval(retrieve_fn=fake_retrieve, answer_fn=fake_answer, judge=False)
    assert report.retrieval_accuracy == 1.0
    assert report.avg_keyword_recall == 1.0
    assert report.avg_faithfulness is None
    assert "Retrieval accuracy" in format_report(report)


async def test_run_eval_detects_retrieval_miss():
    def bad_retrieve(_car, _q):
        return [ContextChunk(manual="Owner's Manual", ref="Wrong Section", text="ctx")]

    async def empty_answer(_car, _q, _ctx):
        return GroundedAnswer(text="no idea", citations=[])

    report = await run_eval(retrieve_fn=bad_retrieve, answer_fn=empty_answer, judge=False)
    assert report.retrieval_accuracy == 0.0
