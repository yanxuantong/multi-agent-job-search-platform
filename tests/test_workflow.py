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
        self.assertGreaterEqual(len(state.orchestrator_decisions), 5)
        self.assertGreaterEqual(len(state.tool_audit), 5)
        self.assertEqual(state.tool_audit[0].tool_name, "jd_intake_validator")
        self.assertIsNotNone(state.eval_summary)
        self.assertTrue(state.eval_summary.passed)

    def test_workflow_completes_when_approved(self) -> None:
        state = run_job_workflow(JOB_TEXT, STORY_BANK, approved=True, run_id="test-approved")

        self.assertEqual(state.stop_reason, StopReason.COMPLETED)
        self.assertIsNotNone(state.tracker_update)
        self.assertIsNotNone(state.interview_pack)
        self.assertGreaterEqual(state.fit_analysis.total, 15)
        self.assertTrue(any(event.tool_name == "application_tracker_writer" for event in state.tool_audit))
        self.assertTrue(state.eval_summary.passed)

    def test_workflow_can_resume_from_human_approval_checkpoint(self) -> None:
        paused = run_job_workflow(JOB_TEXT, STORY_BANK, run_id="test-resume")

        self.assertEqual(paused.stop_reason, StopReason.NEED_USER_APPROVAL)
        self.assertEqual(paused.pending_node, "tracker")

        resumed = resume_job_workflow("test-resume", approved=True)

        self.assertEqual(resumed.stop_reason, StopReason.COMPLETED)
        self.assertIsNotNone(resumed.tracker_update)
        self.assertIsNotNone(resumed.interview_pack)

    def test_rejected_resume_keeps_workflow_paused_before_side_effects(self) -> None:
        paused = run_job_workflow(JOB_TEXT, STORY_BANK, run_id="test-reject")

        rejected = resume_job_workflow("test-reject", approved=False)

        self.assertEqual(rejected.stop_reason, StopReason.NEED_USER_APPROVAL)
        self.assertEqual(rejected.pending_node, "tracker")
        self.assertIsNone(rejected.tracker_update)
        self.assertIn("rejected", rejected.messages[-1])


if __name__ == "__main__":
    unittest.main()
