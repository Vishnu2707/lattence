from fastapi.testclient import TestClient
from lattence.evidence import SecurityPresentation
from lattence_api import create_app


def test_chain_returns_presentation_for_vulnerable_agent() -> None:
    client = TestClient(create_app())
    response = client.get(
        "/v1/chain", params={"path": "examples/vulnerable-agent"}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["cross_layer_summary"]["finding_correlations"] > 0
    presentation = SecurityPresentation.model_validate(
        {key: value for key, value in body.items() if key != "cross_layer_summary"}
    )
    assert presentation.cross_layer_chains


def test_chain_returns_404_for_missing_path() -> None:
    client = TestClient(create_app())
    response = client.get("/v1/chain", params={"path": "examples/does-not-exist"})
    assert response.status_code == 404
