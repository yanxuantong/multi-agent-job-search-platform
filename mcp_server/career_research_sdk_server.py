from __future__ import annotations

from dataclasses import asdict

from jobagent.agents.company_research import research_company
from jobagent.agents.jd_extract import extract_jd
from jobagent.models import JobSearchState


def create_server():
    """Create the official-SDK MCP server for career research.

    The dependency-free ``career_research_server.py`` remains useful for local
    teaching. This file is the production-shaped MCP entrypoint from the
    original Project 1 plan.
    """

    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError as exc:  # pragma: no cover - optional dependency.
        raise RuntimeError("MCP SDK is not installed. Run: python3 -m pip install -e '.[mcp]'") from exc

    server = FastMCP("career-research")

    @server.tool()
    def extract_job_description(job_text: str) -> dict:
        """Extract company, role, skills, and domain signals from a job description."""

        state = JobSearchState(run_id="mcp-sdk-extract", user_goal="mcp", raw_job_text=job_text)
        extract_jd(state)
        return asdict(state.normalized_jd)

    @server.tool()
    def research_company_from_job(job_text: str) -> dict:
        """Generate a company brief from a job description."""

        state = JobSearchState(run_id="mcp-sdk-research", user_goal="mcp", raw_job_text=job_text)
        extract_jd(state)
        research_company(state)
        return asdict(state.company_brief)

    @server.resource("jobagent://prompt/company-research")
    def company_research_prompt() -> str:
        return (
            "Extract company facts, product signals, engineering relevance, risks, "
            "and source notes. Return structured JSON that can be traced and evaled."
        )

    return server


def main() -> int:
    server = create_server()
    server.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
