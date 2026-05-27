from __future__ import annotations

import json
import os

from jobagent.llm.provider import LLMRequest, LLMResponse, ProviderUsage, _rough_tokens


class OpenAIProvider:
    """Optional OpenAI adapter for structured agent nodes.

    Keep this off by default unless a run has an explicit API key and cost
    budget. Agent loops can get expensive faster than normal chat usage.
    """

    def __init__(self, model: str = "gpt-5.4-mini", api_key: str | None = None) -> None:
        try:
            from openai import OpenAI
        except ImportError as exc:  # pragma: no cover - optional dependency.
            raise RuntimeError("OpenAI SDK is not installed. Run: python3 -m pip install -e '.[llm]'") from exc

        self.model = model
        self.client = OpenAI(api_key=api_key or os.environ.get("OPENAI_API_KEY"))

    def generate_structured(self, request: LLMRequest) -> LLMResponse:
        response = self.client.responses.create(
            model=self.model,
            input=[
                {"role": "system", "content": request.system},
                {
                    "role": "user",
                    "content": (
                        f"{request.user}\n\n"
                        f"Return only valid JSON matching this schema description:\n{request.response_schema}"
                    ),
                },
            ],
        )
        text = response.output_text
        usage = getattr(response, "usage", None)
        return LLMResponse(
            content=json.loads(text),
            model=self.model,
            usage=ProviderUsage(
                input_tokens=getattr(usage, "input_tokens", _rough_tokens(request.system + request.user)),
                output_tokens=getattr(usage, "output_tokens", _rough_tokens(text)),
            ),
        )
