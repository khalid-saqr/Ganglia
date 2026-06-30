<div align="center">

# 🧠 Ganglia v1.0.0

**Local-first reasoning-control middleware for Ollama and OpenAI-compatible LLM stacks.**

Ganglia routes each request through a declarative language-game operator, asks the LLM for a structured reasoning object, validates the object, repairs failed outputs, stores a trace, and returns a controlled answer.

[![Python](https://img.shields.io/badge/python-%3E%3D3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](pyproject.toml)
[![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)](LICENSE)
[![FastAPI](https://img.shields.io/badge/FastAPI-runtime-009688?style=for-the-badge&logo=fastapi&logoColor=white)](pyproject.toml)
[![Pydantic](https://img.shields.io/badge/Pydantic-v2-E92063?style=for-the-badge)](pyproject.toml)
[![Ollama](https://img.shields.io/badge/Ollama-compatible-111111?style=for-the-badge)](#how-to-start-in-3-minutes)
[![OpenAI Compatible](https://img.shields.io/badge/OpenAI--compatible-endpoint-412991?style=for-the-badge)](#post-v1chatcompletions)
[![Local First](https://img.shields.io/badge/local--first-runtime-blue?style=for-the-badge)](#what-ganglia-is)
[![JSON Schema](https://img.shields.io/badge/JSON%20Schema-validation-orange?style=for-the-badge)](#validation-and-repair)

</div>

---

## Works with

| LLM runtime | API surface | App integrations | Framework integrations | Runtime tools |
| --- | --- | --- | --- | --- |
| Ollama | OpenAI-compatible clients | Open WebUI, AnythingLLM, Continue.dev | LangChain, LlamaIndex, Haystack | FastAPI, Docker Compose, JSON Schema, local scripts |

Ganglia is named after the basal ganglia: a biological gating system associated with selection, inhibition, sequencing, and release of actions. In this software, Ganglia gates reasoning operations before the answer is released.

## How to start in 3 minutes

### 1. Install and start Ollama

Install Ollama from its official site, then run:

```bash
ollama serve
```

In another terminal:

```bash
ollama pull llama3.1:8b
```

Any reasonably capable local chat model can be used, but `llama3.1:8b` is the default.

### 2. Install Ganglia

From the project directory:

```bash
pip install .
```

For development/testing:

```bash
pip install -e .[test]
```

### 3. Start the middleware

```bash
ganglia serve
```

The server starts at:

```text
http://127.0.0.1:8717
```

### 4. Send the first controlled request

```bash
curl -X POST http://127.0.0.1:8717/reason \
  -H "Content-Type: application/json" \
  -d '{"message":"Map remote work against operational overhead and knowledge siloing."}'
```

### 5. Use the OpenAI-compatible endpoint

```bash
curl -X POST http://127.0.0.1:8717/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "ganglia/auto",
    "messages": [{"role":"user", "content":"Stress-test my SaaS pricing model."}]
  }'
```

## What Ganglia is

Ganglia is a runtime gateway:

```mermaid
flowchart LR
    A[User / App] --> B[Ganglia]
    B --> C[Language-game operator]
    C --> D[Ollama LLM]
    D --> E[Validation / repair]
    E --> F[Trace store]
    E --> G[Controlled answer]
```

It exists to prevent unconstrained free-answering when the user wants a repeatable reasoning protocol.

## What Ganglia is not

Ganglia is not:

- a Custom GPT,
- a prompt collection,
- a chatbot skin,
- a RAG framework,
- a hidden chain-of-thought extractor,
- a claim that internal model cognition is fully controllable.

Ganglia controls the observable reasoning product: the structured object that the LLM must emit and pass through validation.

## Why this matters

Ordinary prompting says:

```text
Please reason this way.
```

Ganglia says:

```text
Use this operator.
Return this JSON schema.
Pass these semantic checks.
Repair failures before release.
Store the trace.
```

This is a stronger enforcement pattern for local LLM stacks.

| Step | Ganglia control point |
| --- | --- |
| 1 | Select a language-game operator. |
| 2 | Compile the operator prompt. |
| 3 | Require the operator JSON schema. |
| 4 | Pass semantic checks. |
| 5 | Repair failures before release. |
| 6 | Store the trace. |
| 7 | Return a controlled answer. |

## Built-in operators

| Operator | Purpose | Use it for |
| --- | --- | --- |
| `coordinate_game` | Forces abstract entities into a two-axis 0-10 coordinate system. | mapping, plotting, positioning, scoring, abstract coordinate systems |
| `grid_game` | Forces content into a comparative matrix. | comparison, classification, matrix design, MECE table forcing, relational ontologies |
| `adversarial_grid_chain` | Applies adversarial testing, then formalises the result as a failure matrix. | stress-testing, falsification, red-team review, risk detection, failure-mode analysis |

### `coordinate_game`

Forces abstract entities into a two-axis 0-10 coordinate system.

Use it for:

- mapping,
- plotting,
- positioning,
- scoring,
- abstract coordinate systems.

Example:

```bash
curl -X POST http://127.0.0.1:8717/reason \
  -H "Content-Type: application/json" \
  -d '{
    "operator": "coordinate_game",
    "message": "Map remote work against operational overhead and knowledge siloing."
  }'
```

### `grid_game`

Forces content into a comparative matrix.

Use it for:

- comparison,
- classification,
- matrix design,
- MECE table forcing,
- relational ontologies.

### `adversarial_grid_chain`

Applies adversarial testing, then formalises the result as a failure matrix.

Use it for:

- stress-testing,
- falsification,
- red-team review,
- risk detection,
- failure-mode analysis.

## API

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Returns status and loaded operator count. |
| `GET` | `/operators` | Lists loaded operators and invalid operator files. |
| `POST` | `/reason` | Native Ganglia endpoint. |
| `POST` | `/v1/chat/completions` | OpenAI-compatible endpoint. |
| `GET` | `/trace` | Lists recent traces. |
| `GET` | `/trace/{trace_id}` | Shows a full trace. |

### `GET /health`

Returns status and loaded operator count.

### `GET /operators`

Lists loaded operators and invalid operator files.

### `POST /reason`

Native Ganglia endpoint.

Request:

```json
{
  "message": "Stress-test this launch plan.",
  "operator": "adversarial_grid_chain",
  "model": "llama3.1:8b"
}
```

`operator` can be omitted or set to `auto`.

Response:

```json
{
  "trace_id": "...",
  "operator": "adversarial_grid_chain",
  "model": "llama3.1:8b",
  "answer": "...",
  "controlled_reasoning": {},
  "repair_attempts": 0
}
```

### `POST /v1/chat/completions`

OpenAI-compatible endpoint.

Use model names to choose operators:

```text
ganglia/auto
ganglia/coordinate_game
ganglia/grid_game
ganglia/adversarial_grid_chain
```

Example:

```bash
curl -X POST http://127.0.0.1:8717/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "ganglia/grid_game",
    "messages": [{"role":"user", "content":"Compare three project options."}]
  }'
```

### `GET /trace`

Lists recent traces.

### `GET /trace/{trace_id}`

Shows a full trace.

Trace records include user messages, compiled prompts, raw model outputs, validation errors, repair attempts, and final answers.

> [!WARNING]
> Disable trace exposure in shared deployments:
>
> ```env
> GANGLIA_EXPOSE_TRACE=false
> ```

## Configuration

Copy `.env.example` if needed:

```bash
cp .env.example .env
```

Important settings:

```env
GANGLIA_HOST=127.0.0.1
GANGLIA_PORT=8717
GANGLIA_REQUIRE_API_KEY=false
GANGLIA_API_KEY=
GANGLIA_OLLAMA_URL=http://localhost:11434
GANGLIA_MODEL=llama3.1:8b
GANGLIA_TRACE_DB=./ganglia_traces.sqlite
GANGLIA_OPERATORS_DIR=./operators
GANGLIA_MAX_RETRIES=2
GANGLIA_TEMPERATURE=0.2
GANGLIA_TIMEOUT_SECONDS=120
GANGLIA_EXPOSE_TRACE=true
```

## CLI

| Command | Purpose |
| --- | --- |
| `ganglia serve` | Start the server. |
| `ganglia operators` | List operators. |
| `ganglia test "Map remote work against operational overhead and knowledge siloing."` | Run a one-off request. |
| `ganglia validate-operator operators/my_game.lg.json` | Validate an operator. |
| `ganglia init-operator my_new_game` | Create an operator template. |
| `ganglia trace list` | List traces. |
| `ganglia trace show TRACE_ID` | Show a trace. |

Start the server:

```bash
ganglia serve
```

List operators:

```bash
ganglia operators
```

Run a one-off request:

```bash
ganglia test "Map remote work against operational overhead and knowledge siloing."
```

Validate an operator:

```bash
ganglia validate-operator operators/my_game.lg.json
```

Create an operator template:

```bash
ganglia init-operator my_new_game
```

List traces:

```bash
ganglia trace list
```

Show a trace:

```bash
ganglia trace show TRACE_ID
```

## Adding a new language-game with one file

Create:

```text
operators/my_new_game.lg.json
```

Then validate:

```bash
ganglia validate-operator operators/my_new_game.lg.json
```

Restart the server and confirm:

```bash
curl http://127.0.0.1:8717/operators
```

A declarative language-game can define:

- metadata,
- routing hints,
- prompt template,
- output JSON schema,
- semantic checks,
- repair instruction,
- renderer template,
- optional chain definition.

For details, read `OPERATORS.md`.

## Integration overview

Ganglia works through the OpenAI-compatible endpoint where possible:

```text
http://127.0.0.1:8717/v1
```

Use model:

```text
ganglia/auto
```

Integration guides are in `INTEGRATIONS.md` for:

| Integration | Connection style | Base URL / model | Notes |
| --- | --- | --- | --- |
| Open WebUI | OpenAI-compatible endpoint | `http://127.0.0.1:8717/v1` / `ganglia/auto` | Listed in `INTEGRATIONS.md`. |
| AnythingLLM | OpenAI-compatible endpoint | `http://127.0.0.1:8717/v1` / `ganglia/auto` | Listed in `INTEGRATIONS.md`. |
| Continue.dev | OpenAI-compatible endpoint | `http://127.0.0.1:8717/v1` / `ganglia/auto` | Listed in `INTEGRATIONS.md`. |
| LangChain | OpenAI-compatible endpoint | `http://127.0.0.1:8717/v1` / `ganglia/auto` | Listed in `INTEGRATIONS.md`. |
| LlamaIndex | OpenAI-compatible endpoint | `http://127.0.0.1:8717/v1` / `ganglia/auto` | Listed in `INTEGRATIONS.md`. |
| Haystack | OpenAI-compatible endpoint | `http://127.0.0.1:8717/v1` / `ganglia/auto` | Listed in `INTEGRATIONS.md`. |
| Custom apps | Native or OpenAI-compatible endpoint | `/reason` or `/v1/chat/completions` | Listed in `INTEGRATIONS.md`. |
| Local scripts | Native or OpenAI-compatible endpoint | `/reason` or `/v1/chat/completions` | Listed in `INTEGRATIONS.md`. |

## Docker

Build and run:

```bash
docker compose up --build
```

The container expects Ollama on the host at:

```text
http://host.docker.internal:11434
```

On Linux, you may need to adjust the compose file or run Ollama in the same Docker network.

## Validation and repair

Ganglia validates in two stages:

1. JSON Schema validation.
2. Semantic validation.

If validation fails, Ganglia sends a repair prompt to the LLM with:

- the original user task,
- the invalid output,
- the validation errors,
- the operator-specific repair instruction.

If repair fails after `GANGLIA_MAX_RETRIES`, the request returns a validation error and stores the trace.

## Production notes

> [!IMPORTANT]
> Before exposing Ganglia beyond localhost:
>
> ```env
> GANGLIA_REQUIRE_API_KEY=true
> GANGLIA_API_KEY=use-a-long-random-token
> ```

Then clients must send:

```http
Authorization: Bearer use-a-long-random-token
```

> [!IMPORTANT]
> Ganglia v1.0.0 intentionally does not support arbitrary Python plugins. Operator files are declarative only.

## Documentation

| Document | Purpose |
| --- | --- |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | Architecture details. |
| [`OPERATORS.md`](OPERATORS.md) | Operator details. |
| [`INTEGRATIONS.md`](INTEGRATIONS.md) | Integration guides. |
| [`SECURITY.md`](SECURITY.md) | Security notes. |
| [`CHANGELOG.md`](CHANGELOG.md) | Release changes. |
| [`examples/`](examples/) | Example operators and scripts. |

## Troubleshooting

### Ollama is not reachable

Check:

```bash
curl http://localhost:11434/api/tags
```

If that fails, start Ollama:

```bash
ollama serve
```

### Model not found

Pull the model:

```bash
ollama pull llama3.1:8b
```

Or set another model:

```env
GANGLIA_MODEL=qwen2.5:7b
```

### OpenAI-compatible tool cannot see models

Check:

```bash
curl http://127.0.0.1:8717/v1/models
```

Use base URL:

```text
http://127.0.0.1:8717/v1
```

not:

```text
http://127.0.0.1:8717
```

### Model returns validation errors

Use a stronger model, lower temperature, simplify the operator schema, or increase retries:

```env
GANGLIA_MAX_RETRIES=3
GANGLIA_TEMPERATURE=0.1
```

## License

MIT.
