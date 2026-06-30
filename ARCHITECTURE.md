# Architecture

Ganglia is a runtime gateway that places an enforceable reasoning protocol between the user and the LLM.

```text
User / App / Agent / IDE
        ↓
Ganglia API Gateway
        ↓
Request Normaliser
        ↓
Operator Router
        ↓
OperatorSpec Loader
        ↓
Prompt Compiler
        ↓
Ollama / LLM backend
        ↓
JSON Schema Validator
        ↓
Semantic Validator
        ↓
Repair / Retry Loop
        ↓
Renderer
        ↓
SQLite Trace Store
        ↓
Final Answer
```

## Enforceable object

Ganglia does not claim to control hidden cognition inside a model. It controls the observable reasoning product:

1. selected operator,
2. compiled prompt,
3. required JSON schema,
4. semantic validation checks,
5. repair/retry loop,
6. traceable final answer.

## Runtime flow

1. The user sends a message to `/reason` or `/v1/chat/completions`.
2. The router selects an operator unless the caller explicitly chooses one.
3. The prompt compiler builds the language-game prompt.
4. The Ollama client calls `/api/chat` with `format` set to the operator's JSON Schema.
5. The output is parsed as JSON.
6. JSON Schema validation runs first.
7. Semantic validation runs second.
8. If validation fails, Ganglia runs a repair prompt and retries.
9. The renderer converts the controlled object into a readable final answer.
10. A trace is saved to SQLite.

## Built-in operators

- `coordinate_game`: maps concepts into a two-axis 0-10 coordinate system.
- `grid_game`: forces content into a MECE matrix.
- `adversarial_grid_chain`: attacks a proposal and renders a failure matrix.

## Extension model

New operators are added declaratively as `.lg.json` or `.lg.md` files. No Python changes are required for ordinary language-games.
