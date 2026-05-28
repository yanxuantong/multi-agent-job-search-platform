from __future__ import annotations

import os
from dataclasses import dataclass

from jobagent.models import JobSearchState
from jobagent.storage import JsonCheckpointStore


class RunStore:
    def ensure_schema(self) -> None:
        raise NotImplementedError

    def save(self, state: JobSearchState) -> None:
        raise NotImplementedError

    def load(self, run_id: str) -> JobSearchState:
        raise NotImplementedError

    def list_recent(self, limit: int = 8) -> list[JobSearchState]:
        raise NotImplementedError

    def health(self) -> dict[str, str]:
        raise NotImplementedError


@dataclass
class LocalRunStore(RunStore):
    checkpoint_store: JsonCheckpointStore

    def ensure_schema(self) -> None:
        return None

    def save(self, state: JobSearchState) -> None:
        self.checkpoint_store.save(state)

    def load(self, run_id: str) -> JobSearchState:
        return self.checkpoint_store.load(run_id)

    def list_recent(self, limit: int = 8) -> list[JobSearchState]:
        paths = sorted(self.checkpoint_store.root.glob("*.json"), key=lambda path: path.stat().st_mtime, reverse=True)
        states: list[JobSearchState] = []
        for path in paths[:limit]:
            states.append(self.checkpoint_store.load(path.stem))
        return states

    def health(self) -> dict[str, str]:
        self.checkpoint_store.root.mkdir(parents=True, exist_ok=True)
        return {"kind": "local_checkpoint", "status": "ok"}


class PostgresRunStore(RunStore):
    def __init__(self, dsn: str) -> None:
        try:
            import psycopg
            from psycopg.types.json import Jsonb
        except ImportError as exc:  # pragma: no cover - dependency is installed in production/web extras.
            raise RuntimeError("psycopg is required for Postgres-backed web runs") from exc

        self._psycopg = psycopg
        self._jsonb = Jsonb
        self.dsn = dsn

    def ensure_schema(self) -> None:
        try:
            with self._psycopg.connect(self.dsn) as conn:
                conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        except Exception:  # noqa: BLE001 - pgvector is useful but not required for the web shell.
            pass

        with self._psycopg.connect(self.dsn) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS web_runs (
                    run_id TEXT PRIMARY KEY,
                    state JSONB NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
                );

                CREATE INDEX IF NOT EXISTS web_runs_updated_at_idx
                ON web_runs (updated_at DESC);
                """
            )

    def save(self, state: JobSearchState) -> None:
        with self._psycopg.connect(self.dsn) as conn:
            conn.execute(
                """
                INSERT INTO web_runs (run_id, state, updated_at)
                VALUES (%s, %s, now())
                ON CONFLICT (run_id) DO UPDATE SET
                    state = EXCLUDED.state,
                    updated_at = now()
                """,
                (state.run_id, self._jsonb(state.to_dict())),
            )

    def load(self, run_id: str) -> JobSearchState:
        with self._psycopg.connect(self.dsn) as conn:
            row = conn.execute("SELECT state FROM web_runs WHERE run_id = %s", (run_id,)).fetchone()
        if not row:
            raise FileNotFoundError(f"No run found for run_id={run_id}")
        return JobSearchState.from_dict(row[0])

    def list_recent(self, limit: int = 8) -> list[JobSearchState]:
        with self._psycopg.connect(self.dsn) as conn:
            rows = conn.execute(
                "SELECT state FROM web_runs ORDER BY updated_at DESC LIMIT %s",
                (limit,),
            ).fetchall()
        return [JobSearchState.from_dict(row[0]) for row in rows]

    def health(self) -> dict[str, str]:
        with self._psycopg.connect(self.dsn) as conn:
            conn.execute("SELECT 1")
        return {"kind": "postgres", "status": "ok"}


def build_run_store() -> RunStore:
    dsn = os.environ.get("JOBAGENT_DATABASE_URL") or os.environ.get("DATABASE_URL")
    if dsn:
        return PostgresRunStore(dsn)
    return LocalRunStore(JsonCheckpointStore())
