from datetime import UTC, datetime
from pathlib import Path

import jsonschema
import pytest
from lattence.discovery import FindingTemplate, MatchSpec, RulePack
from lattence.evidence import (
    Report,
    build_report,
    build_sarif,
    normalize_rule_finding,
    sarif_json,
)
from lattence.graph import Agent, Project, SecurityGraph


def _report(severity: str = "high") -> Report:
    timestamp = datetime(2026, 1, 1, tzinfo=UTC)
    agent = Agent(id="agent:one", name="one", source={"path": "app.py", "line": 12})
    project = Project(
        id="project:fixture",
        name="fixture",
        root=".",
        scanned_at=timestamp,
        nodes=[agent],
    )
    graph = SecurityGraph(
        project_id=project.id, nodes=[agent], edges=[], generated_at=timestamp
    )
    rule = RulePack(
        version="1",
        id="LT-AI-001",
        kind="attack",
        title="Fixture finding",
        description="Fixture rule.",
        severity=severity,
        confidence="high",
        applies_to=["agent"],
        match=MatchSpec(graph={"field": "name", "equals": "one"}),
        finding=FindingTemplate(
            message="Fixture matched.", remediation="Fix the fixture."
        ),
    )
    finding = normalize_rule_finding(rule, agent.id, timestamp, 42)
    return build_report(project, graph, [finding], "0.0.0", 25)


def test_sarif_json_validates_against_real_schema() -> None:
    import json

    document = json.loads(sarif_json(_report()))

    assert document["version"] == "2.1.0"
    run = document["runs"][0]
    assert run["tool"]["driver"]["name"] == "lattence"
    result = run["results"][0]
    assert result["ruleId"] == "LT-AI-001"
    assert result["level"] == "error"
    physical = result["locations"][0]["physicalLocation"]
    assert physical["artifactLocation"]["uri"] == "app.py"
    assert physical["region"]["startLine"] == 12


def test_build_sarif_maps_severity_to_level() -> None:
    document = build_sarif(_report(severity="medium"))

    assert document["runs"][0]["results"][0]["level"] == "warning"


def test_sarif_json_rejects_schema_mismatch(tmp_path: Path) -> None:
    import json

    bad_schema = tmp_path / "bad.json"
    bad_schema.write_text(json.dumps({"type": "object", "required": ["nope"]}))

    with pytest.raises(jsonschema.ValidationError):
        sarif_json(_report(), bad_schema)
