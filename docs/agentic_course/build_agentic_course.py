from __future__ import annotations

from dataclasses import dataclass
from html import escape
from pathlib import Path


OUT_DIR = Path(__file__).resolve().parent
REPO_ROOT = OUT_DIR.parents[1]
UPDATED = "2026-05-30"


@dataclass(frozen=True)
class Link:
    label: str
    url: str
    note: str


@dataclass(frozen=True)
class Chapter:
    slug: str
    part: str
    title: str
    subtitle: str
    concept: list[str]
    allegory: str
    anchors: list[str]
    labs: list[str]
    choices: list[str]
    industry: list[str]
    links: list[Link]
    visual: str


CHAPTERS: list[Chapter] = [
    Chapter(
        "00_overview",
        "Part 0 / 项目入口",
        "第 0 章：这不是聊天机器人，这是一个可运行的 Agentic Product",
        "先把 JobAgent 当成一个可以运行、暂停、恢复、验证、部署的产品，而不是一个 prompt demo。",
        [
            "传统软件工程师很容易把 agent 理解成「一个会聊天的 API」。本章先换掉这个心智模型：JobAgent 是一个 job-search workflow product，输入职位描述，产出结构化 JD、公司研究、fit 分析、简历建议、tracker 更新与面试准备。",
            "默认路径刻意 deterministic、low-cost、无 API key，是为了先看清控制面：graph orchestration、typed state、human approval、checkpoint、eval、trace、guardrails、web surface。",
            "学习目标不是立刻接入最强模型，而是理解怎样把不稳定的智能能力包进稳定的工程边界里。",
        ],
        "把整个系统想成一家求职事务所。客户带着一份 JD 进门，前台收件，分析员拆 JD，研究员查公司，顾问判断匹配度，简历顾问提出修改建议，负责人审批后才更新 tracker，最后面试教练准备问题。真正有价值的不是某个员工多聪明，而是这家事务所的流程不会乱。",
        [
            "README.zh.md",
            "jobagent/cli.py",
            "jobagent/web/app.py",
            "docs/project1_ai_infra_tutorial_zh.html",
        ],
        [
            "运行 `python3 -m jobagent.cli demo`，观察 workflow 停在 approval gate。",
            "运行 `python3 -m jobagent.cli demo --auto-approve`，观察完整结果。",
            "运行 `uvicorn jobagent.web.app:app --reload`，从浏览器提交一份 JD。",
        ],
        [
            "为什么本项目先不用真实 LLM？因为初学阶段最应该先掌握 workflow control，而不是 token 调参。",
            "什么样的输出必须人工审批？任何会影响真实申请、外部系统写入、用户身份或金钱的动作。",
            "这个项目作为 portfolio 应该讲什么？讲 agentic infra，而不是只讲「我调用了模型」。",
        ],
        [
            "2026 年行业重点已经从「agent demo」转向「agent runtime」。OpenAI、AWS、LangGraph 等都在把工具、文件、沙盒、状态、trace、eval、长期运行做成平台能力。",
            "JobAgent 的学习价值正好在这里：它用小代码复刻这些生产系统的核心形状，让读者先理解概念，再决定是否升级到工业框架。",
        ],
        [
            Link("OpenAI Agents SDK evolution", "https://openai.com/index/the-next-evolution-of-the-agents-sdk", "OpenAI 在 2026 年强调沙盒、文件工具和更完整的 agent runtime。"),
            Link("AWS AgentCore release notes", "https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/release-notes.html", "AWS AgentCore 把 runtime、memory、identity、observability、evaluation 放进托管平台。"),
        ],
        "产品闭环图：JD 输入 -> agent workflow -> approval -> tracker/interview outputs。",
    ),
    Chapter(
        "01_graph_engine",
        "Part 1 / 最小心智模型",
        "第 1 章：从 Pipeline 到 Graph：为什么 agent 工程首先是调度问题",
        "Agentic workflow 的第一层不是魔法，而是 node、edge、state、stop condition。",
        [
            "传统 infra 背景的读者熟悉 pipeline、DAG、job queue、state machine。Agent graph 与它们亲缘关系很近，只是每个节点可能包含 LLM、工具调用、检索或人工审批。",
            "`GraphEngine` 是本项目的教学版 orchestrator：它注册节点、按 `next_node` 前进、遇到 `stop_reason` 停止、把错误写进 state。",
            "理解 graph 后，multi-agent 不再是「多个机器人聊天」，而是「多个有边界的节点在同一状态上协作」。",
        ],
        "机场调度塔不会亲自搬运行李，也不会检查护照。它只知道每架飞机当前在哪、下一步去哪里、什么时候必须暂停。GraphEngine 就是这个塔台。",
        [
            "jobagent/graph/engine.py",
            "jobagent/graph/workflow.py",
            "jobagent/agents/",
        ],
        [
            "阅读 `GraphEngine.run()`，标出预算检查、未知节点检查、span 记录、异常转换、stop handling。",
            "在 `workflow.py` 中画出 `ingest -> jd_extract -> company_research -> fit_analysis -> resume_tailor -> tracker -> interview_prep`。",
            "临时把一个 `next_node` 改成不存在的节点，运行测试或 CLI，观察 `TOOL_ERROR`。",
        ],
        [
            "什么时候简单 graph engine 足够？教学、portfolio、小型 deterministic workflow。",
            "什么时候该上 LangGraph？需要长期运行、复杂条件路由、生产 checkpointer、streaming、并发或部署平台。",
            "Graph 节点应该细到什么程度？细到能独立测试、独立追踪、独立恢复。",
        ],
        [
            "LangGraph 官方把自己定位为 long-running stateful workflow 的底层基础设施，核心能力是 durable execution、streaming、human-in-the-loop、memory 与 debugging。",
            "这说明 industry 的抽象重点不是「prompt chain」，而是「可恢复的状态机」。",
        ],
        [
            Link("LangGraph overview", "https://docs.langchain.com/oss/python/langgraph", "LangGraph 官方概览，解释 durable execution、HITL、memory、debugging 等核心能力。"),
            Link("Thinking in LangGraph", "https://docs.langchain.com/oss/python/langgraph/thinking-in-langgraph", "适合对照本项目的 GraphEngine，理解何时需要工业级 graph。"),
        ],
        "塔台调度图：每个 agent 是一个登机口，state 是航班进度板。",
    ),
    Chapter(
        "02_shared_state",
        "Part 1 / 最小心智模型",
        "第 2 章：Shared State：Multi-Agent 系统里的唯一事实表",
        "如果没有 typed shared state，multi-agent 很快会退化成互相转述的聊天记录。",
        [
            "`JobSearchState` 是整个项目最重要的 contract。所有 agent 读写它，而不是靠自然语言互相传话。",
            "State 里既有业务产物：`JDExtract`、`CompanyBrief`、`FitAnalysis`、`ResumeProposal`，也有控制字段：`budget`、`errors`、`approved`、`stop_reason`、`pending_node`。",
            "对传统 infra 工程师来说，可以把它理解成 request context、workflow row、event payload 和 recovery snapshot 的结合体。",
        ],
        "所有机场岗位都看同一块航班大屏。安检不能自己发明一个起飞时间，地勤也不能靠记忆猜飞机是否已放行。Agent 系统里的 shared state 就是这块大屏。",
        [
            "jobagent/models.py",
            "jobagent/storage/checkpoint.py",
            ".jobagent/checkpoints/<run_id>.json",
        ],
        [
            "跑一次 `demo` 后打开 checkpoint JSON，对照 `JobSearchState` 字段。",
            "找出每个 agent 写入哪个字段，画一张 state evolution 表。",
            "给 state 草拟一个新字段 `salary_signals`，判断应该由哪个 node 写入、哪个 node 消费。",
        ],
        [
            "State 应该存原始 LLM 输出还是结构化结果？生产系统通常两者都要，但业务路径应该依赖结构化结果。",
            "State schema 变更如何兼容旧 checkpoint？需要版本字段或迁移策略。",
            "共享 state 会不会变成大泥球？会，所以每个 node 必须有清晰读写范围。",
        ],
        [
            "行业框架正在把 thread、run、state、trace 做成一等对象。Agent 系统的可靠性越来越依赖显式状态，而不是长聊天历史。",
            "LangGraph durable execution 文档特别强调 checkpoint、thread id、determinism 与 side-effect wrapping，这些都与本章 state 设计直接相关。",
        ],
        [
            Link("LangGraph durable execution", "https://docs.langchain.com/oss/python/langgraph/durable-execution", "解释 state checkpoint、resume、deterministic replay 与 idempotency。"),
            Link("OpenAI Agents SDK tracing", "https://openai.github.io/openai-agents-python/tracing/", "展示 agent run 中 generation、tool、handoff、guardrail 等事件如何被结构化记录。"),
        ],
        "State 演化图：空 state -> JDExtract -> CompanyBrief -> FitAnalysis -> ResumeProposal -> TrackerUpdate。",
    ),
    Chapter(
        "03_bounded_agents",
        "Part 1 / 最小心智模型",
        "第 3 章：Bounded Agent：为什么每个 agent 都应该小而窄",
        "一个万能 agent 看起来省事，长期会变成不可测、不可恢复、不可解释的 prompt monster。",
        [
            "本项目每个 agent 都是 bounded node：`ingestion` 只规范输入，`jd_extract` 只抽取 JD，`company_research` 只生成公司 brief，`fit_analysis` 只评分，`resume_tailor` 只产出简历建议。",
            "这种拆分延续了传统工程里的 single responsibility 与 bounded context，只是 service 变成了 agent node。",
            "Bounded agent 的核心不是 prompt 名字，而是输入字段、输出字段、失败方式、是否允许 side effect。",
        ],
        "不要雇一个万能实习生从读 JD、查公司、改简历、更新表格到准备面试全包。你需要一支小团队，每个人都知道自己的桌面在哪里、交付物是什么。",
        [
            "jobagent/agents/ingestion.py",
            "jobagent/agents/jd_extract.py",
            "jobagent/agents/company_research.py",
            "jobagent/agents/fit_analysis.py",
            "jobagent/agents/resume_tailor.py",
            "jobagent/agents/tracker.py",
            "jobagent/agents/interview_prep.py",
        ],
        [
            "给每个 agent 写一句 contract：读取哪些 state 字段、写入哪些字段、返回哪个 next node。",
            "故意让 `fit_analysis` 在没有 `company_brief` 时运行，观察错误边界是否清楚。",
            "新增一个只读 agent 草案，例如 `market_signal_analysis`，先写 contract 不写实现。",
        ],
        [
            "Agent 拆分按任务、按风险、按工具权限还是按团队所有权？本项目主要按任务和风险拆分。",
            "什么时候需要 agent handoff？当下一个 specialist 需要不同 instruction、tool set 或审批边界。",
            "Agent 是否应该互相直接调用？一般不要，优先通过 graph 和 shared state 调度。",
        ],
        [
            "2026 年行业正在从 generalist agent hype 回到 specialist agents + controlled handoff。OpenAI Agents SDK 的 handoffs 与 guardrails 就是这种趋势的体现。",
            "企业落地时，最难的不是让 agent 更会说话，而是让它只在被授权的边界内行动。",
        ],
        [
            Link("OpenAI Agents SDK handoffs", "https://openai.github.io/openai-agents-python/handoffs/", "解释 agent 之间如何交接任务以及 handoff 的边界。"),
            Link("OpenAI Agents SDK guardrails", "https://openai.github.io/openai-agents-python/guardrails/", "解释 input/output guardrails 与 tool guardrails。"),
        ],
        "小团队职责图：每个 agent 只拥有一个窄交付物。",
    ),
    Chapter(
        "04_stop_reason",
        "Part 2 / 控制、暂停、恢复",
        "第 4 章：StopReason：Agentic 系统不是一直跑到死",
        "StopReason 是 agent workflow 的刹车系统，也是调试与产品体验的共同语言。",
        [
            "`StopReason` 把 workflow 结束原因显式化：成功、需要审批、需要更多输入、工具错误、预算用完、低置信度、不安全动作。",
            "没有 stop reason 的系统只能表现为「转圈」「报错」或「胡乱继续」。有了 stop reason，UI、CLI、测试、恢复逻辑都能做正确反应。",
            "这也是从 demo 到 product 的关键一步：系统必须知道自己为什么停。",
        ],
        "一辆车不只有油门。它需要刹车、手刹、故障灯、油量报警、车门未关提醒。Agent workflow 也一样，不能只有 continue。",
        [
            "jobagent/models.py",
            "jobagent/graph/engine.py",
            "jobagent/agents/resume_tailor.py",
        ],
        [
            "把 `RunBudget.max_steps` 调小，触发 `BUDGET_EXCEEDED`。",
            "构造一个缺失字段，让某个 node 抛错，观察 `TOOL_ERROR` 如何进入 state。",
            "比较 `NEED_USER_APPROVAL` 与 `NEED_MORE_INPUT`：一个是放行问题，一个是信息不足问题。",
        ],
        [
            "Stop reason 应该多细？细到 UI/调用方能采取不同动作即可。",
            "错误应该直接 raise 还是写入 state？node 内部可以 raise，graph 层应该转成可观察 state。",
            "低置信度应该自动重试还是停给人？取决于成本、风险和是否有更强 evidence source。",
        ],
        [
            "行业里 human-in-the-loop、guardrails、budget limits、policy controls 都是在给 agent 系统加停止条件。",
            "LangGraph interrupts 直接把暂停、持久化、resume 做成 graph primitive。",
        ],
        [
            Link("LangGraph interrupts", "https://docs.langchain.com/oss/python/langgraph/human-in-the-loop", "解释 graph 如何动态暂停并等待外部输入。"),
            Link("AWS AgentCore policy controls", "https://aws.amazon.com/blogs/aws/amazon-bedrock-agentcore-adds-quality-evaluations-and-policy-controls-for-deploying-trusted-ai-agents/", "AWS 把 policy controls 与 agent evaluation/observability 放到同一生产语境中。"),
        ],
        "刹车面板图：不同 stop reason 对应不同恢复动作。",
    ),
    Chapter(
        "05_hitl",
        "Part 2 / 控制、暂停、恢复",
        "第 5 章：Human-in-the-loop：人工审批不是 UI 功能，是系统边界",
        "HITL 的本质是权限边界：哪些动作可以建议，哪些动作必须由人放行。",
        [
            "JobAgent 在 `resume_tailor` 后暂停，因为简历建议属于 application-facing output。系统可以生成 proposal，但不能假装用户已经接受。",
            "HITL 不是一个按钮，而是一条系统 contract：暂停时保存 state，展示需要审批的内容，用户决定后从 `pending_node` 继续。",
            "这类设计适用于邮件发送、简历投递、CRM 写入、支付、代码 merge、数据删除等高风险动作。",
        ],
        "机场可以自动规划航线，但起飞许可必须由塔台给出。Resume proposal 就像起飞前的放行请求：系统准备好了，但还不能自作主张。",
        [
            "jobagent/agents/resume_tailor.py",
            "jobagent/graph/workflow.py",
            "jobagent/web/templates/run.html",
            "tests/test_workflow.py",
        ],
        [
            "运行 `python3 -m jobagent.cli demo`，记录暂停时的 `stop_reason` 和 `pending_node`。",
            "运行 `python3 -m jobagent.cli resume <run_id> --approve`，确认 workflow 不重跑前序节点。",
            "在 web UI 上完成一次 approval，观察页面如何表达 pending 状态。",
        ],
        [
            "HITL 应该暂停在 action 前还是 action 后？通常是 action 前，尤其是外部 side effect。",
            "审批内容应该可编辑还是只可 approve/reject？生产系统通常需要 edit-and-resume。",
            "谁有审批权？单用户 demo 可以简单处理，企业产品需要 identity、role、audit log。",
        ],
        [
            "LangGraph 官方 HITL API 采用 interrupt + Command resume 模式，和本项目的 pending node mental model 很接近。",
            "OpenAI Agents SDK 也强调 guardrails 与 handoffs 的边界，但要注意不同 guardrail 类型覆盖的调用路径并不完全一样。",
        ],
        [
            Link("LangGraph HITL server API", "https://docs.langchain.com/langgraph-platform/add-human-in-the-loop", "展示 graph run 如何暂停、返回 interrupt、再用 Command resume。"),
            Link("OpenAI tool guardrails", "https://openai.github.io/openai-agents-js/guides/guardrails", "解释 tool guardrails 在工具调用前后如何验证或阻止动作。"),
        ],
        "审批闸门图：proposal -> human decision -> resume tracker。",
    ),
    Chapter(
        "06_checkpoint_resume",
        "Part 2 / 控制、暂停、恢复",
        "第 6 章：Checkpoint 与 Resume：Agentic Workflow 的耐久执行",
        "能暂停不算难；能在正确位置恢复，而且不重复副作用，才是工程能力。",
        [
            "本项目把每次 run 保存为 checkpoint。暂停后，`pending_node` 记录下一步该从哪里继续。",
            "这让用户可以先看 resume proposal，再决定是否 approve。系统不需要重新解析 JD、重新研究公司、重新评分。",
            "Checkpoint 是未来升级 Postgres、queue-backed worker、LangGraph checkpointer 的本地原型。",
        ],
        "办签证时你不希望每补一份材料就重新排队、重新拍照、重新填表。Checkpoint 的价值就是保留已完成步骤，只从缺口继续。",
        [
            "jobagent/storage/checkpoint.py",
            "jobagent/graph/workflow.py",
            "jobagent/web/store.py",
            ".jobagent/checkpoints/",
        ],
        [
            "运行 demo 后删除 checkpoint，再尝试 resume，观察失败形态。",
            "对比 approve 前后 checkpoint JSON，确认哪些字段变化。",
            "思考如果 tracker 写入外部 Notion，resume 时如何避免重复写入。",
        ],
        [
            "本地 JSON checkpoint 适合学习，但 hosted free instance 里 state 可能 ephemeral。",
            "生产环境需要 durable store、idempotency key、side-effect record、schema version。",
            "恢复逻辑应该从 node 边界恢复，不应该依赖 Python stack frame 还活着。",
        ],
        [
            "LangGraph durable execution 文档明确指出，resume 不是从同一行代码继续，而是从合适起点 replay，因此 side effects 要包装、幂等或记录。",
            "这也是 agent workflow 和普通 request/response API 最大的工程差异之一。",
        ],
        [
            Link("LangGraph durable execution", "https://docs.langchain.com/oss/python/langgraph/durable-execution", "重点阅读 determinism、consistent replay、resuming workflows。"),
            Link("AWS AgentCore release notes", "https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/release-notes.html", "托管 agent runtime 对 memory、runtime、observability 的持续增强。"),
        ],
        "恢复时序图：run -> checkpoint -> interrupt -> approve -> resume pending node。",
    ),
    Chapter(
        "07_tool_use",
        "Part 3 / 工具、记忆、检索",
        "第 7 章：Tool Use：Agent 什么时候应该调用工具",
        "工具是 agent 的手，但每只手都要有权限、预算、审计和失败语义。",
        [
            "本项目的默认路径尽量少依赖外部工具，是为了让 workflow 可预测。但 repo 已经保留 integration registry、external tracker、MCP server 等扩展点。",
            "Tool use 的工程问题包括：输入 schema、权限边界、超时、重试、side effect、幂等、日志、成本、错误恢复。",
            "传统 API 调用通常由开发者决定；agent tool call 则可能由模型决定，所以 guardrails 和 tool contract 更重要。",
        ],
        "给实习生一把钥匙不等于让他随便开所有门。每个工具都应该像门禁卡：能开哪些门、什么时候开、开门要不要记录，都必须明确。",
        [
            "jobagent/tools/text.py",
            "jobagent/integrations/registry.py",
            "jobagent/integrations/external_mcp_tracker.py",
            "mcp_server/career_research_server.py",
        ],
        [
            "给 tracker integration 写一个 dry-run mode 设计，确保不会真实写外部系统。",
            "为一个假工具定义输入 schema、输出 schema 和错误类型。",
            "列出哪些工具调用必须经过 HITL。",
        ],
        [
            "工具应该直接暴露给 LLM，还是由 deterministic node 调用？高风险工具优先 deterministic wrapper。",
            "工具失败应该重试几次？取决于是否幂等、是否昂贵、是否会重复 side effect。",
            "工具输出能否直接进入 prompt？需要清洗、裁剪、引用来源。",
        ],
        [
            "OpenAI Agents SDK 在 2026 年强化 file tools、computer use、sandbox execution，说明 agent 正在从「回答」走向「操作」。",
            "操作能力越强，沙盒、权限和审计越不是可选项。",
        ],
        [
            Link("OpenAI new tools for building agents", "https://openai.com/index/new-tools-for-building-agents/", "Responses API 与 Agents SDK 将模型、工具和 agent loop 更紧密地放在一起。"),
            Link("OpenAI Agents SDK tracing", "https://openai.github.io/openai-agents-python/tracing/", "工具调用、handoff、guardrail 都会进入 trace。"),
        ],
        "工具门禁图：agent -> policy -> tool -> trace -> state。",
    ),
    Chapter(
        "08_memory_story_bank",
        "Part 3 / 工具、记忆、检索",
        "第 8 章：Memory 与 Story Bank：不是所有上下文都该塞进 Prompt",
        "Memory 的第一原则：该结构化的结构化，该检索的检索，该短期的不要伪装长期。",
        [
            "`story_bank.json` 是用户职业素材库，帮助 interview prep 和 resume narrative 选择合适故事。",
            "它不同于 workflow state：state 是一次 run 的工作台，story bank 是跨 run 的用户资产。",
            "真正的 agent memory 应该分层：当前任务 state、用户 profile、长期经验库、可检索文档、外部系统记录。",
        ],
        "不要把整间图书馆都塞进会议室。开会时带目录、索引和几本相关书就够了。Memory 工程就是决定什么留在会议桌上，什么留在书架里。",
        [
            "jobagent/memory/story_bank.py",
            "samples/story_bank.json",
            "jobagent/storage/postgres_memory.py",
        ],
        [
            "修改 `samples/story_bank.json`，重新运行 auto-approve，观察 interview pack 的故事匹配变化。",
            "设计一个职业画像 schema：技能、行业偏好、项目故事、禁用信息、目标公司。",
            "写出哪些 memory 可以给模型看，哪些只能用于 deterministic filtering。",
        ],
        [
            "Memory 是否应该自动写入？敏感用户画像最好需要用户确认。",
            "长期 memory 用 Postgres、文件、向量库还是外部知识库？取决于规模、检索需求和隐私边界。",
            "Context window 变大是否意味着不用 memory？不，长上下文也需要选择、排序和治理。",
        ],
        [
            "2026 年 agent platform 普遍把 memory 做成 runtime primitive，但具体实现仍然要面对隐私、授权、更新、删除和评估问题。",
            "JobAgent 的 story bank 是一个轻量起点，可以逐步升级成用户职业 ledger。",
        ],
        [
            Link("AWS AgentCore release notes", "https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/release-notes.html", "AgentCore release notes 多次提到 memory、runtime、identity 与 observability。"),
            Link("LangGraph overview", "https://docs.langchain.com/oss/python/langgraph", "LangGraph 将 short-term working memory 与 long-term memory 放在核心能力中。"),
        ],
        "记忆分层图：run state / story bank / retrieval store / external systems。",
    ),
    Chapter(
        "09_local_rag",
        "Part 3 / 工具、记忆、检索",
        "第 9 章：Local RAG：先理解检索，再上向量数据库",
        "RAG 不是接一个 vector DB，而是选择什么进入上下文的工程。",
        [
            "本项目的 local RAG 已经从简单关键词排序升级为 context pack：query、candidate count、returned chunks、citations、freshness warnings 都会进入 state 和 UI。",
            "向量数据库解决的是一部分 retrieval 问题，不解决 chunk 质量、query rewrite、source attribution、eval、latency、成本、权限过滤。",
            "对于求职场景，RAG 可以用于公司资料、个人项目故事、JD 历史、行业知识，但每类资料的可信度和时效不同。",
        ],
        "检索像给研究员递资料。你不是把整个互联网打印出来放桌上，而是挑出几页最相关、来源可靠、能回答当前问题的材料。",
        [
            "jobagent/retrieval/local_rag.py",
            "jobagent/retrieval/eval_runner.py",
            "samples/job_description.txt",
            "samples/story_bank.json",
            "samples/retrieval_eval_suite.json",
        ],
        [
            "运行 `python3 -m jobagent.cli retrieval-eval`，观察 recall@k、precision@k、MRR 和 failure categories。",
            "打开一次 web run detail，查看 Retrieval context 里每个 agent 的 query、chunk、score、freshness。",
            "给 story bank 增加 expires_at，观察 stale source warning 如何影响 fit concerns。",
        ],
        [
            "RAG 的首个 eval 应该测 retrieval 还是 final answer？两者都要，但先测 retrieval 命中更可控；final answer eval 等 context 稳定后叠加。",
            "是否需要 pgvector？当数据量、语义匹配需求、跨文档检索需求上来后再引入；当前先保留 hybrid_rank_chunks 作为升级接口。",
            "如何避免过期信息？source timestamp、refresh policy、行业动态单独标注；个人 story bank 可以 manual refresh。",
        ],
        [
            "RAG 工程正在从「向量库接入」走向「RAG observability + eval」。Langfuse、LangSmith、Arize 等都在围绕 retrieval trace、dataset experiment、quality score 建能力。",
            "这和 JobAgent 的学习路径一致：先把本地检索做可见、可测、可回归，再逐步升级到 pgvector、reranker 和 final-answer grounding eval。",
        ],
        [
            Link("Langfuse RAG observability and evals", "https://langfuse.com/blog/2025-10-28-rag-observability-and-evals", "展示如何 trace RAG pipeline、评估 retrieval 和 final answer。"),
            Link("Langfuse observation types", "https://langfuse.com/docs/observability/features/observation-types", "Langfuse 将 retriever、tool、agent、guardrail 等作为不同 observation type。"),
        ],
        "RAG 管线图：query -> candidate chunks -> rank -> context -> generation/eval。",
    ),
    Chapter(
        "10_mcp",
        "Part 3 / 工具、记忆、检索",
        "第 10 章：MCP：把工具世界标准化",
        "MCP 可以理解为 agent 的工具协议层，但协议标准化不等于安全自动解决。",
        [
            "本项目提供 dependency-free MCP-shaped teaching stub 和 SDK server，让读者理解 tool/resource/server 的边界。",
            "MCP 的价值在于把 agent 连接外部工具、数据源和服务的方式标准化，减少每个应用自定义 glue code。",
            "但 MCP server 也扩大了攻击面：本地进程、凭证、文件、网络、工具权限都必须治理。",
        ],
        "MCP 像 USB-C：统一接口很方便，但你仍然要知道插上的设备是什么、能读什么数据、会不会反向供电烧坏机器。",
        [
            "mcp_server/career_research_server.py",
            "mcp_server/career_research_sdk_server.py",
            "jobagent/integrations/external_mcp_tracker.py",
        ],
        [
            "阅读 career research MCP stub，写出它暴露了哪些能力。",
            "设计一个 `company_research` MCP tool 的 input/output schema。",
            "列出 MCP server 需要的权限清单和审计字段。",
        ],
        [
            "什么时候用 MCP，什么时候直接写 integration？跨客户端复用时用 MCP，单应用内部逻辑可先直接 integration。",
            "MCP tool 是否应该有网络访问？取决于任务，但必须限制域名、超时和输出大小。",
            "MCP server 如何鉴权？本地 demo 可简单，生产环境要 identity、policy、audit。",
        ],
        [
            "MCP 在 2024-2026 快速成为 agent-tool integration 的事实标准之一，同时安全讨论也明显升温。",
            "教程需要同时讲 adoption 和 risk，避免把协议当成魔法安全层。",
        ],
        [
            Link("Anthropic MCP intro", "https://www.anthropic.com/news/model-context-protocol", "MCP 初始介绍，解释为什么需要统一连接数据源和工具。"),
            Link("MCP resources docs", "https://modelcontextprotocol.io/docs/concepts/resources", "MCP resources、URI、metadata、annotations 的官方概念说明。"),
        ],
        "协议边界图：agent client -> MCP server -> tools/resources -> audit log。",
    ),
    Chapter(
        "11_llm_provider",
        "Part 4 / 真实生产栈",
        "第 11 章：LLM Provider：把模型调用隔离成可替换接口",
        "不要让业务节点直接散落 OpenAI、Anthropic 或其他 SDK 调用。",
        [
            "本项目把 LLM provider 放在独立模块，是为了保留 deterministic 默认路径，同时让真实模型调用成为可替换能力。",
            "Provider abstraction 处理的不只是供应商切换，还包括 retry、timeout、JSON schema、token accounting、model version、fallback、mock testing。",
            "对 agent 系统来说，模型是一个不稳定但强大的依赖，必须像外部服务一样隔离。",
        ],
        "模型供应商像不同航空公司。乘客关心到达目的地，机场系统必须能处理不同航空公司的票号、延误、行李规则和取消策略。",
        [
            "jobagent/llm/provider.py",
            "jobagent/llm/openai_provider.py",
            "jobagent/llm/anthropic_provider.py",
            "pyproject.toml",
        ],
        [
            "阅读 provider interface，写一个 fake provider 的测试计划。",
            "列出真实 LLM 接入后每个 agent 可能新增的失败模式。",
            "设计 structured output parsing 失败时的 fallback 行为。",
        ],
        [
            "是否应该一开始支持多模型？教学项目不必，但 provider 边界应该保留。",
            "模型输出不稳定时靠 prompt 还是 eval？prompt 是实现，eval 是保护网。",
            "高成本模型放在哪些节点？优先放在需要推理/写作质量的节点，而不是 deterministic extraction。",
        ],
        [
            "Datadog 2026 AI Engineering 报告显示 multi-model 已成常态，OpenAI 仍广泛使用，同时 Anthropic 与 Gemini 增长明显。",
            "这意味着 provider abstraction 是现实工程需求，不只是代码洁癖。",
        ],
        [
            Link("Datadog State of AI Engineering 2026", "https://www.datadoghq.com/about/latest-news/press-releases/datadog-state-of-ai-engineering-report-2026/", "报告提到 multi-model 使用与 agent observability 挑战。"),
            Link("OpenAI Agents SDK config", "https://openai.github.io/openai-agents-python/config/", "SDK-wide defaults、client、tracing、logging 等配置入口。"),
        ],
        "Provider adapter 图：agent node -> provider interface -> concrete model SDK -> trace/eval。",
    ),
    Chapter(
        "12_langgraph",
        "Part 4 / 真实生产栈",
        "第 12 章：LangGraph：从教学 GraphEngine 迁移到工业框架",
        "先理解本地 graph，再判断是否需要 LangGraph 的生产能力。",
        [
            "`GraphEngine` 是为了把概念讲清楚；`langgraph_reference.py` 是迁移 mental model。",
            "LangGraph 的价值在 durable execution、interrupt、checkpointer、conditional routing、streaming、deployment、debug visibility。",
            "迁移不是为了追框架，而是当本地 engine 的复杂度开始复制这些能力时，选择成熟实现。",
        ],
        "教学时可以用纸飞机解释空气动力学；真正载客时要用经过认证的飞机。GraphEngine 是纸飞机，LangGraph 是可运营飞机，但你得先懂飞行原理。",
        [
            "jobagent/graph/engine.py",
            "jobagent/graph/langgraph_reference.py",
            "jobagent/graph/workflow.py",
        ],
        [
            "对照 GraphEngine node 与 LangGraph StateGraph node。",
            "把 HITL approval 想象成 LangGraph interrupt，写出迁移伪代码。",
            "列出迁移后哪些测试应该保持不变。",
        ],
        [
            "教学项目是否要直接使用 LangGraph？如果目标是理解底层，可以先不使用。",
            "迁移会带来什么成本？依赖、概念、部署、调试方式、checkpointer 配置。",
            "迁移最先应该保留什么？state schema、node contract、eval suite。",
        ],
        [
            "LangGraph 官方强调它不抽象 prompts 或 architecture，而是提供 long-running stateful workflow 的底层能力。",
            "这正好说明 agent infra 的核心不是模板，而是状态、持久化、恢复和观察。",
        ],
        [
            Link("LangGraph overview", "https://docs.langchain.com/oss/python/langgraph", "官方概览：durable execution、HITL、memory、debugging、deployment。"),
            Link("Thinking in LangGraph", "https://docs.langchain.com/oss/python/langgraph/thinking-in-langgraph", "帮助从业务 workflow 映射到 LangGraph 设计。"),
        ],
        "迁移映射图：GraphEngine concepts -> LangGraph concepts。",
    ),
    Chapter(
        "13_observability",
        "Part 4 / 真实生产栈",
        "第 13 章：Observability：Trace 是 Agent 系统的黑匣子",
        "Agent debug 的第一原则：不要只看最终回答，要看轨迹。",
        [
            "本项目的 `JsonlTracer` 为每个 node 记录 span，包含 step、next_node、stop_reason 等 metadata。",
            "真实 agent observability 还会记录 model generation、tool call、retrieval、guardrail、handoff、latency、token、cost、prompt version、eval score。",
            "Trace 让你回答三个问题：系统看到了什么、做了什么、为什么停在这里。",
        ],
        "飞机失事调查不能只看乘客最后一句话，要看黑匣子。Agent 系统也一样，最终输出只是结果，trace 才是过程证据。",
        [
            "jobagent/observability/tracer.py",
            "jobagent/observability/langfuse_exporter.py",
            ".jobagent/runs/<run_id>/trace.jsonl",
        ],
        [
            "跑一次 workflow，打开 trace JSONL，标出每个 span 的 node 与 next_node。",
            "给 tracer 设计 cost/token 字段，即使当前 deterministic 路径没有 token 成本。",
            "思考如何把本地 trace 映射到 Langfuse observation types。",
        ],
        [
            "日志、metric、trace 谁最重要？agent debugging 首先需要 trace，因为它保留因果路径。",
            "是否记录完整 prompt/output？开发阶段有用，生产环境要考虑 PII、secret、redaction。",
            "Trace 是否要接 OpenTelemetry？如果已有 infra observability 栈，应该考虑统一 schema。",
        ],
        [
            "2026 年 agent observability 已经成为独立工程领域。OpenTelemetry 有 GenAI semantic conventions；Langfuse 支持 traces、sessions、observations、eval scores；OpenAI Agents SDK 默认 tracing。",
            "这说明 agent trace 正在从 nice-to-have 变成 production requirement。",
        ],
        [
            Link("OpenTelemetry GenAI semantic conventions", "https://opentelemetry.io/docs/specs/semconv/gen-ai/", "GenAI spans、events、metrics 的语义规范。"),
            Link("Langfuse observability overview", "https://langfuse.com/docs/observability/overview/", "LLM application tracing、token/cost/latency、tool/retrieval steps。"),
            Link("OpenAI Agents SDK tracing", "https://openai.github.io/openai-agents-python/tracing/", "SDK 默认记录 agent、generation、tool、guardrail、handoff spans。"),
        ],
        "Trace 树图：run trace -> node span -> tool/retrieval/generation observations。",
    ),
    Chapter(
        "14_offline_eval",
        "Part 5 / Eval、安全与产品化",
        "第 14 章：Offline Eval：别靠感觉判断 Agent 有没有变好",
        "Agent 质量不能只靠肉眼体验，必须有回归样例和可重复评估。",
        [
            "本项目的 eval suite 保护两类行为：结构化抽取是否正确，workflow trajectory 是否符合预期。",
            "Eval 是 agent 系统的回归测试，不是一次性的 benchmark。每次改 prompt、模型、node、state schema，都应该跑 eval。",
            "Deterministic eval 尤其适合早期：便宜、稳定、容易定位失败。",
        ],
        "训练运动员不能只问教练「感觉怎么样」。你需要计时器、动作录像、固定测试项目。Agent eval 就是这些固定测试项目。",
        [
            "jobagent/evals/runner.py",
            "samples/eval_suite.json",
            "tests/test_eval_runner.py",
            "jobagent/cli.py",
        ],
        [
            "运行 `python3 -m jobagent.cli eval`，阅读每个 case 的检查方式。",
            "新增一个 JD extraction case，确保 company 和 role 被正确抽取。",
            "故意改坏 extractor，确认 eval 能抓住失败。",
        ],
        [
            "Eval case 应该覆盖最终输出还是中间轨迹？两者都要，早期先覆盖中间结构和 trajectory。",
            "LLM-as-judge 是否必要？语义质量需要，但 deterministic rule 更适合 schema、工具参数、policy。",
            "Eval 结果是否应该进 CI？只要稳定、低成本，就应该进。",
        ],
        [
            "AWS AgentCore Evaluations 在 2026 年 GA，支持自动质量评估、custom evaluator、与 observability 结合。",
            "Langfuse 也在 2026 年推出/强化 code evaluators，用 Python/TypeScript 做确定性检查，补充 LLM-as-judge。",
        ],
        [
            Link("AWS AgentCore Evaluations GA", "https://aws.amazon.com/about-aws/whats-new/2026/03/agentcore-evaluations-generally-available/", "AgentCore Evaluations 支持 LLM-based 与 code-based evaluator。"),
            Link("Langfuse code evaluators", "https://langfuse.com/changelog/2026-05-28-code-evaluators", "Langfuse 支持 deterministic Python/TypeScript checks。"),
            Link("Langfuse LLM-as-a-Judge", "https://langfuse.com/docs/scores/evals", "LLM-as-judge 执行也会产生 trace，便于调试 evaluator。"),
        ],
        "Eval 金字塔：unit tests -> trajectory eval -> semantic eval -> production monitoring。",
    ),
    Chapter(
        "15_guardrails",
        "Part 5 / Eval、安全与产品化",
        "第 15 章：Guardrails：在 Agency 之前先做安全边界",
        "Guardrails 不是让模型更听话，而是让系统先拒绝不该处理的输入和动作。",
        [
            "本项目在 public submission 进入 workflow 前做 secret 与 prompt-injection guardrail。",
            "这体现一个重要原则：高风险输入不要等 agent 自己判断，应该在系统边界先筛掉。",
            "Guardrail 还包括 body size、rate limit、run id validation、content type、security headers、public demo mode 限制。",
        ],
        "开店不能等顾客走到收银台才检查是不是带了危险品。门口安检、货架权限、收银复核、监控录像都是不同层级的 guardrail。",
        [
            "jobagent/security/input_guardrails.py",
            "jobagent/web/app.py",
            "tests/test_input_guardrails.py",
            "tests/test_web_app.py",
        ],
        [
            "提交包含 prompt injection 的 JD，看系统是否拒绝。",
            "提交疑似 credential 的文本，看 finding 如何表达。",
            "列出 web app 中所有 public-surface safety controls。",
        ],
        [
            "Guardrail 应该 blocking 还是 warning？secret、credential、unsafe action 应该 blocking；低质量输入可 warning。",
            "模型级 guardrail 是否足够？不够，工具调用、外部写入、MCP server 都需要系统级 guardrail。",
            "误杀怎么办？需要 finding reason、用户可理解提示、可审计 override 策略。",
        ],
        [
            "2026 年 agent 安全风险明显上升，特别是 MCP/tool servers、computer use、browser use、payments、autonomous writes。",
            "OpenAI Agents SDK 与 AWS AgentCore 都把 guardrails/policy controls 放在生产能力里，而不是事后补丁。",
        ],
        [
            Link("OpenAI Agents SDK guardrails", "https://openai.github.io/openai-agents-js/guides/guardrails", "输入、输出和工具 guardrails 的行为差异。"),
            Link("AWS AgentCore policy controls", "https://aws.amazon.com/blogs/aws/amazon-bedrock-agentcore-adds-quality-evaluations-and-policy-controls-for-deploying-trusted-ai-agents/", "AgentCore 将 policy controls、evaluations、observability 组合成 trusted agents 路径。"),
        ],
        "安全洋葱图：request limits -> input guardrails -> tool policy -> HITL -> audit trace。",
    ),
    Chapter(
        "16_web_product",
        "Part 5 / Eval、安全与产品化",
        "第 16 章：Web Product Surface：把 Workflow 变成可以用的产品",
        "Agent product 的 UI 不是装饰，它负责让用户看见状态、风险和下一步。",
        [
            "JobAgent 的 web surface 把 workflow 变成一个可操作 cockpit：提交 JD、查看 run、审批 proposal、继续流程、查看结果。",
            "Agent UI 最重要的是状态可见：现在在哪个 node、为什么暂停、需要用户做什么、输出是否最终生效。",
            "这也是 portfolio 价值所在：不仅有后端 workflow，还有用户能理解的产品表面。",
        ],
        "一个好机场不是只让飞机飞，它还要让乘客知道登机口、延误原因、安检状态和下一步动作。Agent UI 也是信息机场。",
        [
            "jobagent/web/app.py",
            "jobagent/web/templates/index.html",
            "jobagent/web/templates/run.html",
            "jobagent/web/static/app.css",
            "docs/assets/readme/demo-home.png",
            "docs/assets/readme/demo-review.png",
            "docs/assets/readme/demo-complete.png",
        ],
        [
            "启动 `uvicorn jobagent.web.app:app --reload`，从 UI 完成一次完整 run。",
            "观察 pending approval 页面展示了哪些信息，哪些信息还可以更清楚。",
            "设计一个 workflow strip 的状态枚举：waiting/running/pending/done/error。",
        ],
        [
            "Agent UI 应该像聊天框还是 cockpit？本项目更适合 cockpit，因为 workflow 状态比对话本身更重要。",
            "是否展示中间结果？应展示对用户决策有帮助的中间结果，同时避免信息过载。",
            "错误提示应该技术化还是用户化？UI 用户化，trace/log 技术化。",
        ],
        [
            "很多 agent demo 的弱点是 product surface 不透明：用户不知道 agent 做到哪、卡在哪里、有没有真的完成。",
            "Langfuse Academy 对 tracing 的解释也强调：agent 执行顺序可能 messy，必须用 trace 与状态让行为可理解。",
        ],
        [
            Link("Langfuse tracing academy", "https://langfuse.com/academy/tracing/", "从传统 observability 过渡到 LLM/agent tracing 的教学材料。"),
            Link("Langfuse core concepts", "https://langfuse.com/docs/tracing-data-model", "解释 traces、sessions、observations 的数据模型。"),
        ],
        "Cockpit UI 图：status cards / workflow strip / approval panel / outputs。",
    ),
    Chapter(
        "17_deployment",
        "Part 5 / Eval、安全与产品化",
        "第 17 章：Deployment：从本地 demo 到公开 portfolio",
        "部署 agent product，不只是把 API 跑起来，还要说明状态、成本和安全边界。",
        [
            "本项目提供 Dockerfile、docker-compose、Render Blueprint、health/readiness/ops endpoints。",
            "Hosted demo 默认不用 managed Postgres，因此 run state 在 free web instance 内可能 ephemeral。这不是失败，而是清楚标注 demo 边界。",
            "更接近 production 的路径是：durable Postgres state、queue-backed worker、auth、edge rate limit、budget tracking、observability backend。",
        ],
        "临时展台可以用折叠桌，但你要告诉观众它不是永久门店。Portfolio deployment 也一样：能用、好看、边界诚实，比假装 enterprise SaaS 更可信。",
        [
            "Dockerfile",
            "docker-compose.yml",
            "render.yaml",
            "deploy/langfuse/README.md",
            "jobagent/web/app.py",
        ],
        [
            "运行 web app 后访问 `/healthz`、`/readyz`、`/ops/status`。",
            "阅读 `render.yaml`，指出 health check 和 public demo mode。",
            "设计 production hardening checklist。",
        ],
        [
            "什么时候需要 queue？当 workflow 长、外部 API 慢、并发高或需要 retry/backoff。",
            "什么时候需要 Postgres？当 checkpoint/run state 不能丢，或者多 instance 需要共享状态。",
            "什么时候需要 auth？任何个人数据、真实申请、外部写入、团队使用场景。",
        ],
        [
            "AWS AgentCore 的定位反映了行业变化：agent deployment 需要 runtime、memory、identity、observability、evaluation、policy，不只是 serverless endpoint。",
            "这给 JobAgent 的升级路线提供了很好的工业参照。",
        ],
        [
            Link("AWS AgentCore release notes", "https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/release-notes.html", "AgentCore runtime、memory、observability、MCP server、framework support 的持续更新。"),
            Link("AWS AgentCore Observability", "https://aws.amazon.com/blogs/machine-learning/build-trustworthy-ai-agents-with-amazon-bedrock-agentcore-observability/", "用 CloudWatch/GenAI observability trace 和 debug agents。"),
        ],
        "部署层级图：local CLI -> local web -> Docker -> Render -> durable production stack。",
    ),
    Chapter(
        "18_10x_scale_readiness",
        "Part 5 / Eval、安全与产品化",
        "第 18 章：10x Scale 与 Production Readiness：什么时候可以说它准备好了",
        "Production readiness 不是一句自信判断，而是一组关于流量、状态、恢复、安全和验证的证据。",
        [
            "JobAgent 现在可以诚实地称为 production-shaped：它有 FastAPI surface、Docker/Render 部署、typed state、HITL、checkpoint/resume、trace/audit、guardrails、ops endpoints 和 offline eval。但它还不应该被包装成 fully production-ready SaaS。",
            "10x scale 先考验的不是 agent prompt，而是执行层：`POST /runs` 目前同步跑完整 workflow；默认 local checkpoint 在 Render free instance 上是 ephemeral；in-memory rate limit 不能跨进程共享；Postgres path 存在，但还缺 connection pooling、migration/versioning、idempotent approval 和 background worker。",
            "这一章故意先不实现这些升级，而是把生产判断记录成可复述、可验证、可逐步落地的 checklist。对 portfolio 和面试来说，这种边界意识本身就是很重要的工程经历。",
        ],
        "一次小型展览可以靠一个工作人员现场登记、现场带路、现场收票。但如果人流变成十倍，你不会先训练他说话更漂亮，而是会先加排队系统、票据数据库、入口闸机、监控面板和应急流程。Agent product 的 10x scale 也是同一个逻辑。",
        [
            "jobagent/web/app.py",
            "jobagent/web/store.py",
            "jobagent/graph/workflow.py",
            "jobagent/storage/checkpoint.py",
            "samples/eval_suite.json",
            "render.yaml",
            "README.zh.md",
        ],
        [
            "阅读 `create_run()`，说明为什么同步 workflow 在 10x traffic 下会成为 request latency 与 timeout 风险。",
            "对比 `LocalRunStore` 与 `PostgresRunStore`，写出哪些 state 可以丢、哪些 state 一旦丢就破坏用户信任。",
            "把 `/ops/status`、`/ops/evals`、`python3 -m jobagent.cli eval`、`python3 -m unittest discover -s tests` 组合成一个 release/readiness checklist。",
            "写一个不实现代码的 migration note：从 public demo 到 production SaaS，需要先引入 queue、durable Postgres、auth、distributed rate limit 和 observability backend。",
        ],
        [
            "10x 是什么？如果是 portfolio/demo traffic，当前形态大概率 okay；如果是真用户 SaaS traffic，需要先升级执行、状态和运维层。",
            "什么时候必须引入 queue？当 run 时间不可控、外部 API 变慢、需要 retry/backoff、并发用户会阻塞 web workers，或 run 必须脱离 request 生命周期继续完成。",
            "什么时候必须引入 durable store？当用户期望历史 run、approval、trace、tracker update 可恢复，或服务部署为多实例时。",
            "什么时候可以说 production-ready？只有当 load、restart-resume、approval race、storage failure、guardrail bypass、eval regression 和 observability smoke 都有证据时。",
        ],
        [
            "行业里的 agent platform 越来越把 runtime、durable execution、identity、policy、observability 和 eval 放在一起卖，原因很简单：agent 质量问题最后常常表现为系统可靠性问题。",
            "这一章对应的能力不是某个新框架，而是 FDE/AI infra 面试里很有价值的判断力：能区分 demo-ready、production-shaped、production-ready，并能说清下一步工程升级顺序。",
        ],
        [
            Link("LangGraph durable execution", "https://docs.langchain.com/oss/python/langgraph/durable-execution", "理解 long-running workflow、checkpoint、determinism 和 side-effect idempotency。"),
            Link("OpenTelemetry GenAI conventions", "https://opentelemetry.io/docs/specs/semconv/gen-ai/", "生产观测需要稳定 schema，不能只靠本地日志。"),
            Link("AWS AgentCore release notes", "https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/release-notes.html", "托管 agent runtime 对 memory、identity、observability、evaluation、policy 的平台化参照。"),
        ],
        "Readiness 分层图：demo traffic -> public portfolio -> durable beta -> production SaaS；每层标出 state、queue、auth、rate limit、observability、eval 证据。",
    ),
    Chapter(
        "19_debugging",
        "Part 6 / Capstone",
        "第 19 章：调试一本 Agent 系统：从现象回到 state、trace、node",
        "Agent debug 不应该从改 prompt 开始，而应该从证据链开始。",
        [
            "一个系统输出奇怪结果时，先判断问题发生在输入、guardrail、state、node、tool、checkpoint、trace、UI 还是 eval 覆盖。",
            "本项目适合建立一套可复用 debug playbook：CLI 复现、检查 checkpoint、阅读 trace、定位 node contract、补 eval case、再改实现。",
            "这会训练真正的 agent engineering 手感：少猜，多看证据。",
        ],
        "医生不会一上来就开药。他会问症状、量体温、看化验单、查病史。Agent debug 也一样，prompt 只是最后可能调整的治疗方案之一。",
        [
            "jobagent/graph/engine.py",
            "jobagent/observability/tracer.py",
            "jobagent/storage/checkpoint.py",
            "tests/",
            ".jobagent/runs/",
            ".jobagent/checkpoints/",
        ],
        [
            "制造一次 resume 失败，按 playbook 定位是 checkpoint 缺失还是 pending_node 问题。",
            "制造一次 extraction 错误，先补 eval case，再修 extractor。",
            "制造一次 UI 显示错误，确认 state 与 trace 是否正确，避免误修后端。",
        ],
        [
            "什么时候改 prompt？当 state、tool、retrieval、schema、guardrail 都证明没有问题，而语义质量仍不足。",
            "Debug 输出应该保留多久？本地学习可保留，生产要考虑 PII、retention、redaction。",
            "失败是否要自动恢复？只有可幂等、低风险、可观察的失败才适合自动恢复。",
        ],
        [
            "行业正在用 trace/span/eval 把 agent debugging 从手工猜测变成可观测流程。OpenAI Agents SDK 默认 tracing，Langfuse 将 trace 连接到 dataset、eval、dashboard。",
            "这和本章 playbook 完全一致：先拿轨迹，再谈优化。",
        ],
        [
            Link("OpenAI Agents SDK tracing", "https://openai.github.io/openai-agents-python/tracing/", "默认 trace agent run、generation、tool、guardrail、handoff。"),
            Link("Langfuse core concepts", "https://langfuse.com/docs/tracing-data-model", "解释 traces、sessions、observations 如何组织 agent 行为证据。"),
        ],
        "Debug 决策树：symptom -> reproduce -> state -> trace -> node -> eval -> fix。",
    ),
    Chapter(
        "20_upgrade_choices",
        "Part 6 / Capstone",
        "第 20 章：工程选择题：什么时候该升级技术栈",
        "成熟的 AI infra 判断力，不是知道所有工具，而是知道什么时候不用它们。",
        [
            "本章把升级选项做成 decision matrix：LangGraph、真实 LLM、MCP、Postgres、pgvector、Langfuse、OpenTelemetry、queue、auth、cloud runtime。",
            "每个升级都按同一结构分析：当前痛点、升级收益、新复杂度、JobAgent 落点、验证方式。",
            "这样读者学到的是工程取舍，而不是技术名词收藏。",
        ],
        "工具箱越大，越需要知道什么时候只用螺丝刀。把每个问题都用最大机器解决，最后会把小项目压垮。",
        [
            "pyproject.toml",
            "docker-compose.yml",
            "jobagent/graph/langgraph_reference.py",
            "jobagent/observability/langfuse_exporter.py",
            "jobagent/storage/postgres_memory.py",
            "mcp_server/",
        ],
        [
            "为每个 optional dependency 写出 adoption trigger。",
            "选择一个升级项，写出最小迁移 PR 的范围。",
            "为升级前后定义一条必须保持通过的 eval。",
        ],
        [
            "LangGraph：当 workflow 复杂到本地 engine 开始复制 durable execution/interrupt 时引入。",
            "Langfuse/OpenTelemetry：当 trace 不再只给开发者看，而要做质量、成本、latency、生产监控时引入。",
            "MCP：当工具需要跨客户端复用，或外部生态集成比内部 adapter 更重要时引入。",
            "Postgres/pgvector：当 state/memory 需要持久、并发、查询、语义检索时引入。",
        ],
        [
            "2026 的 agent stack 趋势是组合式：runtime、protocol、observability、eval、deployment、identity 分别由不同工具覆盖。",
            "未来的 AI infra 工程师要能在 OpenAI Agents SDK、LangGraph、MCP、Langfuse、OpenTelemetry、AWS AgentCore、Google A2A 等之间做边界判断。",
        ],
        [
            Link("OpenAI Agents SDK", "https://openai.github.io/openai-agents-python/", "OpenAI 的 agent runtime SDK 文档入口。"),
            Link("OpenTelemetry GenAI conventions", "https://opentelemetry.io/docs/specs/semconv/gen-ai/", "跨平台观测 schema 的关键参考。"),
            Link("AWS AgentCore release notes", "https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/release-notes.html", "托管 agent platform 的工业参照。"),
        ],
        "技术升级决策矩阵：pain -> trigger -> tool -> complexity -> verification。",
    ),
    Chapter(
        "21_capstone",
        "Part 6 / Capstone",
        "第 21 章：最终项目任务：把 JobAgent 改成你的 AI Infra Portfolio",
        "最后一章不是阅读，而是让读者完整交付一个新的 bounded agent。",
        [
            "Capstone 任务：新增一个 agent，例如 `salary_analysis`、`networking_strategy` 或 `company_risk_analysis`。",
            "要求完整接入 state、workflow、checkpoint/resume、eval、trace、web UI，并写出 portfolio narrative。",
            "目标是证明读者掌握 agentic infra 的完整闭环，而不是只会加一个函数。",
        ],
        "毕业设计不是背诵机场规则，而是让你真正新增一个服务窗口：写清职责、接入调度、留下记录、接受检查、让乘客看得懂。",
        [
            "jobagent/models.py",
            "jobagent/agents/",
            "jobagent/graph/workflow.py",
            "jobagent/evals/runner.py",
            "samples/eval_suite.json",
            "jobagent/web/templates/run.html",
            "tests/",
        ],
        [
            "新增 typed artifact，例如 `SalaryAnalysis`。",
            "新增 agent node，并接入 graph。",
            "新增 eval case，覆盖 trajectory 与关键输出。",
            "更新 web UI，让用户能看到新 agent 结果。",
            "写一段 README/portfolio 叙事：你如何设计 bounded multi-agent workflow。",
        ],
        [
            "新 agent 放在哪个位置？取决于它依赖 JD、company brief、fit score 还是 resume proposal。",
            "是否需要 HITL？如果输出会影响真实申请或外部写入，需要。",
            "是否需要真实 LLM？先 deterministic baseline，再用 provider adapter 替换。",
        ],
        [
            "Langfuse 在 2026 年公开了 evaluate AI agent skills 的实践：把 prompts 做成 dataset，运行 agent，trace 行为，再迭代 skill。",
            "这给 Capstone 一个更高阶方向：不仅评估业务输出，也评估 agent 是否遵守工程 playbook。",
        ],
        [
            Link("Langfuse evaluating AI agent skills", "https://langfuse.com/blog/2026-02-26-evaluate-ai-agent-skills", "展示如何用 dataset、trace、experiment 评估 agent skill。"),
            Link("AWS AgentCore Evaluations GA", "https://aws.amazon.com/about-aws/whats-new/2026/03/agentcore-evaluations-generally-available/", "生产 agent eval 的托管平台参照。"),
        ],
        "Capstone 交付图：new artifact -> node -> graph -> eval -> trace -> UI -> portfolio story。",
    ),
]


CSS = """
:root {
  --bg: #f6f7f8;
  --paper: #ffffff;
  --ink: #1f2328;
  --muted: #5f6b76;
  --line: #d8dee4;
  --blue: #2457c5;
  --teal: #0f766e;
  --green: #15803d;
  --amber: #b45309;
  --code: #f1f5f9;
  --dark: #111827;
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  background: var(--bg);
  color: var(--ink);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
  font-size: 16px;
  line-height: 1.72;
}
a { color: var(--blue); text-decoration: none; }
a:hover { text-decoration: underline; }
.wrap { width: min(1160px, calc(100% - 32px)); margin: 0 auto; }
header { background: var(--paper); border-bottom: 1px solid var(--line); }
.hero { padding: 38px 0 28px; display: grid; gap: 14px; }
.eyebrow { color: var(--teal); font-size: 12px; font-weight: 800; letter-spacing: .08em; text-transform: uppercase; }
h1, h2, h3 { margin: 0; line-height: 1.18; letter-spacing: 0; }
h1 { max-width: 960px; font-size: clamp(32px, 5vw, 54px); }
h2 { margin-top: 34px; font-size: 26px; }
h3 { margin-top: 22px; font-size: 19px; }
p { margin: 10px 0 0; }
ul, ol { margin: 10px 0 0; padding-left: 22px; }
li { margin: 6px 0; }
code {
  background: var(--code);
  border: 1px solid #e2e8f0;
  border-radius: 5px;
  padding: 1px 5px;
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: .92em;
}
.lead { max-width: 920px; color: var(--muted); font-size: 18px; }
.meta { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 6px; }
.badge {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  border: 1px solid currentColor;
  border-radius: 999px;
  padding: 3px 10px;
  font-size: 13px;
  font-weight: 700;
}
.badge.green { color: var(--green); }
.badge.blue { color: var(--blue); }
.badge.amber { color: var(--amber); }
nav {
  position: sticky;
  top: 0;
  z-index: 10;
  background: rgba(255,255,255,.94);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--line);
}
.toc { display: flex; gap: 8px; overflow-x: auto; padding: 12px 0; }
.toc a {
  flex: 0 0 auto;
  color: var(--ink);
  background: #f8fafc;
  border: 1px solid var(--line);
  border-radius: 999px;
  padding: 6px 11px;
  font-size: 14px;
}
main { padding: 18px 0 56px; }
section { border-bottom: 1px solid var(--line); padding: 0 0 32px; }
.grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; margin-top: 16px; }
.grid.two { grid-template-columns: repeat(2, minmax(0, 1fr)); }
.card {
  background: var(--paper);
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 16px;
}
.card strong { display: block; margin-bottom: 5px; color: #111827; }
.callout {
  margin-top: 16px;
  border-left: 4px solid var(--teal);
  border-radius: 0 8px 8px 0;
  background: #ecfeff;
  padding: 14px 16px;
}
.callout.warning { border-left-color: var(--amber); background: #fffbeb; }
.chapter-nav { display: flex; justify-content: space-between; gap: 12px; margin: 24px 0 0; }
.chapter-nav a {
  background: var(--paper);
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 10px 12px;
  max-width: 48%;
}
.source-list li { margin-bottom: 8px; }
.visual {
  background: #f8fafc;
  border: 1px dashed #b8c2cc;
  border-radius: 8px;
  padding: 14px 16px;
  color: #334155;
}
.chapter-list { columns: 2; column-gap: 28px; }
.chapter-list li { break-inside: avoid; }
footer { color: var(--muted); padding: 28px 0 42px; font-size: 14px; }
@media (max-width: 860px) {
  .grid, .grid.two { grid-template-columns: 1fr; }
  .chapter-list { columns: 1; }
  .chapter-nav { display: block; }
  .chapter-nav a { display: block; max-width: none; margin-top: 10px; }
}
"""


def link_for(chapter: Chapter) -> str:
    return f"{chapter.slug}.html"


def render_list(items: list[str]) -> str:
    return "<ul>" + "".join(f"<li>{escape(item)}</li>" for item in items) + "</ul>"


def render_anchors(items: list[str]) -> str:
    links = []
    for item in items:
        target = REPO_ROOT / item
        if target.exists():
            href = "../../" + item
            links.append(f'<li><a href="{escape(href)}">{escape(item)}</a></li>')
        else:
            links.append(f"<li><code>{escape(item)}</code></li>")
    return "<ul>" + "".join(links) + "</ul>"


def render_sources(links: list[Link]) -> str:
    return (
        '<ul class="source-list">'
        + "".join(
            f'<li><a href="{escape(link.url)}">{escape(link.label)}</a><br><span>{escape(link.note)}</span></li>'
            for link in links
        )
        + "</ul>"
    )


def render_chapter_body(chapter: Chapter, *, standalone: bool) -> str:
    return f"""
<section id="{escape(chapter.slug)}">
  <div class="eyebrow">{escape(chapter.part)}</div>
  <h2>{escape(chapter.title)}</h2>
  <p class="lead">{escape(chapter.subtitle)}</p>

  <div class="grid">
    <div class="card">
      <strong>概念解释</strong>
      {render_list(chapter.concept)}
    </div>
    <div class="card">
      <strong>寓言 / 类比</strong>
      <p>{escape(chapter.allegory)}</p>
    </div>
    <div class="card">
      <strong>建议配图</strong>
      <p class="visual">{escape(chapter.visual)}</p>
    </div>
  </div>

  <div class="grid two">
    <div class="card">
      <strong>项目代码落点</strong>
      {render_anchors(chapter.anchors)}
    </div>
    <div class="card">
      <strong>运行 / 调试练习</strong>
      {render_list(chapter.labs)}
    </div>
  </div>

  <div class="grid two">
    <div class="card">
      <strong>工程选择题</strong>
      {render_list(chapter.choices)}
    </div>
    <div class="card">
      <strong>Industry Pulse / 行业脉搏</strong>
      {render_list(chapter.industry)}
      <h3>扩展阅读</h3>
      {render_sources(chapter.links)}
    </div>
  </div>
</section>
"""


def html_shell(title: str, subtitle: str, body: str, nav: str = "") -> str:
    nav_block = f"  {nav}\n" if nav else ""
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <style>{CSS}</style>
</head>
<body>
  <header>
    <div class="wrap hero">
      <div class="eyebrow">JobAgent Multi-Agent Course / Updated {UPDATED}</div>
      <h1>{escape(title)}</h1>
      <p class="lead">{escape(subtitle)}</p>
      <div class="meta">
        <span class="badge green">项目驱动</span>
        <span class="badge blue">每章单页</span>
        <span class="badge amber">含 2026 行业扩展</span>
      </div>
    </div>
  </header>
{nav_block}  <main class="wrap">
{body}
  </main>
  <footer class="wrap">
    Generated from <code>docs/agentic_course/build_agentic_course.py</code>. Industry links were refreshed on {UPDATED}; fast-moving AI infra references should be reviewed periodically.
  </footer>
</body>
</html>
"""


def render_index() -> str:
    grouped: dict[str, list[Chapter]] = {}
    for chapter in CHAPTERS:
        grouped.setdefault(chapter.part, []).append(chapter)
    chapter_count = len(CHAPTERS)
    blocks = [
        f"""
<section>
  <h2>怎么使用这套教程</h2>
  <div class="grid">
    <div class="card"><strong>读法</strong><p>先按章节顺序跑一遍，之后把每章当作一个工程 checklist。</p></div>
    <div class="card"><strong>重点</strong><p>每章都连接概念、代码、调试练习和行业扩展，避免只停留在架构图。</p></div>
    <div class="card"><strong>产物</strong><p>本目录包含 {chapter_count} 个单章 HTML 和一个总合集 mega HTML。</p></div>
  </div>
  <div class="callout warning">
    <strong>阅读体验 prototype：</strong>
    如果想看更像“工程实验手册”的新版观感，打开
    <a href="../agentic_course_prototype/index.html">docs/agentic_course_prototype/index.html</a>。
    当前 prototype 先做了第 1 章 GraphEngine 和第 2 章 Shared State。
  </div>
</section>
"""
    ]
    for part, chapters in grouped.items():
        items = "".join(
            f'<li><a href="{escape(link_for(ch))}">{escape(ch.title)}</a><br><span>{escape(ch.subtitle)}</span></li>'
            for ch in chapters
        )
        blocks.append(f"<section><h2>{escape(part)}</h2><ol class=\"chapter-list\">{items}</ol></section>")
    blocks.append(
        '<section><h2>总合集</h2><p><a href="mega_agentic_course_zh.html">打开 mega HTML：完整合并版教程</a></p></section>'
    )
    return html_shell(
        "JobAgent Multi-Agent 工程教程目录",
        "面向传统 software infrastructure 背景读者的项目驱动教程：从本地 graph 到 HITL、checkpoint、MCP、observability、eval 与部署。",
        "\n".join(blocks),
    )


def render_mega() -> str:
    chapter_count = len(CHAPTERS)
    nav = (
        '<nav aria-label="Table of contents"><div class="wrap toc">'
        + "".join(f'<a href="#{escape(ch.slug)}">{escape(ch.slug.split("_", 1)[0])}. {escape(ch.title.split("：", 1)[-1])}</a>' for ch in CHAPTERS)
        + "</div></nav>"
    )
    intro = f"""
<section>
  <h2>总览</h2>
  <p>这份 mega HTML 把 {chapter_count} 个单章教程合并在一起，适合连续阅读、分享或打印。每章仍然保留概念解释、寓言类比、项目代码落点、调试练习、工程选择题和行业扩展阅读。</p>
  <div class="callout">建议先用 <a href="index.html">目录入口</a> 按章节阅读；需要整体浏览时再打开本页。</div>
</section>
"""
    body = intro + "\n".join(render_chapter_body(ch, standalone=False) for ch in CHAPTERS)
    return html_shell(
        "JobAgent Multi-Agent 工程教程：Mega 合集",
        "从传统 infra 到 agentic infra 的完整学习路径，围绕当前 JobAgent 代码与 2026 AI 工业动态展开。",
        body,
        nav,
    )


def render_single(chapter: Chapter, idx: int) -> str:
    prev_ch = CHAPTERS[idx - 1] if idx > 0 else None
    next_ch = CHAPTERS[idx + 1] if idx + 1 < len(CHAPTERS) else None
    chapter_nav = '<div class="chapter-nav">'
    if prev_ch:
        chapter_nav += f'<a href="{escape(link_for(prev_ch))}">上一章：{escape(prev_ch.title)}</a>'
    else:
        chapter_nav += '<a href="index.html">返回目录</a>'
    if next_ch:
        chapter_nav += f'<a href="{escape(link_for(next_ch))}">下一章：{escape(next_ch.title)}</a>'
    else:
        chapter_nav += '<a href="mega_agentic_course_zh.html">打开 Mega 合集</a>'
    chapter_nav += "</div>"
    body = render_chapter_body(chapter, standalone=True) + chapter_nav
    nav = (
        '<nav aria-label="Chapter navigation"><div class="wrap toc">'
        '<a href="index.html">目录</a>'
        '<a href="mega_agentic_course_zh.html">Mega 合集</a>'
        f'<a href="#{escape(chapter.slug)}">本章</a>'
        "</div></nav>"
    )
    return html_shell(chapter.title, chapter.subtitle, body, nav)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "index.html").write_text(render_index(), encoding="utf-8")
    (OUT_DIR / "mega_agentic_course_zh.html").write_text(render_mega(), encoding="utf-8")
    for idx, chapter in enumerate(CHAPTERS):
        (OUT_DIR / link_for(chapter)).write_text(render_single(chapter, idx), encoding="utf-8")


if __name__ == "__main__":
    main()
