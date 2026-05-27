from __future__ import annotations

from jobagent.graph import NodeResult
from jobagent.models import JobSearchState, StopReason


def ingest_job_text(state: JobSearchState) -> NodeResult:
    if not state.raw_job_text or len(state.raw_job_text.strip()) < 40:
        state.messages.append("Please provide a pasted job description or a readable job URL fetch result.")
        return NodeResult(stop_reason=StopReason.NEED_MORE_INPUT)
    state.messages.append("Job text ingested and ready for structured extraction.")
    return NodeResult(next_node="jd_extract")

