from __future__ import annotations

import json
from pathlib import Path

from jobagent.agents.jd_extract import extract_jd
from jobagent.graph.workflow import run_job_workflow
from jobagent.models import JobSearchState


def run_eval_suite(path: str | Path, story_bank: list[dict]) -> dict:
    cases = json.loads(Path(path).read_text(encoding="utf-8"))
    results = []
    passed = 0
    by_type: dict[str, dict[str, int]] = {}
    for case in cases:
        eval_type = case.get("eval_type", "trajectory")
        if eval_type == "single_turn_jd_extract":
            state = JobSearchState(
                run_id=f"eval-{case['id']}",
                user_goal="eval_jd_extract",
                raw_job_text=case["job_text"],
                story_bank=story_bank,
            )
            extract_jd(state)
            checks = _check_extraction_case(case, state)
        else:
            state = run_job_workflow(
                case["job_text"],
                story_bank,
                approved=case.get("approved", False),
                run_id=f"eval-{case['id']}",
            )
            checks = _check_trajectory_case(case, state)
        ok = all(check["passed"] for check in checks)
        failure_categories = _failure_categories(checks)
        passed += int(ok)
        type_counts = by_type.setdefault(eval_type, {"total": 0, "passed": 0, "failed": 0})
        type_counts["total"] += 1
        type_counts["passed"] += int(ok)
        type_counts["failed"] += int(not ok)
        results.append(
            {
                "id": case["id"],
                "eval_type": eval_type,
                "passed": ok,
                "checks": checks,
                "failure_categories": failure_categories,
            }
        )
    return {
        "total": len(cases),
        "passed": passed,
        "failed": len(cases) - passed,
        "pass_rate": round(passed / len(cases), 3) if cases else 0,
        "by_type": {
            eval_type: {
                **counts,
                "pass_rate": round(counts["passed"] / counts["total"], 3) if counts["total"] else 0,
            }
            for eval_type, counts in by_type.items()
        },
        "failure_categories": _suite_failure_categories(results),
        "results": results,
    }


def _check_extraction_case(case: dict, state) -> list[dict]:
    checks = []
    if expected_company := case.get("expected_company"):
        checks.append(
            {
                "name": "company",
                "passed": state.company_name == expected_company,
                "actual": state.company_name,
                "expected": expected_company,
            }
        )
    for skill in case.get("expected_required_skills", []):
        actual = state.normalized_jd.required_skills if state.normalized_jd else []
        checks.append(
            {
                "name": f"required_skill:{skill}",
                "passed": skill in actual,
                "actual": actual,
                "expected": skill,
            }
        )
    return checks


def _failure_categories(checks: list[dict]) -> list[str]:
    categories = []
    for check in checks:
        if check["passed"]:
            continue
        name = check["name"]
        if name.startswith("required_skill"):
            categories.append("skill_extraction")
        elif name in {"company", "stop_reason", "min_fit_score"}:
            categories.append(name)
        else:
            categories.append("unknown")
    return sorted(set(categories))


def _suite_failure_categories(results: list[dict]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for result in results:
        for category in result.get("failure_categories", []):
            counts[category] = counts.get(category, 0) + 1
    return counts


def _check_trajectory_case(case: dict, state) -> list[dict]:
    checks = _check_extraction_case(case, state)
    if stop_reason := case.get("expected_stop_reason"):
        actual_stop = state.stop_reason.value if state.stop_reason else None
        checks.append(
            {
                "name": "stop_reason",
                "passed": actual_stop == stop_reason,
                "actual": actual_stop,
                "expected": stop_reason,
            }
        )
    if min_fit := case.get("min_fit_score"):
        actual_fit = state.fit_analysis.total if state.fit_analysis else 0
        checks.append(
            {
                "name": "min_fit_score",
                "passed": actual_fit >= min_fit,
                "actual": actual_fit,
                "expected": min_fit,
            }
        )
    return checks
