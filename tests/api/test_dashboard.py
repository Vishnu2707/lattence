from fastapi.testclient import TestClient


def test_dashboard_renders_real_cross_layer_chain_for_vulnerable_agent(
    client: TestClient,
) -> None:
    response = client.get("/v1/dashboard", params={"path": "examples/vulnerable-agent"})
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    body = response.text
    assert body.startswith("<!doctype html>")
    assert "32 finding correlations across 9 distinct structural paths" in body
    assert "LT-AI-002 -&gt; LT-PQC-203" in body
    assert "https://" not in body
    assert "fetch(" not in body


def test_dashboard_returns_404_for_missing_path(client: TestClient) -> None:
    response = client.get("/v1/dashboard", params={"path": "examples/does-not-exist"})
    assert response.status_code == 404


def test_dashboard_requires_authentication(client: TestClient) -> None:
    del client.headers["Authorization"]

    response = client.get("/v1/dashboard", params={"path": "examples/vulnerable-agent"})

    assert response.status_code == 401
