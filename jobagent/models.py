from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class StopReason(str, Enum):
    COMPLETED = "COMPLETED"
    NEED_USER_APPROVAL = "NEED_USER_APPROVAL"
    NEED_MORE_INPUT = "NEED_MORE_INPUT"
    TOOL_ERROR = "TOOL_ERROR"
    BUDGET_EXCEEDED = "BUDGET_EXCEEDED"
    LOW_CONFIDENCE = "LOW_CONFIDENCE"
    UNSAFE_OR_DISALLOWED_ACTION = "UNSAFE_OR_DISALLOWED_ACTION"


@dataclass
class Source:
    title: str
    url: str
    note: str = ""


@dataclass
class JDExtract:
    role_title: str
    company_name: str
    responsibilities: list[str]
    required_skills: list[str]
    preferred_skills: list[str]
    domain_signals: list[str]
    seniority_signals: list[str]
    location_signals: list[str]
    unknowns: list[str] = field(default_factory=list)


@dataclass
class CompanyBrief:
    company_summary: str
    product_lines: list[str]
    business_model: str
    recent_signals: list[str]
    engineering_relevance: list[str]
    risks: list[str]
    sources: list[Source]


@dataclass
class FitAnalysis:
    technical_match: int
    domain_interest: int
    logistics_match: int
    narrative_strength: int
    expected_roi: int
    decision: str
    evidence: list[str]
    concerns: list[str]

    @property
    def total(self) -> int:
        return (
            self.technical_match
            + self.domain_interest
            + self.logistics_match
            + self.narrative_strength
            + self.expected_roi
        )


@dataclass
class ResumeProposal:
    bullet_rewrites: list[str]
    cover_letter_outline: list[str]
    recruiter_note: str
    approval_required: bool = True


@dataclass
class TrackerUpdate:
    company_name: str
    role_title: str
    status: str
    fit_score: int
    next_action: str
    notes: list[str]


@dataclass
class InterviewPack:
    technical_questions: list[str]
    behavioral_questions: list[str]
    company_questions: list[str]
    story_matches: list[str]


@dataclass
class RunBudget:
    max_steps: int = 12
    max_tool_calls: int = 20
    steps_used: int = 0
    tool_calls_used: int = 0


@dataclass
class OrchestratorDecision:
    step: int
    action: str
    node: str | None
    rationale: str
    confidence: float
    budget_remaining_steps: int
    budget_remaining_tool_calls: int


@dataclass
class ToolAuditEvent:
    tool_name: str
    node: str
    status: str
    input_summary: str
    output_summary: str
    elapsed_ms: float
    cost_estimate: float = 0.0
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class EvalSummary:
    score: float
    passed: bool
    checks: list[str]
    failure_categories: list[str] = field(default_factory=list)


@dataclass
class AgentError:
    node: str
    message: str
    recoverable: bool = True


@dataclass
class JobSearchState:
    run_id: str
    user_goal: str
    owner_session_hash: str | None = None
    job_url: str | None = None
    raw_job_text: str | None = None
    company_name: str | None = None
    role_title: str | None = None
    normalized_jd: JDExtract | None = None
    company_brief: CompanyBrief | None = None
    fit_analysis: FitAnalysis | None = None
    resume_proposal: ResumeProposal | None = None
    tracker_update: TrackerUpdate | None = None
    interview_pack: InterviewPack | None = None
    sources: list[Source] = field(default_factory=list)
    story_bank: list[dict[str, Any]] = field(default_factory=list)
    messages: list[str] = field(default_factory=list)
    budget: RunBudget = field(default_factory=RunBudget)
    orchestrator_decisions: list[OrchestratorDecision] = field(default_factory=list)
    tool_audit: list[ToolAuditEvent] = field(default_factory=list)
    eval_summary: EvalSummary | None = None
    errors: list[AgentError] = field(default_factory=list)
    approved: bool = False
    stop_reason: StopReason | None = None
    pending_node: str | None = None
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        if self.stop_reason:
            data["stop_reason"] = self.stop_reason.value
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "JobSearchState":
        nested = dict(data)
        for key, factory in (
            ("normalized_jd", JDExtract),
            ("company_brief", CompanyBrief),
            ("fit_analysis", FitAnalysis),
            ("resume_proposal", ResumeProposal),
            ("tracker_update", TrackerUpdate),
            ("interview_pack", InterviewPack),
            ("budget", RunBudget),
            ("eval_summary", EvalSummary),
        ):
            if nested.get(key) is not None:
                if key == "company_brief":
                    brief = dict(nested[key])
                    brief["sources"] = [Source(**source) for source in brief.get("sources", [])]
                    nested[key] = CompanyBrief(**brief)
                else:
                    nested[key] = factory(**nested[key])
        nested["sources"] = [Source(**source) for source in nested.get("sources", [])]
        nested["errors"] = [AgentError(**error) for error in nested.get("errors", [])]
        nested["orchestrator_decisions"] = [
            OrchestratorDecision(**decision) for decision in nested.get("orchestrator_decisions", [])
        ]
        nested["tool_audit"] = [ToolAuditEvent(**event) for event in nested.get("tool_audit", [])]
        if nested.get("stop_reason"):
            nested["stop_reason"] = StopReason(nested["stop_reason"])
        return cls(**nested)
