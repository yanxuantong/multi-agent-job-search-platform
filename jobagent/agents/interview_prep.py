from __future__ import annotations

from jobagent.graph import NodeResult
from jobagent.memory import match_stories
from jobagent.models import InterviewPack, JobSearchState, StopReason


def prepare_interview_pack(state: JobSearchState) -> NodeResult:
    jd = state.normalized_jd
    if not jd:
        raise ValueError("JD extraction must run before interview prep")

    stories = match_stories(state.story_bank, jd.required_skills)
    state.interview_pack = InterviewPack(
        technical_questions=[
            "Design a reliable multi-agent workflow for this role's core use case.",
            "How would you evaluate long-running agent quality beyond single-turn accuracy?",
            f"What tradeoffs would you make when using {', '.join(jd.required_skills[:3]) or 'the listed stack'}?",
        ],
        behavioral_questions=[
            "Tell me about a time you shipped an ambiguous project end to end.",
            "Tell me about a time you disagreed with a technical direction.",
        ],
        company_questions=[
            f"What is the biggest product or engineering risk for {jd.company_name}?",
            "Where could this team use better evals or observability?",
        ],
        story_matches=[
            f"{story.get('title', 'Story')}: {story.get('summary', '')}" for story in stories[:4]
        ],
    )
    state.messages.append("Interview prep pack generated.")
    return NodeResult(stop_reason=StopReason.COMPLETED)

