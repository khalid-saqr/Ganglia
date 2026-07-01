from fastapi.testclient import TestClient

from ganglia_runtime.config import Settings
import ganglia_runtime.server as server


class FakeTraceStore:
    def __init__(self):
        self.last_limit = None

    def list_recent(self, limit=20):
        self.last_limit = limit
        return [{"trace_id": "trace-1", "user_message": "hello", "limit": limit}]

    def get(self, trace_id):
        if trace_id == "trace-1":
            return {"trace_id": trace_id, "final_answer": "answer"}
        return None


class FakeRuntime:
    def __init__(self):
        self.trace_store = FakeTraceStore()


def test_trace_denied_by_default(monkeypatch):
    monkeypatch.setattr(server, "settings", Settings())
    monkeypatch.setattr(server, "runtime", FakeRuntime())
    client = TestClient(server.app)

    response = client.get("/trace")

    assert response.status_code == 403
    assert response.json()["detail"] == "Trace exposure disabled"


def test_trace_access_requires_explicit_exposure_and_api_key(monkeypatch):
    monkeypatch.setattr(
        server,
        "settings",
        Settings(expose_trace=True, trace_require_api_key=True, api_key="secret"),
    )
    monkeypatch.setattr(server, "runtime", FakeRuntime())
    client = TestClient(server.app)

    unauthorized = client.get("/trace")
    authorized = client.get("/trace", headers={"Authorization": "Bearer secret"})
    trace = client.get("/trace/trace-1", headers={"Authorization": "Bearer secret"})

    assert unauthorized.status_code == 401
    assert authorized.status_code == 200
    assert authorized.json() == {"traces": [{"trace_id": "trace-1", "user_message": "hello", "limit": 20}]}
    assert trace.status_code == 200
    assert trace.json() == {"trace_id": "trace-1", "final_answer": "answer"}


def test_trace_exposure_must_be_explicitly_enabled(monkeypatch):
    monkeypatch.delenv("GANGLIA_EXPOSE_TRACE", raising=False)
    monkeypatch.delenv("GANGLIA_TRACE_REQUIRE_API_KEY", raising=False)

    default_settings = Settings.from_env(env_file=None)

    monkeypatch.setenv("GANGLIA_EXPOSE_TRACE", "true")
    enabled_settings = Settings.from_env(env_file=None)

    assert default_settings.expose_trace is False
    assert default_settings.trace_require_api_key is True
    assert enabled_settings.expose_trace is True


def test_trace_limit_rejects_zero_negative_and_too_large(monkeypatch):
    monkeypatch.setattr(server, "settings", Settings(expose_trace=True, trace_require_api_key=False))
    monkeypatch.setattr(server, "runtime", FakeRuntime())
    client = TestClient(server.app)

    for limit in (0, -1, 101):
        response = client.get(f"/trace?limit={limit}")

        assert response.status_code == 422


def test_trace_limit_accepts_upper_bound(monkeypatch):
    runtime = FakeRuntime()
    monkeypatch.setattr(server, "settings", Settings(expose_trace=True, trace_require_api_key=False))
    monkeypatch.setattr(server, "runtime", runtime)
    client = TestClient(server.app)

    response = client.get("/trace?limit=100")

    assert response.status_code == 200
    assert runtime.trace_store.last_limit == 100
    assert response.json() == {"traces": [{"trace_id": "trace-1", "user_message": "hello", "limit": 100}]}
