from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from lattence.governance import Role
from lattence_api import create_app
from lattence_api.sso import MockSSOProvider, set_sso_provider


@pytest.fixture(autouse=True)
def _reset_sso_provider() -> Iterator[None]:
    yield
    set_sso_provider(None)


def test_mock_sso_token_with_role_can_call_matching_route(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("LATTENCE_API_TOKEN", raising=False)
    monkeypatch.delenv("LATTENCE_RBAC_DB", raising=False)
    set_sso_provider(MockSSOProvider())
    client = TestClient(create_app())

    response = client.get(
        "/v1/scan",
        params={"path": "."},
        headers={"Authorization": "Bearer mock-sso:alice:run_scans"},
    )

    assert response.status_code == 200


def test_mock_sso_token_without_role_is_forbidden(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("LATTENCE_API_TOKEN", raising=False)
    monkeypatch.delenv("LATTENCE_RBAC_DB", raising=False)
    set_sso_provider(MockSSOProvider())
    client = TestClient(create_app())

    response = client.get(
        "/v1/scan",
        params={"path": "."},
        headers={"Authorization": "Bearer mock-sso:bob:read_findings"},
    )

    assert response.status_code == 403
    assert "bob" in response.json()["detail"]


def test_unrecognized_token_falls_through_to_legacy(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("LATTENCE_API_TOKEN", "team-secret")
    monkeypatch.delenv("LATTENCE_RBAC_DB", raising=False)
    set_sso_provider(MockSSOProvider())
    client = TestClient(create_app())

    response = client.get(
        "/v1/scan",
        params={"path": "."},
        headers={"Authorization": "Bearer team-secret"},
    )

    assert response.status_code == 200


def test_mock_sso_provider_resolves_and_rejects_tokens() -> None:
    provider = MockSSOProvider()

    identity = provider.resolve("mock-sso:alice:run_scans,read_findings")
    assert identity is not None
    assert identity.caller_id == "alice"
    assert identity.roles == frozenset({Role.RUN_SCANS, Role.READ_FINDINGS})

    assert provider.resolve("not-a-mock-token") is None
    assert provider.resolve("mock-sso:") is None
