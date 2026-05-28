# Multi-Agent Job Search Platform

[English version](README.en.md)

这是一个可以直接使用的 agentic job-search product。它面向学习和作品集展示，但不是只停留在 architecture diagram 上，而是已经部署成一个可以打开、可以提交 JD、可以看到 agent workflow 结果的线上产品。

默认路径刻意保持 deterministic 和 low-cost：不需要 API key，不需要托管向量数据库，也不依赖脆弱的外部调用。先把 multi-agent production pattern 看清楚，再逐步替换成 LangGraph、LLM providers、MCP tools、Langfuse、Postgres 或 pgvector。

**线上产品:** [https://jobagent-demo.onrender.com](https://jobagent-demo.onrender.com)

**完整中文 mega guide:** [docs/project1_ai_infra_tutorial_zh.html](docs/project1_ai_infra_tutorial_zh.html)

## 产品截图

![Start a live job-agent run](docs/assets/readme/demo-home.png)

这个 hosted product 有意保持聚焦，但覆盖了完整的操作闭环：

1. 粘贴职位描述。
2. 让 bounded agent nodes 分析职位。
3. 在 application-facing 输出最终生效前暂停。
4. 人工确认 resume proposal。
5. 继续生成 tracker 和 interview-prep 输出。

![Human approval gate](docs/assets/readme/demo-review.png)

![Completed run after approval](docs/assets/readme/demo-complete.png)

## 这个项目在展示什么

- **Supervisor-style orchestration:** 一个小型 graph engine 协调多个 bounded agent nodes。
- **Typed shared state:** 所有 agents 读写同一个 `JobSearchState` model。
- **Human-in-the-loop control:** resume/application 输出会停在 `NEED_USER_APPROVAL`。
- **Checkpoint and resume:** 暂停后的 run 可以在人工确认后继续。
- **Offline evaluation:** deterministic eval cases 用来保护 workflow，避免 agent 行为漂移。
- **Traceability:** 每次 run 都可以写出本地 JSONL traces。
- **Production surface:** FastAPI/Jinja UI、Dockerfile、Render deployment、安全限制，以及 optional Postgres store。
- **Learning bridge:** 本地教学代码可以映射到 LangGraph、MCP、Langfuse、pgvector 和 hosted LLM providers。

## 本地运行

运行 workflow，并停在 resume proposal 的人工确认点：

```bash
python3 -m jobagent.cli demo
```

确认 proposal 后继续一个 paused run：

```bash
python3 -m jobagent.cli resume <run_id> --approve
```

运行完整 workflow，并写入本地 tracker event：

```bash
python3 -m jobagent.cli demo --auto-approve
```

运行 offline evals：

```bash
python3 -m jobagent.cli eval
```

运行测试：

```bash
python3 -m unittest discover -s tests
```

本地启动 web product：

```bash
uvicorn jobagent.web.app:app --reload
```

然后打开 <http://localhost:8000>。

## Render 部署

这个 repo 包含 Render Blueprint：[render.yaml](render.yaml)。当前 hosted product 在 Render free web plan 上部署一个 Docker web service：

- `jobagent-demo`: 运行 `uvicorn jobagent.web.app:app`
- health check: `/healthz`
- public hosted mode flag: `JOBAGENT_PUBLIC_DEMO_MODE=true`

[Deploy to Render](https://render.com/deploy?repo=https://github.com/yanxuantong/multi-agent-job-search-platform)

当前 Render product 不默认创建 managed Postgres，这样可以先上线展示，不被 billing/payment info 卡住。在这个模式下，run state 使用 web instance 内的 local checkpoint store，应该视为 ephemeral。之后如果要更接近 production，可以添加 Render Postgres，并把 `JOBAGENT_DATABASE_URL` 设置成 private connection string；app 会自动切换到 Postgres run store。

## Production Safety

公开服务已经做了基础限制：

- request body 和 job description 有明确大小上限
- `/runs` 有轻量 per-client rate limit
- run id 在读取 checkpoint store 前会先做格式校验
- form submission 只接受 `application/x-www-form-urlencoded`
- response 包含基础浏览器安全头：CSP、frame protection、no-sniff、referrer policy、permissions policy
- 默认 workflow 不调用外部 LLM API，不执行用户代码，也不会 fetch 任意 job URL

这些控制并不意味着 free hosted instance 已经是 high-availability SaaS。它现在适合 portfolio/public traffic，同时保留清晰升级路径：auth、durable Postgres state、queue-backed workers、edge rate limiting 和 abuse monitoring。

## 架构

```mermaid
flowchart TD
  A["JD text"] --> B["ingest"]
  B --> C["jd_extract"]
  C --> D["company_research"]
  D --> E["fit_analysis"]
  E --> F["resume_tailor"]
  F -->|not approved| G["NEED_USER_APPROVAL"]
  G --> K["checkpoint"]
  K -->|resume approve| H["tracker"]
  F -->|approved| H
  H --> I["interview_prep"]
  I --> J["COMPLETED"]
```

## 怎么读代码

建议从 core workflow 开始：

- [jobagent/models.py](jobagent/models.py): shared state、artifacts 和 `StopReason`。
- [jobagent/graph/engine.py](jobagent/graph/engine.py): 小型 graph runner，对应 LangGraph 的 mental model。
- [jobagent/graph/workflow.py](jobagent/graph/workflow.py): node wiring 和 resume behavior。
- [jobagent/agents/](jobagent/agents): bounded agent responsibilities。
- [jobagent/storage/checkpoint.py](jobagent/storage/checkpoint.py): local checkpoint/resume store。
- [jobagent/web/app.py](jobagent/web/app.py): FastAPI production web surface 和安全控制。
- [jobagent/web/store.py](jobagent/web/store.py): local 或 Postgres-backed web run store。
- [jobagent/evals/runner.py](jobagent/evals/runner.py): offline eval harness。
- [mcp_server/career_research_server.py](mcp_server/career_research_server.py): dependency-free MCP-shaped teaching stub。

本地 runtime artifacts 会写到 `.jobagent/`，并被 git ignore：

- `.jobagent/checkpoints/<run_id>.json`
- `.jobagent/runs/<run_id>/trace.jsonl`
- `.jobagent/applications.jsonl`

## Optional Production-Stack Learning Paths

| Stack item | Code entrypoint | Install hint | Cost note |
| --- | --- | --- | --- |
| Local RAG | `jobagent/retrieval/local_rag.py` | Built in | Local keyword retrieval 免费；hosted embeddings/rerankers 可能收费。 |
| LangGraph | `jobagent/graph/langgraph_reference.py` | `python3 -m pip install -e '.[langgraph]'` | Local library 免费；production checkpointers 可能需要 Postgres。 |
| Claude/OpenAI SDKs | `jobagent/llm/anthropic_provider.py`, `jobagent/llm/openai_provider.py` | `python3 -m pip install -e '.[llm]'` | API usage 通常按 token 计费。 |
| Langfuse | `jobagent/observability/langfuse_exporter.py` | `python3 -m pip install -e '.[observability]'` | Self-host 可以免费；hosted tiers 可能收费。 |
| Postgres/pgvector | `jobagent/storage/postgres_memory.py`, `docker-compose.yml` | `docker compose up postgres -d` | Local Docker 免费；managed databases 收费。 |
| External MCP consumer | `jobagent/integrations/external_mcp_tracker.py` | 选择 Notion 或 Sheets MCP credentials 后连接 | Workspace features 可能收费。 |
| MCP SDK server | `mcp_server/career_research_sdk_server.py` | `python3 -m pip install -e '.[mcp]'` | SDK 免费；connected tools 可能有 API costs。 |
| Docker | `Dockerfile`, `docker-compose.yml` | `docker compose run --rm app` | Local Docker 免费；cloud deploy 可能需要 billing。 |

更完整的技术解释在中文 mega guide：[docs/project1_ai_infra_tutorial_zh.html](docs/project1_ai_infra_tutorial_zh.html)。
