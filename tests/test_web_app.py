from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

from jobagent.storage import JsonCheckpointStore
from jobagent.web.store import LocalRunStore


@unittest.skipUnless(
    importlib.util.find_spec("fastapi") and importlib.util.find_spec("httpx"),
    "FastAPI/httpx web test dependencies are not installed",
)
class WebAppTest(unittest.TestCase):
    def test_web_run_can_pause_and_resume(self) -> None:
        from fastapi.testclient import TestClient
        from jobagent.web.app import create_app

        with tempfile.TemporaryDirectory() as tmp:
            store = LocalRunStore(JsonCheckpointStore(Path(tmp) / "checkpoints"))
            with TestClient(create_app(store)) as client:
                response = client.post(
                    "/runs",
                    data={
                        "job_url": "https://example.com/job",
                        "job_text": (
                            "Company: Anthropic\n"
                            "Role: Applied AI Engineer\n"
                            "Build Python services for RAG, LLM agents, evaluation, observability, and Postgres state."
                        ),
                    },
                    follow_redirects=False,
                )

                self.assertEqual(response.status_code, 303)
                run_url = response.headers["location"]
                detail = client.get(run_url)
                self.assertEqual(detail.status_code, 200)
                self.assertIn("NEED_USER_APPROVAL", detail.text)

                run_id = run_url.rsplit("/", 1)[-1]
                approved = client.post(f"/runs/{run_id}/approve", follow_redirects=False)
                self.assertEqual(approved.status_code, 303)
                completed = client.get(run_url)
                self.assertEqual(completed.status_code, 200)
                self.assertIn("COMPLETED", completed.text)


if __name__ == "__main__":
    unittest.main()
