from datetime import UTC, datetime
from pathlib import Path

import pytest
from lattence.discovery import load_rule_pack
from lattence.graph import Application, SecurityGraph
from lattence_ai.attacks import AttackRunner

RULE = (
    Path(__file__).parents[3]
    / "lattence-packs"
    / "attacks"
    / "availability"
    / "resource-boundary.yaml"
)


def _matched(node: Application) -> bool:
    graph = SecurityGraph(
        project_id="fixture",
        nodes=[node],
        edges=[],
        generated_at=datetime(2026, 1, 1, tzinfo=UTC),
    )
    return AttackRunner(graph, (load_rule_pack(RULE),)).run()[0].matched


@pytest.mark.parametrize(
    ("node", "expected"),
    [
        (Application(id="application:open", name="open"), True),
        (
            Application(
                id="application:bounded",
                name="bounded",
                metadata={"resource_limits": True},
            ),
            False,
        ),
    ],
)
def test_denial_resource_exhaustion_boundary(node: Application, expected: bool) -> None:
    assert _matched(node) is expected
