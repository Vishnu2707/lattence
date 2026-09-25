from datetime import UTC, datetime
from pathlib import Path

import pytest
from lattence.discovery import load_rule_pack
from lattence.graph import Agent, Dataset, Edge, SecurityGraph, SourceRef, Tool
from lattence_ai.attacks import AttackRunner

PACK_ROOT = Path(__file__).parents[3] / "lattence-packs" / "attacks"


def _matched(
    rule_path: str,
    node: Agent | Dataset,
    extra_nodes: tuple[object, ...] = (),
    edges: tuple[Edge, ...] = (),
) -> bool:
    graph = SecurityGraph(
        project_id="fixture",
        nodes=[node, *extra_nodes],
        edges=list(edges),
        generated_at=datetime(2026, 1, 1, tzinfo=UTC),
    )
    rule = load_rule_pack(PACK_ROOT / rule_path)
    observations = AttackRunner(graph, (rule,)).run()
    target = next(obs for obs in observations if obs.target_node_id == node.id)
    return target.matched


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


def _reachable_dataset_fixture(
    dataset: Dataset,
) -> tuple[Agent, Tool, tuple[Edge, ...]]:
    tool = Tool(id="tool:retriever", name="retriever")
    agent = Agent(id="agent:rag", name="rag", tool_ids=[tool.id])
    edges = (
        Edge(id="e1", source_id=agent.id, target_id=tool.id, type="calls"),
        Edge(id="e2", source_id=tool.id, target_id=dataset.id, type="accesses"),
    )
    return agent, tool, edges


@pytest.mark.parametrize(
    ("node", "expected", "reachable"),
    [
        (Dataset(id="dataset:unknown", name="unknown"), True, True),
        (
            Dataset(id="dataset:public", name="public", sensitivity="public"),
            False,
            True,
        ),
        (Dataset(id="dataset:isolated", name="isolated"), False, False),
    ],
)
def test_indirect_prompt_injection(
    node: Dataset, expected: bool, reachable: bool
) -> None:
    extra: tuple[object, ...] = ()
    edges: tuple[Edge, ...] = ()
    if reachable:
        agent, tool, edges = _reachable_dataset_fixture(node)
        extra = (agent, tool)
    assert _matched("prompt-injection/indirect.yaml", node, extra, edges) is expected
