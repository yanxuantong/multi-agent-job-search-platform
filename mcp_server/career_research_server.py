from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jobagent.agents.company_research import research_company
from jobagent.agents.jd_extract import extract_jd
from jobagent.models import JobSearchState


def main() -> int:
    """Dependency-free teaching stub that mirrors an MCP server's tool boundary.

    Real MCP servers use the MCP Python SDK and stdio/SSE transports. This file
    keeps the protocol surface visible without requiring dependencies:

    echo '{"tool":"extract_jd","arguments":{"job_text":"..."}}' | python mcp_server/career_research_server.py
    """

    for line in sys.stdin:
        request = json.loads(line)
        tool = request.get("tool")
        arguments = request.get("arguments", {})
        if tool == "extract_jd":
            state = JobSearchState(run_id="mcp-local", user_goal="mcp", raw_job_text=arguments["job_text"])
            extract_jd(state)
            print(json.dumps({"content": state.normalized_jd.__dict__}, ensure_ascii=True), flush=True)
        elif tool == "research_company":
            state = JobSearchState(run_id="mcp-local", user_goal="mcp", raw_job_text=arguments["job_text"])
            extract_jd(state)
            research_company(state)
            print(json.dumps({"content": state.company_brief.company_summary}, ensure_ascii=True), flush=True)
        else:
            print(json.dumps({"error": f"Unknown tool: {tool}"}, ensure_ascii=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
