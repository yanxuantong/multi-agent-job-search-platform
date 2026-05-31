from __future__ import annotations

from jobagent.models import EvalSummary, JobSearchState, StopReason


def summarize_run_quality(state: JobSearchState) -> EvalSummary:
    checks: list[str] = []
    failures: list[str] = []

    _record(checks, failures, "jd_extracted", bool(state.normalized_jd), "extraction")
    _record(checks, failures, "fit_analysis_present", bool(state.fit_analysis), "fit_analysis")
    _record(checks, failures, "resume_proposal_present", bool(state.resume_proposal), "resume")
    _record(checks, failures, "orchestrator_decisions_present", bool(state.orchestrator_decisions), "orchestration")
    _record(checks, failures, "tool_audit_present", bool(state.tool_audit), "tool_audit")
    if state.stop_reason == StopReason.COMPLETED:
        _record(checks, failures, "tracker_update_present", bool(state.tracker_update), "side_effect")
        _record(checks, failures, "interview_pack_present", bool(state.interview_pack), "interview_prep")
    else:
        _record(
            checks,
            failures,
            "safe_pause_before_side_effect",
            state.stop_reason == StopReason.NEED_USER_APPROVAL and state.tracker_update is None,
            "hitl",
        )

    passed_count = sum(1 for check in checks if check.endswith(":pass"))
    score = round(passed_count / len(checks), 3) if checks else 0.0
    return EvalSummary(
        score=score,
        passed=not failures,
        checks=checks,
        failure_categories=sorted(set(failures)),
    )


def _record(checks: list[str], failures: list[str], name: str, passed: bool, category: str) -> None:
    checks.append(f"{name}:{'pass' if passed else 'fail'}")
    if not passed:
        failures.append(category)
