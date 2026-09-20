import os
from pathlib import Path

from fastapi.testclient import TestClient
from lattence.governance import AuditLog


def test_scan_records_a_completed_audit_event(client: TestClient) -> None:
    response = client.get("/v1/scan", params={"path": "examples/vulnerable-agent"})
    assert response.status_code == 200

    log = AuditLog(_audit_db_path())
    events = log.query(action="scan")
    assert events
    assert events[0].result == "completed"
    assert events[0].actor == "team-token"


def test_attack_records_a_completed_audit_event(client: TestClient) -> None:
    response = client.post(
        "/v1/attack",
        params={"path": "examples/vulnerable-agent", "offline": True},
    )
    assert response.status_code == 200

    log = AuditLog(_audit_db_path())
    events = log.query(action="attack")
    assert events
    assert events[0].result == "completed"


def _audit_db_path() -> Path:
    configured = os.environ.get("LATTENCE_AUDIT_DB")
    assert configured is not None
    return Path(configured)
