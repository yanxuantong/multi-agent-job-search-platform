from __future__ import annotations

from typing import Any

from jobagent.graph.workflow import build_graph
from jobagent.models import JobSearchState, StopReason
from jobagent.observability import JsonlTracer


LANGGRAPH_MIGRATION_NOTES = [
    "Replace GraphEngine.add_node with StateGraph.add_node.",
    "Replace NodeResult.next_node with conditional edges.",
    "Replace StopReason.NEED_USER_APPROVAL with LangGraph interrupt().",
    "Replace JsonCheckpointStore with a LangGraph checkpointer such as SQLite or Postgres.",
    "Keep JobSearchState as the contract so agent nodes do not pass loose strings.",
]


def build_langgraph_reference_app(run_id: str):
    """Build a LangGraph app when optional dependencies are installed.

    This adapter is intentionally not used by the default CLI. The default path
    stays dependency-free, while this file gives the original Project 1 stack a
    concrete place to land.
    """

    try:
        from langgraph.graph import END, StateGraph
        from langgraph.checkpoint.memory import InMemorySaver
    except ImportError as exc:  # pragma: no cover - depends on optional extras.
        raise RuntimeError(
            "LangGraph is not installed. Run: python3 -m pip install -e '.[langgraph]'"
        ) from exc

    teaching_graph = build_graph(JsonlTracer(run_id))
    graph = StateGraph(dict)

    def make_node(name: str):
        def _node(state_dict: dict[str, Any]) -> dict[str, Any]:
            state = JobSearchState.from_dict(state_dict)
            result = teaching_graph.nodes[name](state)
            state.pending_node = result.next_node
            state.stop_reason = result.stop_reason
            return state.to_dict()

        return _node

    for node_name in teaching_graph.nodes:
        graph.add_node(node_name, make_node(node_name))

    graph.set_entry_point("ingest")
    graph.add_edge("ingest", "jd_extract")
    graph.add_edge("jd_extract", "company_research")
    graph.add_edge("company_research", "fit_analysis")
    graph.add_edge("fit_analysis", "resume_tailor")
    graph.add_conditional_edges(
        "resume_tailor",
        _resume_route,
        {
            "tracker": "tracker",
            "end": END,
        },
    )
    graph.add_edge("tracker", "interview_prep")
    graph.add_edge("interview_prep", END)
    return graph.compile(checkpointer=InMemorySaver())


def _resume_route(state: dict[str, Any]) -> str:
    if state.get("stop_reason") == StopReason.NEED_USER_APPROVAL.value:
        return "end"
    return "tracker"
