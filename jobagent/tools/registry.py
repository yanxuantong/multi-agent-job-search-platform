from __future__ import annotations

from dataclasses import dataclass

from jobagent.models import JobSearchState, ToolAuditEvent


@dataclass(frozen=True)
class ToolSpec:
    name: str
    node: str
    purpose: str
    side_effect: bool = False
    cost_estimate: float = 0.0


class ToolRegistry:
    """Registry of approved node/tool boundaries for audit and policy checks."""

    def __init__(self, specs: list[ToolSpec]) -> None:
        self.node_tools = {spec.node: spec for spec in specs}

    @classmethod
    def default(cls) -> "ToolRegistry":
        return cls(
            [
                ToolSpec("jd_intake_validator", "ingest", "validate and normalize submitted job text"),
                ToolSpec("jd_signal_extractor", "jd_extract", "extract company, role, skills, and domain signals"),
                ToolSpec("company_brief_builder", "company_research", "produce a sourced company brief"),
                ToolSpec("fit_score_calculator", "fit_analysis", "score role fit against the story bank"),
                ToolSpec("resume_proposal_builder", "resume_tailor", "draft human-reviewable positioning"),
                ToolSpec("application_tracker_writer", "tracker", "prepare tracker update", side_effect=True),
                ToolSpec("interview_pack_builder", "interview_prep", "produce interview preparation packet"),
            ]
        )

    def get_for_node(self, node: str) -> ToolSpec | None:
        return self.node_tools.get(node)

    def audit(
        self,
        state: JobSearchState,
        node: str,
        *,
        status: str,
        elapsed_ms: float,
        output_summary: str,
    ) -> None:
        spec = self.get_for_node(node)
        if spec is None:
            return
        state.tool_audit.append(
            ToolAuditEvent(
                tool_name=spec.name,
                node=node,
                status=status,
                input_summary=_input_summary(state, node),
                output_summary=output_summary,
                elapsed_ms=round(elapsed_ms, 2),
                cost_estimate=spec.cost_estimate,
            )
        )


def _input_summary(state: JobSearchState, node: str) -> str:
    if node == "ingest":
        return f"job_text_chars={len(state.raw_job_text or '')}"
    if node == "jd_extract":
        return "raw_job_text"
    if node == "company_research":
        return f"company={state.company_name or 'unknown'} role={state.role_title or 'unknown'}"
    if node == "fit_analysis":
        return f"stories={len(state.story_bank)}"
    if node == "resume_tailor":
        return f"fit_score={state.fit_analysis.total if state.fit_analysis else 'missing'}"
    if node == "tracker":
        return f"approved={state.approved}"
    if node == "interview_prep":
        return f"company={state.company_name or 'unknown'}"
    return "state"


def summarize_node_output(state: JobSearchState, node: str) -> str:
    if node == "ingest":
        return state.messages[-1] if state.messages else "ingested"
    if node == "jd_extract":
        return f"{state.company_name or 'Unknown'} - {state.role_title or 'Unknown'}"
    if node == "company_research":
        return state.company_brief.company_summary if state.company_brief else "no company brief"
    if node == "fit_analysis":
        return f"fit={state.fit_analysis.total}/25 decision={state.fit_analysis.decision}" if state.fit_analysis else "no fit"
    if node == "resume_tailor":
        return f"bullets={len(state.resume_proposal.bullet_rewrites)}" if state.resume_proposal else "no proposal"
    if node == "tracker":
        return state.tracker_update.status if state.tracker_update else "no tracker update"
    if node == "interview_prep":
        return f"questions={len(state.interview_pack.technical_questions)}" if state.interview_pack else "no prep"
    return "completed"
