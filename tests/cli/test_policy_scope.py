from datetime import UTC, datetime
from pathlib import Path

import pytest
from lattence.cli.policy import ScopeValidationError, check_report_scope
from lattence.cli.targets import TargetDeclaration, load_scope_declaration
from lattence.discovery import FindingTemplate, MatchSpec, RulePack
from lattence.evidence import Report, build_report, normalize_rule_finding
from lattence.graph import Agent, Project, SecurityGraph, SourceRef

NOW = datetime(2026, 1, 1, tzinfo=UTC)


def _report(source_path: str = "src/agent.py") -> Report:
    agent = Agent(
        id="agent:one",
        name="one",
        source=SourceRef(path=source_path),
    )
    project = Project(
        id="project:fixture",
        name="fixture",
        root=".",
        scanned_at=NOW,
        nodes=[agent],
    )
    graph = SecurityGraph(
        project_id=project.id,
        nodes=[agent],
        edges=[],
        generated_at=NOW,
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
        finding=FindingTemplate(message="Matched.", remediation="Fix it."),
    )
    finding = normalize_rule_finding(rule, agent.id, NOW, 1)
    return build_report(project, graph, [finding], "0.0.0", 100)


def _declaration(value: str) -> TargetDeclaration:
    return TargetDeclaration.model_validate(
        {
            "version": "1",
            "authorization": "owned-or-authorized",
            "targets": [{"kind": "project", "value": value}],
        }
    )


def test_scope_loader_accepts_equivalent_file_path(tmp_path: Path) -> None:
    scope = tmp_path / "scope.yaml"
    scope.write_text(
        """\
version: "1"
authorization: owned-or-authorized
targets:
  - kind: project
    value: src
""",
        encoding="utf-8",
    )

    declaration = load_scope_declaration(scope)

    assert declaration.targets[0].value == "src"


def test_scope_check_accepts_target_below_declared_project_path() -> None:
    result = check_report_scope(_report(), _declaration("src"))

    assert result.allowed
    assert result.touched_node_ids == ("agent:one",)
    assert result.out_of_scope_node_ids == ()


def test_scope_check_rejects_target_outside_declared_project_path() -> None:
    result = check_report_scope(_report(), _declaration("tests"))

    assert not result.allowed
    assert result.out_of_scope_node_ids == ("agent:one",)


def test_scope_check_rejects_finding_with_missing_graph_target() -> None:
    report = _report().model_copy(
        update={
            "findings": [
                _report()
                .findings[0]
                .model_copy(update={"target_node_id": "agent:missing"})
            ]
        }
    )

    with pytest.raises(ScopeValidationError, match="missing graph node"):
        check_report_scope(report, _declaration("."))
