from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from jobagent.evals.runner import run_eval_suite


class EvalRunnerTest(unittest.TestCase):
    def test_eval_runner_reports_pass_rate(self) -> None:
        suite = [
            {
                "id": "case-1",
                "eval_type": "trajectory",
                "job_text": "Company: Anthropic\nRole: Applied AI Engineer\nPython RAG LLM agents evaluation observability",
                "expected_company": "Anthropic",
                "expected_required_skills": ["python", "rag", "llm"],
                "expected_stop_reason": "NEED_USER_APPROVAL",
                "min_fit_score": 12,
            }
        ]
        stories = [
            {
                "title": "RAG project",
                "summary": "Built Python RAG and LLM tooling.",
                "impact": "Shipped AI infra.",
                "skills": ["Python", "RAG", "LLM", "evaluation"],
            }
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "suite.json"
            path.write_text(json.dumps(suite), encoding="utf-8")
            result = run_eval_suite(path, stories)

        self.assertEqual(result["total"], 1)
        self.assertEqual(result["failed"], 0)
        self.assertEqual(result["pass_rate"], 1.0)
        self.assertEqual(result["by_type"]["trajectory"]["passed"], 1)

    def test_eval_runner_distinguishes_single_turn_extraction(self) -> None:
        suite = [
            {
                "id": "extract-only",
                "eval_type": "single_turn_jd_extract",
                "job_text": "Company: ToolBridge AI\nRole: Integrations Engineer\nPython MCP agents observability",
                "expected_company": "ToolBridge AI",
                "expected_required_skills": ["python", "mcp", "agents", "observability"],
            }
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "suite.json"
            path.write_text(json.dumps(suite), encoding="utf-8")
            result = run_eval_suite(path, [])

        self.assertEqual(result["failed"], 0)
        self.assertEqual(result["by_type"]["single_turn_jd_extract"]["total"], 1)
        self.assertEqual(result["results"][0]["eval_type"], "single_turn_jd_extract")


if __name__ == "__main__":
    unittest.main()
