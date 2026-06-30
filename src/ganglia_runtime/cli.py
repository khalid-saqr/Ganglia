from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import uvicorn

from .config import Settings
from .operator_loader import OperatorRegistry, load_operator_file
from .operator_spec import operator_spec_schema
from .runtime import GangliaRuntime


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ganglia", description="Ganglia v1.0.0 reasoning-control runtime")
    sub = parser.add_subparsers(dest="command", required=True)

    serve = sub.add_parser("serve", help="Start the Ganglia API server")
    serve.add_argument("--host", default=None)
    serve.add_argument("--port", type=int, default=None)

    sub.add_parser("operators", help="List loaded operators")

    test = sub.add_parser("test", help="Run a one-off reasoning request")
    test.add_argument("message")
    test.add_argument("--operator", default="auto")
    test.add_argument("--model", default=None)

    validate = sub.add_parser("validate-operator", help="Validate an .lg.json or .lg.md operator file")
    validate.add_argument("path")

    init = sub.add_parser("init-operator", help="Create a starter .lg.json operator template")
    init.add_argument("operator_id")
    init.add_argument("--output", default=None)

    trace = sub.add_parser("trace", help="Trace commands")
    trace_sub = trace.add_subparsers(dest="trace_command", required=True)
    trace_sub.add_parser("list")
    show = trace_sub.add_parser("show")
    show.add_argument("trace_id")

    schema = sub.add_parser("operator-spec-schema", help="Print the OperatorSpec v1 JSON schema")
    schema.add_argument("--output", default=None)

    args = parser.parse_args(argv)
    settings = Settings.from_env()

    if args.command == "serve":
        uvicorn.run("ganglia_runtime.server:app", host=args.host or settings.host, port=args.port or settings.port, reload=False)
        return 0

    if args.command == "operators":
        registry = OperatorRegistry().load(settings.operators_path)
        print(json.dumps([op.model_dump() for op in registry.list()], indent=2, ensure_ascii=False))
        if registry.invalid:
            print("Invalid operators:", file=sys.stderr)
            print(json.dumps(registry.invalid, indent=2), file=sys.stderr)
        return 0

    if args.command == "test":
        runtime = GangliaRuntime(settings=settings)
        print(json.dumps(runtime.reason(args.message, args.operator, args.model), indent=2, ensure_ascii=False))
        return 0

    if args.command == "validate-operator":
        spec = load_operator_file(Path(args.path))
        print(json.dumps({"valid": True, "operator": spec.id, "name": spec.name}, indent=2))
        return 0

    if args.command == "init-operator":
        out = Path(args.output or f"{args.operator_id}.lg.json")
        template = _operator_template(args.operator_id)
        out.write_text(json.dumps(template, indent=2), encoding="utf-8")
        print(f"Created {out}")
        return 0

    if args.command == "trace":
        runtime = GangliaRuntime(settings=settings)
        if args.trace_command == "list":
            print(json.dumps(runtime.trace_store.list_recent(), indent=2, ensure_ascii=False))
            return 0
        if args.trace_command == "show":
            trace = runtime.trace_store.get(args.trace_id)
            if not trace:
                print("Trace not found", file=sys.stderr)
                return 1
            print(json.dumps(trace, indent=2, ensure_ascii=False))
            return 0

    if args.command == "operator-spec-schema":
        schema_doc = operator_spec_schema()
        if args.output:
            Path(args.output).write_text(json.dumps(schema_doc, indent=2), encoding="utf-8")
        else:
            print(json.dumps(schema_doc, indent=2))
        return 0

    return 1


def _operator_template(operator_id: str) -> dict:
    return {
        "id": operator_id,
        "name": operator_id.replace("_", " ").title(),
        "version": "1.0.0",
        "category": "engine",
        "description": "Describe the language-game purpose here.",
        "routing": {"intent_hints": [], "default_when_user_mentions": [], "priority": 0},
        "chain": [],
        "system_prompt": "You are executing a Ganglia language-game operator.",
        "operator_rules": ["Obey the user task through this operator.", "Return only valid JSON."],
        "prompt_template": "User request:\n{{ user_message }}\n\nExecute this operator.",
        "output_schema": {
            "type": "object",
            "required": ["operator", "final_answer"],
            "properties": {"operator": {"type": "string"}, "final_answer": {"type": "string"}},
        },
        "semantic_validation": {"must_include_fields": ["operator", "final_answer"], "min_string_length": {"final_answer": 20}},
        "repair_prompt": "Repair the output so it matches the schema and operator rules.",
        "renderer": {"mode": "markdown", "template": "{{ final_answer }}"},
    }


if __name__ == "__main__":
    raise SystemExit(main())
