from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import time

from jobagent.models import AgentError, JobSearchState, StopReason
from jobagent.observability import JsonlTracer
from jobagent.orchestration import JobSearchOrchestrator
from jobagent.tools import ToolRegistry, summarize_node_output


@dataclass
class NodeResult:
    next_node: str | None = None
    stop_reason: StopReason | None = None


NodeFn = Callable[[JobSearchState], NodeResult]


class GraphEngine:
    """Tiny graph runner that mirrors the LangGraph mental model for learning."""

    def __init__(
        self,
        tracer: JsonlTracer,
        orchestrator: JobSearchOrchestrator | None = None,
        tools: ToolRegistry | None = None,
    ) -> None:
        self.tracer = tracer
        self.tools = tools or ToolRegistry.default()
        self.orchestrator = orchestrator or JobSearchOrchestrator(self.tools)
        self.nodes: dict[str, NodeFn] = {}

    def add_node(self, name: str, fn: NodeFn) -> None:
        self.nodes[name] = fn

    def run(self, state: JobSearchState, start: str) -> JobSearchState:
        current = start
        while current:
            action = self.orchestrator.plan(state, current)
            self.orchestrator.record(state, action)
            if action.action in {"STOP", "BLOCK"}:
                return state
            if action.action == "ASK_HUMAN":
                return state
            if current not in self.nodes:
                state.errors.append(AgentError(current, f"Unknown node: {current}", recoverable=False))
                state.stop_reason = StopReason.TOOL_ERROR
                return state

            state.budget.steps_used += 1
            state.budget.tool_calls_used += 1
            started = time.perf_counter()
            with self.tracer.span(current) as metadata:
                metadata["step"] = state.budget.steps_used
                metadata["tool_call"] = self.tools.get_for_node(current).name if self.tools.get_for_node(current) else None
                metadata["orchestrator_action"] = action.action
                metadata["orchestrator_rationale"] = action.rationale
                try:
                    result = self.nodes[current](state)
                    metadata["next_node"] = result.next_node
                    metadata["stop_reason"] = result.stop_reason.value if result.stop_reason else None
                except Exception as exc:  # noqa: BLE001 - convert node exceptions into graph state.
                    state.errors.append(AgentError(current, str(exc), recoverable=False))
                    state.stop_reason = StopReason.TOOL_ERROR
                    metadata["stop_reason"] = state.stop_reason.value
                    elapsed_ms = (time.perf_counter() - started) * 1000
                    self.tools.audit(
                        state,
                        current,
                        status="error",
                        elapsed_ms=elapsed_ms,
                        output_summary=str(exc),
                    )
                    return state
            elapsed_ms = (time.perf_counter() - started) * 1000
            self.tools.audit(
                state,
                current,
                status="stopped" if result.stop_reason else "ok",
                elapsed_ms=elapsed_ms,
                output_summary=summarize_node_output(state, current),
            )

            if result.stop_reason:
                state.stop_reason = result.stop_reason
                state.pending_node = result.next_node
                return state
            current = result.next_node

        state.stop_reason = state.stop_reason or StopReason.COMPLETED
        state.pending_node = None
        return state
