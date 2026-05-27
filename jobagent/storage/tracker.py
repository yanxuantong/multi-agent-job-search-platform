from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from jobagent.models import TrackerUpdate


class JsonlApplicationTracker:
    def __init__(self, path: str | Path = ".jobagent/applications.jsonl") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, update: TrackerUpdate) -> None:
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(asdict(update), ensure_ascii=True) + "\n")

