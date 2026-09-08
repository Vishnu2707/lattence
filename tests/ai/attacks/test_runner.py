from datetime import UTC, datetime

import pytest
from lattence.discovery import FindingTemplate, MatchSpec, RulePack
from lattence.graph import Agent, SecurityGraph
from lattence_ai.attacks import AttackRunner
from lattence_ai.attacks import TestCase as AttackTestCase


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


def _graph(enabled: bool) -> SecurityGraph:
    return SecurityGraph(
        project_id="fixture",
        nodes=[Agent(id="agent:one", name="one", delegation_enabled=enabled)],
        edges=[],
        generated_at=datetime(2026, 1, 1, tzinfo=UTC),
    )


def test_runner_generates_and_executes_matching_tests() -> None:
    runner = AttackRunner(_graph(True), (_rule(),))

    tests = runner.generate_tests()
    observation = runner.observe(tests[0])
    raw = runner.execute(tests[0])

    assert observation.matched
    assert observation.target_node_id == "agent:one"
    assert raw.payload["matched"] is True
    assert raw.error is None
    assert tests == runner.generate_tests()


def test_runner_records_negative_observation() -> None:
    observation = AttackRunner(_graph(False), (_rule(),)).run()[0]

    assert not observation.matched


def test_runner_rejects_unknown_rule_reference() -> None:
    runner = AttackRunner(_graph(True), (_rule(),))
    invalid = AttackTestCase(
        id="invalid",
        title="invalid",
        target_node_id="agent:one",
        inputs={"rule_id": "LT-AI-999"},
        timeout_seconds=1,
        replay_seed=1,
    )

    with pytest.raises(ValueError, match="unknown attack rule"):
        runner.observe(invalid)
