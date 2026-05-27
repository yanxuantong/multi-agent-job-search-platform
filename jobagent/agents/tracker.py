from __future__ import annotations

from jobagent.graph import NodeResult
from jobagent.models import JobSearchState, TrackerUpdate
from jobagent.storage import JsonlApplicationTracker


def propose_tracker_update(state: JobSearchState) -> NodeResult:
    jd = state.normalized_jd
    fit = state.fit_analysis
    if not jd or not fit:
        raise ValueError("JD and fit analysis must run before tracker update")

    update = TrackerUpdate(
        company_name=jd.company_name,
        role_title=jd.role_title,
        status="ready_to_apply",
        fit_score=fit.total,
        next_action="Review generated resume bullets, then submit manually.",
        notes=fit.evidence + fit.concerns,
    )
    state.tracker_update = update
    JsonlApplicationTracker().append(update)
    state.messages.append("Application tracker update written.")
    return NodeResult(next_node="interview_prep")

