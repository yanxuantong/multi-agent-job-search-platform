from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from jobagent.memory import story_documents
from jobagent.models import SourceDocument
from jobagent.retrieval import chunk_documents, hybrid_rank_chunks, retrieve_context
from jobagent.retrieval.eval_runner import run_retrieval_eval_suite


STORIES = [
    {
        "title": "Production RAG system",
        "summary": "Built RAG and LLM support tooling.",
        "impact": "Improved support reliability.",
        "skills": ["RAG", "LLM", "Python", "observability"],
        "tags": ["ai", "infra"],
    },
    {
        "title": "Calendar command parser",
        "summary": "Built an AI calendar parser.",
        "impact": "Verified natural-language command behavior.",
        "skills": ["LLM", "evaluation", "agent", "Python"],
        "tags": ["product"],
    },
]


class RetrievalTest(unittest.TestCase):
    def test_story_bank_retrieval_returns_citable_context(self) -> None:
        context = retrieve_context(
            story_documents(STORIES),
            ["RAG", "observability"],
            query="production rag evidence",
            limit=2,
        )

        self.assertEqual(context.returned_count, 1)
        self.assertEqual(context.selected_chunks[0].chunk_id, "story:production-rag-system:0")
        self.assertEqual(context.citations[0].title, "Production RAG system")
        self.assertEqual(context.citations[0].freshness_status, "fresh")
        self.assertEqual(context.freshness_warnings, [])

    def test_stale_source_creates_freshness_warning(self) -> None:
        document = SourceDocument(
            source_id="industry:old-agent-report",
            source_type="industry_report",
            title="Old agent report",
            text="RAG observability benchmark for AI agents",
            captured_at="2024-01-01T00:00:00+00:00",
            expires_at="2024-06-01T00:00:00+00:00",
            refresh_policy="quarterly",
        )

        context = retrieve_context(
            [document],
            ["RAG", "observability"],
            now=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )

        self.assertEqual(context.selected_chunks[0].freshness_status, "stale")
        self.assertIn("refresh policy: quarterly", context.freshness_warnings[0])

    def test_hybrid_rank_can_promote_semantic_match(self) -> None:
        documents = [
            SourceDocument(
                source_id="story:keyword",
                source_type="story_bank",
                title="Keyword",
                text="RAG observability",
            ),
            SourceDocument(
                source_id="story:semantic",
                source_type="story_bank",
                title="Semantic",
                text="customer deployment reliability",
            ),
        ]
        chunks = chunk_documents(documents)
        ranked = hybrid_rank_chunks(
            chunks,
            ["RAG"],
            semantic_scores={"story:semantic:0": 0.95},
            limit=2,
        )

        self.assertEqual(ranked[0].chunk_id, "story:semantic:0")

    def test_retrieval_eval_reports_recall_precision_and_mrr(self) -> None:
        suite = [
            {
                "id": "rag-hit",
                "query": "RAG LLM observability",
                "query_terms": ["RAG", "LLM", "observability"],
                "expected_chunk_ids": ["story:production-rag-system:0"],
                "k": 2,
                "min_recall_at_k": 1.0,
            }
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "retrieval_eval.json"
            path.write_text(json.dumps(suite), encoding="utf-8")
            result = run_retrieval_eval_suite(path, story_documents(STORIES))

        self.assertEqual(result["failed"], 0)
        self.assertEqual(result["average_recall_at_k"], 1.0)
        self.assertGreater(result["average_mrr"], 0)


if __name__ == "__main__":
    unittest.main()
