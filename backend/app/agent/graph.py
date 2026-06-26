"""The ingestion state graph.

    START → parse → search → validate ─┬─(coverage)──→ fetch → ingest → END
                          ▲            ├─(retry)─────→ search
                          └────────────┘
                                       └─(give up)───→ END  (failed event emitted)

Compiled once and reused. Run it with `stream_mode="custom"` to receive the
IngestionEvents the nodes emit.
"""

from __future__ import annotations

from functools import lru_cache

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from app.agent.nodes import fetch, ingest, parse, search, validate
from app.agent.state import AgentState


def _route_after_validate(state: AgentState) -> str:
    if state.get("failed"):
        return "give_up"
    if state.get("selected"):
        return "proceed"
    return "retry"


def _route_after_fetch(state: AgentState) -> str:
    # No real PDF downloaded → end (the UI shows the upload prompt).
    return "give_up" if state.get("failed") else "ingest"


def build_graph() -> CompiledStateGraph:
    builder = StateGraph(AgentState)
    builder.add_node("parse", parse)
    builder.add_node("search", search)
    builder.add_node("validate", validate)
    builder.add_node("fetch", fetch)
    builder.add_node("ingest", ingest)

    builder.add_edge(START, "parse")
    builder.add_edge("parse", "search")
    builder.add_edge("search", "validate")
    builder.add_conditional_edges(
        "validate",
        _route_after_validate,
        {"proceed": "fetch", "retry": "search", "give_up": END},
    )
    builder.add_conditional_edges(
        "fetch",
        _route_after_fetch,
        {"ingest": "ingest", "give_up": END},
    )
    builder.add_edge("ingest", END)

    return builder.compile()


@lru_cache
def get_graph() -> CompiledStateGraph:
    return build_graph()
