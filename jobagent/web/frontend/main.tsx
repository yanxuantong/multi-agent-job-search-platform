import React from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

type Status = "COMPLETED" | "NEED_USER_APPROVAL" | "TOOL_ERROR" | string;

type RunSummary = {
  run_id: string;
  company: string;
  role: string;
  stop_reason: Status;
  fit_score: number | null;
  decision?: string | null;
  pending_node?: string | null;
  updated_at?: string;
};

type WorkflowStep = {
  name: string;
  label?: string;
  status?: string;
};

type AgentCard = {
  name: string;
  detail: string;
};

type HomeProps = {
  sampleText: string;
  runs: RunSummary[];
  stats: {
    total: number;
    awaiting: number;
    completed: number;
    agents: number;
  };
  workflowSteps: WorkflowStep[];
  agentCards: AgentCard[];
  publicDemoMode: boolean;
};

type FitAnalysis = {
  technical_match: number;
  domain_interest: number;
  logistics_match: number;
  narrative_strength: number;
  expected_roi: number;
  decision: string;
  evidence: string[];
  concerns: string[];
};

type ResumeProposal = {
  bullet_rewrites: string[];
  cover_letter_outline: string[];
  recruiter_note: string;
  approval_required: boolean;
};

type RetrievalChunk = {
  title: string;
  text: string;
  score: number;
  freshness_status: string;
};

type RetrievalContext = {
  query: string;
  selected_chunks: RetrievalChunk[];
  freshness_warnings: string[];
  candidate_count: number;
  returned_count: number;
  retriever: string;
};

type TrackerUpdate = {
  status: string;
  next_action: string;
  notes: string[];
};

type InterviewPack = {
  technical_questions: string[];
  behavioral_questions: string[];
  company_questions: string[];
  story_matches: string[];
};

type EvalSummary = {
  score: number;
  passed: boolean;
  checks: string[];
  failure_categories: string[];
};

type JobSearchState = {
  fit_analysis: FitAnalysis | null;
  resume_proposal: ResumeProposal | null;
  retrieval_contexts: RetrievalContext[];
  tracker_update: TrackerUpdate | null;
  interview_pack: InterviewPack | null;
  eval_summary: EvalSummary | null;
  messages: string[];
};

type TraceRow = {
  node: string;
  tool: string;
  status: string;
  elapsed_ms: number;
  input: string;
  output: string;
  action: string;
  rationale: string;
  confidence: number | null;
};

type RunProps = {
  state: JobSearchState;
  summary: RunSummary;
  scores: [string, number][];
  runSteps: WorkflowStep[];
  traceRows: TraceRow[];
  canApprove: boolean;
  publicDemoMode: boolean;
};

type RootPayload =
  | { page: "home"; props: HomeProps }
  | { page: "run"; props: RunProps };

function parsePayload(root: HTMLElement): RootPayload {
  const rawPage = root.dataset.page;
  const rawProps = root.dataset.props;
  if (!rawPage || !rawProps) {
    throw new Error("Scout mount data is missing.");
  }

  const props = JSON.parse(rawProps) as unknown;
  if (rawPage === "home") {
    return { page: "home", props: props as HomeProps };
  }
  if (rawPage === "run") {
    return { page: "run", props: props as RunProps };
  }
  throw new Error(`Unsupported Scout page: ${rawPage}`);
}

function statusClass(status: Status | undefined): string {
  if (status === "COMPLETED" || status === "done") {
    return "complete";
  }
  if (status === "NEED_USER_APPROVAL" || status === "active") {
    return "paused";
  }
  if (status === "idle") {
    return "idle";
  }
  return "error";
}

function formatScore(score: number | null | undefined): string {
  if (score === null || score === undefined) {
    return "pending";
  }
  return `${score}/25`;
}

function AppShell({
  children,
  publicDemoMode,
  detail = false
}: {
  children: React.ReactNode;
  publicDemoMode: boolean;
  detail?: boolean;
}) {
  return (
    <>
      <header className={`scout-shell ${detail ? "detail" : ""}`}>
        <nav className="topbar wrap" aria-label="Product navigation">
          <a className="brand" href="/" aria-label="JobAgent Scout home">
            <span className="brand-mark">JA</span>
            <span>
              <strong>JobAgent</strong>
              <small>Scout</small>
            </span>
          </a>
          <div className="nav-meta">
            {publicDemoMode ? <span className="pill info">public hosted mode</span> : null}
            <a className="button ghost" href={detail ? "/" : "https://github.com/yanxuantong/multi-agent-job-search-platform"}>
              {detail ? "New run" : "GitHub"}
            </a>
          </div>
        </nav>
      </header>
      {children}
    </>
  );
}

function Pill({ children, status }: { children: React.ReactNode; status?: Status }) {
  return <span className={`pill ${statusClass(status)}`}>{children}</span>;
}

function SectionHead({
  label,
  title,
  aside,
  compact = false
}: {
  label: string;
  title: string;
  aside?: React.ReactNode;
  compact?: boolean;
}) {
  return (
    <div className={`section-head ${compact ? "compact" : ""}`}>
      <div>
        <span className="kicker">{label}</span>
        <h2>{title}</h2>
      </div>
      {aside}
    </div>
  );
}

function WorkflowStrip({ steps, numbered = true }: { steps: WorkflowStep[]; numbered?: boolean }) {
  return (
    <section className="workflow-strip" aria-label="Agent workflow">
      {steps.map((step, index) => (
        <article className={`workflow-step ${statusClass(step.status)}`} key={`${step.name}-${index}`}>
          <span className="step-index">{numbered ? index + 1 : step.status ?? ""}</span>
          <strong>{step.name}</strong>
          <span>{step.label ?? step.status ?? "queued"}</span>
        </article>
      ))}
    </section>
  );
}

function HomePage({ props }: { props: HomeProps }) {
  const error = new URLSearchParams(window.location.search).get("error");
  return (
    <AppShell publicDemoMode={props.publicDemoMode}>
      <main className="wrap workspace">
        <section className="command-layout" aria-label="Scout command workspace">
          <div className="command-copy">
            <span className="kicker">React / TypeScript cockpit</span>
            <h1>Scout turns a job post into a reviewable agent workflow.</h1>
            <p className="lead">
              Paste a role, inspect bounded agents, pause at the resume proposal, and only continue after a human review.
            </p>
          </div>
          <div className="stat-grid" aria-label="Run summary">
            <StatCard value={props.stats.total} label="recent runs" />
            <StatCard value={props.stats.awaiting} label="awaiting approval" />
            <StatCard value={props.stats.completed} label="completed" />
            <StatCard value={props.stats.agents} label="bounded agents" />
          </div>
        </section>

        <WorkflowStrip steps={props.workflowSteps} />

        <div className="dashboard-grid">
          <section id="start-run" className="panel command-panel">
            <SectionHead
              label="Command center"
              title="Start a job-agent run"
              aside={<span className="pill complete">deterministic baseline</span>}
            />
            {error === "short_job_text" ? (
              <p className="notice error">Job description needs at least 20 characters.</p>
            ) : null}
            <form method="post" action="/runs">
              <label htmlFor="job_url">Job URL</label>
              <input id="job_url" name="job_url" type="url" placeholder="https://company.com/careers/job-id" />

              <label htmlFor="job_text">Job description</label>
              <textarea id="job_text" name="job_text" defaultValue={props.sampleText} />

              <div className="form-footer">
                <label className="check-row small" htmlFor="auto_approve">
                  <input id="auto_approve" name="auto_approve" type="checkbox" />
                  Auto-approve this run
                </label>
                <button type="submit">Run workflow</button>
              </div>
            </form>
          </section>

          <aside className="stack" aria-label="Scout side panels">
            <section className="panel">
              <SectionHead label="Agent roster" title="Bounded specialists" compact />
              <div className="agent-list">
                {props.agentCards.map((agent, index) => (
                  <article className="agent-card" key={agent.name}>
                    <span className="agent-index">{index + 1}</span>
                    <div>
                      <strong>{agent.name}</strong>
                      <p className="small muted">{agent.detail}</p>
                    </div>
                  </article>
                ))}
              </div>
            </section>

            <section className="panel">
              <SectionHead label="Product controls" title="Guardrails" compact />
              <div className="guardrail-list">
                <span className="pill complete">HITL approval</span>
                <span className="pill complete">input guardrails</span>
                <span className="pill complete">request IDs</span>
                <span className="pill complete">ops status</span>
              </div>
              <p className="small muted guardrail-note">
                Public runs are bounded by size limits, rate limits, secret detection, prompt-injection screening, and checkpointed resume behavior.
              </p>
            </section>

            <section className="panel">
              <SectionHead label="Activity" title="Recent runs" compact />
              <div className="run-list">
                {props.runs.length ? (
                  props.runs.map((run) => <RunItem run={run} key={run.run_id} />)
                ) : (
                  <p className="small muted">No runs yet.</p>
                )}
              </div>
            </section>
          </aside>
        </div>
      </main>
    </AppShell>
  );
}

function StatCard({ value, label }: { value: number; label: string }) {
  return (
    <article className="stat">
      <strong>{value}</strong>
      <span>{label}</span>
    </article>
  );
}

function RunItem({ run }: { run: RunSummary }) {
  return (
    <a className="run-item" href={`/runs/${run.run_id}`}>
      <span className="run-title">{run.company} - {run.role}</span>
      <span className="small muted mono">{run.run_id}</span>
      <span className="run-badges">
        <Pill status={run.stop_reason}>{run.stop_reason}</Pill>
        <span className="pill info">fit {formatScore(run.fit_score)}</span>
      </span>
    </a>
  );
}

function RunPage({ props }: { props: RunProps }) {
  const { state, summary } = props;
  return (
    <AppShell publicDemoMode={props.publicDemoMode} detail>
      <main className="wrap workspace">
        <section className="run-header" aria-label="Run detail summary">
          <div>
            <span className="kicker">Run detail</span>
            <h1>{summary.company} - {summary.role}</h1>
            <p className="lead">
              Review the agent output, approve resume-facing changes, and inspect every generated artifact before the workflow continues.
            </p>
            <div className="run-badges hero-badges">
              <Pill status={summary.stop_reason}>{summary.stop_reason}</Pill>
              <span className="pill info">fit {formatScore(summary.fit_score)}</span>
              <span className="pill info mono">{summary.run_id}</span>
            </div>
          </div>
          <ApprovalCard summary={summary} canApprove={props.canApprove} />
        </section>

        <WorkflowStrip steps={props.runSteps} />

        <div className="detail-grid">
          <div className="stack">
            {state.fit_analysis ? <FitAnalysisPanel analysis={state.fit_analysis} scores={props.scores} /> : null}
            {state.resume_proposal ? <ResumeProposalPanel proposal={state.resume_proposal} /> : null}
            {state.retrieval_contexts.length ? <RetrievalPanel contexts={state.retrieval_contexts} /> : null}
            {state.tracker_update ? <TrackerPanel tracker={state.tracker_update} /> : null}
            {state.interview_pack ? <InterviewPanel pack={state.interview_pack} /> : null}
            {state.eval_summary ? <EvalPanel evalSummary={state.eval_summary} /> : null}
          </div>
          <RunLog messages={state.messages} />
        </div>

        {props.traceRows.length ? <TracePanel rows={props.traceRows} /> : null}
      </main>
    </AppShell>
  );
}

function ApprovalCard({ summary, canApprove }: { summary: RunSummary; canApprove: boolean }) {
  return (
    <aside className="approval-card">
      <span className="kicker">Human gate</span>
      {canApprove ? (
        <>
          <h2>Approval required</h2>
          <p className="small muted">Resume proposal is paused before tracker and interview-prep side effects.</p>
          <form method="post" action={`/runs/${summary.run_id}/approve`}>
            <button type="submit">Approve and continue</button>
          </form>
        </>
      ) : (
        <>
          <h2>Workflow clear</h2>
          <p className="small muted">No pending approval step for this run.</p>
          <a className="button secondary" href="/">Start another run</a>
        </>
      )}
    </aside>
  );
}

function FitAnalysisPanel({ analysis, scores }: { analysis: FitAnalysis; scores: [string, number][] }) {
  return (
    <section className="panel">
      <SectionHead label="Decision support" title="Fit analysis" aside={<span className="pill info">{analysis.decision}</span>} />
      <div className="metric-grid">
        {scores.map(([label, value]) => (
          <article className="metric" key={label}>
            <strong>{value}</strong>
            <span className="small muted">{label}</span>
          </article>
        ))}
      </div>
      <TwoColumnList leftTitle="Evidence" leftItems={analysis.evidence} rightTitle="Concerns" rightItems={analysis.concerns} />
    </section>
  );
}

function ResumeProposalPanel({ proposal }: { proposal: ResumeProposal }) {
  return (
    <section className="panel">
      <SectionHead
        label="Application surface"
        title="Resume proposal"
        aside={proposal.approval_required ? <span className="pill paused">approval required</span> : null}
      />
      <div className="proposal">
        <div>
          <h3>Bullet rewrites</h3>
          <List items={proposal.bullet_rewrites} />
        </div>
        <div>
          <h3>Cover letter outline</h3>
          <List items={proposal.cover_letter_outline} />
          <h3>Recruiter note</h3>
          <p>{proposal.recruiter_note}</p>
        </div>
      </div>
    </section>
  );
}

function RetrievalPanel({ contexts }: { contexts: RetrievalContext[] }) {
  return (
    <section className="panel">
      <SectionHead label="RAG evidence" title="Retrieval context" compact />
      <div className="retrieval-stack">
        {contexts.map((context) => (
          <article className="retrieval-context" key={context.query}>
            <div className="retrieval-head">
              <div>
                <h3>{context.query}</h3>
                <p className="small muted">
                  {context.retriever} · {context.returned_count}/{context.candidate_count} chunks
                </p>
              </div>
              {context.freshness_warnings.length ? <span className="pill paused">refresh needed</span> : <span className="pill complete">fresh</span>}
            </div>
            <div className="retrieval-grid">
              {context.selected_chunks.slice(0, 3).map((chunk) => (
                <article className="retrieval-chunk" key={`${context.query}-${chunk.title}-${chunk.score}`}>
                  <div className="chunk-meta">
                    <strong>{chunk.title}</strong>
                    <span className="small muted">score {chunk.score} · {chunk.freshness_status}</span>
                  </div>
                  <p>{chunk.text}</p>
                </article>
              ))}
            </div>
            {context.freshness_warnings.length ? <List items={context.freshness_warnings} className="warning-list" /> : null}
          </article>
        ))}
      </div>
    </section>
  );
}

function TrackerPanel({ tracker }: { tracker: TrackerUpdate }) {
  return (
    <section className="panel">
      <SectionHead label="Application ops" title="Tracker update" compact />
      <p><strong>Status:</strong> {tracker.status}</p>
      <p><strong>Next action:</strong> {tracker.next_action}</p>
      <List items={tracker.notes} />
    </section>
  );
}

function InterviewPanel({ pack }: { pack: InterviewPack }) {
  return (
    <section className="panel">
      <SectionHead label="Prep packet" title="Interview prep" compact />
      <div className="proposal">
        <div>
          <h3>Technical</h3>
          <List items={pack.technical_questions} />
          <h3>Behavioral</h3>
          <List items={pack.behavioral_questions} />
        </div>
        <div>
          <h3>Company</h3>
          <List items={pack.company_questions} />
          <h3>Story matches</h3>
          <List items={pack.story_matches} />
        </div>
      </div>
    </section>
  );
}

function EvalPanel({ evalSummary }: { evalSummary: EvalSummary }) {
  return (
    <section className="panel">
      <SectionHead
        label="Quality gate"
        title="Run evaluation"
        aside={<span className={`pill ${evalSummary.passed ? "complete" : "paused"}`}>score {evalSummary.score}</span>}
      />
      <div className="proposal">
        <div>
          <h3>Checks</h3>
          <List items={evalSummary.checks} />
        </div>
        <div>
          <h3>Failure categories</h3>
          {evalSummary.failure_categories.length ? <List items={evalSummary.failure_categories} /> : <p className="small muted">No failed quality categories for this run.</p>}
        </div>
      </div>
    </section>
  );
}

function RunLog({ messages }: { messages: string[] }) {
  return (
    <aside className="panel run-log">
      <SectionHead label="Trace" title="Run messages" compact />
      <ol>
        {messages.map((message, index) => <li key={`${message}-${index}`}>{message}</li>)}
      </ol>
    </aside>
  );
}

function TracePanel({ rows }: { rows: TraceRow[] }) {
  return (
    <section className="panel trace-panel">
      <SectionHead label="Control plane" title="Orchestrator and tool audit" />
      <div className="trace-table" role="table" aria-label="Orchestrator and tool audit">
        <div className="trace-row trace-head" role="row">
          <span>Node</span>
          <span>Tool</span>
          <span>Decision</span>
          <span>Result</span>
          <span>Latency</span>
        </div>
        {rows.map((row, index) => (
          <div className="trace-row" role="row" key={`${row.node}-${row.tool}-${index}`}>
            <span><strong>{row.node}</strong><small>{row.input}</small></span>
            <span>{row.tool}</span>
            <span><strong>{row.action}</strong><small>{row.rationale}</small></span>
            <span><strong>{row.status}</strong><small>{row.output}</small></span>
            <span>{Math.round(row.elapsed_ms)} ms</span>
          </div>
        ))}
      </div>
    </section>
  );
}

function TwoColumnList({
  leftTitle,
  leftItems,
  rightTitle,
  rightItems
}: {
  leftTitle: string;
  leftItems: string[];
  rightTitle: string;
  rightItems: string[];
}) {
  return (
    <div className="proposal">
      <div>
        <h3>{leftTitle}</h3>
        <List items={leftItems} />
      </div>
      <div>
        <h3>{rightTitle}</h3>
        <List items={rightItems} />
      </div>
    </div>
  );
}

function List({ items, className = "" }: { items: string[]; className?: string }) {
  return (
    <ul className={className}>
      {items.map((item, index) => <li key={`${item}-${index}`}>{item}</li>)}
    </ul>
  );
}

const root = document.getElementById("scout-root");

if (root) {
  const payload = parsePayload(root);
  createRoot(root).render(payload.page === "home" ? <HomePage props={payload.props} /> : <RunPage props={payload.props} />);
}
