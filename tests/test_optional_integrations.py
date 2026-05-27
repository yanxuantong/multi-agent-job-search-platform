from __future__ import annotations

import importlib.util
import os
import unittest
from uuid import uuid4


def _has_package(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


class OptionalIntegrationsTest(unittest.TestCase):
    @unittest.skipUnless(_has_package("langgraph"), "LangGraph optional dependency is not installed")
    def test_langgraph_reference_app_compiles(self) -> None:
        from jobagent.graph.langgraph_reference import build_langgraph_reference_app

        app = build_langgraph_reference_app("test-langgraph-reference")

        self.assertEqual(type(app).__name__, "CompiledStateGraph")

    @unittest.skipUnless(_has_package("mcp"), "MCP optional dependency is not installed")
    def test_mcp_sdk_server_can_be_created(self) -> None:
        from mcp_server.career_research_sdk_server import create_server

        server = create_server()

        self.assertEqual(type(server).__name__, "FastMCP")

    @unittest.skipUnless(
        _has_package("anthropic") and _has_package("openai"),
        "LLM provider optional dependencies are not installed",
    )
    def test_llm_provider_constructors_do_not_call_network(self) -> None:
        from jobagent.llm.anthropic_provider import AnthropicProvider
        from jobagent.llm.openai_provider import OpenAIProvider

        self.assertEqual(type(AnthropicProvider(api_key="test-key")).__name__, "AnthropicProvider")
        self.assertEqual(type(OpenAIProvider(api_key="test-key")).__name__, "OpenAIProvider")

    @unittest.skipUnless(
        os.environ.get("JOBAGENT_DATABASE_URL") and _has_package("psycopg") and _has_package("pgvector"),
        "Postgres/pgvector integration requires JOBAGENT_DATABASE_URL and optional dependencies",
    )
    def test_postgres_memory_round_trip(self) -> None:
        from jobagent.storage.postgres_memory import PostgresMemoryStore

        store = PostgresMemoryStore(os.environ["JOBAGENT_DATABASE_URL"])
        store.ensure_schema()
        embedding = [0.0] * 1536
        embedding[0] = 1.0
        namespace = f"stories-{uuid4()}"
        record_id = f"story-{uuid4()}"
        store.upsert_semantic(
            record_id=record_id,
            namespace=namespace,
            content="Built Python RAG agents",
            embedding=embedding,
            metadata={"skill": "rag"},
        )
        store.append_episode(
            record_id=f"episode-{uuid4()}",
            run_id="test-run",
            event_type="application_ready",
            content="Ready to apply",
            metadata={"company": "Anthropic"},
        )

        rows = store.search_semantic(namespace=namespace, embedding=embedding, limit=1)

        self.assertGreaterEqual(len(rows), 1)
        self.assertEqual(rows[0].id, record_id)
        self.assertEqual(rows[0].metadata["skill"], "rag")


if __name__ == "__main__":
    unittest.main()
