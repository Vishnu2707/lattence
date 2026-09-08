from datetime import UTC, datetime
from pathlib import Path

import pytest
from lattence.discovery import load_rule_pack
from lattence.graph import Secret, SecurityGraph, Tool
from lattence_ai.attacks import AttackRunner

PACK_ROOT = Path(__file__).parents[3] / "lattence-packs" / "attacks" / "output"


def _matched(rule_name: str, node: Tool | Secret) -> bool:
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
        (Tool(id="tool:write", name="write", side_effects=True), True),
        (Tool(id="tool:read", name="read"), False),
    ],
)
def test_unsafe_output_handling(node: Tool, expected: bool) -> None:
    assert _matched("unsafe-handling.yaml", node) is expected


@pytest.mark.parametrize(
    ("node", "expected"),
    [
        (
            Secret(
                id="secret:exposed",
                name="exposed",
                kind="token",
                location="config.py:1",
                exposed_value=True,
            ),
            True,
        ),
        (
            Secret(
                id="secret:reference",
                name="reference",
                kind="token",
                location="environment",
            ),
            False,
        ),
    ],
)
def test_data_disclosure(node: Secret, expected: bool) -> None:
    assert _matched("data-disclosure.yaml", node) is expected
