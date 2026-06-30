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
