from datetime import UTC, datetime
from pathlib import Path

import pytest
from lattence.discovery import load_rule_pack
from lattence.graph import Agent, SecurityGraph, Tool
from lattence_ai.attacks import AttackRunner

PACK_ROOT = Path(__file__).parents[3] / "lattence-packs" / "attacks" / "agency"


def _matched(rule_name: str, node: Agent | Tool) -> bool:
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
            Agent(id="agent:delegating", name="delegating", delegation_enabled=True),
            True,
        ),
        (Agent(id="agent:bounded", name="bounded"), False),
    ],
)
def test_excessive_agency(node: Agent, expected: bool) -> None:
    assert _matched("excessive.yaml", node) is expected


@pytest.mark.parametrize(
    ("node", "expected"),
    [
        (Tool(id="tool:delete", name="delete", permissions={"delete"}), True),
        (Tool(id="tool:read", name="read", permissions={"read"}), False),
    ],
)
def test_unsafe_tool_use(node: Tool, expected: bool) -> None:
    assert _matched("unsafe-tool.yaml", node) is expected
