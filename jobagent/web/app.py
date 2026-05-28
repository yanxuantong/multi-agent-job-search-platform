from __future__ import annotations

import os
import re
import time
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from pathlib import Path
from urllib.parse import parse_qs

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from jobagent.graph.workflow import resume_job_state, run_job_workflow
from jobagent.memory import load_story_bank
from jobagent.models import JobSearchState, StopReason
from jobagent.web.store import RunStore, build_run_store


PACKAGE_DIR = Path(__file__).parent
TEMPLATE_DIR = PACKAGE_DIR / "templates"
STATIC_DIR = PACKAGE_DIR / "static"
DEFAULT_JOB_FILE = Path("samples/job_description.txt")
DEFAULT_STORY_BANK = Path("samples/story_bank.json")
MAX_REQUEST_BODY_BYTES = int(os.environ.get("JOBAGENT_MAX_REQUEST_BODY_BYTES", "200000"))
MIN_JOB_TEXT_CHARS = 20
MAX_JOB_TEXT_CHARS = int(os.environ.get("JOBAGENT_MAX_JOB_TEXT_CHARS", "12000"))
MAX_JOB_URL_CHARS = int(os.environ.get("JOBAGENT_MAX_JOB_URL_CHARS", "2048"))
MAX_FORM_FIELDS = 8
RUN_ID_PATTERN = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
    re.IGNORECASE,
)
RATE_LIMIT_WINDOW_SECONDS = int(os.environ.get("JOBAGENT_RATE_LIMIT_WINDOW_SECONDS", "60"))
RATE_LIMIT_POST_RUNS = int(os.environ.get("JOBAGENT_RATE_LIMIT_POST_RUNS", "12"))


def create_app(store: RunStore | None = None) -> FastAPI:
    run_store = store or build_run_store()
    post_run_hits: defaultdict[str, deque[float]] = defaultdict(deque)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.run_store.ensure_schema()
        yield

    app = FastAPI(title="Multi-Agent Job Search Platform", version="0.1.0", lifespan=lifespan)
    app.state.run_store = run_store
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    templates = Jinja2Templates(directory=TEMPLATE_DIR)

    @app.middleware("http")
    async def production_safety_headers(request: Request, call_next):
        if request.method in {"POST", "PUT", "PATCH"}:
            content_length = request.headers.get("content-length")
            if content_length:
                try:
                    body_size = int(content_length)
                except ValueError:
                    return PlainTextResponse("Invalid Content-Length", status_code=400)
                if body_size > MAX_REQUEST_BODY_BYTES:
                    return PlainTextResponse("Request body too large", status_code=413)

        if request.method == "POST" and request.url.path == "/runs":
            retry_after = _rate_limit_retry_after(request, post_run_hits)
            if retry_after is not None:
                return PlainTextResponse(
                    "Too many workflow runs. Please wait before starting another run.",
                    status_code=429,
                    headers={"Retry-After": str(retry_after)},
                )

        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "no-referrer")
        response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        response.headers.setdefault(
            "Content-Security-Policy",
            "default-src 'self'; img-src 'self' data:; object-src 'none'; "
            "frame-ancestors 'none'; base-uri 'self'; form-action 'self'",
        )
        if request.url.scheme == "https" or request.headers.get("x-forwarded-proto") == "https":
            response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
        return response

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/", response_class=HTMLResponse)
    def index(request: Request) -> HTMLResponse:
        sample_text = DEFAULT_JOB_FILE.read_text(encoding="utf-8") if DEFAULT_JOB_FILE.exists() else ""
        runs = app.state.run_store.list_recent()
        run_summaries = [_run_summary(run) for run in runs]
        return templates.TemplateResponse(
            request,
            "index.html",
            {
                "sample_text": sample_text,
                "runs": run_summaries,
                "stats": _run_stats(run_summaries),
                "workflow_steps": _workflow_steps(),
                "agent_cards": _agent_cards(),
                "public_demo_mode": _public_demo_mode(),
            },
        )

    @app.post("/runs")
    async def create_run(request: Request) -> RedirectResponse:
        form = await _read_urlencoded_form(request)
        job_text = form.get("job_text", "").strip()
        job_url = form.get("job_url", "").strip() or None
        approved = form.get("auto_approve") == "on"
        validation_error = _validate_job_submission(job_text, job_url)
        if validation_error == "short_job_text":
            return RedirectResponse("/?error=short_job_text", status_code=303)
        if validation_error:
            raise HTTPException(status_code=400, detail=validation_error)

        stories = load_story_bank(DEFAULT_STORY_BANK)
        state = run_job_workflow(job_text, stories, job_url=job_url, approved=approved)
        app.state.run_store.save(state)
        return RedirectResponse(f"/runs/{state.run_id}", status_code=303)

    @app.get("/runs/{run_id}", response_class=HTMLResponse)
    def show_run(request: Request, run_id: str) -> HTMLResponse:
        _validate_run_id_or_404(run_id)
        state = _load_or_404(app.state.run_store, run_id)
        return templates.TemplateResponse(
            request,
            "run.html",
            {
                "state": state,
                "summary": _run_summary(state),
                "scores": _score_rows(state),
                "run_steps": _run_steps(state),
                "can_approve": state.stop_reason == StopReason.NEED_USER_APPROVAL and bool(state.pending_node),
                "public_demo_mode": _public_demo_mode(),
            },
        )

    @app.post("/runs/{run_id}/approve")
    def approve_run(run_id: str) -> RedirectResponse:
        _validate_run_id_or_404(run_id)
        state = _load_or_404(app.state.run_store, run_id)
        state = resume_job_state(state, approved=True)
        app.state.run_store.save(state)
        return RedirectResponse(f"/runs/{state.run_id}", status_code=303)

    return app


def _load_or_404(store: RunStore, run_id: str) -> JobSearchState:
    try:
        return store.load(run_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


async def _read_urlencoded_form(request: Request) -> dict[str, str]:
    content_type = request.headers.get("content-type", "").lower()
    if not content_type.startswith("application/x-www-form-urlencoded"):
        raise HTTPException(status_code=415, detail="Only application/x-www-form-urlencoded submissions are accepted")

    body_bytes = await request.body()
    if len(body_bytes) > MAX_REQUEST_BODY_BYTES:
        raise HTTPException(status_code=413, detail="Request body too large")

    try:
        body = body_bytes.decode("utf-8")
        parsed = parse_qs(body, keep_blank_values=True, max_num_fields=MAX_FORM_FIELDS)
    except (UnicodeDecodeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail="Invalid form body") from exc
    return {key: values[-1] if values else "" for key, values in parsed.items()}


def _validate_job_submission(job_text: str, job_url: str | None) -> str | None:
    if len(job_text) < MIN_JOB_TEXT_CHARS:
        return "short_job_text"
    if len(job_text) > MAX_JOB_TEXT_CHARS:
        return f"job_text must be at most {MAX_JOB_TEXT_CHARS} characters"
    if job_url:
        if len(job_url) > MAX_JOB_URL_CHARS:
            return f"job_url must be at most {MAX_JOB_URL_CHARS} characters"
        if not job_url.lower().startswith(("https://", "http://")):
            return "job_url must start with http:// or https://"
    return None


def _validate_run_id_or_404(run_id: str) -> None:
    if not RUN_ID_PATTERN.fullmatch(run_id):
        raise HTTPException(status_code=404, detail="Run not found")


def _rate_limit_retry_after(request: Request, hits_by_client: defaultdict[str, deque[float]]) -> int | None:
    now = time.monotonic()
    key = _client_key(request)
    hits = hits_by_client[key]
    while hits and now - hits[0] > RATE_LIMIT_WINDOW_SECONDS:
        hits.popleft()
    if len(hits) >= RATE_LIMIT_POST_RUNS:
        return max(1, int(RATE_LIMIT_WINDOW_SECONDS - (now - hits[0])))
    hits.append(now)
    return None


def _client_key(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for", "").split(",", 1)[0].strip()
    if forwarded_for:
        return forwarded_for
    return request.client.host if request.client else "unknown"


def _run_summary(state: JobSearchState) -> dict[str, object]:
    return {
        "run_id": state.run_id,
        "company": state.company_name or "Unknown company",
        "role": state.role_title or "Unknown role",
        "stop_reason": state.stop_reason.value if state.stop_reason else "UNKNOWN",
        "fit_score": state.fit_analysis.total if state.fit_analysis else None,
        "decision": state.fit_analysis.decision if state.fit_analysis else None,
        "pending_node": state.pending_node,
        "updated_at": state.updated_at,
    }


def _score_rows(state: JobSearchState) -> list[tuple[str, int]]:
    if not state.fit_analysis:
        return []
    return [
        ("Technical match", state.fit_analysis.technical_match),
        ("Domain interest", state.fit_analysis.domain_interest),
        ("Logistics match", state.fit_analysis.logistics_match),
        ("Narrative strength", state.fit_analysis.narrative_strength),
        ("Expected ROI", state.fit_analysis.expected_roi),
    ]


def _run_stats(runs: list[dict[str, object]]) -> dict[str, int]:
    completed = sum(1 for run in runs if run["stop_reason"] == StopReason.COMPLETED.value)
    awaiting = sum(1 for run in runs if run["stop_reason"] == StopReason.NEED_USER_APPROVAL.value)
    return {
        "total": len(runs),
        "completed": completed,
        "awaiting": awaiting,
        "agents": len(_agent_cards()),
    }


def _workflow_steps() -> list[dict[str, str]]:
    return [
        {"name": "Ingest", "label": "JD intake"},
        {"name": "Extract", "label": "role signals"},
        {"name": "Research", "label": "company brief"},
        {"name": "Score", "label": "fit analysis"},
        {"name": "Tailor", "label": "resume proposal"},
        {"name": "Approve", "label": "human gate"},
        {"name": "Prep", "label": "tracker + interview"},
    ]


def _agent_cards() -> list[dict[str, str]]:
    return [
        {"name": "JD Extractor", "detail": "normalizes role, company, and skill signals"},
        {"name": "Researcher", "detail": "builds a company-facing context brief"},
        {"name": "Fit Analyst", "detail": "scores technical, domain, logistics, and ROI"},
        {"name": "Resume Tailor", "detail": "drafts human-reviewable positioning"},
    ]


def _run_steps(state: JobSearchState) -> list[dict[str, str]]:
    status_by_node = {
        "ingest": "done" if any("ingested" in message.lower() for message in state.messages) else "idle",
        "jd_extract": "done" if state.role_title else "idle",
        "company_research": "done" if state.company_brief else "idle",
        "fit_analysis": "done" if state.fit_analysis else "idle",
        "resume_tailor": "done" if state.resume_proposal else "idle",
        "approval": "active" if state.stop_reason == StopReason.NEED_USER_APPROVAL else "done",
        "tracker": "done" if state.tracker_update else "idle",
        "interview_prep": "done" if state.interview_pack else "idle",
    }
    if state.pending_node:
        status_by_node[state.pending_node] = "active"
    if state.stop_reason == StopReason.COMPLETED:
        status_by_node["approval"] = "done"
    return [
        {"name": "Ingest", "key": "ingest", "status": status_by_node["ingest"]},
        {"name": "Extract", "key": "jd_extract", "status": status_by_node["jd_extract"]},
        {"name": "Research", "key": "company_research", "status": status_by_node["company_research"]},
        {"name": "Score", "key": "fit_analysis", "status": status_by_node["fit_analysis"]},
        {"name": "Tailor", "key": "resume_tailor", "status": status_by_node["resume_tailor"]},
        {"name": "Approve", "key": "approval", "status": status_by_node["approval"]},
        {"name": "Tracker", "key": "tracker", "status": status_by_node["tracker"]},
        {"name": "Prep", "key": "interview_prep", "status": status_by_node["interview_prep"]},
    ]


def _public_demo_mode() -> bool:
    return os.environ.get("JOBAGENT_PUBLIC_DEMO_MODE", "true").lower() in {"1", "true", "yes", "on"}


app = create_app()
