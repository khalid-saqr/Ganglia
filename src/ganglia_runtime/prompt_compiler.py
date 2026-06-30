from __future__ import annotations

from jinja2 import Template

from .operator_spec import OperatorSpec


def compile_messages(spec: OperatorSpec, user_message: str, context: dict | None = None) -> list[dict[str, str]]:
    context = context or {}
    rules = "\n".join(f"{idx + 1}. {rule}" for idx, rule in enumerate(spec.operator_rules))
    prompt = Template(spec.prompt_template).render(
        user_message=user_message,
        operator=spec,
        rules=rules,
        context=context,
    )
    system = f"""{spec.system_prompt.strip()}

Operator ID: {spec.id}
Operator Name: {spec.name}
Operator Category: {spec.category}

Operator Rules:
{rules}

Return only JSON that matches the required schema. Do not wrap JSON in markdown fences."""
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": prompt},
    ]
