from fastapi.testclient import TestClient
from lattence.evidence import Report


def test_scan_returns_report_for_vulnerable_agent(client: TestClient) -> None:
    response = client.get("/v1/scan", params={"path": "examples/vulnerable-agent"})
    assert response.status_code == 200
    Report.model_validate(response.json())


def test_scan_returns_404_for_missing_path(client: TestClient) -> None:
    response = client.get("/v1/scan", params={"path": "examples/does-not-exist"})
    assert response.status_code == 404
