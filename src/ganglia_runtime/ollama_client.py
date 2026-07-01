from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx

from .errors import LLMClientError


@dataclass(frozen=True)
class ChatUsage:
    prompt_tokens: int
    completion_tokens: int

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens

    def to_openai_usage(self) -> dict[str, int]:
        return {
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
        }


@dataclass(frozen=True)
class ChatResult:
    content: str
    usage: ChatUsage | None = None


def _usage_from_ollama_response(data: dict[str, Any]) -> ChatUsage | None:
    prompt_tokens = data.get("prompt_eval_count")
    completion_tokens = data.get("eval_count")
    if isinstance(prompt_tokens, int) and isinstance(completion_tokens, int):
        return ChatUsage(prompt_tokens=prompt_tokens, completion_tokens=completion_tokens)
    return None


class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434", timeout_seconds: int = 120) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def chat(self, *, model: str, messages: list[dict[str, str]], schema: dict, temperature: float = 0.2) -> ChatResult:
        payload = {
            "model": model,
            "messages": messages,
            "format": schema,
            "stream": False,
            "options": {"temperature": temperature},
        }
        try:
            response = httpx.post(f"{self.base_url}/api/chat", json=payload, timeout=self.timeout_seconds)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise LLMClientError(f"Ollama request failed: {exc}") from exc
        data = response.json()
        try:
            content = data["message"]["content"]
        except KeyError as exc:
            raise LLMClientError(f"Unexpected Ollama response: {data}") from exc
        return ChatResult(content=content, usage=_usage_from_ollama_response(data))
