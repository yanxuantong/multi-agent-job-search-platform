from __future__ import annotations

import re

from jobagent.graph import NodeResult
from jobagent.models import JDExtract, JobSearchState
from jobagent.tools import extract_bullets, normalize_lines

SKILLS = [
    "python",
    "java",
    "spark",
    "rag",
    "llm",
    "agent",
    "agents",
    "langgraph",
    "mcp",
    "postgres",
    "distributed systems",
    "aws",
    "kubernetes",
    "evaluation",
    "observability",
]


def extract_jd(state: JobSearchState) -> NodeResult:
    text = state.raw_job_text or ""
    lines = normalize_lines(text)
    first_lines = " ".join(lines[:6])

    company = _first_match(text, r"(?:Company|公司)\s*[:\-]\s*([A-Za-z0-9 .,&-]+)")
    role = _first_match(text, r"(?:Role|Title|职位)\s*[:\-]\s*([A-Za-z0-9 /,+&-]+)")
    if not company:
        company = _guess_company(first_lines)
    if not role:
        role = _guess_role(first_lines)

    lowered = text.lower()
    required = [skill for skill in SKILLS if skill in lowered]
    preferred = extract_bullets(text, ("preferred", "nice to have", "bonus", "plus"), limit=5)
    responsibilities = extract_bullets(
        text,
        ("build", "own", "design", "deploy", "partner", "evaluate", "ship", "develop"),
        limit=6,
    )
    domains = [word for word in ("ai", "infra", "enterprise", "search", "developer tools") if word in lowered]
    seniority = [word for word in ("senior", "staff", "principal", "lead", "mid-level") if word in lowered]
    location = extract_bullets(text, ("remote", "hybrid", "new york", "san francisco", "bay area", "visa"), limit=4)

    state.company_name = company
    state.role_title = role
    state.normalized_jd = JDExtract(
        role_title=role,
        company_name=company,
        responsibilities=responsibilities or lines[:4],
        required_skills=required,
        preferred_skills=preferred,
        domain_signals=domains,
        seniority_signals=seniority,
        location_signals=location,
        unknowns=[] if required else ["No explicit technical keywords were extracted."],
    )
    state.messages.append(f"Extracted JD for {role} at {company}.")
    return NodeResult(next_node="company_research")


def _first_match(text: str, pattern: str) -> str | None:
    match = re.search(pattern, text, flags=re.IGNORECASE)
    return match.group(1).strip() if match else None


def _guess_company(text: str) -> str:
    match = re.search(r"\bat\s+([A-Z][A-Za-z0-9 .,&-]{2,40})", text)
    return match.group(1).strip() if match else "Unknown Company"


def _guess_role(text: str) -> str:
    role_words = ("Engineer", "Developer", "Architect", "Applied AI", "Forward Deployed")
    for word in role_words:
        match = re.search(rf"([A-Za-z ]*{word}[A-Za-z /]*)", text, flags=re.IGNORECASE)
        if match:
            return match.group(1).strip().title()
    return "Unknown Role"

