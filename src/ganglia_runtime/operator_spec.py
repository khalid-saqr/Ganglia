from __future__ import annotations

from typing import Any, Literal
from pydantic import BaseModel, Field, field_validator

OperatorCategory = Literal["engine", "mapper", "modifier", "modifier_to_engine", "chain"]


class RoutingSpec(BaseModel):
    intent_hints: list[str] = Field(default_factory=list)
    default_when_user_mentions: list[str] = Field(default_factory=list)
    priority: int = 0


class SemanticValidationSpec(BaseModel):
    must_include_fields: list[str] = Field(default_factory=list)
    min_items: dict[str, int] = Field(default_factory=dict)
    min_string_length: dict[str, int] = Field(default_factory=dict)
    coordinate_fields_must_be_between: list[float] | None = None
    must_not_include_forbidden_terms_in: list[str] = Field(default_factory=list)
    require_markdown_table_in: str | None = None


class RendererSpec(BaseModel):
    mode: Literal["markdown", "json"] = "markdown"
    template: str = "{{ final_answer }}"


class OperatorSpec(BaseModel):
    id: str
    name: str
    version: str = "1.0.0"
    category: OperatorCategory
    description: str = ""
    routing: RoutingSpec = Field(default_factory=RoutingSpec)
    chain: list[str] = Field(default_factory=list)
    system_prompt: str
    operator_rules: list[str] = Field(default_factory=list)
    prompt_template: str
    output_schema: dict[str, Any]
    semantic_validation: SemanticValidationSpec = Field(default_factory=SemanticValidationSpec)
    repair_prompt: str
    renderer: RendererSpec = Field(default_factory=RendererSpec)

    @field_validator("id")
    @classmethod
    def id_must_be_slug(cls, value: str) -> str:
        allowed = set("abcdefghijklmnopqrstuvwxyz0123456789_-/")
        if not value or any(ch not in allowed for ch in value):
            raise ValueError("operator id must be lowercase slug using letters, numbers, _, -, /")
        return value

    @field_validator("output_schema")
    @classmethod
    def schema_must_be_object(cls, value: dict[str, Any]) -> dict[str, Any]:
        if value.get("type") != "object":
            raise ValueError("output_schema must be a JSON Schema object")
        return value


def operator_spec_schema() -> dict[str, Any]:
    return OperatorSpec.model_json_schema()
