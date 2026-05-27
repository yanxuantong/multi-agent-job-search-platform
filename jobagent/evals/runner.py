from __future__ import annotations

import json
from pathlib import Path

from jobagent.graph.workflow import run_job_workflow


def run_eval_suite(path: str | Path, story_bank: list[dict]) -> dict:
    cases = json.loads(Path(path).read_text(encoding="utf-8"))
    results = []
    passed = 0
    for case in cases:
        state = run_job_workflow(
            case["job_text"],
            story_bank,
            approved=case.get("approved", False),
            run_id=f"eval-{case['id']}",
        )
        checks = _check_case(case, state)
        ok = all(check["passed"] for check in checks)
        passed += int(ok)
        results.append({"id": case["id"], "passed": ok, "checks": checks})
    return {
        "total": len(cases),
        "passed": passed,
        "failed": len(cases) - passed,
        "pass_rate": round(passed / len(cases), 3) if cases else 0,
        "results": results,
    }


def _check_case(case: dict, state) -> list[dict]:
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

