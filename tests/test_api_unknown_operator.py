from fastapi.testclient import TestClient

from ganglia_runtime.server import app


client = TestClient(app)


def test_reason_unknown_operator_returns_404():
    response = client.post(
        "/reason",
        json={"message": "Stress-test this SaaS pricing model for failure modes", "operator": "does_not_exist"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Unknown operator: does_not_exist"


def test_openai_model_unknown_ganglia_operator_returns_404():
    response = client.post(
        "/v1/chat/completions",
        json={
            "model": "ganglia/does_not_exist",
            "messages": [{"role": "user", "content": "Stress-test this SaaS pricing model for failure modes"}],
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Unknown operator: does_not_exist"
