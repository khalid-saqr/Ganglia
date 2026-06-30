from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="ganglia/auto",
    base_url="http://127.0.0.1:8717/v1",
    api_key="local",
)

print(llm.invoke("Stress-test this plan.").content)
