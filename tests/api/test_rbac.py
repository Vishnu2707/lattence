from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from lattence.governance import ApiKeyStore, Role
from lattence_api import create_app


@pytest.fixture
def rbac_store(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> ApiKeyStore:
    db_path = tmp_path / "rbac.db"
    monkeypatch.setenv("LATTENCE_RBAC_DB", str(db_path))
    monkeypatch.delenv("LATTENCE_API_TOKEN", raising=False)
    return ApiKeyStore(db_path)


def test_rbac_key_with_role_can_call_matching_route(rbac_store: ApiKeyStore) -> None:
    key = rbac_store.create_key("alice", frozenset({Role.RUN_SCANS}))
    client = TestClient(create_app())

    response = client.get(
        "/v1/scan",
        params={"path": "."},
        headers={"Authorization": f"Bearer {key}"},
    )

    assert response.status_code == 200


def test_rbac_key_without_role_is_forbidden(rbac_store: ApiKeyStore) -> None:
    key = rbac_store.create_key("bob", frozenset({Role.READ_FINDINGS}))
    client = TestClient(create_app())

    response = client.get(
        "/v1/scan",
        params={"path": "."},
        headers={"Authorization": f"Bearer {key}"},
    )

    assert response.status_code == 403
    assert "bob" in response.json()["detail"]


def test_unknown_key_with_rbac_configured_returns_401(
    rbac_store: ApiKeyStore,
) -> None:
    client = TestClient(create_app())

    response = client.get(
        "/v1/scan",
        params={"path": "."},
        headers={"Authorization": "Bearer not-a-real-key"},
    )

    assert response.status_code == 401


def test_legacy_team_token_still_works_alongside_rbac(
    rbac_store: ApiKeyStore, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("LATTENCE_API_TOKEN", "team-secret")
    client = TestClient(create_app())

    response = client.get(
        "/v1/scan",
        params={"path": "."},
        headers={"Authorization": "Bearer team-secret"},
    )

    assert response.status_code == 200
