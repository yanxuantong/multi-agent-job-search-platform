from __future__ import annotations

from jobagent.graph import NodeResult
from jobagent.memory import match_stories
from jobagent.models import FitAnalysis, JobSearchState, StopReason


def analyze_fit(state: JobSearchState) -> NodeResult:
    jd = state.normalized_jd
    if not jd:
        raise ValueError("JD extraction must run before fit analysis")

    matches = match_stories(state.story_bank, jd.required_skills)
    technical = min(5, max(1, len(set(jd.required_skills)) // 2))
    narrative = min(5, max(1, len(matches) + 1))
    domain = 4 if any(signal in jd.domain_signals for signal in ("ai", "infra", "developer tools")) else 3
    logistics = 3 if not jd.location_signals else 4
    roi = 4 if technical + narrative >= 6 else 3
    total = technical + narrative + domain + logistics + roi
    decision = "apply" if total >= 16 else "review"

    state.fit_analysis = FitAnalysis(
        technical_match=technical,
        domain_interest=domain,
        logistics_match=logistics,
        narrative_strength=narrative,
        expected_roi=roi,
        decision=decision,
        evidence=[
            f"Matched skills: {', '.join(jd.required_skills[:8]) or 'none'}",
            f"Matched story count: {len(matches)}",
            f"Domain signals: {', '.join(jd.domain_signals) or 'none'}",
        ],
        concerns=[] if decision == "apply" else ["Fit score is below apply threshold; review before spending time."],
    )
    state.messages.append(f"Fit analysis decision: {decision} ({total}/25).")
    if total < 12:
        return NodeResult(stop_reason=StopReason.LOW_CONFIDENCE)
    return NodeResult(next_node="resume_tailor")

