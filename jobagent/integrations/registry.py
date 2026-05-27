from __future__ import annotations

import importlib.util
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class IntegrationStatus:
    name: str
    original_stack_item: str
    local_learning_entrypoint: str
    package_imports: list[str]
    enabled: bool
    setup_hint: str
    cost_note: str

    def to_dict(self) -> dict:
        return asdict(self)


def list_learning_integrations() -> list[IntegrationStatus]:
    """Report optional production-stack learning paths without requiring them."""

    return [
        _status(
            name="Local RAG retrieval",
            original_stack_item="Company research RAG, chunking, and retrieval ranking",
            local_learning_entrypoint="jobagent/retrieval/local_rag.py",
            package_imports=[],
            setup_hint="Read local_rag.py before replacing keyword ranking with embeddings or rerankers",
            cost_note="Deterministic local retrieval is free; hosted embeddings or rerankers may cost money.",
        ),
        _status(
            name="LangGraph orchestration",
            original_stack_item="LangGraph state graph, interrupts, checkpointing",
            local_learning_entrypoint="jobagent/graph/langgraph_reference.py",
            package_imports=["langgraph"],
            setup_hint="python3 -m pip install -e '.[langgraph]'",
            cost_note="Library is local/free; production checkpointers may need Postgres.",
        ),
        _status(
            name="LLM providers",
            original_stack_item="Claude/OpenAI SDK adapters with structured outputs",
            local_learning_entrypoint="jobagent/llm/anthropic_provider.py and jobagent/llm/openai_provider.py",
            package_imports=["anthropic", "openai"],
            setup_hint="python3 -m pip install -e '.[llm]' and set ANTHROPIC_API_KEY or OPENAI_API_KEY",
            cost_note="API usage is usually billed per token; keep mock mode as the default.",
        ),
        _status(
            name="Langfuse observability",
            original_stack_item="Per-agent trace, latency, token, and cost tracking",
            local_learning_entrypoint="jobagent/observability/langfuse_exporter.py",
            package_imports=["langfuse"],
            setup_hint="python3 -m pip install -e '.[observability]' and configure Langfuse keys",
            cost_note="Self-host can be free but has ops cost; hosted tiers may be paid.",
        ),
        _status(
            name="Postgres pgvector memory",
            original_stack_item="Long-term semantic/episodic memory in Postgres + pgvector",
            local_learning_entrypoint="jobagent/storage/postgres_memory.py and docker-compose.yml",
            package_imports=["psycopg", "pgvector"],
            setup_hint="docker compose up postgres -d && python3 -m pip install -e '.[postgres]'",
            cost_note="Local Docker is free; managed databases are usually paid.",
        ),
        _status(
            name="External MCP tracker consumer",
            original_stack_item="Consume one existing MCP server such as Notion or Google Sheets",
            local_learning_entrypoint="jobagent/integrations/external_mcp_tracker.py",
            package_imports=[],
            setup_hint="Read the adapter first, then connect it to a real Notion/Sheets MCP client when credentials exist",
            cost_note="Local payload construction is free; third-party workspace features may require accounts or billing.",
        ),
        _status(
            name="MCP career-research server",
            original_stack_item="Implement custom career-research MCP server",
            local_learning_entrypoint="mcp_server/career_research_sdk_server.py",
            package_imports=["mcp"],
            setup_hint="python3 -m pip install -e '.[mcp]'",
            cost_note="SDK is free; tools called from MCP may have their own API costs.",
        ),
        _status(
            name="Docker deployment touchpoint",
            original_stack_item="Dockerized app plus local Postgres/pgvector service",
            local_learning_entrypoint="Dockerfile and docker-compose.yml",
            package_imports=[],
            setup_hint="docker compose run --rm app python3 -m jobagent.cli eval",
            cost_note="Local Docker is free; Fly.io, Render, Modal, and databases may require billing.",
        ),
    ]


def _status(
    *,
    name: str,
    original_stack_item: str,
    local_learning_entrypoint: str,
    package_imports: list[str],
    setup_hint: str,
    cost_note: str,
) -> IntegrationStatus:
    return IntegrationStatus(
        name=name,
        original_stack_item=original_stack_item,
        local_learning_entrypoint=local_learning_entrypoint,
        package_imports=package_imports,
        enabled=all(_is_importable(package_name) for package_name in package_imports),
        setup_hint=setup_hint,
        cost_note=cost_note,
    )


def _is_importable(package_name: str) -> bool:
    return importlib.util.find_spec(package_name) is not None
