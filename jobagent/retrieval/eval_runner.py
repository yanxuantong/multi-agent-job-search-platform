from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jobagent.models import SourceDocument
from jobagent.retrieval import retrieve_context


def run_retrieval_eval_suite(
    suite_path: str | Path,
    documents: list[SourceDocument],
) -> dict[str, Any]:
    cases = json.loads(Path(suite_path).read_text(encoding="utf-8"))
    if not isinstance(cases, list):
        raise ValueError("Retrieval eval suite must be a list of case objects")

    results = [_run_case(case, documents) for case in cases]
    failed = [result for result in results if not result["passed"]]
    total = len(results)
    return {
        "total": total,
        "passed": total - len(failed),
        "failed": len(failed),
        "pass_rate": round((total - len(failed)) / total, 4) if total else 0.0,
        "average_recall_at_k": _average(results, "recall_at_k"),
        "average_precision_at_k": _average(results, "precision_at_k"),
        "average_mrr": _average(results, "mrr"),
        "failure_categories": sorted({category for result in failed for category in result["failure_categories"]}),
        "results": results,
    }


def _run_case(case: dict[str, Any], documents: list[SourceDocument]) -> dict[str, Any]:
    query = str(case.get("query", ""))
    query_terms = [str(term) for term in case.get("query_terms", query.split()) if str(term)]
    expected = set(str(chunk_id) for chunk_id in case.get("expected_chunk_ids", []))
    prohibited = set(str(chunk_id) for chunk_id in case.get("prohibited_chunk_ids", []))
    k = int(case.get("k", 5))
    min_recall = float(case.get("min_recall_at_k", 1.0))
    require_fresh = bool(case.get("require_fresh", True))

    context = retrieve_context(documents, query_terms, query=query, limit=k)
    retrieved_ids = [chunk.chunk_id for chunk in context.selected_chunks]
    retrieved_set = set(retrieved_ids)
    expected_hits = expected & retrieved_set
    prohibited_hits = prohibited & retrieved_set
    recall = len(expected_hits) / len(expected) if expected else 1.0
    precision = len(expected_hits) / len(retrieved_ids) if retrieved_ids else 0.0
    mrr = _reciprocal_rank(retrieved_ids, expected)

    failure_categories = []
    if recall < min_recall:
        failure_categories.append("missing_expected_chunk")
    if prohibited_hits:
        failure_categories.append("prohibited_chunk_returned")
    if require_fresh and context.freshness_warnings:
        failure_categories.append("stale_source_returned")

    return {
        "id": case.get("id", "unnamed"),
        "query": query,
        "k": k,
        "retrieved_chunk_ids": retrieved_ids,
        "expected_chunk_ids": sorted(expected),
        "prohibited_hits": sorted(prohibited_hits),
        "recall_at_k": round(recall, 4),
        "precision_at_k": round(precision, 4),
        "mrr": round(mrr, 4),
        "freshness_warnings": context.freshness_warnings,
        "failure_categories": failure_categories,
        "passed": not failure_categories,
    }


def _reciprocal_rank(retrieved_ids: list[str], expected: set[str]) -> float:
    if not expected:
        return 1.0
    for index, chunk_id in enumerate(retrieved_ids, start=1):
        if chunk_id in expected:
            return 1.0 / index
    return 0.0


def _average(results: list[dict[str, Any]], field: str) -> float:
    if not results:
        return 0.0
    return round(sum(float(result[field]) for result in results) / len(results), 4)
