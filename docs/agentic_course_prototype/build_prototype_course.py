from __future__ import annotations

import re
from dataclasses import dataclass
from html import escape
from pathlib import Path

from course_content import CHAPTERS, DEEP_DIVES, UPDATED

OUT_DIR = Path(__file__).resolve().parent
REPO_ROOT = OUT_DIR.parents[1]


@dataclass(frozen=True)
class CodeRow:
    line: str
    src: str
    comment: str
    kind: str = ""


CODE: dict[str, list[CodeRow]] = {
    "00_overview": [
        CodeRow("32", "def run_job_workflow(raw_job_text: str, story_bank: list[dict], *, approved: bool = False, ...):", "产品入口先创建一次 run", "hot"),
        CodeRow("42", "state = JobSearchState(run_id=run_id, user_goal=user_goal, raw_job_text=raw_job_text, ...)", "把用户输入装进 typed state", "hot"),
        CodeRow("50", "graph = build_graph(JsonlTracer(state.run_id))", "每次 run 都带 trace", "hot"),
        CodeRow("51", "state = graph.run(state, \"ingest\")", "从 ingest 节点进入 agent workflow", "hot"),
        CodeRow("52", "JsonCheckpointStore().save(state)", "结束或暂停后都保存 checkpoint", "warn"),
    ],
    "01_graph_engine": [
        CodeRow("29", "def run(self, state: JobSearchState, start: str) -> JobSearchState:", "入口只有 state 和起点节点"),
        CodeRow("30", "    current = start", "current 是塔台正在调度的节点名", "hot"),
        CodeRow("32", "        if state.budget.steps_used >= state.budget.max_steps:", "预算是第一道刹车", "warn"),
        CodeRow("35", "        if current not in self.nodes:", "未知节点不猜，直接显式失败", "warn"),
        CodeRow("41", "        with self.tracer.span(current) as metadata:", "每个节点都进入 trace 黑匣子", "hot"),
        CodeRow("44", "            result = self.nodes[current](state)", "真正调用 bounded agent node", "hot"),
        CodeRow("53", "        if result.stop_reason:", "节点要求暂停或停止", "warn"),
        CodeRow("55", "            state.pending_node = result.next_node", "resume 时从这里继续", "warn"),
        CodeRow("57", "        current = result.next_node", "没有 stop，就进入下一节点", "hot"),
    ],
    "02_shared_state": [
        CodeRow("114", "class JobSearchState:", "所有节点围绕这个对象协作"),
        CodeRow("118", "    raw_job_text: str | None = None", "用户输入的原始事实", "hot"),
        CodeRow("121", "    normalized_jd: JDExtract | None = None", "jd_extract 写入结构化 JD", "hot"),
        CodeRow("122", "    company_brief: CompanyBrief | None = None", "company_research 写入公司理解", "hot"),
        CodeRow("123", "    fit_analysis: FitAnalysis | None = None", "fit_analysis 写入评分和证据", "hot"),
        CodeRow("124", "    resume_proposal: ResumeProposal | None = None", "HITL 前的建议产物", "hot"),
        CodeRow("130", "    budget: RunBudget = field(default_factory=RunBudget)", "预算限制 workflow 步数和工具调用", "warn"),
        CodeRow("133", "    stop_reason: StopReason | None = None", "系统为什么停", "warn"),
        CodeRow("134", "    pending_node: str | None = None", "resume 后从哪里继续", "warn"),
    ],
    "03_bounded_agents": [
        CodeRow("20", "graph.add_node(\"ingest\", ingest_job_text)", "输入清洗是第一个 bounded node", "hot"),
        CodeRow("23", "graph.add_node(\"jd_extract\", extract_jd)", "抽取 JD，不研究公司", "hot"),
        CodeRow("24", "graph.add_node(\"company_research\", research_company)", "公司研究独立成 node", "hot"),
        CodeRow("25", "graph.add_node(\"fit_analysis\", analyze_fit)", "匹配度判断独立成 node", "hot"),
        CodeRow("26", "graph.add_node(\"resume_tailor\", tailor_resume)", "简历建议也是独立边界", "warn"),
        CodeRow("27", "graph.add_node(\"tracker\", propose_tracker_update)", "外部记录动作放在审批后", "warn"),
    ],
    "04_stop_reason": [
        CodeRow("9", "class StopReason(str, Enum):", "停止原因是系统 contract"),
        CodeRow("10", "    COMPLETED = \"COMPLETED\"", "正常结束", "hot"),
        CodeRow("11", "    NEED_USER_APPROVAL = \"NEED_USER_APPROVAL\"", "需要人类放行", "warn"),
        CodeRow("13", "    TOOL_ERROR = \"TOOL_ERROR\"", "工具或节点失败", "warn"),
        CodeRow("14", "    BUDGET_EXCEEDED = \"BUDGET_EXCEEDED\"", "预算刹车", "warn"),
        CodeRow("16", "    UNSAFE_OR_DISALLOWED_ACTION = \"UNSAFE_OR_DISALLOWED_ACTION\"", "安全边界刹车", "warn"),
    ],
    "05_hitl": [
        CodeRow("8", "def tailor_resume(state: JobSearchState) -> NodeResult:", "简历建议节点是 HITL 边界"),
        CodeRow("15", "    if not state.approved:", "用户未批准时不能继续", "warn"),
        CodeRow("16", "        return NodeResult(next_node=\"tracker\", stop_reason=StopReason.NEED_USER_APPROVAL)", "保存下一站，但先暂停", "warn"),
        CodeRow("67", "state.approved = approved", "resume 时写入人类决策", "hot"),
        CodeRow("70", "state = graph.run(state, state.pending_node)", "从 pending node 继续，而不是重跑全部", "hot"),
    ],
    "06_checkpoint_resume": [
        CodeRow("9", "class JsonCheckpointStore:", "本地 checkpointer"),
        CodeRow("13", "self.root.mkdir(parents=True, exist_ok=True)", "确保 checkpoint 目录存在", "hot"),
        CodeRow("19", "path.write_text(json.dumps(state.to_dict(), indent=2, ensure_ascii=True), ...)", "把 typed state 落盘", "hot"),
        CodeRow("24", "if not path.exists():", "resume 前先确认 checkpoint 存在", "warn"),
        CodeRow("26", "return JobSearchState.from_dict(json.loads(path.read_text(...)))", "从 JSON 恢复 dataclass state", "hot"),
    ],
    "07_tool_use": [
        CodeRow("1", "Tool contract = schema + permission + timeout + trace + failure mode", "工具不是自由动作，而是受控能力", "warn"),
        CodeRow("2", "External side effect -> require HITL or idempotency key", "写外部系统时要先设计安全边界", "warn"),
        CodeRow("3", "Tool result -> sanitize -> store in state -> cite source", "工具输出进入系统前要清洗和记录", "hot"),
    ],
    "08_memory_story_bank": [
        CodeRow("1", "story_bank = load_story_bank(\"samples/story_bank.json\")", "长期素材库不是聊天历史", "hot"),
        CodeRow("2", "state.story_bank = story_bank", "一次 run 只拿需要的素材进入 state", "hot"),
        CodeRow("3", "interview_pack.story_matches = select_relevant_stories(state)", "下游 agent 使用结构化素材", "hot"),
        CodeRow("4", "memory writes should be explicit and reviewable", "长期记忆写入需要边界", "warn"),
    ],
    "09_local_rag": [
        CodeRow("27", "class SourceDocument:", "资料先变成带治理字段的 source contract", "hot"),
        CodeRow("71", "class RetrievalContext:", "一次检索要留下完整证据包", "hot"),
        CodeRow("115", "def retrieve_context(...):", "context assembly 是 RAG 和 downstream agents 的边界", "hot"),
        CodeRow("132", "freshness_warnings = [...]", "相关不够，还要判断信息是否过期", "warn"),
        CodeRow("150", "def hybrid_rank_chunks(...):", "保留 keyword + semantic 的升级接口", "warn"),
    ],
    "10_mcp": [
        CodeRow("14", "def main() -> int:", "教学版 MCP-shaped server 从简单入口开始"),
        CodeRow("17", "print(json.dumps({...}))", "先表达 tool/resource contract，再接 SDK", "hot"),
        CodeRow("1", "MCP server boundary = tools + resources + credentials + audit", "协议标准化不等于安全自动解决", "warn"),
    ],
    "11_llm_provider": [
        CodeRow("8", "class LLMRequest:", "业务节点不直接依赖某个厂商 SDK", "hot"),
        CodeRow("26", "class LLMResponse:", "输出、usage、metadata 要结构化", "hot"),
        CodeRow("32", "class LLMProvider(Protocol):", "provider interface 是替换边界", "hot"),
        CodeRow("37", "class MockLLMProvider:", "测试和默认路径可以不用真实模型", "warn"),
        CodeRow("63", "def _rough_tokens(text: str) -> int:", "成本估算也应进 provider 层", "warn"),
    ],
    "12_langgraph": [
        CodeRow("1", "GraphEngine concept -> LangGraph StateGraph", "先映射概念，再迁移框架", "hot"),
        CodeRow("2", "JobSearchState -> graph state schema", "state contract 应该保留", "hot"),
        CodeRow("3", "pending_node / StopReason -> interrupt + resume", "HITL 迁移到 graph primitive", "warn"),
        CodeRow("4", "JsonCheckpointStore -> durable checkpointer", "checkpoint 升级为生产存储", "warn"),
    ],
    "13_observability": [
        CodeRow("19", "class JsonlTracer:", "本地 tracer 是生产 observability 的雏形", "hot"),
        CodeRow("28", "return _TraceSpan(self.run_id, name, self.root)", "每个 node 都变成 span", "hot"),
        CodeRow("41", "self.metadata[\"started_at\"] = datetime.now(timezone.utc).isoformat()", "trace 需要时间线", "hot"),
        CodeRow("54", "path.write_text(json.dumps(event, ensure_ascii=True) + \"\\n\", ...)", "JSONL 方便追加、排查和导出", "warn"),
    ],
    "14_offline_eval": [
        CodeRow("11", "def run_eval_suite(path: str | Path, story_bank: list[dict]) -> dict:", "eval 是 agent workflow 的回归入口", "hot"),
        CodeRow("28", "state = run_job_workflow(...)", "trajectory case 用固定输入跑完整 workflow", "hot"),
        CodeRow("63", "\"failure_categories\": _suite_failure_categories(results)", "报告要能定位失败类型", "warn"),
        CodeRow("115", "def _check_trajectory_case(case: dict, state) -> list[dict]:", "trajectory 也应该被 deterministic 检查", "hot"),
        CodeRow("11", "def run_retrieval_eval_suite(...):", "RAG 单独有 retrieval-first eval runner", "warn"),
    ],
    "15_guardrails": [
        CodeRow("13", "SECRET_PATTERNS = (...)", "secrets 在 workflow 前拦截", "warn"),
        CodeRow("23", "PROMPT_INJECTION_PATTERNS = (...)", "instruction override 在入口处拦截", "warn"),
        CodeRow("31", "def inspect_public_submission(job_text: str, job_url: str | None = None):", "public surface 先过 guardrail", "hot"),
        CodeRow("38", "if pattern.search(text):", "命中后生成可解释 finding", "hot"),
    ],
    "16_web_product": [
        CodeRow("42", "def create_app(store: RunStore | None = None) -> FastAPI:", "web surface 把 workflow 变成产品", "hot"),
        CodeRow("227", "def _validate_job_submission(job_text: str, job_url: str | None) -> str | None:", "用户输入先校验", "warn"),
        CodeRow("240", "def _validate_run_id_or_404(run_id: str) -> None:", "读取 checkpoint 前校验 run id", "warn"),
        CodeRow("300", "def _workflow_steps() -> list[dict[str, str]]:", "UI 需要显式展示 workflow 状态", "hot"),
    ],
    "17_deployment": [
        CodeRow("1", "Dockerfile -> uvicorn jobagent.web.app:app", "部署的是 web product，不只是脚本", "hot"),
        CodeRow("2", "render.yaml -> healthCheckPath: /healthz", "公开 demo 需要健康检查", "hot"),
        CodeRow("3", "JOBAGENT_PUBLIC_DEMO_MODE=true", "public mode 要明确边界", "warn"),
        CodeRow("4", "JOBAGENT_DATABASE_URL -> Postgres run store", "durable state 是生产升级点", "warn"),
    ],
    "18_10x_scale_readiness": [
        CodeRow("1", "POST /runs currently executes the workflow inside the web request", "10x scale 先会碰到 request 生命周期边界", "warn"),
        CodeRow("2", "LocalRunStore / PostgresRunStore", "状态存储决定 restart 和多实例能力", "hot"),
        CodeRow("3", "JsonCheckpointStore -> durable database checkpointer", "checkpoint 从学习版升级到生产版", "warn"),
        CodeRow("4", "readiness = health + storage + eval + security + observability", "ready 不是单个 endpoint，而是一组证据", "hot"),
    ],
    "19_debugging": [
        CodeRow("1", "Symptom -> CLI reproduce -> checkpoint -> trace -> state -> node -> eval", "先收证据，再改实现", "hot"),
        CodeRow("2", "If state is wrong: inspect upstream node contract", "不要直接改 UI 或 prompt", "warn"),
        CodeRow("3", "If trace is missing: inspect tracer span boundary", "没有轨迹就很难 debug", "warn"),
        CodeRow("4", "If eval is missing: add failing case before fixing", "先锁住回归，再修 bug", "hot"),
    ],
    "20_upgrade_choices": [
        CodeRow("1", "Pain: local engine repeats durable execution logic -> consider LangGraph", "升级要由痛点触发", "hot"),
        CodeRow("2", "Pain: JSON state is ephemeral -> add Postgres", "状态不可丢时才上 durable store", "warn"),
        CodeRow("3", "Pain: traces need dashboards/evals -> add Langfuse/OpenTelemetry", "观察需求上来后再接平台", "hot"),
        CodeRow("4", "Pain: tools need cross-client reuse -> expose MCP server", "协议化是复用需求，不是装饰", "warn"),
    ],
    "21_capstone": [
        CodeRow("1", "Add SalaryAnalysis dataclass to models.py", "先扩展 state contract", "hot"),
        CodeRow("2", "Add salary_analysis node under jobagent/agents/", "再新增 bounded agent", "hot"),
        CodeRow("3", "Wire graph.add_node(\"salary_analysis\", analyze_salary)", "接入调度图", "hot"),
        CodeRow("4", "Add eval case before polishing output", "用 eval 锁住行为", "warn"),
        CodeRow("5", "Expose result in run.html", "最后才更新产品表面", "warn"),
    ],
}


def chapter_number(chapter) -> str:
    return chapter.slug.split("_", 1)[0]


def link_for(chapter) -> str:
    return f"{chapter.slug}.html"


def format_inline(text: str) -> str:
    text = escape(text)
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", text)


def link_path(path: str) -> str:
    target = REPO_ROOT / path
    if target.exists():
        return f'<a href="../../{escape(path)}"><code>{escape(path)}</code></a>'
    return f"<code>{escape(path)}</code>"


def sidebar(chapter) -> str:
    links = [
        '<a href="index.html">课程首页</a>',
        *[
            f'<a class="{"active" if other.slug == chapter.slug else ""}" href="{escape(link_for(other))}">{escape(chapter_number(other))} {escape(other.title.split("：", 1)[-1])}</a>'
            for other in CHAPTERS
        ],
    ]
    return f"""
<aside class="sidebar">
  <div class="brand">
    <div class="brand-mark">{escape(chapter_number(chapter))}</div>
    <h1>{escape(chapter.title.split("：", 1)[-1])}</h1>
    <p>{escape(chapter.subtitle)}</p>
  </div>
  <nav class="nav-block" aria-label="Course">
    {''.join(links)}
  </nav>
</aside>
"""


def inspector(chapter) -> str:
    checks = "".join(
        f'<label><input data-check="{escape(chapter.slug)}-{idx}" type="checkbox"> {format_inline(item)}</label>'
        for idx, item in enumerate(chapter.labs[:3], start=1)
    )
    sources = "".join(f'<li><a href="{escape(link.url)}">{escape(link.label)}</a></li>' for link in chapter.links)
    return f"""
<aside class="inspector">
  <div class="inspector-card">
    <h3>本章目标</h3>
    <p>{format_inline(chapter.subtitle)}</p>
  </div>
  <div class="inspector-card">
    <h3>阅读进度</h3>
    <div class="progress"><span data-progress></span></div>
  </div>
  <div class="inspector-card">
    <h3>Lab Checklist</h3>
    <div class="checklist">{checks}</div>
  </div>
  <div class="inspector-card">
    <h3>Industry Pulse</h3>
    <ul>{sources}</ul>
  </div>
</aside>
"""


def diagram(chapter) -> str:
    slug = chapter.slug
    if slug in {"01_graph_engine", "03_bounded_agents", "12_langgraph"}:
        return """
<div class="diagram" aria-label="Workflow orchestration diagram">
  <svg viewBox="0 0 980 310" role="img">
    <defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#007a83"/></marker></defs>
    <rect x="18" y="34" width="944" height="230" rx="22" fill="#fff" stroke="#d8e0e5"/>
    <text x="42" y="72" fill="#26323b" font-size="20" font-weight="800">JobAgent workflow map</text>
    <g fill="#e4f7f7" stroke="#007a83" stroke-width="2">
      <rect x="48" y="128" width="96" height="48" rx="12"/><rect x="178" y="128" width="110" height="48" rx="12"/>
      <rect x="322" y="128" width="142" height="48" rx="12"/><rect x="498" y="128" width="116" height="48" rx="12"/>
      <rect x="648" y="128" width="132" height="48" rx="12"/><rect x="814" y="128" width="106" height="48" rx="12"/>
    </g>
    <g fill="#26323b" font-size="14" font-weight="800" text-anchor="middle">
      <text x="96" y="158">ingest</text><text x="233" y="158">jd_extract</text><text x="393" y="158">company_research</text>
      <text x="556" y="158">fit_analysis</text><text x="714" y="158">resume_tailor</text><text x="867" y="158">tracker</text>
    </g>
    <g stroke="#007a83" stroke-width="2.4" marker-end="url(#arrow)">
      <line x1="144" y1="152" x2="170" y2="152"/><line x1="288" y1="152" x2="314" y2="152"/>
      <line x1="464" y1="152" x2="490" y2="152"/><line x1="614" y1="152" x2="640" y2="152"/><line x1="780" y1="152" x2="806" y2="152"/>
    </g>
    <rect x="640" y="208" width="148" height="36" rx="18" fill="#fff4df" stroke="#b36b00"/>
    <text x="714" y="231" text-anchor="middle" fill="#8a5200" font-size="13" font-weight="800">approval gate</text>
  </svg>
</div>
"""
    if slug in {"02_shared_state", "06_checkpoint_resume", "08_memory_story_bank"}:
        return """
<div class="diagram" aria-label="State evolution diagram">
  <svg viewBox="0 0 980 360" role="img">
    <rect x="18" y="24" width="944" height="294" rx="22" fill="#fff" stroke="#d8e0e5"/>
    <text x="44" y="64" fill="#26323b" font-size="20" font-weight="900">JobSearchState grows through the run</text>
    <g fill="#fbfcfd" stroke="#d8e0e5">
      <rect x="56" y="98" width="160" height="74" rx="14"/><rect x="250" y="98" width="160" height="74" rx="14"/>
      <rect x="444" y="98" width="160" height="74" rx="14"/><rect x="638" y="98" width="160" height="74" rx="14"/>
      <rect x="250" y="214" width="160" height="74" rx="14"/><rect x="444" y="214" width="160" height="74" rx="14"/><rect x="638" y="214" width="160" height="74" rx="14"/>
    </g>
    <g fill="#007a83" font-size="13" font-weight="900">
      <text x="76" y="126">raw_job_text</text><text x="270" y="126">normalized_jd</text><text x="464" y="126">company_brief</text><text x="658" y="126">fit_analysis</text>
      <text x="270" y="242">resume_proposal</text><text x="464" y="242">tracker_update</text><text x="658" y="242">interview_pack</text>
    </g>
    <g fill="#5d6975" font-size="12">
      <text x="76" y="148">user input</text><text x="270" y="148">extract</text><text x="464" y="148">research</text><text x="658" y="148">score</text>
      <text x="270" y="264">HITL</text><text x="464" y="264">approve</text><text x="658" y="264">prepare</text>
    </g>
    <rect x="806" y="104" width="112" height="178" rx="16" fill="#fff4df" stroke="#b36b00"/>
    <text x="862" y="134" text-anchor="middle" fill="#8a5200" font-size="13" font-weight="900">control</text>
    <text x="830" y="166" fill="#5d6975" font-size="12">budget</text><text x="830" y="190" fill="#5d6975" font-size="12">errors</text>
    <text x="830" y="214" fill="#5d6975" font-size="12">approved</text><text x="830" y="238" fill="#5d6975" font-size="12">stop_reason</text><text x="830" y="262" fill="#5d6975" font-size="12">pending_node</text>
  </svg>
</div>
"""
    return f"""
<div class="diagram" aria-label="Concept map">
  <svg viewBox="0 0 980 300" role="img">
    <rect x="18" y="24" width="944" height="226" rx="22" fill="#fff" stroke="#d8e0e5"/>
    <text x="44" y="64" fill="#26323b" font-size="20" font-weight="900">{escape(chapter.visual)}</text>
    <rect x="62" y="112" width="230" height="72" rx="16" fill="#e4f7f7" stroke="#007a83"/>
    <rect x="374" y="112" width="230" height="72" rx="16" fill="#fbfcfd" stroke="#d8e0e5"/>
    <rect x="686" y="112" width="230" height="72" rx="16" fill="#fff4df" stroke="#b36b00"/>
    <text x="177" y="142" text-anchor="middle" fill="#005b62" font-size="15" font-weight="900">Concept</text>
    <text x="489" y="142" text-anchor="middle" fill="#26323b" font-size="15" font-weight="900">Project Code</text>
    <text x="801" y="142" text-anchor="middle" fill="#8a5200" font-size="15" font-weight="900">Production Pattern</text>
    <text x="177" y="164" text-anchor="middle" fill="#5d6975" font-size="12">mental model</text>
    <text x="489" y="164" text-anchor="middle" fill="#5d6975" font-size="12">files and tests</text>
    <text x="801" y="164" text-anchor="middle" fill="#5d6975" font-size="12">industry reading</text>
  </svg>
</div>
"""


def annotated_code(slug: str) -> str:
    rows = CODE.get(slug, CODE["00_overview"])
    body = "".join(
        f'<div class="code-row {escape(row.kind)}"><span class="line">{escape(row.line)}</span><span class="src">{escape(row.src)}</span><span class="comment">{escape(row.comment)}</span></div>'
        for row in rows
    )
    return f'<div class="annotated-code" role="region" aria-label="Annotated code excerpt">{body}</div>'


def steps(items: list[str]) -> str:
    return '<div class="steps">' + "".join(f'<div class="step">{format_inline(item)}</div>' for item in items) + "</div>"


def source_links(chapter) -> str:
    return '<div class="source-links">' + "".join(
        f'<a class="source-link" href="{escape(link.url)}"><strong>{escape(link.label)}</strong><span>{escape(link.note)}</span></a>'
        for link in chapter.links
    ) + "</div>"


def deep_dive(slug: str) -> str:
    content = DEEP_DIVES.get(slug)
    if not content:
        return ""
    return f"""
  <section class="lesson-section deep-dive-section">
    <h2>扩展工程手册：把这一章做成可执行练习</h2>
    {content}
  </section>
"""


def file_panels(chapter) -> str:
    cards = []
    for anchor in chapter.anchors:
        cards.append(f'<div class="panel"><strong>{link_path(anchor)}</strong><p>阅读这一章时，把这个文件当作项目里的实物锚点。先看它在 workflow 中的位置，再看它和 state、trace、eval 的关系。</p></div>')
    return '<div class="split">' + "".join(cards[:2]) + "</div>" + ("<div class=\"split\">" + "".join(cards[2:4]) + "</div>" if len(cards) > 2 else "")


def article(chapter) -> str:
    concept_paras = "".join(f"<p>{format_inline(p)}</p>" for p in chapter.concept)
    industry_paras = "".join(f"<p>{format_inline(p)}</p>" for p in chapter.industry)
    choices = " ".join(chapter.choices)
    return f"""
<article class="lesson">
  <section class="lesson-section">
    <h2>这一章先解决什么问题</h2>
    <div class="article-prose">
      {concept_paras}
      <p>{format_inline(chapter.allegory)}</p>
    </div>
  </section>

  <section class="lesson-section">
    <h2>系统图：把概念放回项目现场</h2>
    <div class="article-prose">
      <p>这张图不是装饰，而是本章的定位器。你可以先看图，再打开对应的项目文件。这样读代码时不会迷路：每个文件都不是孤立片段，而是在 JobAgent 这个 agentic workflow 里承担一个明确位置。</p>
    </div>
    {diagram(chapter)}
  </section>

  <section class="lesson-section">
    <h2>代码走读：眼睛先放在高亮行</h2>
    <div class="article-prose">
      <p>下面的代码摘录不是为了让你背实现细节，而是训练阅读顺序。青色行表示主路径，琥珀色行表示控制、停止、安全或恢复边界。读 agent 系统时，先找这些边界，通常比先看 prompt 更有效。</p>
      <p>对应的项目文件在这里：{', '.join(link_path(anchor) for anchor in chapter.anchors[:4])}。</p>
    </div>
    {annotated_code(chapter.slug)}
    {file_panels(chapter)}
  </section>

  <section class="lesson-section" id="lab">
    <h2>动手实验：把知识点落到一次操作里</h2>
    <div class="article-prose">
      <p>这一章不只要求你“理解”。你应该至少跑一次命令、打开一次文件、观察一次 state 或 trace。JobAgent 的教学价值在于它是可运行项目，不是架构幻灯片。</p>
    </div>
    {steps(chapter.labs)}
  </section>

  {deep_dive(chapter.slug)}

  <section class="lesson-section">
    <h2>工程选择题：什么时候这样做，什么时候不要这样做</h2>
    <div class="article-prose">
      <p>{format_inline(choices)}</p>
      <p>这些问题比答案本身更重要。Multi-agent 工程的成熟度，不在于堆多少框架，而在于你能说清楚每个边界为什么存在、什么时候需要升级、升级会带来什么新复杂度。</p>
    </div>
  </section>

  <section class="lesson-section">
    <h2>行业脉搏：把本章放到 2026 AI infra 里看</h2>
    <div class="article-prose">
      {industry_paras}
      <p>读这些链接时，不要只记产品名。更重要的是把它们映射回本项目：哪些能力已经在 JobAgent 里有教学版，哪些能力属于未来的生产升级。</p>
    </div>
    {source_links(chapter)}
  </section>
</article>
"""


def render_chapter(chapter, idx: int) -> str:
    prev_ch = CHAPTERS[idx - 1] if idx else None
    next_ch = CHAPTERS[idx + 1] if idx + 1 < len(CHAPTERS) else None
    footer = '<nav class="footer-nav">'
    footer += f'<a class="button" href="{escape(link_for(prev_ch))}">上一章：{escape(prev_ch.title)}</a>' if prev_ch else '<a class="button" href="index.html">返回课程首页</a>'
    footer += f'<a class="button primary" href="{escape(link_for(next_ch))}">下一章：{escape(next_ch.title)}</a>' if next_ch else '<a class="button primary" href="index.html">回到课程首页</a>'
    footer += "</nav>"
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(chapter.title)} / JobAgent Agentic Engineering Course</title>
  <link rel="stylesheet" href="assets/course.css">
</head>
<body>
  <div class="shell">
    {sidebar(chapter)}
    <main class="reading">
      <section class="hero">
        <div class="kicker">{escape(chapter.part)} / Lesson {escape(chapter_number(chapter))}</div>
        <h1>{escape(chapter.title)}</h1>
        <p class="subtitle">{escape(chapter.subtitle)}</p>
        <div class="hero-actions">
          <a class="button primary" href="#lab">直接做实验</a>
          <a class="button" href="index.html">课程目录</a>
        </div>
      </section>
      {article(chapter)}
      {footer}
    </main>
    {inspector(chapter)}
  </div>
  <script src="assets/course.js"></script>
</body>
</html>
"""


def render_index() -> str:
    chapter_items = "".join(
        f'<a class="source-link" href="{escape(link_for(ch))}"><strong>{escape(ch.title)}</strong><span>{escape(ch.subtitle)}</span></a>'
        for ch in CHAPTERS
    )
    fake_chapter = CHAPTERS[0]
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>JobAgent Agentic Engineering Course</title>
  <link rel="stylesheet" href="assets/course.css">
</head>
<body>
  <div class="shell">
    {sidebar(fake_chapter).replace('class="active" href="00_overview.html"', 'href="00_overview.html"').replace('<a href="index.html">课程首页</a>', '<a class="active" href="index.html">课程首页</a>')}
    <main class="reading">
      <section class="hero">
        <div class="kicker">Source of Truth / Updated {UPDATED}</div>
        <h1>JobAgent Agentic Engineering Course</h1>
        <p class="subtitle">这是现在唯一维护的课程版本：22 章文章式教程，左侧课程地图，中间连续讲解，右侧 lab 和行业脉搏。正文里保留图解、代码高亮、项目文件链接和扩展阅读。</p>
        <div class="hero-actions">
          <a class="button primary" href="00_overview.html">开始第 0 章</a>
        </div>
      </section>
      <article class="lesson">
        <section class="lesson-section">
          <h2>阅读方式</h2>
          <div class="article-prose">
            <p>这套课程更像工程实验手册。每章先给你一个问题，再把问题放回 JobAgent 的真实文件、真实命令和真实调试路径里。</p>
            <p>配图只承担教学任务：定位系统位置、解释状态变化、展示调试路径。代码块里的重点行会高亮，右侧注释告诉你为什么要看这一行。</p>
          </div>
          <img class="concept-img" src="assets/reading-experience-concept.png" alt="JobAgent course reading experience concept">
        </section>
        <section class="lesson-section">
          <h2>全部章节</h2>
          <div class="source-links">{chapter_items}</div>
        </section>
      </article>
    </main>
    <aside class="inspector">
      <div class="inspector-card"><h3>课程状态</h3><p>22 章已生成。后续内容更新都从这套文章式课程生成。</p></div>
      <div class="inspector-card"><h3>阅读进度</h3><div class="progress"><span data-progress></span></div></div>
    </aside>
  </div>
  <script src="assets/course.js"></script>
</body>
</html>
"""


def write_html(path: Path, content: str) -> None:
    normalized = "\n".join(line.rstrip() for line in content.splitlines()) + "\n"
    path.write_text(normalized, encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_html(OUT_DIR / "index.html", render_index())
    for idx, chapter in enumerate(CHAPTERS):
        write_html(OUT_DIR / link_for(chapter), render_chapter(chapter, idx))


if __name__ == "__main__":
    main()
