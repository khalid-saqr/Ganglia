# Security

Ganglia v1.0.0 is local-first reasoning middleware. It is designed to constrain LLM response structure, not to execute tools, run shell commands, or mutate user files.

## Defaults

- Binds to `127.0.0.1` by default.
- Uses Ollama at `http://localhost:11434` by default.
- Stores traces in a local SQLite database.
- Loads only declarative `.lg.json` and `.lg.md` operator files.
- Does not execute arbitrary Python code from operator files.
- Does not call external web services except the configured LLM backend.
- Does not support streaming in v1.0.0.

## API keys

Set these values before exposing Ganglia outside localhost:

```env
GANGLIA_REQUIRE_API_KEY=true
GANGLIA_API_KEY=replace-with-a-long-random-token
```

Clients then send:

```http
Authorization: Bearer replace-with-a-long-random-token
```

## Operator safety

Operator files are data. They can define prompts, schemas, semantic checks, repair prompts, and renderers. They cannot run code. This is deliberate. If future versions add Python plugins, they should be opt-in and sandboxed.

## Trace privacy

Trace records contain user messages, compiled prompts, model outputs, and final answers. Disable trace exposure for shared deployments:

```env
GANGLIA_EXPOSE_TRACE=false
```

You may also point `GANGLIA_TRACE_DB` to an encrypted volume or periodically delete the SQLite file.
