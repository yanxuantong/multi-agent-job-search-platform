from __future__ import annotations

from jobagent.graph import NodeResult
from jobagent.memory import match_stories
from jobagent.models import JobSearchState, ResumeProposal, StopReason


def tailor_resume(state: JobSearchState) -> NodeResult:
    jd = state.normalized_jd
    fit = state.fit_analysis
    if not jd or not fit:
        raise ValueError("JD and fit analysis must run before resume tailoring")

    stories = match_stories(state.story_bank, jd.required_skills)
    bullet_rewrites = []
    for story in stories[:3]:
        impact = story.get("impact", "delivered measurable product impact").rstrip(".")
        skills = ", ".join(story.get("skills", [])[:3])
        bullet_rewrites.append(f"Position {story.get('title', 'project')} as evidence of {skills}: {impact}.")
    if not bullet_rewrites:
        bullet_rewrites.append("Add a concrete project bullet that maps to the role's top required skills.")

    state.resume_proposal = ResumeProposal(
        bullet_rewrites=bullet_rewrites,
        cover_letter_outline=[
            f"Open with why {jd.company_name} and this {jd.role_title} role match your applied AI direction.",
            "Use one production RAG/infra story as proof of shipping reliability.",
            "Close with interest in evaluation, agent reliability, and customer-facing product impact.",
        ],
        recruiter_note=(
            f"I'm interested in the {jd.role_title} role because it combines "
            f"{', '.join(jd.required_skills[:3]) or 'applied AI engineering'} with production ownership."
        ),
    )
    state.messages.append("Resume proposal generated and waiting for human approval.")
    if not state.approved:
        return NodeResult(next_node="tracker", stop_reason=StopReason.NEED_USER_APPROVAL)
    return NodeResult(next_node="tracker")
