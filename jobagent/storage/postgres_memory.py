from __future__ import annotations

from dataclasses import dataclass
from typing import Any


MEMORY_SCHEMA_SQL = """
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS semantic_memory (
    id TEXT PRIMARY KEY,
    namespace TEXT NOT NULL,
    content TEXT NOT NULL,
    embedding vector(1536),
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS episodic_memory (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS semantic_memory_embedding_idx
ON semantic_memory USING ivfflat (embedding vector_cosine_ops);

CREATE INDEX IF NOT EXISTS episodic_memory_run_id_idx
ON episodic_memory (run_id);
"""


@dataclass(frozen=True)
class MemoryRecord:
    id: str
    content: str
    metadata: dict[str, Any]


class PostgresMemoryStore:
    """Optional pgvector-backed long-term memory store.

    This separates semantic memory (preferences, reusable story facts) from
    episodic memory (specific applications, approvals, and run events).
    """

    def __init__(self, dsn: str) -> None:
        try:
            import psycopg
        except ImportError as exc:  # pragma: no cover - optional dependency.
            raise RuntimeError("psycopg is not installed. Run: python3 -m pip install -e '.[postgres]'") from exc

        self._psycopg = psycopg
        self.dsn = dsn

    def ensure_schema(self) -> None:
        with self._psycopg.connect(self.dsn) as conn:
            conn.execute(MEMORY_SCHEMA_SQL)

    def upsert_semantic(
        self,
        *,
        record_id: str,
        namespace: str,
        content: str,
        embedding: list[float],
        metadata: dict[str, Any],
    ) -> None:
        with self._psycopg.connect(self.dsn) as conn:
            conn.execute(
                """
                INSERT INTO semantic_memory (id, namespace, content, embedding, metadata, updated_at)
                VALUES (%s, %s, %s, %s, %s, now())
                ON CONFLICT (id) DO UPDATE SET
                    namespace = EXCLUDED.namespace,
                    content = EXCLUDED.content,
                    embedding = EXCLUDED.embedding,
                    metadata = EXCLUDED.metadata,
                    updated_at = now()
                """,
                (record_id, namespace, content, embedding, metadata),
            )

    def append_episode(
        self,
        *,
        record_id: str,
        run_id: str,
        event_type: str,
        content: str,
        metadata: dict[str, Any],
    ) -> None:
        with self._psycopg.connect(self.dsn) as conn:
            conn.execute(
                """
                INSERT INTO episodic_memory (id, run_id, event_type, content, metadata)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (record_id, run_id, event_type, content, metadata),
            )

    def search_semantic(self, *, namespace: str, embedding: list[float], limit: int = 5) -> list[MemoryRecord]:
        with self._psycopg.connect(self.dsn) as conn:
            rows = conn.execute(
                """
                SELECT id, content, metadata
                FROM semantic_memory
                WHERE namespace = %s
                ORDER BY embedding <=> %s
                LIMIT %s
                """,
                (namespace, embedding, limit),
            ).fetchall()
        return [MemoryRecord(id=row[0], content=row[1], metadata=row[2]) for row in rows]
