from __future__ import annotations

import time
import uuid
from typing import Any


TEXT_CONTENT_TYPES = {"text", "input_text"}
SUPPORTED_MESSAGE_ROLES = {"user", "system", "developer"}


def _text_from_content_parts(content: list[Any]) -> str:
    text_parts: list[str] = []
    for item in content:
        if not isinstance(item, dict):
            continue
        if item.get("type") not in TEXT_CONTENT_TYPES:
            continue
        text = item.get("text", "")
        if isinstance(text, str) and text:
            text_parts.append(text)
    return "\n".join(text_parts)


def messages_to_user_message(messages: list[dict[str, Any]]) -> str:
    parts: list[str] = []
    for message in messages:
        role = message.get("role", "user")
        if role not in SUPPORTED_MESSAGE_ROLES:
            continue

        content = message.get("content", "")
        if isinstance(content, list):
            content = _text_from_content_parts(content)
        if isinstance(content, str) and content:
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
