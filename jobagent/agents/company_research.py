from __future__ import annotations

from jobagent.graph import NodeResult
from jobagent.llm import LLMRequest, MockLLMProvider
from jobagent.models import CompanyBrief, JobSearchState, Source
from jobagent.prompts import get_prompt


def research_company(state: JobSearchState) -> NodeResult:
    jd = state.normalized_jd
    if not jd:
        raise ValueError("JD extraction must run before company research")

    company = jd.company_name
    role = jd.role_title
    sources = [
        Source(title="Job description", url=state.job_url or "local://pasted-job-description"),
    ]
    prompt = get_prompt("company_research")
    provider_response = MockLLMProvider().generate_structured(
        LLMRequest(
            prompt_name=prompt.name,
            prompt_version=prompt.version,
            system=prompt.system,
            user=state.raw_job_text or "",
            response_schema=prompt.response_schema,
            metadata={"company": company, "role": role},
        )
    )
    state.sources.extend(sources)
    state.company_brief = CompanyBrief(
        company_summary=(
            f"{company} is being evaluated through the lens of the {role} opening. "
            "This reference implementation uses local JD evidence; production would enrich this with official sources."
        ),
        product_lines=_product_lines(jd.domain_signals),
        business_model="Unknown from local JD; mark this for official company-source enrichment.",
        recent_signals=jd.domain_signals or ["No recent signal extracted from the pasted JD."],
        engineering_relevance=[
            f"Role mentions {skill}." for skill in jd.required_skills[:6]
        ]
        or ["Engineering relevance needs more source material."],
        risks=[
            "Company research is not externally sourced in offline demo mode.",
            "Verify visa/location fit manually before applying.",
        ],
        sources=sources,
    )
    state.messages.append(
        f"Provider boundary exercised: {provider_response.model} prompt={prompt.name}@{prompt.version}."
    )
    state.messages.append("Company research brief generated.")
    return NodeResult(next_node="fit_analysis")


def _product_lines(domain_signals: list[str]) -> list[str]:
    if "developer tools" in domain_signals:
        return ["Developer tools", "AI workflow automation"]
    if "enterprise" in domain_signals:
        return ["Enterprise AI", "Workflow automation"]
    if "search" in domain_signals:
        return ["Search", "Knowledge retrieval"]
    return ["Product line requires external research"]
