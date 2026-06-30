# Changelog

## v1.0.0

Initial production-oriented release of Ganglia.

- FastAPI server with native `/reason` endpoint.
- OpenAI-compatible `/v1/chat/completions` and `/v1/models` endpoints.
- Ollama native `/api/chat` client with JSON Schema format support.
- Declarative `.lg.json` operator loading.
- Optional `.lg.md` operator parsing with YAML front matter and JSON schema section.
- Built-in Coordinate Game, Grid Game, and Adversarial → Grid Chain operators.
- JSON Schema validation, semantic validation, repair/retry loop, and SQLite traces.
- CLI commands for serving, testing, listing operators, validating operators, and reading traces.
- Integration examples for Open WebUI, AnythingLLM, Continue.dev, LangChain, LlamaIndex, Haystack, custom apps, and local scripts.
