from __future__ import annotations

import json
from typing import Any

from jsonschema import Draft202012Validator

from .operator_spec import OperatorSpec


def extract_json_object(text: str) -> dict[str, Any]:
    """Parse JSON from model output, tolerating common markdown fences."""
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`").strip()
        if text.lower().startswith("json"):
            text = text[4:].strip()
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise
        parsed = json.loads(text[start : end + 1])
    if not isinstance(parsed, dict):
        raise ValueError("model output must be a JSON object")
    return parsed


def validate_schema(spec: OperatorSpec, obj: dict[str, Any]) -> list[str]:
    validator = Draft202012Validator(spec.output_schema)
    errors = sorted(validator.iter_errors(obj), key=lambda err: list(err.path))
    return [f"schema error at {list(err.path) or '$'}: {err.message}" for err in errors]


def validate_semantic(spec: OperatorSpec, obj: dict[str, Any]) -> list[str]:
    rules = spec.semantic_validation
    errors: list[str] = []

    for field in rules.must_include_fields:
        if _get_path(obj, field) in (None, "", [], {}):
            errors.append(f"semantic error: required non-empty field '{field}' missing")

    for field, minimum in rules.min_items.items():
        value = _get_path(obj, field)
        if not isinstance(value, list) or len(value) < minimum:
            errors.append(f"semantic error: field '{field}' must contain at least {minimum} items")

    for field, minimum in rules.min_string_length.items():
        value = _get_path(obj, field)
        if not isinstance(value, str) or len(value.strip()) < minimum:
            errors.append(f"semantic error: field '{field}' must be a string with at least {minimum} characters")

    if rules.coordinate_fields_must_be_between:
        lo, hi = rules.coordinate_fields_must_be_between
        for path, value in _walk(obj):
            if path.endswith(("x_coordinate", "y_coordinate", ".x", ".y")):
                if not isinstance(value, (int, float)) or not (lo <= float(value) <= hi):
                    errors.append(f"semantic error: coordinate '{path}' must be between {lo} and {hi}")

    forbidden_terms = obj.get("forbidden_terms") if isinstance(obj.get("forbidden_terms"), list) else []
    if forbidden_terms and rules.must_not_include_forbidden_terms_in:
        lowered_terms = [str(term).lower() for term in forbidden_terms]
        for field in rules.must_not_include_forbidden_terms_in:
            value = _get_path(obj, field)
            text = json.dumps(value, ensure_ascii=False).lower()
            for term in lowered_terms:
                if term and term in text:
                    errors.append(f"semantic error: forbidden term '{term}' appears in field '{field}'")

    if rules.require_markdown_table_in:
        value = _get_path(obj, rules.require_markdown_table_in)
        if not isinstance(value, str) or "|" not in value:
            errors.append(f"semantic error: field '{rules.require_markdown_table_in}' must contain a markdown table")

    return errors


def validate_output(spec: OperatorSpec, obj: dict[str, Any]) -> list[str]:
    return validate_schema(spec, obj) + validate_semantic(spec, obj)


def _get_path(obj: dict[str, Any], path: str) -> Any:
    cur: Any = obj
    for part in path.split("."):
        if isinstance(cur, dict):
            cur = cur.get(part)
        else:
            return None
    return cur


def _walk(value: Any, prefix: str = ""):
    if isinstance(value, dict):
        for k, v in value.items():
            path = f"{prefix}.{k}" if prefix else k
            yield from _walk(v, path)
    elif isinstance(value, list):
        for idx, item in enumerate(value):
            path = f"{prefix}[{idx}]"
            yield from _walk(item, path)
    else:
        yield prefix, value
