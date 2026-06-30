from __future__ import annotations

import json
import re
from importlib import resources
from pathlib import Path
from typing import Iterable

import yaml
from pydantic import ValidationError

from .errors import OperatorLoadError
from .operator_spec import OperatorSpec


_JSON_BLOCK_RE = re.compile(r"```json\s*(.*?)\s*```", re.DOTALL | re.IGNORECASE)


def load_operator_file(path: Path) -> OperatorSpec:
    suffixes = "".join(path.suffixes)
    try:
        if suffixes.endswith(".lg.json") or path.suffix == ".json":
            data = json.loads(path.read_text(encoding="utf-8"))
        elif suffixes.endswith(".lg.md") or path.suffix == ".md":
            data = _parse_markdown_operator(path.read_text(encoding="utf-8"))
        else:
            raise OperatorLoadError(f"Unsupported operator file type: {path}")
        return OperatorSpec.model_validate(data)
    except (json.JSONDecodeError, OSError, ValidationError, yaml.YAMLError) as exc:
        raise OperatorLoadError(f"Could not load operator {path}: {exc}") from exc


def _parse_markdown_operator(text: str) -> dict:
    """Parse a human-friendly .lg.md operator.

    Supported format:
    - YAML front matter between --- lines containing metadata, routing, semantic_validation, renderer.
    - Headings named System Prompt, Operator Rules, Prompt Template, Output Schema, Repair Prompt.
    - Output Schema can be either plain JSON under the heading or the first fenced json block.
    """
    frontmatter: dict = {}
    body = text
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            frontmatter = yaml.safe_load(parts[1]) or {}
            body = parts[2]

    sections = _split_markdown_sections(body)
    schema_text = sections.get("output schema", "")
    match = _JSON_BLOCK_RE.search(schema_text) or _JSON_BLOCK_RE.search(body)
    if match:
        output_schema = json.loads(match.group(1))
    elif schema_text.strip():
        output_schema = json.loads(schema_text.strip())
    else:
        raise OperatorLoadError(".lg.md operator missing Output Schema section")

    rules_text = sections.get("operator rules", "")
    rules = [line.strip(" -\t") for line in rules_text.splitlines() if line.strip().lstrip().startswith(("-", "1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9."))]

    data = dict(frontmatter)
    data.setdefault("system_prompt", sections.get("system prompt", "").strip())
    data.setdefault("operator_rules", rules)
    data.setdefault("prompt_template", sections.get("prompt template", "").strip())
    data.setdefault("output_schema", output_schema)
    data.setdefault("repair_prompt", sections.get("repair prompt", "").strip())
    if not data.get("renderer"):
        data["renderer"] = {"mode": "markdown", "template": sections.get("renderer", "{{ final_answer }}").strip() or "{{ final_answer }}"}
    return data


def _split_markdown_sections(body: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for line in body.splitlines():
        if line.startswith("#"):
            title = line.lstrip("#").strip().lower()
            current = title
            sections.setdefault(current, [])
        elif current:
            sections[current].append(line)
    return {k: "\n".join(v).strip() for k, v in sections.items()}


def iter_operator_paths(directory: Path | None) -> Iterable[Path]:
    if not directory or not directory.exists():
        return []
    return sorted([p for p in directory.rglob("*") if p.suffix in {".json", ".md"} and (".lg." in p.name or p.name.endswith((".json", ".md")))])


def load_builtin_operators() -> list[OperatorSpec]:
    specs: list[OperatorSpec] = []
    package_files = resources.files("ganglia_runtime").joinpath("operators")
    for file in package_files.iterdir():
        if file.name.endswith(".lg.json"):
            data = json.loads(file.read_text(encoding="utf-8"))
            specs.append(OperatorSpec.model_validate(data))
    return specs


class OperatorRegistry:
    def __init__(self) -> None:
        self.operators: dict[str, OperatorSpec] = {}
        self.invalid: dict[str, str] = {}

    def register(self, spec: OperatorSpec, *, overwrite: bool = True) -> None:
        if spec.id in self.operators and not overwrite:
            return
        self.operators[spec.id] = spec

    def load(self, user_dir: Path | None = None) -> "OperatorRegistry":
        for spec in load_builtin_operators():
            self.register(spec)
        for path in iter_operator_paths(user_dir):
            try:
                self.register(load_operator_file(path))
            except OperatorLoadError as exc:
                self.invalid[str(path)] = str(exc)
        return self

    def get(self, operator_id: str) -> OperatorSpec | None:
        return self.operators.get(operator_id)

    def list(self) -> list[OperatorSpec]:
        return sorted(self.operators.values(), key=lambda op: (op.routing.priority, op.id), reverse=True)
