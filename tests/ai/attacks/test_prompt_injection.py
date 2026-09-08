from datetime import UTC, datetime
from pathlib import Path

import pytest
from lattence.discovery import load_rule_pack
from lattence.graph import Agent, Dataset, SecurityGraph, SourceRef
from lattence_ai.attacks import AttackRunner

PACK_ROOT = Path(__file__).parents[3] / "lattence-packs" / "attacks"


def _matched(rule_path: str, node: Agent | Dataset) -> bool:
    graph = SecurityGraph(
        project_id="fixture",
        nodes=[node],
        edges=[],
        generated_at=datetime(2026, 1, 1, tzinfo=UTC),
    )
    rule = load_rule_pack(PACK_ROOT / rule_path)
    return AttackRunner(graph, (rule,)).run()[0].matched


@pytest.mark.parametrize(
    ("node", "expected"),
    [
        (Agent(id="agent:open", name="open"), True),
        (
            Agent(
                id="agent:bounded",
                name="bounded",
                instructions_source=SourceRef(path="instructions.md"),
            ),
            False,
        ),
    ],
)
def test_direct_prompt_injection(node: Agent, expected: bool) -> None:
    assert _matched("prompt-injection/direct.yaml", node) is expected


@pytest.mark.parametrize(
    ("node", "expected"),
    [
        (Dataset(id="dataset:unknown", name="unknown"), True),
        (Dataset(id="dataset:public", name="public", sensitivity="public"), False),
    ],
)
def test_indirect_prompt_injection(node: Dataset, expected: bool) -> None:
    assert _matched("prompt-injection/indirect.yaml", node) is expected
