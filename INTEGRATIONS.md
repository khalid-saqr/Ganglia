# Integrations

Ganglia exposes two surfaces:

- Native endpoint: `POST /reason`
- OpenAI-compatible endpoint: `POST /v1/chat/completions`

Use `/reason` when you control the client. Use `/v1/chat/completions` when the target tool already expects an OpenAI-style API.

## Open WebUI

Recommended route: add Ganglia as an OpenAI-compatible connection.

Base URL:

```text
http://127.0.0.1:8717/v1
```

API key:

```text
anything-local
```

Model:

```text
ganglia/auto
```

You can also select a fixed operator as a model name:

```text
ganglia/coordinate_game
ganglia/grid_game
ganglia/adversarial_grid_chain
```

### Optional Pipe Function

Ganglia includes a starter Pipe at:

```text
src/ganglia_runtime/integrations/open_webui_pipe.py
```

Use the OpenAI-compatible connection first. Use the Pipe only if you want Ganglia to appear as a custom model inside Open WebUI.

## AnythingLLM

Recommended route: configure a Generic OpenAI-compatible LLM provider.

Base URL:

```text
http://127.0.0.1:8717/v1
```

API key:

```text
anything-local
```

Model:

```text
ganglia/auto
```

If your AnythingLLM build does not expose a compatible custom base URL field, run Ganglia externally and call `/reason` from a custom agent skill or workflow.

## Continue.dev

Use the OpenAI provider with a local base URL.

Example `config.yaml`:

```yaml
models:
  - name: Ganglia Auto
    provider: openai
    model: ganglia/auto
    apiBase: http://127.0.0.1:8717/v1
    apiKey: local
```

Some Continue.dev builds use `baseUrl` rather than `apiBase`; use the field expected by your installed version.

## LangChain

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="ganglia/auto",
    base_url="http://127.0.0.1:8717/v1",
    api_key="local",
)

print(llm.invoke("Stress-test my SaaS pricing model.").content)
```

Native `/reason` route:

```python
import requests

resp = requests.post(
    "http://127.0.0.1:8717/reason",
    json={"message": "Map remote work against operational overhead and knowledge siloing."},
    timeout=120,
)
print(resp.json()["answer"])
```

## LlamaIndex

```python
from llama_index.llms.openai_like import OpenAILike

llm = OpenAILike(
    model="ganglia/auto",
    api_base="http://127.0.0.1:8717/v1",
    api_key="local",
    is_chat_model=True,
)

response = llm.complete("Compare three project risks in a matrix.")
print(response)
```

## Haystack

```python
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret

llm = OpenAIChatGenerator(
    api_key=Secret.from_token("local"),
    api_base_url="http://127.0.0.1:8717/v1",
    model="ganglia/auto",
)

result = llm.run(messages=[ChatMessage.from_user("Stress-test this launch plan.")])
print(result["replies"][0].text)
```

If your Haystack version uses a different constructor keyword, keep the same principle: OpenAI-compatible generator, base URL `http://127.0.0.1:8717/v1`, model `ganglia/auto`.

## Custom apps

JavaScript:

```javascript
const res = await fetch("http://127.0.0.1:8717/reason", {
  method: "POST",
  headers: {"Content-Type": "application/json"},
  body: JSON.stringify({
    message: "Map remote work against operational overhead and knowledge siloing.",
    operator: "coordinate_game"
  })
});
const data = await res.json();
console.log(data.answer);
```

Python:

```python
import requests

r = requests.post(
    "http://127.0.0.1:8717/reason",
    json={"message": "Stress-test this plan.", "operator": "adversarial_grid_chain"},
    timeout=120,
)
print(r.json()["answer"])
```

## Local scripts

Use `examples/python_local_script.py` or call the runtime directly:

```python
from ganglia_runtime import GangliaRuntime

runtime = GangliaRuntime()
result = runtime.reason("Compare three options in a grid.", operator="grid_game")
print(result["answer"])
```
