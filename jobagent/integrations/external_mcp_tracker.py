from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from jobagent.models import TrackerUpdate


@dataclass(frozen=True)
class MCPToolInvocation:
    server_name: str
    tool_name: str
    arguments: dict[str, Any]
    idempotency_key: str


class ExternalMCPTrackerAdapter:
    """Learning boundary for consuming an existing MCP tracker server.

    The original Project 1 plan asks for both sides of MCP:
    - implement a custom career-research server
    - consume an existing server such as Notion or Google Sheets

    This adapter keeps the consumer contract explicit without forcing a Notion
    or Google account into the default local run.
    """

    def __init__(self, server_name: str = "notion") -> None:
        self.server_name = server_name

    def build_tracker_write(self, update: TrackerUpdate) -> MCPToolInvocation:
        return MCPToolInvocation(
            server_name=self.server_name,
            tool_name="create_or_update_application",
            arguments={
                "company_name": update.company_name,
                "role_title": update.role_title,
                "status": update.status,
                "fit_score": update.fit_score,
                "next_action": update.next_action,
                "notes": update.notes,
            },
            idempotency_key=f"{update.company_name}:{update.role_title}".lower().replace(" ", "-"),
        )

    def to_json_rpc_payload(self, invocation: MCPToolInvocation) -> dict[str, Any]:
        return {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": invocation.tool_name,
                "arguments": invocation.arguments,
                "metadata": {"idempotency_key": invocation.idempotency_key},
            },
            "id": invocation.idempotency_key,
        }

    def serialize_tracker_write(self, update: TrackerUpdate) -> dict[str, Any]:
        return self.to_json_rpc_payload(self.build_tracker_write(update))


def tracker_update_as_mcp_arguments(update: TrackerUpdate) -> dict[str, Any]:
    return asdict(ExternalMCPTrackerAdapter().build_tracker_write(update))
