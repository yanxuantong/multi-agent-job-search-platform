from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from jobagent.integrations.external_mcp_tracker import ExternalMCPTrackerAdapter
from jobagent.integrations import list_learning_integrations
from jobagent.models import TrackerUpdate
from jobagent.observability.langfuse_exporter import LangfuseTraceExporter
from jobagent.retrieval import chunk_text, rank_chunks, retrieve_context
from jobagent.models import SourceDocument
from jobagent.storage.postgres_memory import MEMORY_SCHEMA_SQL


class LearningIntegrationsTest(unittest.TestCase):
    def test_original_project_stack_has_code_entrypoints(self) -> None:
        statuses = list_learning_integrations()
        names = {status.name for status in statuses}

        self.assertIn("Local RAG retrieval", names)
        self.assertIn("LangGraph orchestration", names)
        self.assertIn("LLM providers", names)
        self.assertIn("Langfuse observability", names)
        self.assertIn("Postgres pgvector memory", names)
        self.assertIn("External MCP tracker consumer", names)
        self.assertIn("MCP career-research server", names)
        self.assertIn("Docker deployment touchpoint", names)

        for status in statuses:
            self.assertTrue(status.local_learning_entrypoint)
            self.assertTrue(status.setup_hint)
            self.assertTrue(status.cost_note)

    def test_pgvector_schema_separates_semantic_and_episodic_memory(self) -> None:
        self.assertIn("CREATE EXTENSION IF NOT EXISTS vector", MEMORY_SCHEMA_SQL)
        self.assertIn("CREATE TABLE IF NOT EXISTS semantic_memory", MEMORY_SCHEMA_SQL)
        self.assertIn("CREATE TABLE IF NOT EXISTS episodic_memory", MEMORY_SCHEMA_SQL)
        self.assertIn("embedding vector(1536)", MEMORY_SCHEMA_SQL)

    def test_langfuse_exporter_accepts_fake_client_for_local_learning(self) -> None:
        fake = FakeLangfuseClient()
        with tempfile.TemporaryDirectory() as tmp:
            trace_path = Path(tmp) / "trace.jsonl"
            trace_path.write_text(
                json.dumps(
                    {
                        "run_id": "run-1",
                        "node": "company_research",
                        "event": "node",
                        "elapsed_ms": 12.5,
                        "metadata": {"model": "mock"},
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            summary = LangfuseTraceExporter(fake).export_jsonl_trace(trace_path)

        self.assertEqual(summary.exported_events, 1)
        self.assertEqual(fake.traces[0]["id"], "run-1")
        self.assertEqual(fake.traces[0]["name"], "jobagent:company_research")
        self.assertTrue(fake.flushed)

    def test_external_mcp_tracker_payload_is_idempotent(self) -> None:
        update = TrackerUpdate(
            company_name="Anthropic",
            role_title="Applied AI Engineer",
            status="ready_to_apply",
            fit_score=21,
            next_action="Review and submit manually.",
            notes=["Matched RAG", "Matched eval"],
        )
        payload = ExternalMCPTrackerAdapter().serialize_tracker_write(update)

        self.assertEqual(payload["method"], "tools/call")
        self.assertEqual(payload["params"]["name"], "create_or_update_application")
        self.assertEqual(payload["params"]["metadata"]["idempotency_key"], "anthropic:applied-ai-engineer")
        self.assertEqual(payload["params"]["arguments"]["fit_score"], 21)

    def test_local_rag_chunking_and_ranking_is_deterministic(self) -> None:
        text = "Python RAG agents need evaluation. Java services need capacity planning."
        chunks = chunk_text(text, source="sample", max_words=5, overlap_words=1)
        ranked = rank_chunks(chunks, ["rag", "agents", "evaluation"])

        self.assertGreaterEqual(len(chunks), 2)
        self.assertEqual(ranked[0].source, "sample")
        self.assertGreater(ranked[0].score, 0)

    def test_local_rag_context_includes_source_metadata(self) -> None:
        documents = [
            SourceDocument(
                source_id="story:rag",
                source_type="story_bank",
                title="RAG project",
                text="Built Python RAG evaluation tooling.",
                captured_at="2026-01-01T00:00:00+00:00",
            )
        ]
        context = retrieve_context(documents, ["RAG", "evaluation"], limit=1)

        self.assertEqual(context.citations[0].source_id, "story:rag")
        self.assertEqual(context.selected_chunks[0].title, "RAG project")


class FakeLangfuseClient:
    def __init__(self) -> None:
        self.traces = []
        self.flushed = False

    def trace(self, **kwargs) -> None:
        self.traces.append(kwargs)

    def flush(self) -> None:
        self.flushed = True


if __name__ == "__main__":
    unittest.main()
