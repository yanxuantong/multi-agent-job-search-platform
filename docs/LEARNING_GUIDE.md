# Learning Guide

This codebase is meant to teach the shape of a production multi-agent system before adding heavyweight dependencies.

## 1. Read The State First

Start with `jobagent/models.py`.

The most important idea is that agents do not pass loose strings around. They update a typed `JobSearchState`:

- `normalized_jd`
- `company_brief`
- `fit_analysis`
- `resume_proposal`
- `tracker_update`
- `interview_pack`
- `stop_reason`
- `pending_node`

In a real LangGraph project this state would become the `StateGraph` state schema.

## 2. Read The Graph

Read `jobagent/graph/workflow.py`, then `jobagent/graph/engine.py`.

The graph runner is intentionally tiny:

1. Run current node.
2. Record a trace span.
3. Respect `next_node`.
4. Stop on `StopReason`.
5. Save a checkpoint.

This maps directly to LangGraph concepts: nodes, edges, interrupts, checkpointing, and resumability.

## 3. Read One Agent At A Time

Each file under `jobagent/agents/` owns one bounded responsibility.

The important learning pattern is not the heuristic text extraction. The important pattern is the contract:

- inputs come from `JobSearchState`
- outputs are typed artifacts
- failures become graph-visible stop reasons or errors
- no agent secretly controls the whole workflow

## 4. Understand HITL

Run:

```bash
python3 -m jobagent.cli demo
```

The run stops at `NEED_USER_APPROVAL` and writes a checkpoint under `.jobagent/checkpoints/`.

Then resume:

```bash
python3 -m jobagent.cli resume <run_id> --approve
```

That is the core pattern behind human-in-the-loop agent products: pause, persist, wait for a human decision, resume from a known node.

## 5. Understand Evals

Run:

```bash
python3 -m jobagent.cli eval
```

The eval suite checks schema-level and workflow-level behavior:

- expected company
- expected extracted skills
- expected stop reason
- minimum fit score

Production evals should add source-grounding checks, human labels, LLM judges with rubrics, and regression dashboards.

## 6. Where Real LLM Calls Go

The provider boundary is in `jobagent/llm/provider.py`.

The prompt registry is in `jobagent/prompts/registry.py`.

Production migration:

- Implement `AnthropicProvider.generate_structured`.
- Implement `OpenAIProvider.generate_structured`.
- Keep the same `LLMRequest` and `LLMResponse` shape.
- Track prompt name/version in traces and evals.

## 7. Migration Map

Current teaching code -> production version:

- `GraphEngine` -> LangGraph `StateGraph`
- `JsonCheckpointStore` -> LangGraph checkpointer backed by Postgres
- `JsonlTracer` -> Langfuse/OpenTelemetry
- `MockLLMProvider` -> Anthropic/OpenAI SDK adapter
- `JsonlApplicationTracker` -> Postgres plus Notion/Google Sheets MCP
- `mcp_server/career_research_server.py` -> official MCP Python SDK server

