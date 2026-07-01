from fastapi.testclient import TestClient

from ganglia_runtime.config import Settings
import ganglia_runtime.server as server


class FakeRegistry:
    invalid = []


class FakeRuntime:
    def __init__(self):
        self.registry = FakeRegistry()

    def operators(self):
        return [{"id": "fake_operator"}]


def test_require_auth_rejects_missing_bearer_token(monkeypatch):
    monkeypatch.setattr(server, "settings", Settings(require_api_key=True, api_key="secret"))
    monkeypatch.setattr(server, "runtime", FakeRuntime())
    client = TestClient(server.app)

    response = client.get("/operators")

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or missing API key"


def test_require_auth_rejects_invalid_bearer_token(monkeypatch):
    monkeypatch.setattr(server, "settings", Settings(require_api_key=True, api_key="secret"))
    monkeypatch.setattr(server, "runtime", FakeRuntime())
    client = TestClient(server.app)

    response = client.get("/operators", headers={"Authorization": "Bearer wrong"})

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or missing API key"


def test_require_auth_accepts_valid_bearer_token(monkeypatch):
    monkeypatch.setattr(server, "settings", Settings(require_api_key=True, api_key="secret"))
    monkeypatch.setattr(server, "runtime", FakeRuntime())
    client = TestClient(server.app)

    response = client.get("/operators", headers={"Authorization": "Bearer secret"})

    assert response.status_code == 200
    assert response.json() == {"operators": [{"id": "fake_operator"}], "invalid": []}
