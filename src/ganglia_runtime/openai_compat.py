from __future__ import annotations

import time
import uuid
from typing import Any


def messages_to_user_message(messages: list[dict[str, Any]]) -> str:
    parts: list[str] = []
    for message in messages:
        role = message.get("role", "user")
        content = message.get("content", "")
        if isinstance(content, list):
            text_parts = []
            for item in content:
                if isinstance(item, dict) and item.get("type") in {"text", "input_text"}:
                    text_parts.append(str(item.get("text", "")))
            content = "\n".join(text_parts)
        if role in {"user", "system", "developer"} and content:
            parts.append(f"[{role}] {content}")
    return "\n".join(parts).strip()


def model_to_operator(model: str | None) -> str:
    if not model:
        return "auto"
    if model.startswith("ganglia/"):
        return model.split("/", 1)[1] or "auto"
    return "auto"


def completion_response(*, model: str, content: str, trace_id: str | None = None) -> dict[str, Any]:
    return {
        "id": f"chatcmpl-ganglia-{uuid.uuid4().hex[:24]}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": content},
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
        "ganglia": {"trace_id": trace_id},
    }


def models_response(operator_ids: list[str]) -> dict[str, Any]:
    now = int(time.time())
    data = [{"id": "ganglia/auto", "object": "model", "created": now, "owned_by": "ganglia"}]
    data.extend({"id": f"ganglia/{op_id}", "object": "model", "created": now, "owned_by": "ganglia"} for op_id in operator_ids)
    return {"object": "list", "data": data}
