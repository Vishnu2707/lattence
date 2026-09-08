from datetime import UTC, datetime
from pathlib import Path

from lattence.discovery import FindingTemplate, MatchSpec, RulePack
from lattence.evidence import (
    Report,
    build_report,
    normalize_rule_finding,
    report_json,
    write_json_report,
)
from lattence.graph import Agent, Project, SecurityGraph

SCHEMA = Path(__file__).parents[2] / "docs" / "schemas" / "report.v1.json"


def _report() -> Report:
    timestamp = datetime(2026, 1, 1, tzinfo=UTC)
    agent = Agent(id="agent:one", name="one")
    project = Project(
        id="project:fixture",
        name="fixture",
        root=".",
        scanned_at=timestamp,
        nodes=[agent],
    )
    graph = SecurityGraph(
        project_id=project.id,
        nodes=[agent],
        edges=[],
        generated_at=timestamp,
    )
    rule = RulePack(
        version="1",
        id="LT-AI-001",
        kind="attack",
        title="Fixture finding",
        description="Fixture rule.",
        severity="high",
        confidence="high",
        applies_to=["agent"],
        match=MatchSpec(graph={"field": "name", "equals": "one"}),
        finding=FindingTemplate(
            message="Fixture matched.", remediation="Fix the fixture."
        ),
    )
    finding = normalize_rule_finding(rule, agent.id, timestamp, 42)
    return build_report(project, graph, [finding], "0.0.0", 25)


def test_report_json_validates_and_is_stable() -> None:
    report = _report()

    rendered = report_json(report, SCHEMA)

    assert rendered == report_json(report, SCHEMA)
    assert Report.model_validate_json(rendered) == report
    assert report.summary.total == 1
    assert report.summary.high == 1


def test_writes_valid_json_report(tmp_path: Path) -> None:
    destination = tmp_path / "reports" / "report.json"

    write_json_report(_report(), destination, SCHEMA)

    assert destination.read_text(encoding="utf-8").endswith("\n")
