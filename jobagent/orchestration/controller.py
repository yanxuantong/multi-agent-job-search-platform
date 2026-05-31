from __future__ import annotations

from dataclasses import dataclass

from jobagent.models import JobSearchState, OrchestratorDecision, StopReason
from jobagent.tools.registry import ToolRegistry


@dataclass(frozen=True)
class NextAction:
    action: str
    node: str | None
    rationale: str
    confidence: float


class JobSearchOrchestrator:
    """Control plane for routing, budget checks, and decision audit."""

    def __init__(self, tools: ToolRegistry | None = None) -> None:
        self.tools = tools or ToolRegistry.default()

    def plan(self, state: JobSearchState, node: str) -> NextAction:
        if state.budget.steps_used >= state.budget.max_steps:
            return NextAction(
                action="STOP",
                node=None,
                rationale="Step budget exhausted before the next node could run.",
                confidence=1.0,
            )
        if state.budget.tool_calls_used >= state.budget.max_tool_calls:
            return NextAction(
                action="STOP",
                node=None,
                rationale="Tool-call budget exhausted before the next node could run.",
                confidence=1.0,
            )
        if node not in self.tools.node_tools:
            return NextAction(
                action="BLOCK",
                node=None,
                rationale=f"No approved tool boundary is registered for node '{node}'.",
                confidence=0.95,
            )
        if node == "tracker" and not state.approved:
            return NextAction(
                action="ASK_HUMAN",
                node=node,
                rationale="Tracker updates are side effects and require explicit human approval.",
                confidence=1.0,
            )
        return NextAction(
            action="RUN_AGENT",
            node=node,
            rationale=f"Run bounded node '{node}' through its registered tool boundary.",
            confidence=0.9,
        )

    def record(self, state: JobSearchState, action: NextAction) -> None:
        state.orchestrator_decisions.append(
            OrchestratorDecision(
                step=state.budget.steps_used + 1,
                action=action.action,
                node=action.node,
                rationale=action.rationale,
                confidence=action.confidence,
                budget_remaining_steps=max(0, state.budget.max_steps - state.budget.steps_used),
                budget_remaining_tool_calls=max(0, state.budget.max_tool_calls - state.budget.tool_calls_used),
            )
        )
        if action.action == "STOP":
            state.stop_reason = StopReason.BUDGET_EXCEEDED
        elif action.action == "BLOCK":
            state.stop_reason = StopReason.UNSAFE_OR_DISALLOWED_ACTION
        elif action.action == "ASK_HUMAN":
            state.stop_reason = StopReason.NEED_USER_APPROVAL
            state.pending_node = action.node
