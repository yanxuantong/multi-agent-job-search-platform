from __future__ import annotations

from uuid import uuid4

from jobagent.agents import (
    analyze_fit,
    extract_jd,
    ingest_job_text,
    prepare_interview_pack,
    propose_tracker_update,
    research_company,
    tailor_resume,
)
from jobagent.evals.run_quality import summarize_run_quality
from jobagent.graph import GraphEngine
from jobagent.models import JobSearchState, StopReason
from jobagent.observability import JsonlTracer
from jobagent.storage import JsonCheckpointStore


def build_graph(tracer: JsonlTracer) -> GraphEngine:
    graph = GraphEngine(tracer)
    graph.add_node("ingest", ingest_job_text)
    graph.add_node("jd_extract", extract_jd)
    graph.add_node("company_research", research_company)
    graph.add_node("fit_analysis", analyze_fit)
    graph.add_node("resume_tailor", tailor_resume)
    graph.add_node("tracker", propose_tracker_update)
    graph.add_node("interview_prep", prepare_interview_pack)
    return graph


def run_job_workflow(
    raw_job_text: str,
    story_bank: list[dict],
    *,
    job_url: str | None = None,
    user_goal: str = "decide_apply_and_prepare",
    approved: bool = False,
    run_id: str | None = None,
) -> JobSearchState:
    run_id = run_id or str(uuid4())
    state = JobSearchState(
        run_id=run_id,
        user_goal=user_goal,
        job_url=job_url,
        raw_job_text=raw_job_text,
        story_bank=story_bank,
        approved=approved,
    )
    graph = build_graph(JsonlTracer(state.run_id))
    state = graph.run(state, "ingest")
    state.eval_summary = summarize_run_quality(state)
    JsonCheckpointStore().save(state)
    return state


def resume_job_workflow(run_id: str, *, approved: bool) -> JobSearchState:
    store = JsonCheckpointStore()
    state = store.load(run_id)
    state = resume_job_state(state, approved=approved)
    store.save(state)
    return state


def resume_job_state(state: JobSearchState, *, approved: bool) -> JobSearchState:
    if not state.pending_node:
        return state
    state.approved = approved
    if not approved:
        state.stop_reason = state.stop_reason or StopReason.NEED_USER_APPROVAL
        state.messages.append("Resume proposal was rejected; workflow remains paused before side effects.")
        return state
    state.stop_reason = None
    graph = build_graph(JsonlTracer(state.run_id))
    state = graph.run(state, state.pending_node)
    state.eval_summary = summarize_run_quality(state)
    return state
