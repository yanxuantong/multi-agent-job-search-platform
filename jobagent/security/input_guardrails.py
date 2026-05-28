from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class GuardrailFinding:
    code: str
    message: str
    severity: str = "block"


SECRET_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("private_key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----", re.IGNORECASE)),
    ("openai_key", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")),
    ("anthropic_key", re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}\b")),
    ("github_token", re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b")),
    ("aws_access_key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("generic_api_key", re.compile(r"\b(api[_-]?key|secret|password)\s*[:=]\s*['\"]?[^'\"\s]{12,}", re.IGNORECASE)),
)

PROMPT_INJECTION_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("ignore_instructions", re.compile(r"\bignore (all )?(previous|prior|above) instructions\b", re.IGNORECASE)),
    ("reveal_prompt", re.compile(r"\b(reveal|print|show|dump).{0,30}(system|developer) (prompt|message|instructions)\b", re.IGNORECASE)),
    ("exfiltrate", re.compile(r"\b(exfiltrate|send|post).{0,40}(secrets?|tokens?|credentials?)\b", re.IGNORECASE)),
    ("tool_override", re.compile(r"\b(call|use|invoke).{0,40}(unauthorized|hidden|internal) tool\b", re.IGNORECASE)),
)


def inspect_public_submission(job_text: str, job_url: str | None = None) -> list[GuardrailFinding]:
    text = "\n".join(part for part in (job_url or "", job_text) if part)
    findings: list[GuardrailFinding] = []

    for code, pattern in SECRET_PATTERNS:
        if pattern.search(text):
            findings.append(
                GuardrailFinding(
                    code=f"secret_{code}",
                    message="Public submissions must not include secrets, credentials, or private keys.",
                )
            )
            break

    for code, pattern in PROMPT_INJECTION_PATTERNS:
        if pattern.search(text):
            findings.append(
                GuardrailFinding(
                    code=f"prompt_injection_{code}",
                    message="This public workflow rejects instruction-override or credential-exfiltration payloads.",
                )
            )
            break

    return findings
