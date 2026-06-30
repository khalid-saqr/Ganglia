import requests

resp = requests.post(
    "http://127.0.0.1:8717/reason",
    json={
        "message": "Compare Open WebUI, AnythingLLM, and Continue.dev as frontends for local reasoning middleware.",
        "operator": "grid_game",
    },
    timeout=120,
)
resp.raise_for_status()
print(resp.json()["answer"])
