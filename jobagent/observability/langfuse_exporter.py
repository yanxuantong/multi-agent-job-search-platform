from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class ExportSummary:
    trace_path: str
    exported_events: int
    destination: str


class LangfuseTraceExporter:
    """Export local JSONL traces to Langfuse when the SDK is configured.

    Tests can pass a fake client with a ``trace`` method. Production use can
    rely on the Langfuse SDK client created when optional dependencies exist.
    """

    def __init__(self, client: Any | None = None) -> None:
        self.client = client or self._default_client()

    def export_jsonl_trace(self, trace_path: str | Path) -> ExportSummary:
        path = Path(trace_path)
        events = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        for event in events:
            self._record_event(event)
        flush = getattr(self.client, "flush", None)
        if callable(flush):
            flush()
        return ExportSummary(str(path), len(events), "langfuse")

    def _record_event(self, event: dict[str, Any]) -> None:
        trace = getattr(self.client, "trace", None)
        if not callable(trace):
            raise RuntimeError("Langfuse client must expose a trace(...) method")
        trace(
            id=event.get("run_id"),
            name=f"jobagent:{event.get('node')}",
            metadata={
                "event": event.get("event"),
                "elapsed_ms": event.get("elapsed_ms"),
                **event.get("metadata", {}),
            },
        )

    @staticmethod
    def _default_client() -> Any:
        try:
            from langfuse import Langfuse
        except ImportError as exc:  # pragma: no cover - optional dependency.
            raise RuntimeError(
                "Langfuse SDK is not installed. Run: python3 -m pip install -e '.[observability]'"
            ) from exc
        return Langfuse()
