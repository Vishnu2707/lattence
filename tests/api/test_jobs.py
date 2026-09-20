import os
import time
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient
from lattence.governance import ApiKeyStore, AuditLog, Role
from lattence_api import create_app


def _wait_for_completion(
    client: TestClient, job_id: str, timeout: float = 10.0
) -> dict[str, Any]:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        response = client.get(f"/v1/jobs/{job_id}")
        body: dict[str, Any] = response.json()
        if body["status"] in {"succeeded", "failed"}:
            return body
        time.sleep(0.05)
    raise TimeoutError(f"job {job_id} did not complete within {timeout}s")


def test_submit_scan_job_completes_and_matches_direct_scan(client: TestClient) -> None:
    submit = client.post(
        "/v1/jobs",
        params={"operation": "scan", "path": "examples/vulnerable-agent"},
    )
    assert submit.status_code == 200
    job = submit.json()
    assert job["status"] in {"queued", "running", "succeeded"}

    completed = _wait_for_completion(client, job["id"])
    assert completed["status"] == "succeeded"
    assert completed["result"]["summary"]["total"] == 13

    direct = client.get("/v1/scan", params={"path": "examples/vulnerable-agent"})
    assert completed["result"]["summary"] == direct.json()["summary"]


def test_submit_job_without_role_is_forbidden(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db_path = tmp_path / "rbac.db"
    monkeypatch.setenv("LATTENCE_RBAC_DB", str(db_path))
    monkeypatch.delenv("LATTENCE_API_TOKEN", raising=False)
    key = ApiKeyStore(db_path).create_key("bob", frozenset({Role.READ_FINDINGS}))
    limited_client = TestClient(create_app())

    response = limited_client.post(
        "/v1/jobs",
        params={"operation": "scan", "path": "."},
        headers={"Authorization": f"Bearer {key}"},
    )

    assert response.status_code == 403


def test_get_unknown_job_returns_404(client: TestClient) -> None:
    response = client.get("/v1/jobs/does-not-exist")
    assert response.status_code == 404


def test_list_jobs_includes_submitted_job(client: TestClient) -> None:
    submit = client.post(
        "/v1/jobs",
        params={"operation": "scan", "path": "examples/vulnerable-agent"},
    )
    job_id = submit.json()["id"]
    _wait_for_completion(client, job_id)

    listing = client.get("/v1/jobs")
    assert listing.status_code == 200
    assert any(job["id"] == job_id for job in listing.json())


def test_job_submission_and_completion_are_audited(client: TestClient) -> None:
    submit = client.post(
        "/v1/jobs",
        params={"operation": "scan", "path": "examples/vulnerable-agent"},
    )
    job_id = submit.json()["id"]
    _wait_for_completion(client, job_id)

    db_path = os.environ["LATTENCE_AUDIT_DB"]
    log = AuditLog(Path(db_path))
    submit_events = log.query(action="job_submit:scan")
    complete_events = log.query(action="job_complete:scan")
    assert any(event.details.get("job_id") == job_id for event in submit_events)
    assert any(event.details.get("job_id") == job_id for event in complete_events)
