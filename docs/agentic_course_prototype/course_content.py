from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


OUT_DIR = Path(__file__).resolve().parent
REPO_ROOT = OUT_DIR.parents[1]
UPDATED = "2026-06-10"


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




DEEP_DIVES: dict[str, str] = {
    "09_local_rag": """
  <div class="deep-dive">
    <h3>这章真正解决的问题</h3>
    <p>第 9 章不是为了证明“用了 RAG”，而是为了让你看清楚 retrieval 在 agent workflow 里的工程位置：它决定哪些材料可以进入 downstream agent 的上下文，并且把这个决定变成可检查、可回归、可展示的证据。</p>
    <div class="system-map">
      <div class="map-row"><strong>Input</strong><span><code>samples/story_bank.json</code> 里的项目经历会先被转换为 <code>SourceDocument</code>。这一步给每条资料补上 <code>source_id</code>、<code>source_type</code>、<code>captured_at</code>、<code>expires_at</code>、<code>refresh_policy</code> 等治理字段。</span></div>
      <div class="map-row"><strong>Chunk</strong><span><code>chunk_documents()</code> 调用 <code>chunk_text()</code>，把文档切成 <code>RetrievedChunk</code>。当前 story bank 很短，所以通常每条 story 只有一个 chunk，但接口已经能支持长文档。</span></div>
      <div class="map-row"><strong>Rank</strong><span><code>rank_chunks()</code> 用 deterministic keyword score 排序；<code>hybrid_rank_chunks()</code> 预留 keyword + semantic score 的升级接口，后续可以接 pgvector 或 reranker。</span></div>
      <div class="map-row"><strong>Context</strong><span><code>retrieve_context()</code> 产出 <code>RetrievalContext</code>，其中包含 query、query_terms、candidate_count、returned_count、selected_chunks、citations、freshness_warnings。</span></div>
      <div class="map-row"><strong>Workflow</strong><span><code>fit_analysis</code>、<code>resume_tailor</code>、<code>interview_prep</code> 都会把 context 写入 <code>JobSearchState.retrieval_contexts</code>，所以 checkpoint、CLI summary、web run detail 都能看到证据链。</span></div>
      <div class="map-row"><strong>Eval</strong><span><code>jobagent/retrieval/eval_runner.py</code> 先测 retrieval hit quality：expected chunk 是否命中、prohibited chunk 是否误召回、stale source 是否被挡住。</span></div>
    </div>

    <h3>代码解读：每个文件负责什么</h3>
    <div class="code-map">
      <div class="code-item"><h4><code>jobagent/models.py</code></h4><p>定义 RAG 的 typed contract。<code>SourceDocument</code> 是原始资料，<code>RetrievedChunk</code> 是可进入上下文的片段，<code>RetrievalCitation</code> 是 UI/报告可展示的出处，<code>RetrievalContext</code> 是一次检索的完整证据包。重点看这些 dataclass 的字段，而不是只看算法。</p></div>
      <div class="code-item"><h4><code>jobagent/retrieval/local_rag.py</code></h4><p>实现本地 retrieval pipeline：切块、关键词排序、freshness 判断、context assembly、hybrid ranking。这里是以后替换成 embedding、pgvector、reranker 的边界。</p></div>
      <div class="code-item"><h4><code>jobagent/memory/story_bank.py</code></h4><p>把用户项目经历从普通 JSON dict 转成 <code>SourceDocument</code>。它保留 <code>match_stories()</code> 这个旧 API，同时内部开始复用 retrieval context，避免 workflow 和旧测试断裂。</p></div>
      <div class="code-item"><h4><code>jobagent/agents/fit_analysis.py</code></h4><p>用 retrieved story evidence 支撑 fit score。它会把 top source 和命中 chunk 数写进 evidence；如果 source stale，会进入 concerns。</p></div>
      <div class="code-item"><h4><code>jobagent/agents/resume_tailor.py</code></h4><p>用 retrieved stories 生成 bullet rewrite。这里体现一个重要原则：RAG 不是只服务问答，也可以服务结构化产品动作，比如简历定位。</p></div>
      <div class="code-item"><h4><code>jobagent/agents/interview_prep.py</code></h4><p>复用同一份 retrieval context 思路，为面试故事匹配提供证据。它验证了 context layer 可以被多个 bounded agent 共享。</p></div>
      <div class="code-item"><h4><code>jobagent/retrieval/eval_runner.py</code></h4><p>实现 retrieval-first eval。它不评价最终文案好不好，而是先回答：该找的 chunk 找到了吗？不该出现的 chunk 有没有出现？过期资料有没有污染上下文？</p></div>
      <div class="code-item"><h4><code>jobagent/web/templates/run.html</code></h4><p>把 retrieval context 展示到产品页面。你可以在 run detail 看到 query、retriever、score、freshness、top chunk text。这是从“黑盒 agent”走向“可检查 agent”的关键。</p></div>
    </div>

    <h3>动手实验：按顺序执行</h3>
    <div class="lab-steps">
      <div class="lab-step"><h4>实验 1：跑 retrieval eval baseline</h4><p>目标：确认当前 story bank 的 retrieval hit quality。</p><pre><code>cd "/Users/xuantongyan/Documents/jobAgent 2"
.venv/bin/python -m jobagent.cli retrieval-eval</code></pre><p>看输出里的 <code>pass_rate</code>、<code>average_recall_at_k</code>、<code>average_precision_at_k</code>、<code>average_mrr</code>。当前重点不是 precision 必须 1.0，而是 expected chunk 在 top-k 内稳定命中。</p></div>
      <div class="lab-step"><h4>实验 2：查看 retrieval eval case 怎么写</h4><p>目标：理解一个 retrieval case 的组成。</p><pre><code>sed -n '1,220p' samples/retrieval_eval_suite.json</code></pre><p>重点看 <code>query</code>、<code>query_terms</code>、<code>expected_chunk_ids</code>、<code>k</code>、<code>require_fresh</code>。这些字段让 retrieval eval 不依赖模型输出，因此很适合早期 CI。</p></div>
      <div class="lab-step"><h4>实验 3：制造一个 stale source 失败</h4><p>目标：确认 freshness policy 真的能挡住过期材料。这个实验只写 <code>/tmp</code>，不会改 repo 文件。</p><pre><code>.venv/bin/python - &lt;&lt;'PY'
import json
from pathlib import Path
stories = json.loads(Path("samples/story_bank.json").read_text())
stories[0]["expires_at"] = "2024-01-01T00:00:00+00:00"
stories[0]["refresh_policy"] = "quarterly"
Path("/tmp/jobagent_story_bank_stale.json").write_text(json.dumps(stories), encoding="utf-8")
PY
.venv/bin/python -m jobagent.cli retrieval-eval --story-bank /tmp/jobagent_story_bank_stale.json || true</code></pre><p>预期你会看到 <code>stale_source_returned</code> 或 freshness warning。这里的学习点是：RAG 的质量不只是相关性，还包括时效性。</p></div>
      <div class="lab-step"><h4>实验 4：跑一次 workflow，再查看 checkpoint 里的 context</h4><p>目标：确认 retrieval context 真的进入 workflow state。</p><pre><code>.venv/bin/python -m jobagent.cli demo --auto-approve
.venv/bin/python - &lt;&lt;'PY'
import json
from pathlib import Path
latest = max(Path(".jobagent/checkpoints").glob("*.json"), key=lambda p: p.stat().st_mtime)
data = json.loads(latest.read_text())
print(latest)
for context in data["retrieval_contexts"]:
    print("\\nQUERY:", context["query"])
    print("CHUNKS:", context["returned_count"], "/", context["candidate_count"])
    print("TOP:", context["citations"][0]["title"] if context["citations"] else "none")
PY</code></pre><p>这一步会让你看到 RAG 不只是 eval runner 的孤立功能，而是 workflow state 的一部分。</p></div>
      <div class="lab-step"><h4>实验 5：从产品 UI 观察 RAG evidence</h4><p>目标：把代码里的 context 和用户可见产品联系起来。</p><pre><code>.venv/bin/uvicorn jobagent.web.app:app --host 127.0.0.1 --port 8000</code></pre><p>打开 <code>http://127.0.0.1:8000</code>，提交 sample JD，进入 run detail，找到 <strong>RAG evidence</strong> 区块。检查 query、chunk score、freshness 是否符合你的预期。</p></div>
    </div>

    <h3>工程选择 Q&amp;A</h3>
    <div class="qa-grid">
      <div class="qa-card"><h4>Q: 为什么第一个 RAG eval 不直接测 final answer？</h4><p><strong>A:</strong> final answer 同时受 retrieval、prompt、LLM、写作格式影响，失败后很难定位。retrieval hit eval 更可控：给定 corpus 和 query，应该命中哪个 chunk 是明确的。先把这一层锁住，再叠加 faithfulness、citation grounding 和 answer quality。</p></div>
      <div class="qa-card"><h4>Q: 为什么现在还不用 pgvector？</h4><p><strong>A:</strong> 当前 story bank 数据很小，关键词足以暴露 retrieval contract、freshness、eval、UI trace 这些核心问题。过早上 pgvector 会增加数据库、embedding、迁移、成本，却还没有证明语义检索是瓶颈。等出现同义词、跨文档、多来源、上百上千 chunks 时再升级。</p></div>
      <div class="qa-card"><h4>Q: keyword retrieval 会不会太简单？</h4><p><strong>A:</strong> 简单不是问题，不可测才是问题。当前实现故意 deterministic，方便你理解和回归。真正的升级路径是保留 <code>RetrievalContext</code> contract，只替换 ranker 或 candidate generator。</p></div>
      <div class="qa-card"><h4>Q: 如何避免 RAG 把旧信息说成新信息？</h4><p><strong>A:</strong> 每个 source 都应该带 <code>captured_at</code>、<code>published_at</code>、<code>expires_at</code>、<code>refresh_policy</code>。个人项目故事可以 manual refresh；公司新闻、岗位状态、行业报告应该更短 refresh window，并在 UI 里暴露 warning。</p></div>
      <div class="qa-card"><h4>Q: 什么时候该加入 reranker？</h4><p><strong>A:</strong> 当 candidate recall 很高但 top-k 排序经常错时，reranker 才值得。也就是说，先用 retrieval eval 区分是“没召回”还是“排序差”，不要直接把所有问题都归因于没有 reranker。</p></div>
    </div>
  </div>
""",
    "14_offline_eval": """
  <div class="deep-dive">
    <h3>这章真正解决的问题</h3>
    <p>第 14 章关注的是 agent 系统的质量控制：当你改了 extractor、workflow、RAG、prompt 或 UI 后，怎样知道系统没有退化。这里的 eval 不是 Kaggle 式 benchmark，而是工程回归套件。</p>
    <div class="system-map">
      <div class="map-row"><strong>Dataset</strong><span><code>samples/eval_suite.json</code> 保存固定案例。每个 case 描述输入 JD、期望 company、期望 skills、期望 stop reason、最低 fit score。</span></div>
      <div class="map-row"><strong>Runner</strong><span><code>jobagent/evals/runner.py</code> 读取 suite，根据 <code>eval_type</code> 分派到 single-turn JD extraction 或完整 trajectory workflow。</span></div>
      <div class="map-row"><strong>System Under Test</strong><span>single-turn case 只跑 <code>extract_jd()</code>；trajectory case 跑 <code>run_job_workflow()</code>，因此会覆盖 graph、agents、HITL、fit score、state serialization。</span></div>
      <div class="map-row"><strong>Checks</strong><span>每个 case 产出一组 deterministic checks，例如 company 是否匹配、required skill 是否出现、stop_reason 是否正确、fit score 是否达标。</span></div>
      <div class="map-row"><strong>Report</strong><span>runner 汇总 total、passed、failed、pass_rate、by_type、failure_categories、results。CLI 和 tests 都复用这个结构。</span></div>
      <div class="map-row"><strong>Next Layer</strong><span>第 9 章新增 retrieval eval；未来还可以加 final-answer grounding、resume rubric、human-label calibration、LLM-as-judge。</span></div>
    </div>

    <h3>代码解读：每个文件负责什么</h3>
    <div class="code-map">
      <div class="code-item"><h4><code>samples/eval_suite.json</code></h4><p>这是离线 eval dataset。它应该尽量接近你真实关心的岗位类型：AI engineer、FDE、RAG backend、agent observability、MCP tooling 等。新增功能时，先补 case，再改实现。</p></div>
      <div class="code-item"><h4><code>jobagent/evals/runner.py</code></h4><p>主 eval runner。重点看它如何读 JSON、如何按 case type 分派、如何把 check 结果汇总成 pass/fail 和 failure category。</p></div>
      <div class="code-item"><h4><code>jobagent/evals/run_quality.py</code></h4><p>单次 workflow 的质量门。它不是 dataset eval，而是产品运行后检查本次 run 是否生成了关键 artifact，例如 JD、fit analysis、resume proposal、tool audit。</p></div>
      <div class="code-item"><h4><code>jobagent/retrieval/eval_runner.py</code></h4><p>RAG 专属 eval runner。它补上第 14 章的一个重要分支：除了 workflow trajectory，也要评估 retrieval trajectory。</p></div>
      <div class="code-item"><h4><code>tests/test_eval_runner.py</code></h4><p>把 eval runner 自身纳入单测。它验证 failure categories、pass rate、case parsing 等逻辑，避免 eval 工具本身悄悄坏掉。</p></div>
      <div class="code-item"><h4><code>jobagent/cli.py</code></h4><p>把 eval 暴露成可执行命令：<code>eval</code> 跑 workflow/JD suite，<code>retrieval-eval</code> 跑 RAG suite。面试展示时，CLI 是最直接的证据。</p></div>
    </div>

    <h3>动手实验：按顺序执行</h3>
    <div class="lab-steps">
      <div class="lab-step"><h4>实验 1：跑主 eval suite</h4><p>目标：确认当前 workflow/JD extraction baseline。</p><pre><code>cd "/Users/xuantongyan/Documents/jobAgent 2"
.venv/bin/python -m jobagent.cli eval</code></pre><p>看 <code>total</code>、<code>pass_rate</code>、<code>by_type</code>、<code>failure_categories</code>。如果 failed 不为 0，先看第一个失败 case，而不是直接改代码。</p></div>
      <div class="lab-step"><h4>实验 2：定位一个 eval case</h4><p>目标：把 JSON case 和 runner check 对上。</p><pre><code>sed -n '1,120p' samples/eval_suite.json
sed -n '1,240p' jobagent/evals/runner.py</code></pre><p>对照 case 里的 <code>expected_company</code>、<code>expected_required_skills</code>、<code>expected_stop_reason</code>，再看 runner 如何生成 checks。</p></div>
      <div class="lab-step"><h4>实验 3：制造一个安全的失败 case</h4><p>目标：理解 failure category 怎么帮助定位。这个实验只写 <code>/tmp</code>。</p><pre><code>.venv/bin/python - &lt;&lt;'PY'
import json
from pathlib import Path
case = {
  "id": "intentional-skill-failure",
  "eval_type": "single_turn_jd_extract",
  "job_text": "Company: Example AI\\nRole: AI Engineer\\nBuild Python and RAG systems.",
  "expected_company": "Example AI",
  "expected_required_skills": ["kubernetes"],
}
Path("/tmp/jobagent_eval_failure.json").write_text(json.dumps([case]), encoding="utf-8")
PY
.venv/bin/python -m jobagent.cli eval --suite /tmp/jobagent_eval_failure.json || true</code></pre><p>预期这个 case 会失败，因为 JD 中没有 Kubernetes。重点观察输出里的 failed check 和 failure_categories。</p></div>
      <div class="lab-step"><h4>实验 4：同时跑 workflow eval 和 retrieval eval</h4><p>目标：理解两类 eval 的边界。</p><pre><code>.venv/bin/python -m jobagent.cli eval
.venv/bin/python -m jobagent.cli retrieval-eval</code></pre><p>主 eval 回答“workflow 有没有按预期运行”；retrieval eval 回答“RAG 是否命中正确证据”。这两个问题不要混在一个指标里。</p></div>
      <div class="lab-step"><h4>实验 5：运行测试里的 eval 保护</h4><p>目标：确认 eval runner 自身也被回归测试保护。</p><pre><code>.venv/bin/python -m unittest tests.test_eval_runner tests.test_retrieval</code></pre><p>如果你未来修改 eval schema 或 runner，这组测试应该第一时间告诉你有没有破坏评估工具。</p></div>
    </div>

    <h3>工程选择 Q&amp;A</h3>
    <div class="qa-grid">
      <div class="qa-card"><h4>Q: Eval 应该覆盖最终输出还是中间轨迹？</h4><p><strong>A:</strong> 两者都要，但早期优先中间结构和 trajectory。因为它们稳定、便宜、可定位。最终输出质量要测，但最好建立在 typed artifact、retrieval context、tool audit 已经可靠的基础上。</p></div>
      <div class="qa-card"><h4>Q: Deterministic checks 会不会太死板？</h4><p><strong>A:</strong> 对语义质量来说可能死板，但对 schema、路由、工具参数、stop reason、policy boundary 来说非常合适。AI 系统不是所有东西都要用 LLM judge。</p></div>
      <div class="qa-card"><h4>Q: 什么时候引入 LLM-as-judge？</h4><p><strong>A:</strong> 当你要评估“答案是否充分”“语气是否适合”“是否忠实引用 retrieved context”这类开放问题时可以引入。但 judge prompt、judge model、抽样审计也要版本化，否则 judge 本身会漂。</p></div>
      <div class="qa-card"><h4>Q: Eval suite 多大才有意义？</h4><p><strong>A:</strong> 初期 10-20 个高价值 case 就很有用，重点是覆盖真实风险：热门目标岗位、容易抽错的公司名、容易误判的技能、HITL 边界、RAG 证据命中。数量增长应该来自真实失败，而不是为了好看。</p></div>
      <div class="qa-card"><h4>Q: Eval 是否应该进 CI？</h4><p><strong>A:</strong> 只要稳定、低成本、无外部凭证，就应该进。当前 deterministic suite 和 retrieval suite 都适合 CI；真实 LLM eval 可以先 nightly 或手动触发。</p></div>
      <div class="qa-card"><h4>Q: Eval 失败后先改什么？</h4><p><strong>A:</strong> 先看 failure category，再看 trace/state。不要第一反应改 prompt。很多失败来自 extractor rule、state contract、retrieval source、stop reason 或 fixture 预期不清。</p></div>
    </div>
  </div>
""",
    "12_langgraph": """
  <div class="deep-dive">
    <h3>这章真正解决的问题</h3>
    <p>第 12 章不是要你立刻把教学版 <code>GraphEngine</code> 替换掉，而是要建立迁移判断力：当 workflow 开始需要 durable execution、interrupt、resume、streaming、distributed worker 和可视化调试时，哪些本地概念应该一一映射到 LangGraph。</p>
    <div class="system-map">
      <div class="map-row"><strong>Teaching Engine</strong><span><code>jobagent/graph/engine.py</code> 用最少代码表达 node、edge、budget、stop_reason、pending_node、trace span。它是理解概念的底座。</span></div>
      <div class="map-row"><strong>Workflow Contract</strong><span><code>jobagent/graph/workflow.py</code> 是 canonical graph wiring。迁移到 LangGraph 时，最应该保持的是节点职责和状态 contract，而不是一行行照搬 engine。</span></div>
      <div class="map-row"><strong>Reference Adapter</strong><span><code>jobagent/graph/langgraph_reference.py</code> 展示如何把 <code>JobSearchState</code> 包进 <code>StateGraph</code>，并把 resume gate 映射成 conditional routing。</span></div>
      <div class="map-row"><strong>Interrupt Boundary</strong><span>当前系统用 <code>StopReason.NEED_USER_APPROVAL</code> 和 <code>pending_node</code> 表达 HITL 暂停；LangGraph 里可以升级为 interrupt/checkpointer 模式。</span></div>
      <div class="map-row"><strong>Durability</strong><span><code>JsonCheckpointStore</code> 是学习版 checkpoint；生产路径会迁移到 LangGraph checkpointer 或数据库-backed state。</span></div>
    </div>

    <h3>代码解读：每个文件负责什么</h3>
    <div class="code-map">
      <div class="code-item"><h4><code>jobagent/graph/engine.py</code></h4><p>本地 orchestrator。它负责按节点名调度、检查预算、记录 trace、处理 stop_reason，并在暂停时写下 <code>pending_node</code>。读这个文件时重点看控制流，而不是把它当成生产框架。</p></div>
      <div class="code-item"><h4><code>jobagent/graph/workflow.py</code></h4><p>业务 workflow 的唯一装配点。哪些 agent 节点存在、它们如何连接、resume 后从哪里继续，都应该先在这里理解清楚。</p></div>
      <div class="code-item"><h4><code>jobagent/graph/langgraph_reference.py</code></h4><p>LangGraph 迁移参考，不是默认 runtime。它把教学 engine 的概念翻译成 <code>StateGraph</code>、conditional edges 和 checkpointer，并用 optional dependency 保持主路径轻量。</p></div>
      <div class="code-item"><h4><code>jobagent/models.py</code></h4><p><code>JobSearchState</code> 是迁移时最重要的资产。框架可以换，但 state schema、artifact 字段、stop_reason 和审批语义必须稳定。</p></div>
      <div class="code-item"><h4><code>tests/test_optional_integrations.py</code></h4><p>验证 optional integration 的边界：没装 LangGraph 时不让主测试坏掉；装了以后能检查 reference app 构建路径。</p></div>
    </div>

    <h3>动手实验：按顺序执行</h3>
    <div class="lab-steps">
      <div class="lab-step"><h4>实验 1：对照两个 graph 文件</h4><p>目标：找出本地 engine 与 LangGraph reference 的概念映射。</p><pre><code>sed -n '1,140p' jobagent/graph/engine.py
sed -n '1,220p' jobagent/graph/langgraph_reference.py</code></pre><p>记录：node wrapper 在哪里、conditional route 在哪里、checkpoint 在哪里、HITL 暂停如何表达。</p></div>
      <div class="lab-step"><h4>实验 2：跑 optional integration 测试</h4><p>目标：确认 LangGraph 是可选增强，不影响默认学习路径。</p><pre><code>.venv/bin/python -m unittest tests.test_optional_integrations</code></pre><p>如果环境没装 LangGraph，测试应该 skip 或验证 graceful boundary；这就是 optional dependency 的正确行为。</p></div>
      <div class="lab-step"><h4>实验 3：写一张迁移表</h4><p>目标：把“换框架”变成可执行迁移计划。</p><pre><code>rg -n "GraphEngine|pending_node|StopReason|JsonCheckpointStore|build_langgraph" jobagent tests</code></pre><p>把每个结果分到四列：current concept、LangGraph concept、must preserve、migration risk。这个表比直接改代码更有价值。</p></div>
    </div>

    <h3>工程选择 Q&amp;A</h3>
    <div class="qa-grid">
      <div class="qa-card"><h4>Q: 现在应该直接迁移 LangGraph 吗？</h4><p><strong>A:</strong> 不急。当前目标是学习和 portfolio，教学 engine 更透明。等你要做长任务、复杂分支、跨进程 resume、生产级 checkpoint 和可视化 debug，再迁移更自然。</p></div>
      <div class="qa-card"><h4>Q: 迁移时最怕丢什么？</h4><p><strong>A:</strong> 最怕丢 state contract、eval suite 和 HITL 语义。框架 API 可以重写，但用户审批边界、trace 证据、checkpoint 恢复必须保持。</p></div>
      <div class="qa-card"><h4>Q: LangGraph 会不会让系统自动变 production-ready？</h4><p><strong>A:</strong> 不会。它提供 durable workflow primitives，但 auth、rate limit、data retention、eval、observability、deployment 和 cost control 仍然要你设计。</p></div>
      <div class="qa-card"><h4>Q: 面试时怎么讲这一章？</h4><p><strong>A:</strong> 讲“我先用小 engine 学清楚 orchestrator 的 invariants，再保留 LangGraph 迁移适配层”。这比只说“我用了 LangGraph”更像 AI infra 工程师。</p></div>
    </div>
  </div>
""",
    "13_observability": """
  <div class="deep-dive">
    <h3>这章真正解决的问题</h3>
    <p>第 13 章把 agent 从“看最终输出”推进到“看执行证据”。一个 multi-agent workflow 出错时，最终结果只告诉你它错了，trace 才告诉你它在哪里、为什么、用什么状态错了。</p>
    <div class="system-map">
      <div class="map-row"><strong>Run</strong><span>每次 workflow 都有 run_id，trace、checkpoint、web detail 都围绕同一个 run_id 聚合。</span></div>
      <div class="map-row"><strong>Span</strong><span><code>JsonlTracer.span(node)</code> 让每个 agent node 都产生 started_at、completed_at、status、metadata。</span></div>
      <div class="map-row"><strong>Metadata</strong><span>engine 会把 next_node、stop_reason、steps_used 等信息写进 span，形成可复盘的执行轨迹。</span></div>
      <div class="map-row"><strong>Export</strong><span><code>langfuse_exporter.py</code> 说明本地 JSONL trace 如何映射到外部观测平台。</span></div>
      <div class="map-row"><strong>Product</strong><span>web run detail 和 ops endpoints 使用这些证据，让用户和开发者都能知道系统当前状态。</span></div>
    </div>

    <h3>代码解读：每个文件负责什么</h3>
    <div class="code-map">
      <div class="code-item"><h4><code>jobagent/observability/tracer.py</code></h4><p>本地 trace 核心。<code>JsonlTracer</code> 创建 span，<code>TraceEvent</code> 规定事件结构，<code>_TraceSpan</code> 在进入和退出节点时写 JSONL。</p></div>
      <div class="code-item"><h4><code>jobagent/graph/engine.py</code></h4><p>调用 tracer 的地方。engine 不只调节点，还把节点结果转成 trace metadata，因此调度和观测是连在一起的。</p></div>
      <div class="code-item"><h4><code>jobagent/observability/langfuse_exporter.py</code></h4><p>外部观测平台适配器。它把本地 trace event 转成 Langfuse observation，展示“本地先打证据，再接平台”的升级方式。</p></div>
      <div class="code-item"><h4><code>tests/test_learning_integrations.py</code></h4><p>用 fake Langfuse client 测 exporter，不需要真实凭证。这个测试模式很适合学习外部 SDK integration。</p></div>
      <div class="code-item"><h4><code>.jobagent/runs/&lt;run_id&gt;/trace.jsonl</code></h4><p>真实运行后的证据文件。调试时先看这里，而不是先猜 prompt 或 UI。</p></div>
    </div>

    <h3>动手实验：按顺序执行</h3>
    <div class="lab-steps">
      <div class="lab-step"><h4>实验 1：生成一条本地 trace</h4><pre><code>.venv/bin/python -m jobagent.cli demo --auto-approve
latest=$(find .jobagent/runs -name trace.jsonl -print | sort | tail -1)
sed -n '1,80p' "$latest"</code></pre><p>目标：看到每个 node 的 started/completed 事件，以及 metadata 里的 next_node 和 stop_reason。</p></div>
      <div class="lab-step"><h4>实验 2：阅读 tracer 写入逻辑</h4><pre><code>sed -n '1,140p' jobagent/observability/tracer.py
sed -n '35,75p' jobagent/graph/engine.py</code></pre><p>目标：确认 trace 是由 workflow 执行自然产生的，不是事后拼出来的日志。</p></div>
      <div class="lab-step"><h4>实验 3：验证 Langfuse exporter 的 fake-client 测试</h4><pre><code>.venv/bin/python -m unittest tests.test_learning_integrations</code></pre><p>目标：学习怎样在没有真实外部账号时测试 integration contract。</p></div>
    </div>

    <h3>工程选择 Q&amp;A</h3>
    <div class="qa-grid">
      <div class="qa-card"><h4>Q: log、metric、trace 谁最先做？</h4><p><strong>A:</strong> agent workflow 先做 trace。因为 agent 质量问题通常是路径问题：哪个节点看到了什么、调用了什么、为什么停下。</p></div>
      <div class="qa-card"><h4>Q: 是否记录完整 prompt 和输出？</h4><p><strong>A:</strong> 开发期很有用，生产期要经过 redaction、retention 和 access control。求职产品里可能有简历、公司、个人经历，不能随便外发。</p></div>
      <div class="qa-card"><h4>Q: 什么时候接 Langfuse 或 OpenTelemetry？</h4><p><strong>A:</strong> 当 trace 不只是给你本地 debug，而要支持 dashboard、团队排查、eval linkage、成本/延迟分析时，就值得接。</p></div>
      <div class="qa-card"><h4>Q: Trace 和 eval 怎么配合？</h4><p><strong>A:</strong> eval 告诉你失败了，trace 告诉你失败路径。最好的 agent regression 报告应该能从 failed case 直接跳到 trace。</p></div>
    </div>
  </div>
""",
    "15_guardrails": """
  <div class="deep-dive">
    <h3>这章真正解决的问题</h3>
    <p>第 15 章把系统边界放在模型能力之前：公开产品不能把任意文本直接交给 agent。攻击、误输入、secret 泄露、run id 猜测、超大请求和未授权审批都应该在 workflow 外层先被限制。</p>
    <div class="system-map">
      <div class="map-row"><strong>Request Boundary</strong><span>FastAPI middleware 限制请求体大小、设置 security headers，并把异常变成可控响应。</span></div>
      <div class="map-row"><strong>Input Inspection</strong><span><code>inspect_public_submission()</code> 在创建 run 前扫描 secret 和 prompt injection pattern。</span></div>
      <div class="map-row"><strong>Run Identity</strong><span><code>_validate_run_id_or_404()</code> 避免路径遍历和奇怪 run id 进入 checkpoint/store 层。</span></div>
      <div class="map-row"><strong>Approval Ownership</strong><span>公开模式下审批绑定 creator session，防止别人拿到 run_id 后替你批准。</span></div>
      <div class="map-row"><strong>Ops Exposure</strong><span><code>JOBAGENT_PUBLIC_DEMO_MODE</code> 会隐藏敏感 ops surface，避免公开 demo 泄露过多运行细节。</span></div>
    </div>

    <h3>代码解读：每个文件负责什么</h3>
    <div class="code-map">
      <div class="code-item"><h4><code>jobagent/security/input_guardrails.py</code></h4><p>输入安全扫描器。它返回结构化 <code>GuardrailFinding</code>，让 UI/API 能解释为什么拒绝，而不是只给一个模糊错误。</p></div>
      <div class="code-item"><h4><code>jobagent/web/app.py</code></h4><p>安全边界最多的文件：body limit、headers、rate limit、run id validation、submission validation、public demo mode、approval owner session 都在这里。</p></div>
      <div class="code-item"><h4><code>tests/test_input_guardrails.py</code></h4><p>验证 secret/prompt-injection pattern。这里适合加入未来真实攻击样例，作为安全 regression suite。</p></div>
      <div class="code-item"><h4><code>tests/test_web_app.py</code></h4><p>覆盖 web public surface：创建 run、审批、ops route、run id validation、公开模式行为。安全补丁应该优先在这里加测试。</p></div>
    </div>

    <h3>动手实验：按顺序执行</h3>
    <div class="lab-steps">
      <div class="lab-step"><h4>实验 1：跑 guardrail 和 web 安全测试</h4><pre><code>.venv/bin/python -m unittest tests.test_input_guardrails tests.test_web_app</code></pre><p>目标：确认入口安全边界有回归保护。</p></div>
      <div class="lab-step"><h4>实验 2：阅读 public submission 检查</h4><pre><code>sed -n '1,140p' jobagent/security/input_guardrails.py
rg -n "guardrail|PUBLIC_DEMO|approve|rate|run_id" jobagent/web/app.py</code></pre><p>目标：把安全控制分成输入、身份、速率、运维暴露、审批五类。</p></div>
      <div class="lab-step"><h4>实验 3：设计一个攻击样例</h4><pre><code>sed -n '1,220p' tests/test_input_guardrails.py</code></pre><p>目标：新增测试前先写出攻击意图：它是 secret 泄露、prompt injection、越权审批，还是 DoS？安全测试应该对应威胁模型。</p></div>
    </div>

    <h3>工程选择 Q&amp;A</h3>
    <div class="qa-grid">
      <div class="qa-card"><h4>Q: Guardrail 应该 blocking 还是 warning？</h4><p><strong>A:</strong> secret、credential、越权外部写入、审批绕过应该 blocking；低质量输入、缺少 URL、信息不完整可以 warning 或引导用户补充。</p></div>
      <div class="qa-card"><h4>Q: 模型级 guardrail 够吗？</h4><p><strong>A:</strong> 不够。模型 guardrail 是一层，但 web request、tool permission、MCP server、external side effect、HITL 都需要系统级边界。</p></div>
      <div class="qa-card"><h4>Q: 误杀怎么办？</h4><p><strong>A:</strong> Finding 要可解释，UI 要给用户改写输入的机会。真正需要 override 的场景必须有审计记录和权限控制。</p></div>
      <div class="qa-card"><h4>Q: 对 portfolio 来说安全做到什么程度？</h4><p><strong>A:</strong> 至少能讲清 threat model，并用测试证明 public route、approval、run id、request size、secret scanning 有基本保护。</p></div>
    </div>
  </div>
""",
    "16_web_product": """
  <div class="deep-dive">
    <h3>这章真正解决的问题</h3>
    <p>第 16 章把 agent workflow 从脚本变成产品。对求职平台来说，UI 的价值不是好看而已，而是让用户理解系统现在做到哪里、需要他们批准什么、哪些输出已经可以信任。</p>
    <div class="system-map">
      <div class="map-row"><strong>Home</strong><span><code>index.html</code> 是 command center：提交 JD、查看 workflow strip、理解 bounded agents。</span></div>
      <div class="map-row"><strong>Create Run</strong><span><code>POST /runs</code> 校验输入、通过 guardrail、创建 workflow run，并写入 store/checkpoint。</span></div>
      <div class="map-row"><strong>Review Gate</strong><span>resume proposal 生成后进入 approval 状态，UI 展示 proposal 和风险，让人类决定是否继续。</span></div>
      <div class="map-row"><strong>Run Detail</strong><span><code>run.html</code> 展示 artifacts、trace rows、retrieval evidence、tool audit 和最终结果。</span></div>
      <div class="map-row"><strong>Ops</strong><span><code>/healthz</code>、<code>/readyz</code>、<code>/ops/status</code> 让部署环境能判断服务状态。</span></div>
    </div>

    <h3>代码解读：每个文件负责什么</h3>
    <div class="code-map">
      <div class="code-item"><h4><code>jobagent/web/app.py</code></h4><p>FastAPI product shell。它连接表单、store、workflow、approval、ops endpoint 和模板渲染，是产品化的中枢。</p></div>
      <div class="code-item"><h4><code>jobagent/web/store.py</code></h4><p>run store 抽象。LocalRunStore 适合本地/公开 demo；PostgresRunStore 是 durable state 的升级边界。</p></div>
      <div class="code-item"><h4><code>jobagent/web/templates/index.html</code></h4><p>首页产品体验。它应该让用户不用懂内部代码也能开始一次 job-agent run。</p></div>
      <div class="code-item"><h4><code>jobagent/web/templates/run.html</code></h4><p>run detail 页面。这里最能体现 agent product 与普通表单的差异：状态、审批、证据、trace、RAG context 都在同一页。</p></div>
      <div class="code-item"><h4><code>jobagent/web/static/app.css</code></h4><p>产品 UI 的视觉系统。它不仅管颜色，还影响信息密度、卡片层级、移动端可读性和审批区域的清晰度。</p></div>
    </div>

    <h3>动手实验：按顺序执行</h3>
    <div class="lab-steps">
      <div class="lab-step"><h4>实验 1：本地启动产品面</h4><pre><code>.venv/bin/uvicorn jobagent.web.app:app --host 127.0.0.1 --port 8000</code></pre><p>打开 <code>http://127.0.0.1:8000</code>，提交 sample JD，观察从 pending approval 到 completed 的页面变化。</p></div>
      <div class="lab-step"><h4>实验 2：阅读 route 到模板的数据流</h4><pre><code>rg -n "TemplateResponse|create_run|approve_run|_run_summary|_trace_rows|_workflow_steps" jobagent/web/app.py
sed -n '1,220p' jobagent/web/templates/run.html</code></pre><p>目标：弄清楚每个 UI 区块的数据来自 state、store、trace 还是 helper。</p></div>
      <div class="lab-step"><h4>实验 3：跑 web regression 测试</h4><pre><code>.venv/bin/python -m unittest tests.test_web_app</code></pre><p>目标：确认 UI/API 关键流程没有被文案或路由调整破坏。</p></div>
    </div>

    <h3>工程选择 Q&amp;A</h3>
    <div class="qa-grid">
      <div class="qa-card"><h4>Q: Agent UI 应该是聊天框还是 cockpit？</h4><p><strong>A:</strong> JobAgent 更适合 cockpit。它是有阶段、有审批、有证据链的 workflow，用户关心状态和决策点，不只是自由聊天。</p></div>
      <div class="qa-card"><h4>Q: 中间结果要不要展示？</h4><p><strong>A:</strong> 要展示能帮助用户判断的中间结果：fit concerns、resume proposal、RAG evidence、trace summary。不要把所有内部字段都塞进页面。</p></div>
      <div class="qa-card"><h4>Q: 错误提示怎么分层？</h4><p><strong>A:</strong> UI 给用户可行动的错误，trace/log 给开发者技术细节。两者应该由同一 run_id 连接起来。</p></div>
      <div class="qa-card"><h4>Q: 为什么 portfolio 需要 UI？</h4><p><strong>A:</strong> 因为 FDE/AI engineer 不只是写 workflow，还要把复杂系统交到用户手里。UI 是你理解产品边界的证据。</p></div>
    </div>
  </div>
""",
    "17_deployment": """
  <div class="deep-dive">
    <h3>这章真正解决的问题</h3>
    <p>第 17 章回答“它能不能被别人打开使用”。部署 agent product 不是只把 Python 服务跑起来，还要说明健康检查、配置、状态持久性、成本、安全边界和后续升级路径。</p>
    <div class="system-map">
      <div class="map-row"><strong>Container</strong><span><code>Dockerfile</code> 定义可重复运行环境，生产命令启动 <code>uvicorn jobagent.web.app:app</code>。</span></div>
      <div class="map-row"><strong>Local Stack</strong><span><code>docker-compose.yml</code> 让 web、Postgres、Langfuse 等组件可以在本地组合验证。</span></div>
      <div class="map-row"><strong>Render Blueprint</strong><span><code>render.yaml</code> 描述托管服务、健康检查、环境变量和 public demo mode。</span></div>
      <div class="map-row"><strong>Runtime Health</strong><span><code>/healthz</code> 证明进程活着；<code>/readyz</code> 应该证明依赖和 store 能工作。</span></div>
      <div class="map-row"><strong>Boundary</strong><span>公开 demo 可以使用轻量 state，但 production SaaS 需要 durable store、auth、queue、observability backend 和 budget controls。</span></div>
    </div>

    <h3>代码解读：每个文件负责什么</h3>
    <div class="code-map">
      <div class="code-item"><h4><code>Dockerfile</code></h4><p>部署镜像入口。它说明服务运行需要哪些系统层、Python 包和启动命令。</p></div>
      <div class="code-item"><h4><code>render.yaml</code></h4><p>Render 部署蓝图。重点看 <code>healthCheckPath</code>、环境变量和是否启用 public demo mode。</p></div>
      <div class="code-item"><h4><code>docker-compose.yml</code></h4><p>本地 production-like 环境。它适合练习服务依赖、Postgres、observability backend 的组合。</p></div>
      <div class="code-item"><h4><code>jobagent/web/app.py</code></h4><p>暴露 health/readiness/ops endpoints。部署平台依赖这些 endpoint 判断服务是否可以接流量。</p></div>
      <div class="code-item"><h4><code>deploy/langfuse/README.md</code></h4><p>观测平台部署说明。它把第 13 章 trace 能力推进到外部系统。</p></div>
    </div>

    <h3>动手实验：按顺序执行</h3>
    <div class="lab-steps">
      <div class="lab-step"><h4>实验 1：读部署蓝图</h4><pre><code>sed -n '1,180p' render.yaml
sed -n '1,160p' Dockerfile</code></pre><p>目标：找出启动命令、健康检查、环境变量和 public demo 边界。</p></div>
      <div class="lab-step"><h4>实验 2：本地检查 health/readiness</h4><pre><code>.venv/bin/uvicorn jobagent.web.app:app --host 127.0.0.1 --port 8000
# 另开终端:
curl -s http://127.0.0.1:8000/healthz
curl -s http://127.0.0.1:8000/readyz
curl -s http://127.0.0.1:8000/ops/status</code></pre><p>目标：理解部署平台看到的不是 UI，而是这些运行状态信号。</p></div>
      <div class="lab-step"><h4>实验 3：检查当前 store 边界</h4><pre><code>sed -n '1,220p' jobagent/web/store.py
rg -n "JOBAGENT_DATABASE_URL|PUBLIC_DEMO|readyz|ops/status" jobagent/web/app.py render.yaml README.md</code></pre><p>目标：写出 demo state 与 durable production state 的差异。</p></div>
    </div>

    <h3>工程选择 Q&amp;A</h3>
    <div class="qa-grid">
      <div class="qa-card"><h4>Q: Render 部署就等于 production-ready 吗？</h4><p><strong>A:</strong> 不等于。它证明可公开访问和可运行，但 production-ready 还需要持久状态、认证、队列、审计、监控、预算和恢复证据。</p></div>
      <div class="qa-card"><h4>Q: 什么时候必须上 Postgres？</h4><p><strong>A:</strong> 当用户期望历史 run 不丢、审批可恢复、多实例共享状态，或者你要分析运行数据时。</p></div>
      <div class="qa-card"><h4>Q: 什么时候必须上 queue？</h4><p><strong>A:</strong> 当 workflow 超过 request timeout、外部 API 慢、需要 retry/backoff，或并发 run 会阻塞 web worker 时。</p></div>
      <div class="qa-card"><h4>Q: 免费托管会不会有成本风险？</h4><p><strong>A:</strong> 如果不接真实 LLM，成本主要是 hosting。接真实模型后必须做 rate limit、budget cap、key isolation 和 abuse monitoring。</p></div>
    </div>
  </div>
""",
    "18_10x_scale_readiness": """
  <div class="deep-dive">
    <h3>这章真正解决的问题</h3>
    <p>第 18 章训练的是 production judgment。JobAgent 已经是 production-shaped：有 web surface、typed state、checkpoint、trace、eval、guardrails 和部署。但它还不是 full SaaS，因为 10x traffic 会首先打到执行、状态、恢复和运维层。</p>
    <div class="system-map">
      <div class="map-row"><strong>Execution</strong><span>当前 <code>POST /runs</code> 同步执行 workflow。10x 后应拆成 web request + background job + status polling。</span></div>
      <div class="map-row"><strong>State</strong><span>LocalRunStore/JSON checkpoint 适合学习和 demo；durable beta 需要 Postgres、migration、connection pooling 和 backup。</span></div>
      <div class="map-row"><strong>Concurrency</strong><span>内存 rate limit 和单进程状态不适合多实例。生产要用共享 rate limit 和 idempotency key。</span></div>
      <div class="map-row"><strong>Recovery</strong><span>approval、resume、tool side effect 都需要幂等设计，避免重复提交或丢失用户决策。</span></div>
      <div class="map-row"><strong>Evidence</strong><span>readiness 需要测试、eval、restart smoke、ops endpoint、trace 和安全验证共同证明。</span></div>
    </div>

    <h3>代码解读：每个文件负责什么</h3>
    <div class="code-map">
      <div class="code-item"><h4><code>jobagent/web/app.py</code></h4><p>当前 request lifecycle 所在地。重点读 <code>create_run</code> 和 <code>approve_run</code>：它们告诉你同步执行、审批 resume 和错误处理在哪里发生。</p></div>
      <div class="code-item"><h4><code>jobagent/web/store.py</code></h4><p>LocalRunStore 与 PostgresRunStore 的边界。这里决定 run summary、creator session、approval 状态和持久化能力。</p></div>
      <div class="code-item"><h4><code>jobagent/storage/checkpoint.py</code></h4><p>workflow state checkpoint。10x 升级时，它会变成数据库表、object store 或 LangGraph checkpointer 的候选迁移点。</p></div>
      <div class="code-item"><h4><code>samples/eval_suite.json</code></h4><p>readiness 的质量证据。每次 production-ish 改动都应该证明核心 trajectory 没退化。</p></div>
      <div class="code-item"><h4><code>render.yaml</code></h4><p>部署层证据。它说明当前公开服务如何启动，也暴露了哪些还只是 demo 边界。</p></div>
    </div>

    <h3>动手实验：按顺序执行</h3>
    <div class="lab-steps">
      <div class="lab-step"><h4>实验 1：定位同步执行风险</h4><pre><code>rg -n "def create_run|run_job_workflow|approve_run|resume_job_workflow" jobagent/web/app.py</code></pre><p>目标：标出哪些代码如果 workflow 变慢，会直接拖住 HTTP request。</p></div>
      <div class="lab-step"><h4>实验 2：比较两个 store 的生产含义</h4><pre><code>sed -n '1,260p' jobagent/web/store.py</code></pre><p>目标：列出 LocalRunStore 能做什么、PostgresRunStore 补了什么、还缺 migration/pooling/retention 哪些部分。</p></div>
      <div class="lab-step"><h4>实验 3：跑一次 readiness mini-gate</h4><pre><code>.venv/bin/python -m unittest discover -s tests
.venv/bin/python -m jobagent.cli eval
.venv/bin/python -m jobagent.cli retrieval-eval</code></pre><p>目标：把测试和 eval 视为 readiness evidence，而不是开发结束后的仪式。</p></div>
    </div>

    <h3>工程选择 Q&amp;A</h3>
    <div class="qa-grid">
      <div class="qa-card"><h4>Q: 10x 首先扩哪里？</h4><p><strong>A:</strong> 先扩执行层和状态层：background worker、durable store、idempotency、shared rate limit。不要先优化 prompt。</p></div>
      <div class="qa-card"><h4>Q: 什么叫 production-shaped？</h4><p><strong>A:</strong> 架构形状接近生产：有边界、状态、测试、观测、安全和部署。但容量、恢复、权限、运维证据还没达到真实 SaaS。</p></div>
      <div class="qa-card"><h4>Q: readiness checklist 应该包含什么？</h4><p><strong>A:</strong> load、restart-resume、approval race、storage failure、guardrail bypass、eval regression、trace smoke、ops endpoint 和 cost cap。</p></div>
      <div class="qa-card"><h4>Q: 面试时怎么讲边界不显弱？</h4><p><strong>A:</strong> 说清楚当前是 public product/portfolio surface，并列出升级顺序和验证证据。诚实边界本身就是 production thinking。</p></div>
    </div>
  </div>
""",
    "19_debugging": """
  <div class="deep-dive">
    <h3>这章真正解决的问题</h3>
    <p>第 19 章给你一套 debug playbook：agent 系统出错时，不要第一反应改 prompt，而是沿着 input、state、checkpoint、trace、node、eval、UI 的证据链逐步缩小范围。</p>
    <div class="system-map">
      <div class="map-row"><strong>Reproduce</strong><span>先用 CLI 或 web run 复现问题，固定输入和 run_id。</span></div>
      <div class="map-row"><strong>Checkpoint</strong><span>检查 <code>.jobagent/checkpoints</code>，确认 typed state 是否已经错误。</span></div>
      <div class="map-row"><strong>Trace</strong><span>检查 <code>.jobagent/runs</code> 的 JSONL，确认哪个 node 停下、下一步是什么、有没有异常。</span></div>
      <div class="map-row"><strong>Node Contract</strong><span>如果 state 错，回到对应 agent 文件；如果 state 对但 UI 错，再看 template/helper。</span></div>
      <div class="map-row"><strong>Regression</strong><span>补 eval 或 unit test，再修实现。不要只靠手动刷新页面确认。</span></div>
    </div>

    <h3>代码解读：每个文件负责什么</h3>
    <div class="code-map">
      <div class="code-item"><h4><code>jobagent/graph/engine.py</code></h4><p>调度证据源。预算、未知节点、stop_reason、pending_node、trace metadata 都在这里形成。</p></div>
      <div class="code-item"><h4><code>jobagent/storage/checkpoint.py</code></h4><p>状态快照入口。它让你能判断 bug 是否已经写进 state，还是只是展示层问题。</p></div>
      <div class="code-item"><h4><code>jobagent/observability/tracer.py</code></h4><p>时间线证据。trace 适合判断执行顺序、节点耗时、异常和暂停原因。</p></div>
      <div class="code-item"><h4><code>jobagent/evals/runner.py</code></h4><p>回归保护。发现 bug 后，如果能写成 eval case，就应该先把失败固定下来。</p></div>
      <div class="code-item"><h4><code>tests/</code></h4><p>更小粒度的保护网。UI bug、guardrail bug、store bug、retrieval bug 不一定都放进大 eval，很多更适合 unit test。</p></div>
    </div>

    <h3>动手实验：按顺序执行</h3>
    <div class="lab-steps">
      <div class="lab-step"><h4>实验 1：从 run_id 找证据</h4><pre><code>.venv/bin/python -m jobagent.cli demo --auto-approve
ls -t .jobagent/checkpoints | head
find .jobagent/runs -name trace.jsonl -print | sort | tail -1</code></pre><p>目标：把一次运行对应的 checkpoint 和 trace 找出来。</p></div>
      <div class="lab-step"><h4>实验 2：读 checkpoint 和 trace</h4><pre><code>latest_checkpoint=$(ls -t .jobagent/checkpoints/*.json | head -1)
python3 -m json.tool "$latest_checkpoint" | sed -n '1,120p'
latest_trace=$(find .jobagent/runs -name trace.jsonl -print | sort | tail -1)
sed -n '1,80p' "$latest_trace"</code></pre><p>目标：练习判断问题是在 state artifact、node route，还是展示层。</p></div>
      <div class="lab-step"><h4>实验 3：用 eval 锁住失败</h4><pre><code>sed -n '1,180p' samples/eval_suite.json
sed -n '1,220p' jobagent/evals/runner.py</code></pre><p>目标：学会在修 bug 前设计一个最小失败 case。</p></div>
    </div>

    <h3>工程选择 Q&amp;A</h3>
    <div class="qa-grid">
      <div class="qa-card"><h4>Q: 什么时候才改 prompt？</h4><p><strong>A:</strong> 当 input、retrieval、state、tool、guardrail、UI 都证明没问题，而语义质量仍然不足时。prompt 是候选原因，不是默认原因。</p></div>
      <div class="qa-card"><h4>Q: trace 太多怎么办？</h4><p><strong>A:</strong> 本地学习可以保留较多；生产要按 run_id、user、时间窗口检索，并设置 retention、redaction 和采样策略。</p></div>
      <div class="qa-card"><h4>Q: checkpoint 和 trace 哪个先看？</h4><p><strong>A:</strong> 输出内容错，先看 checkpoint；执行路径错，先看 trace。两者最终要结合。</p></div>
      <div class="qa-card"><h4>Q: 自动 retry 是不是好事？</h4><p><strong>A:</strong> 只有幂等、低风险、可观察的失败才适合 retry。外部写入和审批动作不能随便自动重放。</p></div>
    </div>
  </div>
""",
    "20_upgrade_choices": """
  <div class="deep-dive">
    <h3>这章真正解决的问题</h3>
    <p>第 20 章把“我知道很多技术名词”变成“我知道什么时候引入它们”。对 AI infra 来说，成熟度不是堆栈越满越好，而是每个升级都有触发条件、复杂度预算和验证方式。</p>
    <div class="system-map">
      <div class="map-row"><strong>Inventory</strong><span><code>integrations/registry.py</code> 列出本项目的学习型 integration：LangGraph、LLM providers、Langfuse、Postgres/pgvector、MCP、Docker/Render。</span></div>
      <div class="map-row"><strong>Trigger</strong><span>每个升级项都应该由痛点触发：durability、semantic retrieval、tool reuse、observability、model quality、deployment scale。</span></div>
      <div class="map-row"><strong>Complexity</strong><span>升级会带来依赖、凭证、迁移、成本、故障模式和测试矩阵。</span></div>
      <div class="map-row"><strong>Boundary</strong><span>用 provider、store、retriever、exporter、MCP server 等边界把升级限制在可替换位置。</span></div>
      <div class="map-row"><strong>Verification</strong><span>每次升级都必须有保持不变的 eval/test：trajectory、retrieval hit、web route 或 exporter contract。</span></div>
    </div>

    <h3>代码解读：每个文件负责什么</h3>
    <div class="code-map">
      <div class="code-item"><h4><code>jobagent/integrations/registry.py</code></h4><p>技术栈目录。它适合用来复盘每个 integration 的状态、学习目的和 adoption trigger。</p></div>
      <div class="code-item"><h4><code>pyproject.toml</code></h4><p>依赖边界。看 optional dependency 和测试配置，能判断哪些能力是默认路径，哪些是可选增强。</p></div>
      <div class="code-item"><h4><code>jobagent/storage/postgres_memory.py</code></h4><p>Postgres/pgvector 方向的雏形。它代表 memory/retrieval 从本地 JSON 走向 durable query layer。</p></div>
      <div class="code-item"><h4><code>mcp_server/</code></h4><p>MCP-shaped 工具边界。它适合当工具需要跨客户端复用，而不是只在本项目内部调用时升级。</p></div>
      <div class="code-item"><h4><code>tests/test_learning_integrations.py</code></h4><p>integration contract 测试。它展示如何在不依赖真实云服务的情况下验证 adapter 行为。</p></div>
    </div>

    <h3>动手实验：按顺序执行</h3>
    <div class="lab-steps">
      <div class="lab-step"><h4>实验 1：打印 integration inventory</h4><pre><code>.venv/bin/python - &lt;&lt;'PY'
from jobagent.integrations.registry import list_learning_integrations
for item in list_learning_integrations():
    print(item.name, "-", item.status)
    print("  trigger:", item.adoption_trigger)
PY</code></pre><p>目标：把技术栈看成 adoption decision，而不是 checklist。</p></div>
      <div class="lab-step"><h4>实验 2：选择一个升级写最小 PR 范围</h4><pre><code>rg -n "LangGraph|Langfuse|Postgres|pgvector|MCP|OpenAI|Anthropic" jobagent tests pyproject.toml docker-compose.yml</code></pre><p>目标：列出会触碰的文件、必须保持通过的测试、以及新增失败模式。</p></div>
      <div class="lab-step"><h4>实验 3：跑 integration 相关测试</h4><pre><code>.venv/bin/python -m unittest tests.test_learning_integrations tests.test_optional_integrations</code></pre><p>目标：确认 optional integration 不破坏默认路径。</p></div>
    </div>

    <h3>工程选择 Q&amp;A</h3>
    <div class="qa-grid">
      <div class="qa-card"><h4>Q: 什么时候引入 LangGraph？</h4><p><strong>A:</strong> 当本地 engine 开始复制 durable execution、interrupt、复杂 routing、streaming、checkpoint 可视化时。</p></div>
      <div class="qa-card"><h4>Q: 什么时候引入 pgvector？</h4><p><strong>A:</strong> 当 corpus 变大、同义词/语义匹配明显影响 recall、需要跨文档检索，且你已有 retrieval eval 能证明升级收益时。</p></div>
      <div class="qa-card"><h4>Q: 什么时候接真实 LLM provider？</h4><p><strong>A:</strong> 当 deterministic baseline 已经稳定，而写作质量、语义判断或开放推理成为瓶颈时。接入前先有成本、超时、重试、structured output 失败策略。</p></div>
      <div class="qa-card"><h4>Q: 什么时候做 MCP？</h4><p><strong>A:</strong> 当工具要被多个客户端或 agent runtime 复用，或者你希望把 capability 明确暴露成协议资源时。</p></div>
    </div>
  </div>
""",
    "21_capstone": """
  <div class="deep-dive">
    <h3>这章真正解决的问题</h3>
    <p>第 21 章把前面所有能力串成一次真实工程交付：新增一个 bounded agent，并把它接入 typed state、workflow、checkpoint、eval、trace、web UI 和 portfolio narrative。它考的是闭环，不是单点功能。</p>
    <div class="system-map">
      <div class="map-row"><strong>Artifact</strong><span>先在 <code>models.py</code> 定义 typed output，例如 <code>SalaryAnalysis</code> 或 <code>NetworkingStrategy</code>。</span></div>
      <div class="map-row"><strong>Agent</strong><span>在 <code>jobagent/agents/</code> 新增 bounded node，只读它需要的 state，只写它负责的 artifact。</span></div>
      <div class="map-row"><strong>Graph</strong><span>在 <code>workflow.py</code> 接入 node 和 edge，决定它在 JD、company、fit、resume、approval 之间的位置。</span></div>
      <div class="map-row"><strong>Eval</strong><span>在 <code>samples/eval_suite.json</code> 和 runner/tests 里覆盖 trajectory 与关键输出。</span></div>
      <div class="map-row"><strong>Product</strong><span>在 <code>run.html</code> 展示新 artifact，让用户看到它为什么有用。</span></div>
      <div class="map-row"><strong>Story</strong><span>最后写 README/portfolio 叙事：你如何设计 bounded multi-agent workflow，并如何验证它。</span></div>
    </div>

    <h3>代码解读：每个文件负责什么</h3>
    <div class="code-map">
      <div class="code-item"><h4><code>jobagent/models.py</code></h4><p>新增能力的 contract 起点。不要先写自由 dict，先定义 dataclass/schema，后续 checkpoint、UI、eval 都会受益。</p></div>
      <div class="code-item"><h4><code>jobagent/agents/</code></h4><p>bounded agent 的实现目录。一个新 agent 应该职责窄、输入明确、输出结构化、失败模式可解释。</p></div>
      <div class="code-item"><h4><code>jobagent/graph/workflow.py</code></h4><p>调度接入点。新增 node 后必须决定边的位置、HITL 前后关系、resume 行为和 stop_reason。</p></div>
      <div class="code-item"><h4><code>jobagent/evals/runner.py</code></h4><p>如果新 artifact 是核心能力，eval runner 需要能检查它。否则功能只是 UI 上看起来存在，缺少回归证据。</p></div>
      <div class="code-item"><h4><code>jobagent/web/templates/run.html</code></h4><p>产品展示层。用户应该能看懂新 agent 产物、证据和下一步动作，而不是只看到 JSON。</p></div>
      <div class="code-item"><h4><code>tests/</code></h4><p>小粒度行为保护。新增 agent 通常需要 agent unit test、workflow trajectory test、web render/API test。</p></div>
    </div>

    <h3>动手实验：按顺序执行</h3>
    <div class="lab-steps">
      <div class="lab-step"><h4>实验 1：选择一个新 agent 并定位插入点</h4><pre><code>rg -n "graph.add_node|graph.add_edge|resume_tailor|fit_analysis|interview_prep" jobagent/graph jobagent/agents</code></pre><p>目标：判断新 agent 应该依赖哪些上游 artifact，以及它是否应该在 HITL 前出现。</p></div>
      <div class="lab-step"><h4>实验 2：列出需要触碰的 contract</h4><pre><code>rg -n "class .*Analysis|JobSearchState|to_dict|from_dict|eval_type|workflow_steps" jobagent samples tests</code></pre><p>目标：把新增功能拆成 state、serialization、workflow、eval、UI、tests 六块，不要只改 agent 函数。</p></div>
      <div class="lab-step"><h4>实验 3：定义完成标准</h4><pre><code>.venv/bin/python -m unittest discover -s tests
.venv/bin/python -m jobagent.cli eval
.venv/bin/python -m jobagent.cli retrieval-eval</code></pre><p>目标：把 capstone 的完成标准写成能跑的命令。真正的项目经历要能被验证。</p></div>
    </div>

    <h3>工程选择 Q&amp;A</h3>
    <div class="qa-grid">
      <div class="qa-card"><h4>Q: 第一个 capstone agent 选什么最好？</h4><p><strong>A:</strong> 选能服务 AI engineer/FDE 求职叙事的能力：company risk analysis、networking strategy、salary/leveling analysis、interview loop planner。它要能展示产品价值和 infra 边界。</p></div>
      <div class="qa-card"><h4>Q: 新 agent 需要 HITL 吗？</h4><p><strong>A:</strong> 如果它影响真实申请、外部写入、联系人触达或简历最终内容，就需要 HITL 或至少 review gate。如果只是内部分析，可先不需要。</p></div>
      <div class="qa-card"><h4>Q: 需要真实 LLM 才算完整吗？</h4><p><strong>A:</strong> 不需要。先 deterministic baseline + provider boundary + eval。真实 LLM 是质量升级，不是系统设计的前提。</p></div>
      <div class="qa-card"><h4>Q: Portfolio 叙事怎么写？</h4><p><strong>A:</strong> 写你如何划分 bounded agent、如何管理 shared state、如何做 HITL、RAG、trace、eval、deployment 和安全边界。重点是工程判断，不是炫功能数量。</p></div>
    </div>
  </div>
""",
}
