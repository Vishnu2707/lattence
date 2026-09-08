from datetime import UTC, datetime
from pathlib import Path

import pytest
from lattence.discovery import load_rule_pack
from lattence.graph import Agent, SecurityGraph, SourceRef
from lattence_ai.attacks import AttackRunner

PACK_ROOT = Path(__file__).parents[3] / "lattence-packs" / "attacks" / "instructions"


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
        (
            Agent(
                id="agent:sourced",
                name="sourced",
                instructions_source=SourceRef(path="instructions.md"),
            ),
            True,
        ),
        (Agent(id="agent:unset", name="unset"), False),
    ],
)
def test_system_instruction_extraction(node: Agent, expected: bool) -> None:
    assert _matched("extraction.yaml", node) is expected


@pytest.mark.parametrize(
    ("node", "expected"),
    [
        (
            Agent(id="agent:delegating", name="delegating", delegation_enabled=True),
            True,
        ),
        (Agent(id="agent:local", name="local"), False),
    ],
)
def test_system_instruction_override(node: Agent, expected: bool) -> None:
    assert _matched("override.yaml", node) is expected
