from __future__ import annotations

import json
import os

from jobagent.llm.provider import LLMRequest, LLMResponse, ProviderUsage, _rough_tokens


class AnthropicProvider:
    """Optional Claude adapter for the original Project 1 stack.

    The default workflow uses MockLLMProvider. This adapter is opt-in because
    Claude API calls require credentials and are normally usage-billed.
    """

    def __init__(self, model: str = "claude-sonnet-4-5", api_key: str | None = None) -> None:
        try:
            from anthropic import Anthropic
        except ImportError as exc:  # pragma: no cover - optional dependency.
            raise RuntimeError("Anthropic SDK is not installed. Run: python3 -m pip install -e '.[llm]'") from exc

        self.model = model
        self.client = Anthropic(api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"))

    def generate_structured(self, request: LLMRequest) -> LLMResponse:
        message = self.client.messages.create(
            model=self.model,
            max_tokens=1200,
            system=request.system,
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"{request.user}\n\n"
                        f"Return only valid JSON matching this schema description:\n{request.response_schema}"
                    ),
                }
            ],
        )
        text = "".join(
            block.text for block in message.content
            if getattr(block, "type", None) == "text" and hasattr(block, "text")
        )
        usage = getattr(message, "usage", None)
        return LLMResponse(
            content=json.loads(text),
            model=self.model,
            usage=ProviderUsage(
                input_tokens=getattr(usage, "input_tokens", _rough_tokens(request.system + request.user)),
                output_tokens=getattr(usage, "output_tokens", _rough_tokens(text)),
            ),
        )
