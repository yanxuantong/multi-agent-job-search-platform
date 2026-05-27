from __future__ import annotations

import unittest

from jobagent.graph.workflow import resume_job_workflow, run_job_workflow
from jobagent.models import StopReason


STORY_BANK = [
    {
        "title": "Production RAG system",
        "summary": "Built RAG and LLM support tooling.",
        "impact": "Improved support reliability.",
        "skills": ["RAG", "LLM", "Python", "observability", "distributed systems"],
        "tags": ["ai", "infra"],
    }
]

JOB_TEXT = """
Company: Anthropic
Role: Applied AI Engineer
Build Python services for RAG, LLM agents, evaluation, observability, and Postgres-backed state.
"""


class WorkflowTest(unittest.TestCase):
    def test_workflow_stops_for_human_approval_by_default(self) -> None:
        state = run_job_workflow(JOB_TEXT, STORY_BANK, run_id="test-hitl")

        self.assertEqual(state.stop_reason, StopReason.NEED_USER_APPROVAL)
        self.assertEqual(state.company_name, "Anthropic")
        self.assertIsNotNone(state.resume_proposal)
        self.assertIsNone(state.tracker_update)

    def test_workflow_completes_when_approved(self) -> None:
        state = run_job_workflow(JOB_TEXT, STORY_BANK, approved=True, run_id="test-approved")

        self.assertEqual(state.stop_reason, StopReason.COMPLETED)
        self.assertIsNotNone(state.tracker_update)
        self.assertIsNotNone(state.interview_pack)
        self.assertGreaterEqual(state.fit_analysis.total, 15)

    def test_workflow_can_resume_from_human_approval_checkpoint(self) -> None:
        paused = run_job_workflow(JOB_TEXT, STORY_BANK, run_id="test-resume")

        self.assertEqual(paused.stop_reason, StopReason.NEED_USER_APPROVAL)
        self.assertEqual(paused.pending_node, "tracker")

        resumed = resume_job_workflow("test-resume", approved=True)

        self.assertEqual(resumed.stop_reason, StopReason.COMPLETED)
        self.assertIsNotNone(resumed.tracker_update)
        self.assertIsNotNone(resumed.interview_pack)


if __name__ == "__main__":
    unittest.main()
