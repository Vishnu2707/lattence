from datetime import UTC, datetime

from lattence.discovery import FindingTemplate, MatchSpec, RulePack
from lattence.evidence import Report, build_report, normalize_rule_finding
from lattence.graph import Agent, Project, SecurityGraph
from lattence_ai.attacks import AttackRunner, VerificationOutcome, verify_finding

TIMESTAMP = datetime(2026, 1, 1, tzinfo=UTC)


def _rule() -> RulePack:
    return RulePack(
        version="1",
        id="LT-AGENT-001",
        kind="attack",
        title="Delegation boundary",
        description="Detect delegation without a boundary.",
        severity="high",
        confidence="high",
        applies_to=["agent"],
        match=MatchSpec(graph={"field": "delegation_enabled", "equals": True}),
        finding=FindingTemplate(
            message="Delegation is enabled.",
            remediation="Define a delegation boundary.",
        ),
    )


def _report(enabled: bool) -> Report:
    nodes = [Agent(id="agent:one", name="one", delegation_enabled=enabled)]
    graph = SecurityGraph(
        project_id="fixture", nodes=nodes, edges=[], generated_at=TIMESTAMP
    )
    project = Project(
        id="project:fixture",
        name="fixture",
        root=".",
        scanned_at=TIMESTAMP,
        nodes=nodes,
    )
    rule = _rule()
    runner = AttackRunner(graph, (rule,))
    findings = []
    for test in runner.generate_tests():
        observation = runner.observe(test)
        if observation.matched:
            findings.append(
                normalize_rule_finding(
                    rule, observation.target_node_id, observation.observed_at, 1
                )
            )
    return build_report(project, graph, findings, "0.0.0", 0.0)


def test_verify_finds_the_same_vulnerable_outcome() -> None:
    report = _report(enabled=True)

    outcome = verify_finding(report, "LT-AGENT-001", (_rule(),))

    assert outcome is VerificationOutcome.VULNERABLE


def test_verify_reports_resolved_when_the_target_no_longer_matches() -> None:
    vulnerable_report = _report(enabled=True)
    fixed_report = vulnerable_report.model_copy(
        update={"graph": _report(enabled=False).graph}
    )

    outcome = verify_finding(fixed_report, "LT-AGENT-001", (_rule(),))

    assert outcome is VerificationOutcome.RESOLVED


def test_verify_reports_not_found_for_an_unknown_finding_id() -> None:
    report = _report(enabled=True)

    outcome = verify_finding(report, "LT-AI-999", (_rule(),))

    assert outcome is VerificationOutcome.NOT_FOUND


def test_replay_returns_none_for_an_unknown_rule_or_node() -> None:
    graph = _report(enabled=True).graph
    runner = AttackRunner(graph, (_rule(),))

    assert runner.replay("LT-AI-999", "agent:one") is None
    assert runner.replay("LT-AGENT-001", "agent:missing") is None
