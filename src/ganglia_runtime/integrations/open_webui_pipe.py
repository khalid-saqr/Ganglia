"""Open WebUI Pipe starter for Ganglia.

Use Open WebUI's OpenAI-compatible connection first if possible. This Pipe is for
cases where you want Ganglia to appear as a custom model inside Open WebUI.
"""

import requests


class Pipe:
    class Valves:
        GANGLIA_URL: str = "http://127.0.0.1:8717/reason"
        OPERATOR: str = "auto"

    def __init__(self):
        self.valves = self.Valves()

    def pipes(self):
        return [
            {"id": "ganglia-auto", "name": "Ganglia Auto"},
            {"id": "ganglia-coordinate", "name": "Ganglia Coordinate Game"},
            {"id": "ganglia-grid", "name": "Ganglia Grid Game"},
            {"id": "ganglia-adversarial-grid", "name": "Ganglia Adversarial Grid"},
        ]

    def pipe(self, body: dict):
        messages = body.get("messages", [])
        user_text = "\n".join([m.get("content", "") for m in messages if m.get("role") == "user"])
        model = body.get("model", "ganglia-auto")
        operator = {
            "ganglia-coordinate": "coordinate_game",
            "ganglia-grid": "grid_game",
            "ganglia-adversarial-grid": "adversarial_grid_chain",
        }.get(model, self.valves.OPERATOR)
        response = requests.post(
            self.valves.GANGLIA_URL,
            json={"message": user_text, "operator": operator},
            timeout=120,
        )
        response.raise_for_status()
        return response.json()["answer"]
