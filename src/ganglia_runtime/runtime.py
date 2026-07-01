from __future__ import annotations

from typing import Any

from .config import Settings
from .errors import OperatorNotFoundError, ValidationFailure
from .ollama_client import ChatResult, ChatUsage, OllamaClient
from .operator_loader import OperatorRegistry
from .prompt_compiler import compile_messages
from .renderers import render_answer
from .repair import compile_repair_messages
from .router import route_operator
from .trace_store import ReasoningTrace, TraceStore
from .validators import extract_json_object, validate_output


def _add_usage(left: ChatUsage | None, right: ChatUsage | None) -> ChatUsage | None:
    if left is None:
        return right
    if right is None:
        return left
    return ChatUsage(
        prompt_tokens=left.prompt_tokens + right.prompt_tokens,
        completion_tokens=left.completion_tokens + right.completion_tokens,
    )


class GangliaRuntime:
    def __init__(
        self,
        settings: Settings | None = None,
        llm_client: OllamaClient | None = None,
        registry: OperatorRegistry | None = None,
        trace_store: TraceStore | None = None,
    ) -> None:
        self.settings = settings or Settings.from_env()
        self.registry = registry or OperatorRegistry().load(self.settings.operators_path)
        self.llm_client = llm_client or OllamaClient(self.settings.ollama_url, self.settings.timeout_seconds)
        self.trace_store = trace_store or TraceStore(self.settings.trace_db_path)

    def operators(self) -> list[dict[str, Any]]:
        return [
            {
                "id": op.id,
                "name": op.name,
                "version": op.version,
                "category": op.category,
                "description": op.description,
                "routing": op.routing.model_dump(),
            }
            for op in self.registry.list()
        ]

    def reason(self, message: str, operator: str | None = "auto", model: str | None = None) -> dict[str, Any]:
        selected_id = route_operator(message, self.registry, operator)
        spec = self.registry.get(selected_id)
        if not spec:
            raise OperatorNotFoundError(f"Unknown operator: {selected_id}")

        model = model or self.settings.model
        messages = compile_messages(spec, message)
        trace = ReasoningTrace.new(operator=spec.id, model=model, user_message=message, compiled_messages=messages)

        chat_result = self.llm_client.chat(model=model, messages=messages, schema=spec.output_schema, temperature=self.settings.temperature)
        raw = chat_result.content if isinstance(chat_result, ChatResult) else chat_result
        usage = chat_result.usage if isinstance(chat_result, ChatResult) else None
        trace.raw_model_output = raw
        current: dict[str, Any] | str
        try:
            current = extract_json_object(raw)
        except Exception as exc:
            current = raw
            errors = [f"parse error: {exc}"]
        else:
            errors = validate_output(spec, current)

        attempts = 0
        while errors and attempts < self.settings.max_retries:
            attempts += 1
            trace.repair_attempts = attempts
            repair_messages = compile_repair_messages(spec, message, current, errors)
            repair_result = self.llm_client.chat(
                model=model,
                messages=repair_messages,
                schema=spec.output_schema,
                temperature=min(self.settings.temperature, 0.2),
            )
            raw_repair = repair_result.content if isinstance(repair_result, ChatResult) else repair_result
            if isinstance(repair_result, ChatResult):
                usage = _add_usage(usage, repair_result.usage)
            trace.raw_model_output = raw_repair
            try:
                current = extract_json_object(raw_repair)
                errors = validate_output(spec, current)
            except Exception as exc:
                current = raw_repair
                errors = [f"repair parse error: {exc}"]

        trace.validation_errors = errors
        if errors:
            self.trace_store.save(trace)
            raise ValidationFailure("; ".join(errors))

        assert isinstance(current, dict)
        final_answer = render_answer(spec, current)
        trace.validated_output = current
        trace.final_answer = final_answer
        self.trace_store.save(trace)
        return {
            "trace_id": trace.trace_id,
            "operator": spec.id,
            "model": model,
            "answer": final_answer,
            "controlled_reasoning": current,
            "repair_attempts": attempts,
            "usage": usage.to_openai_usage() if usage else None,
        }
