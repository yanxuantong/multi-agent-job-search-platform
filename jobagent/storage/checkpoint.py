from __future__ import annotations

import json
from pathlib import Path

from jobagent.models import JobSearchState


class JsonCheckpointStore:
    """Local checkpointer that mirrors the role of LangGraph checkpointing."""

    def __init__(self, root: str | Path = ".jobagent/checkpoints") -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def path_for(self, run_id: str) -> Path:
        return self.root / f"{run_id}.json"

    def save(self, state: JobSearchState) -> Path:
        path = self.path_for(state.run_id)
        path.write_text(json.dumps(state.to_dict(), indent=2, ensure_ascii=True), encoding="utf-8")
        return path

    def load(self, run_id: str) -> JobSearchState:
        path = self.path_for(run_id)
        if not path.exists():
            raise FileNotFoundError(f"No checkpoint found for run_id={run_id}")
        return JobSearchState.from_dict(json.loads(path.read_text(encoding="utf-8")))

