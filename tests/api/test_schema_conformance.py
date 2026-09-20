import json
from pathlib import Path

import jsonschema
from fastapi.testclient import TestClient

_SCHEMA = json.loads(Path("docs/schemas/report.v1.json").read_text(encoding="utf-8"))


def test_scan_response_conforms_to_report_schema(client: TestClient) -> None:
    response = client.get("/v1/scan", params={"path": "examples/vulnerable-agent"})
    assert response.status_code == 200
    jsonschema.Draft202012Validator(_SCHEMA).validate(response.json())


def test_attack_response_conforms_to_report_schema(client: TestClient) -> None:
    response = client.post(
        "/v1/attack",
        params={"path": "examples/vulnerable-agent", "offline": True},
    )
    assert response.status_code == 200
    jsonschema.Draft202012Validator(_SCHEMA).validate(response.json())
