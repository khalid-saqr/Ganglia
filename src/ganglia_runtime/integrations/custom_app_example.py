import requests

response = requests.post(
    "http://127.0.0.1:8717/reason",
    json={"message": "Compare three options in a matrix.", "operator": "grid_game"},
    timeout=120,
)
response.raise_for_status()
print(response.json()["answer"])
