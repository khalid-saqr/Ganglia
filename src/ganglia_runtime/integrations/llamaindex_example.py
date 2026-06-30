from llama_index.llms.openai_like import OpenAILike

llm = OpenAILike(
    model="ganglia/auto",
    api_base="http://127.0.0.1:8717/v1",
    api_key="local",
    is_chat_model=True,
)

print(llm.complete("Map remote work against operational overhead and knowledge siloing."))
