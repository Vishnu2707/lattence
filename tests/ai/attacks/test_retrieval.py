from datetime import UTC, datetime
from pathlib import Path

import pytest
from lattence.discovery import load_rule_pack
from lattence.graph import Agent, Database, Dataset, Edge, SecurityGraph, Tool
from lattence_ai.attacks import AttackRunner

PACK_ROOT = Path(__file__).parents[3] / "lattence-packs" / "attacks" / "retrieval"


def _matched(
    rule_name: str,
    node: Database | Dataset,
    extra_nodes: tuple[object, ...] = (),
    edges: tuple[Edge, ...] = (),
) -> bool:
    graph = SecurityGraph(
        project_id="fixture",
        nodes=[node, *extra_nodes],
        edges=list(edges),
        generated_at=datetime(2026, 1, 1, tzinfo=UTC),
    )
    observations = AttackRunner(graph, (load_rule_pack(PACK_ROOT / rule_name),)).run()
    target = next(obs for obs in observations if obs.target_node_id == node.id)
    return target.matched


def _reachable_sink_fixture(
    sink: Database | Dataset,
) -> tuple[Agent, Tool, tuple[Edge, ...]]:
    tool = Tool(id="tool:retriever", name="retriever")
    agent = Agent(id="agent:rag", name="rag", tool_ids=[tool.id])
    edges = (
        Edge(id="e1", source_id=agent.id, target_id=tool.id, type="calls"),
        Edge(id="e2", source_id=tool.id, target_id=sink.id, type="accesses"),
    )
    return agent, tool, edges


@pytest.mark.parametrize(
    ("node", "expected", "reachable"),
    [
        (
            Database(
                id="database:vector",
                name="vector",
                engine="fixture",
                metadata={"vector_store": True},
            ),
            True,
            True,
        ),
        (Database(id="database:sql", name="sql", engine="sql"), False, True),
        (
            Database(
                id="database:orphan",
                name="orphan",
                engine="fixture",
                metadata={"vector_store": True},
            ),
            False,
            False,
        ),
    ],
)
def test_retrieval_corpus_poisoning(
    node: Database, expected: bool, reachable: bool
) -> None:
    extra: tuple[object, ...] = ()
    edges: tuple[Edge, ...] = ()
    if reachable:
        agent, tool, edges = _reachable_sink_fixture(node)
        extra = (agent, tool)
    assert _matched("poisoning.yaml", node, extra, edges) is expected


@pytest.mark.parametrize(
    ("node", "expected", "reachable"),
    [
        (Dataset(id="dataset:unknown", name="unknown"), True, True),
        (
            Dataset(id="dataset:internal", name="internal", sensitivity="internal"),
            False,
            True,
        ),
        (Dataset(id="dataset:isolated", name="isolated"), False, False),
    ],
)
def test_untrusted_retrieved_context(
    node: Dataset, expected: bool, reachable: bool
) -> None:
    extra: tuple[object, ...] = ()
    edges: tuple[Edge, ...] = ()
    if reachable:
        agent, tool, edges = _reachable_sink_fixture(node)
        extra = (agent, tool)
    assert _matched("untrusted-context.yaml", node, extra, edges) is expected
