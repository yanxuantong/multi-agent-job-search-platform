from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PromptSpec:
    name: str
    version: str
    system: str
    response_schema: str


PROMPTS = {
    "company_research": PromptSpec(
        name="company_research",
        version="v1",
        system=(
            "You are a company research agent. Produce sourced, job-relevant research. "
            "Separate evidence from inference and mark unknowns explicitly."
        ),
        response_schema="CompanyBrief",
    ),
    "resume_tailor": PromptSpec(
        name="resume_tailor",
        version="v1",
        system=(
            "You are a resume tailoring agent. Do not invent experience. "
            "Map each suggestion to evidence from the story bank and stop for human review."
        ),
        response_schema="ResumeProposal",
    ),
    "fit_analysis": PromptSpec(
        name="fit_analysis",
        version="v1",
        system=(
            "You are a fit-analysis agent. Score fit with evidence, concerns, and an explicit apply/review/skip decision."
        ),
        response_schema="FitAnalysis",
    ),
}


def get_prompt(name: str) -> PromptSpec:
    try:
        return PROMPTS[name]
    except KeyError as exc:
        raise KeyError(f"Unknown prompt: {name}") from exc

