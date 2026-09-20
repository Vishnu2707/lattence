from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from lattence_api import create_app

TEST_TOKEN = "test-token"


@pytest.fixture
def api_token(monkeypatch: pytest.MonkeyPatch) -> str:
    monkeypatch.setenv("LATTENCE_API_TOKEN", TEST_TOKEN)
    return TEST_TOKEN


@pytest.fixture
def client(api_token: str) -> Iterator[TestClient]:
    with TestClient(create_app()) as test_client:
        test_client.headers["Authorization"] = f"Bearer {api_token}"
        yield test_client
