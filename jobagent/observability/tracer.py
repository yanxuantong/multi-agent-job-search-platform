from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass
class TraceEvent:
    run_id: str
    node: str
    event: str
    elapsed_ms: float
    metadata: dict[str, Any]


class JsonlTracer:
    """Small local tracing sink shaped like a Langfuse/OpenTelemetry adapter."""

    def __init__(self, run_id: str, root: Path | str = ".jobagent/runs") -> None:
        self.run_id = run_id
        self.run_dir = Path(root) / run_id
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.path = self.run_dir / "trace.jsonl"

    def span(self, node: str, event: str = "node"):
        return _TraceSpan(self, node, event)

    def record(self, event: TraceEvent) -> None:
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(asdict(event), ensure_ascii=True) + "\n")


class _TraceSpan:
    def __init__(self, tracer: JsonlTracer, node: str, event: str) -> None:
        self.tracer = tracer
        self.node = node
        self.event = event
        self.started = 0.0
        self.metadata: dict[str, Any] = {}

    def __enter__(self):
        self.started = time.perf_counter()
        return self.metadata

    def __exit__(self, exc_type, exc, _tb) -> None:
        elapsed_ms = (time.perf_counter() - self.started) * 1000
        if exc:
            self.metadata["error"] = str(exc)
        self.tracer.record(
            TraceEvent(
                run_id=self.tracer.run_id,
                node=self.node,
                event=self.event,
                elapsed_ms=round(elapsed_ms, 2),
                metadata=self.metadata,
            )
        )

