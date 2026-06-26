"""Run the evaluation: `uv run python -m app.eval`.

Builds the eval car's index from sample manuals, runs the labeled set against the
real vector store + Gemini, and prints a metrics report.
"""

from __future__ import annotations

import asyncio
import sys

from app.eval.dataset import EVAL_CAR
from app.eval.harness import format_report, run_eval
from app.llm.client import llm_available
from app.rag.process import process_manuals
from app.rag.store import embeddings_available, index_chunks

_FETCHED = [
    {"name": "Owner's Manual", "kind": "owner", "url": "", "source": "manualslib",
     "ok": True, "path": None},
    {"name": "Workshop Manual", "kind": "workshop", "url": "", "source": "archive",
     "ok": True, "path": None},
]


def _build_index() -> int:
    chunks, _ = process_manuals(EVAL_CAR, _FETCHED)
    return index_chunks(EVAL_CAR, chunks)


async def _main() -> None:
    # Windows consoles default to cp1252; avoid crashes on any unicode in output.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if not embeddings_available():
        print("GOOGLE_API_KEY not set - cannot embed/retrieve. Aborting.")
        return
    n = _build_index()
    car = f"{EVAL_CAR.make} {EVAL_CAR.model} {EVAL_CAR.year}"
    print(f"Indexed {n} chunks for {car}. Running eval...")
    # Pace calls so free-tier rate limits don't throttle the back half.
    report = await run_eval(judge=llm_available(), delay=6.0)
    print(format_report(report))


if __name__ == "__main__":
    asyncio.run(_main())
