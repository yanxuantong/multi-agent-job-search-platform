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
    def _client(self, tmp: str):
        from fastapi.testclient import TestClient
        from jobagent.web.app import create_app

        store = LocalRunStore(JsonCheckpointStore(Path(tmp) / "checkpoints"))
        return TestClient(create_app(store))

    def test_web_run_can_pause_and_resume(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self._client(tmp) as client:
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

    def test_web_responses_include_security_headers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self._client(tmp) as client:
                response = client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["x-content-type-options"], "nosniff")
        self.assertEqual(response.headers["x-frame-options"], "DENY")
        self.assertEqual(response.headers["referrer-policy"], "no-referrer")
        self.assertIn("frame-ancestors 'none'", response.headers["content-security-policy"])

    def test_web_rejects_oversized_job_text(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self._client(tmp) as client:
                response = client.post(
                    "/runs",
                    data={
                        "job_text": "A" * 12001,
                    },
                )

        self.assertEqual(response.status_code, 400)
        self.assertIn("job_text must be at most", response.text)

    def test_web_rejects_oversized_request_body(self) -> None:
        from jobagent.web import app as web_app

        with tempfile.TemporaryDirectory() as tmp:
            with self._client(tmp) as client:
                response = client.post(
                    "/runs",
                    content=b"job_text=" + (b"A" * (web_app.MAX_REQUEST_BODY_BYTES + 1)),
                    headers={"content-type": "application/x-www-form-urlencoded"},
                )

        self.assertEqual(response.status_code, 413)

    def test_web_rejects_json_submission(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self._client(tmp) as client:
                response = client.post(
                    "/runs",
                    json={"job_text": "Build reliable production AI agent systems with observability."},
                )

        self.assertEqual(response.status_code, 415)

    def test_web_rejects_invalid_run_id_before_store_lookup(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self._client(tmp) as client:
                response = client.get("/runs/not-a-real-run-id")

        self.assertEqual(response.status_code, 404)
        self.assertIn("Run not found", response.text)

    def test_web_rate_limits_run_creation(self) -> None:
        from jobagent.web import app as web_app

        original_limit = web_app.RATE_LIMIT_POST_RUNS
        web_app.RATE_LIMIT_POST_RUNS = 2
        try:
            with tempfile.TemporaryDirectory() as tmp:
                with self._client(tmp) as client:
                    payload = {
                        "job_text": (
                            "Company: Example\n"
                            "Role: AI Engineer\n"
                            "Build production agent systems with evaluation, tracing, and FastAPI."
                        )
                    }
                    self.assertEqual(client.post("/runs", data=payload, follow_redirects=False).status_code, 303)
                    self.assertEqual(client.post("/runs", data=payload, follow_redirects=False).status_code, 303)
                    limited = client.post("/runs", data=payload, follow_redirects=False)
        finally:
            web_app.RATE_LIMIT_POST_RUNS = original_limit

        self.assertEqual(limited.status_code, 429)
        self.assertIn("Retry-After", limited.headers)


if __name__ == "__main__":
    unittest.main()
