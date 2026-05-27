from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path
from urllib.parse import parse_qs

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
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


def create_app(store: RunStore | None = None) -> FastAPI:
    run_store = store or build_run_store()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.run_store.ensure_schema()
        yield

    app = FastAPI(title="Multi-Agent Job Search Platform", version="0.1.0", lifespan=lifespan)
    app.state.run_store = run_store
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    templates = Jinja2Templates(directory=TEMPLATE_DIR)

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/", response_class=HTMLResponse)
    def index(request: Request) -> HTMLResponse:
        sample_text = DEFAULT_JOB_FILE.read_text(encoding="utf-8") if DEFAULT_JOB_FILE.exists() else ""
        runs = app.state.run_store.list_recent()
        return templates.TemplateResponse(
            request,
            "index.html",
            {
                "sample_text": sample_text,
                "runs": [_run_summary(run) for run in runs],
                "public_demo_mode": _public_demo_mode(),
            },
        )

    @app.post("/runs")
    async def create_run(request: Request) -> RedirectResponse:
        form = await _read_urlencoded_form(request)
        job_text = form.get("job_text", "").strip()
        job_url = form.get("job_url", "").strip() or None
        approved = form.get("auto_approve") == "on"
        if len(job_text) < 20:
            return RedirectResponse("/?error=short_job_text", status_code=303)

        stories = load_story_bank(DEFAULT_STORY_BANK)
        state = run_job_workflow(job_text, stories, job_url=job_url, approved=approved)
        app.state.run_store.save(state)
        return RedirectResponse(f"/runs/{state.run_id}", status_code=303)

    @app.get("/runs/{run_id}", response_class=HTMLResponse)
    def show_run(request: Request, run_id: str) -> HTMLResponse:
        state = _load_or_404(app.state.run_store, run_id)
        return templates.TemplateResponse(
            request,
            "run.html",
            {
                "state": state,
                "summary": _run_summary(state),
                "scores": _score_rows(state),
                "can_approve": state.stop_reason == StopReason.NEED_USER_APPROVAL and bool(state.pending_node),
                "public_demo_mode": _public_demo_mode(),
            },
        )

    @app.post("/runs/{run_id}/approve")
    def approve_run(run_id: str) -> RedirectResponse:
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
    body = (await request.body()).decode("utf-8")
    parsed = parse_qs(body, keep_blank_values=True)
    return {key: values[-1] if values else "" for key, values in parsed.items()}


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


def _public_demo_mode() -> bool:
    return os.environ.get("JOBAGENT_PUBLIC_DEMO_MODE", "true").lower() in {"1", "true", "yes", "on"}


app = create_app()
