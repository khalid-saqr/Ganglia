from __future__ import annotations

import json

from .operator_spec import OperatorSpec


def compile_repair_messages(
    spec: OperatorSpec,
    user_message: str,
    invalid_output: dict | str,
    validation_errors: list[str],
) -> list[dict[str, str]]:
    invalid_text = invalid_output if isinstance(invalid_output, str) else json.dumps(invalid_output, ensure_ascii=False, indent=2)
    return [
        {
            "role": "system",
            "content": f"""You are Ganglia's repair stage for a failed language-game output.

Operator: {spec.id} / {spec.name}

{spec.repair_prompt}

Return only valid JSON matching the operator schema. Do not include markdown fences or commentary.""",
        },
        {
            "role": "user",
            "content": f"""Original user message:
{user_message}

Invalid output:
{invalid_text}

Validation errors:
{json.dumps(validation_errors, ensure_ascii=False, indent=2)}

Repair the output while preserving the original task and operator rules.""",
        },
    ]
