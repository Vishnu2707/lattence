import pytest
from fastapi.testclient import TestClient
from lattence_api import create_app


def test_v1_route_without_token_configured_returns_503(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("LATTENCE_API_TOKEN", raising=False)
    client = TestClient(create_app())
    response = client.get("/v1/scan", params={"path": "."})
    assert response.status_code == 503


def test_v1_route_without_authorization_header_returns_401(api_token: str) -> None:
    client = TestClient(create_app())
    response = client.get("/v1/scan", params={"path": "."})
    assert response.status_code == 401


def test_v1_route_with_wrong_token_returns_401(api_token: str) -> None:
    client = TestClient(create_app())
    response = client.get(
        "/v1/scan",
        params={"path": "."},
        headers={"Authorization": "Bearer wrong-token"},
    )
    assert response.status_code == 401
