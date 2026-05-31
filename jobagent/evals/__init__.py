"""Evaluation helpers for offline suites and per-run quality summaries."""

__all__ = ["run_eval_suite", "summarize_run_quality"]


def __getattr__(name: str):
    if name == "run_eval_suite":
        from jobagent.evals.runner import run_eval_suite

        return run_eval_suite
    if name == "summarize_run_quality":
        from jobagent.evals.run_quality import summarize_run_quality

        return summarize_run_quality
    raise AttributeError(name)
