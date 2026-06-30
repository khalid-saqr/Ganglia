# OperatorSpec v1

Ganglia operators are declarative language-game definitions. A new ordinary language-game can be added by placing one `.lg.json` file in the configured operators directory.

Default directory:

```env
GANGLIA_OPERATORS_DIR=./operators
```

## Minimal operator file

```json
{
  "id": "my_game",
  "name": "My Game",
  "version": "1.0.0",
  "category": "engine",
  "description": "What this language-game does.",
  "routing": {
    "intent_hints": ["map", "compare"],
    "default_when_user_mentions": ["map this"],
    "priority": 10
  },
  "chain": [],
  "system_prompt": "You are executing a Ganglia language-game operator.",
  "operator_rules": [
    "Obey this operator's rules.",
    "Return only JSON."
  ],
  "prompt_template": "User request:\n{{ user_message }}\n\nExecute the operator.",
  "output_schema": {
    "type": "object",
    "required": ["operator", "final_answer"],
    "properties": {
      "operator": {"type": "string"},
      "final_answer": {"type": "string"}
    }
  },
  "semantic_validation": {
    "must_include_fields": ["operator", "final_answer"],
    "min_string_length": {"final_answer": 20}
  },
  "repair_prompt": "Repair the output so it obeys the operator schema.",
  "renderer": {
    "mode": "markdown",
    "template": "{{ final_answer }}"
  }
}
```

## Required fields

| Field | Purpose |
|---|---|
| `id` | Lowercase slug. This becomes the operator name used in API calls. |
| `name` | Human-readable name. |
| `version` | Operator version. |
| `category` | One of `engine`, `mapper`, `modifier`, `modifier_to_engine`, `chain`. |
| `description` | Short explanation. |
| `routing` | Hints used by the automatic router. |
| `system_prompt` | Global instruction for this operator. |
| `operator_rules` | Explicit language-game rules. |
| `prompt_template` | Jinja template compiled with `user_message`, `operator`, `rules`, and `context`. |
| `output_schema` | JSON Schema object sent to the LLM and used for validation. |
| `semantic_validation` | Extra checks beyond JSON Schema. |
| `repair_prompt` | Instruction used if validation fails. |
| `renderer` | Final answer template. |

## Supported semantic validation rules

```json
{
  "must_include_fields": ["operator", "final_answer"],
  "min_items": {"rows": 2},
  "min_string_length": {"final_answer": 30},
  "coordinate_fields_must_be_between": [0, 10],
  "must_not_include_forbidden_terms_in": ["final_answer"],
  "require_markdown_table_in": "final_answer"
}
```

## Adding the fourth language-game

1. Copy `examples/add_new_operator_example.lg.json`.
2. Rename it to `operators/isomorphism_game.lg.json`.
3. Edit `id`, `name`, prompts, schema, and renderer.
4. Validate it:

```bash
ganglia validate-operator operators/isomorphism_game.lg.json
```

5. Restart Ganglia:

```bash
ganglia serve
```

6. Confirm it loaded:

```bash
curl http://127.0.0.1:8717/operators
```

## `.lg.md` support

`.lg.md` is supported for human-friendly operators. It uses YAML front matter plus sections named:

- `System Prompt`
- `Operator Rules`
- `Prompt Template`
- `Output Schema`
- `Repair Prompt`
- `Renderer`

`.lg.json` remains the canonical production format.
