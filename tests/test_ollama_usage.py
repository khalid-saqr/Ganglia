from ganglia_runtime.ollama_client import OllamaClient


class FakeResponse:
    def __init__(self, data):
        self.data = data

    def raise_for_status(self):
        return None

    def json(self):
        return self.data


def test_ollama_chat_returns_usage_counts(monkeypatch):
    def fake_post(*args, **kwargs):
        return FakeResponse({"message": {"content": "{}"}, "prompt_eval_count": 5, "eval_count": 3})

    monkeypatch.setattr("ganglia_runtime.ollama_client.httpx.post", fake_post)

    result = OllamaClient().chat(model="m", messages=[], schema={})

    assert result.content == "{}"
    assert result.usage is not None
    assert result.usage.to_openai_usage() == {"prompt_tokens": 5, "completion_tokens": 3, "total_tokens": 8}


def test_ollama_chat_leaves_usage_empty_without_exact_counts(monkeypatch):
    def fake_post(*args, **kwargs):
        return FakeResponse({"message": {"content": "{}"}})

    monkeypatch.setattr("ganglia_runtime.ollama_client.httpx.post", fake_post)

    result = OllamaClient().chat(model="m", messages=[], schema={})

    assert result.content == "{}"
    assert result.usage is None
