from datetime import UTC, datetime
from pathlib import Path

import pytest
from lattence.discovery import load_rule_pack
from lattence.graph import MCPServer, SecurityGraph, Tool
from lattence_ai.attacks import AttackRunner

PACK_ROOT = Path(__file__).parents[3] / "lattence-packs" / "attacks" / "tools"


def _matched(rule_name: str, node: Tool | MCPServer) -> bool:
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
        (Tool(id="tool:open", name="open"), True),
        (
            Tool(
                id="tool:typed",
                name="typed",
                input_schema={"type": "object", "additionalProperties": False},
            ),
            False,
        ),
    ],
)
def test_tool_argument_injection(node: Tool, expected: bool) -> None:
    assert _matched("argument-injection.yaml", node) is expected


@pytest.mark.parametrize(
    ("node", "expected"),
    [
        (
            MCPServer(
                id="mcp_server:privileged",
                name="privileged",
                transport="stdio",
                auth_method="configured",
            ),
            True,
        ),
        (
            MCPServer(id="mcp_server:local", name="local", transport="stdio"),
            False,
        ),
    ],
)
def test_confused_deputy(node: MCPServer, expected: bool) -> None:
    assert _matched("confused-deputy.yaml", node) is expected
