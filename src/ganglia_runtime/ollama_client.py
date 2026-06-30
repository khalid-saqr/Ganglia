from __future__ import annotations

import httpx

from .errors import LLMClientError


class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434", timeout_seconds: int = 120) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def chat(self, *, model: str, messages: list[dict[str, str]], schema: dict, temperature: float = 0.2) -> str:
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
            return data["message"]["content"]
        except KeyError as exc:
            raise LLMClientError(f"Unexpected Ollama response: {data}") from exc
