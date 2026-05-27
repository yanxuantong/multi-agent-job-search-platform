from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from jobagent.models import AgentError, JobSearchState, StopReason
from jobagent.observability import JsonlTracer


@dataclass
class NodeResult:
    next_node: str | None = None
    stop_reason: StopReason | None = None


NodeFn = Callable[[JobSearchState], NodeResult]


class GraphEngine:
    """Tiny graph runner that mirrors the LangGraph mental model for learning."""

    def __init__(self, tracer: JsonlTracer) -> None:
        self.tracer = tracer
        self.nodes: dict[str, NodeFn] = {}

    def add_node(self, name: str, fn: NodeFn) -> None:
        self.nodes[name] = fn

    def run(self, state: JobSearchState, start: str) -> JobSearchState:
        current = start
        while current:
            if state.budget.steps_used >= state.budget.max_steps:
                state.stop_reason = StopReason.BUDGET_EXCEEDED
                return state
            if current not in self.nodes:
                state.errors.append(AgentError(current, f"Unknown node: {current}", recoverable=False))
                state.stop_reason = StopReason.TOOL_ERROR
                return state

            state.budget.steps_used += 1
            with self.tracer.span(current) as metadata:
                metadata["step"] = state.budget.steps_used
                try:
                    result = self.nodes[current](state)
                    metadata["next_node"] = result.next_node
                    metadata["stop_reason"] = result.stop_reason.value if result.stop_reason else None
                except Exception as exc:  # noqa: BLE001 - convert node exceptions into graph state.
                    state.errors.append(AgentError(current, str(exc), recoverable=False))
                    state.stop_reason = StopReason.TOOL_ERROR
                    metadata["stop_reason"] = state.stop_reason.value
                    return state

            if result.stop_reason:
                state.stop_reason = result.stop_reason
                state.pending_node = result.next_node
                return state
            current = result.next_node

        state.stop_reason = state.stop_reason or StopReason.COMPLETED
        state.pending_node = None
        return state
