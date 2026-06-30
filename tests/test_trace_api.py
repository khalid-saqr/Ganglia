from fastapi.testclient import TestClient

from ganglia_runtime.config import Settings
import ganglia_runtime.server as server


class FakeTraceStore:
    def list_recent(self, limit=20):
        return [{"trace_id": "trace-1", "user_message": "hello"}]

    def get(self, trace_id):
        if trace_id == "trace-1":
            return {"trace_id": trace_id, "final_answer": "answer"}
        return None


class FakeRuntime:
    trace_store = FakeTraceStore()


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
    assert authorized.json() == {"traces": [{"trace_id": "trace-1", "user_message": "hello"}]}
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
