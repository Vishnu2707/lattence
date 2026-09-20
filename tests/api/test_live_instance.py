import threading
import time
from collections.abc import Iterator

import httpx
import pytest
import uvicorn
from lattence.evidence import Report, SecurityPresentation
from lattence_api import create_app


@pytest.fixture
def live_server(api_token: str) -> Iterator[str]:
    config = uvicorn.Config(create_app(), host="127.0.0.1", port=0, log_level="warning")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    deadline = time.monotonic() + 5
    while not server.started and time.monotonic() < deadline:
        time.sleep(0.01)
    assert server.started, "live server did not start within 5 seconds"
    port = server.servers[0].sockets[0].getsockname()[1]
    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        server.should_exit = True
        thread.join(timeout=5)


def _headers(api_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {api_token}"}


def test_live_health_is_reachable_over_real_http(live_server: str) -> None:
    response = httpx.get(f"{live_server}/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_live_scan_against_vulnerable_agent(live_server: str, api_token: str) -> None:
    response = httpx.get(
        f"{live_server}/v1/scan",
        params={"path": "examples/vulnerable-agent"},
        headers=_headers(api_token),
    )
    assert response.status_code == 200
    Report.model_validate(response.json())


def test_live_attack_against_vulnerable_agent(live_server: str, api_token: str) -> None:
    response = httpx.post(
        f"{live_server}/v1/attack",
        params={"path": "examples/vulnerable-agent", "offline": True},
        headers=_headers(api_token),
    )
    assert response.status_code == 200
    report = Report.model_validate(response.json())
    assert report.summary.total > 0


def test_live_chain_against_vulnerable_agent(live_server: str, api_token: str) -> None:
    response = httpx.get(
        f"{live_server}/v1/chain",
        params={"path": "examples/vulnerable-agent"},
        headers=_headers(api_token),
    )
    assert response.status_code == 200
    body = response.json()
    presentation = SecurityPresentation.model_validate(
        {key: value for key, value in body.items() if key != "cross_layer_summary"}
    )
    assert presentation.cross_layer_chains


def test_live_v1_route_rejects_missing_token(live_server: str) -> None:
    response = httpx.get(f"{live_server}/v1/scan", params={"path": "."})
    assert response.status_code == 401
