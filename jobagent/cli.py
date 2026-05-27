from __future__ import annotations

import argparse
import json
from pathlib import Path

from jobagent.evals.runner import run_eval_suite
from jobagent.graph.workflow import resume_job_workflow, run_job_workflow
from jobagent.memory import load_story_bank


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="jobagent")
    subcommands = parser.add_subparsers(dest="command", required=True)

    demo = subcommands.add_parser("demo", help="Run the reference multi-agent workflow.")
    demo.add_argument("--job-file", default="samples/job_description.txt")
    demo.add_argument("--story-bank", default="samples/story_bank.json")
    demo.add_argument("--job-url", default=None)
    demo.add_argument("--auto-approve", action="store_true", help="Continue past HITL and write tracker output.")

    resume = subcommands.add_parser("resume", help="Resume a checkpointed run after HITL approval.")
    resume.add_argument("run_id")
    resume.add_argument("--approve", action="store_true", help="Approve the pending artifact and continue.")
    resume.add_argument("--reject", action="store_true", help="Reject the pending artifact and keep the run paused.")

    eval_cmd = subcommands.add_parser("eval", help="Run offline eval cases.")
    eval_cmd.add_argument("--suite", default="samples/eval_suite.json")
    eval_cmd.add_argument("--story-bank", default="samples/story_bank.json")

    args = parser.parse_args(argv)
    if args.command == "demo":
        return _run_demo(args)
    if args.command == "resume":
        return _run_resume(args)
    if args.command == "eval":
        return _run_eval(args)
    return 1


def _run_demo(args: argparse.Namespace) -> int:
    job_text = Path(args.job_file).read_text(encoding="utf-8")
    stories = load_story_bank(args.story_bank)
    state = run_job_workflow(
        job_text,
        stories,
        job_url=args.job_url,
        approved=args.auto_approve,
    )
    print(json.dumps(_summary(state), indent=2, ensure_ascii=False))
    return 0


def _run_eval(args: argparse.Namespace) -> int:
    stories = load_story_bank(args.story_bank)
    result = run_eval_suite(args.suite, stories)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["failed"] == 0 else 2


def _run_resume(args: argparse.Namespace) -> int:
    if args.approve == args.reject:
        raise SystemExit("Choose exactly one: --approve or --reject")
    state = resume_job_workflow(args.run_id, approved=args.approve)
    print(json.dumps(_summary(state), indent=2, ensure_ascii=False))
    return 0


def _summary(state) -> dict:
    return {
        "run_id": state.run_id,
        "stop_reason": state.stop_reason.value if state.stop_reason else None,
        "company": state.company_name,
        "role": state.role_title,
        "fit_score": state.fit_analysis.total if state.fit_analysis else None,
        "decision": state.fit_analysis.decision if state.fit_analysis else None,
        "messages": state.messages,
        "resume_proposal": state.resume_proposal.__dict__ if state.resume_proposal else None,
        "tracker_update": state.tracker_update.__dict__ if state.tracker_update else None,
        "interview_pack": state.interview_pack.__dict__ if state.interview_pack else None,
        "trace_path": f".jobagent/runs/{state.run_id}/trace.jsonl",
        "checkpoint_path": f".jobagent/checkpoints/{state.run_id}.json",
        "pending_node": state.pending_node,
    }


if __name__ == "__main__":
    raise SystemExit(main())
