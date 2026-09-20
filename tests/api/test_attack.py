from fastapi.testclient import TestClient
from lattence.evidence import Report
from lattence_api import create_app


def test_attack_returns_report_for_vulnerable_agent() -> None:
    client = TestClient(create_app())
    response = client.post(
        "/v1/attack",
        params={"path": "examples/vulnerable-agent", "offline": True},
    )
    assert response.status_code == 200
    report = Report.model_validate(response.json())
    assert report.summary.total > 0


def test_attack_returns_400_without_target_declaration() -> None:
    client = TestClient(create_app())
    response = client.post("/v1/attack", params={"path": "."})
    assert response.status_code == 400
