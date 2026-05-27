from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass
class LLMRequest:
    prompt_name: str
    prompt_version: str
    system: str
    user: str
    response_schema: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ProviderUsage:
    input_tokens: int
    output_tokens: int
    estimated_cost_usd: float = 0.0


@dataclass
class LLMResponse:
    content: dict[str, Any]
    model: str
    usage: ProviderUsage


class LLMProvider(Protocol):
    def generate_structured(self, request: LLMRequest) -> LLMResponse:
        ...


class MockLLMProvider:
    """Deterministic provider for tests and demos.

    Real providers should implement the same method using Anthropic/OpenAI
    structured outputs or tool calls.
    """

    model = "mock-local-structured-v1"

    def generate_structured(self, request: LLMRequest) -> LLMResponse:
        content = {
            "prompt_name": request.prompt_name,
            "prompt_version": request.prompt_version,
            "summary": "Mock provider response; replace this with a real SDK adapter.",
            "metadata": request.metadata,
        }
        return LLMResponse(
            content=content,
            model=self.model,
            usage=ProviderUsage(
                input_tokens=_rough_tokens(request.system + request.user),
                output_tokens=_rough_tokens(json.dumps(content)),
            ),
        )


def _rough_tokens(text: str) -> int:
    return max(1, len(text.split()))

