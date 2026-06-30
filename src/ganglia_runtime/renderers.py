from __future__ import annotations

import json
from typing import Any

from jinja2 import Template

from .operator_spec import OperatorSpec


def render_answer(spec: OperatorSpec, output: dict[str, Any]) -> str:
    if spec.renderer.mode == "json":
        return json.dumps(output, ensure_ascii=False, indent=2)
    return Template(spec.renderer.template).render(**output, output=output).strip()
