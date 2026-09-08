from datetime import UTC, datetime
from pathlib import Path

import pytest
from lattence.discovery import load_rule_pack
from lattence.graph import Agent, SecurityGraph
from lattence_ai.attacks import AttackRunner

PACK_ROOT = Path(__file__).parents[3] / "lattence-packs" / "attacks" / "agent-state"


def _matched(rule_name: str, node: Agent) -> bool:
    graph = SecurityGraph(
        project_id="fixture",
        nodes=[node],
        edges=[],
        generated_at=datetime(2026, 1, 1, tzinfo=UTC),
    )
    return (
        AttackRunner(graph, (load_rule_pack(PACK_ROOT / rule_name),)).run()[0].matched
    )


@pytest.mark.parametrize(
    ("node", "expected"),
    [
        (Agent(id="agent:delegate", name="delegate", delegation_enabled=True), True),
        (Agent(id="agent:local", name="local"), False),
    ],
)
def test_insecure_delegation(node: Agent, expected: bool) -> None:
    assert _matched("delegation.yaml", node) is expected


@pytest.mark.parametrize(
    ("node", "expected"),
    [
        (Agent(id="agent:memory", name="memory", memory_enabled=True), True),
        (Agent(id="agent:stateless", name="stateless"), False),
    ],
)
def test_memory_poisoning(node: Agent, expected: bool) -> None:
    assert _matched("memory-poisoning.yaml", node) is expected
