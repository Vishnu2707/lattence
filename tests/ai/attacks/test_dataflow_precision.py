"""Regression tests for the "sink shape without real data flow" bug class.

A real self-scan false positive was found at
lattence-cli/src/lattence/cli/workflow.py:208: the discovery layer
mistakenly classified a plain f-string error message as a `dataset` node
whose `sensitivity` field defaults to `unknown`. Rules LT-AI-002,
LT-AI-007, and LT-AI-008 matched that field shape alone, so they fired as
if untrusted, unclassified retrieved context had reached an agent, even
though the node was never wired into any agent's tool path. It looked
like a sink because of its field values, not because anything actually
flowed into it.

Each rule below now also requires `AttackRunner` to find a genuine graph
path (agent -calls-> tool -accesses-> sink) using the existing
`lattence.graph.traversal` machinery via `match.requires_path`, not a
second traversal mechanism. Each test pairs a fixture that should
genuinely fire (the sink sits on a real agent tool path) with a fixture
that only superficially resembles it (same field shape, no path), styled
directly on the workflow.py case: a node that matches on shape alone but
carries no real data-flow edge to any agent.
"""

from datetime import UTC, datetime
from pathlib import Path

from lattence.discovery import load_rule_pack
from lattence.graph import Agent, Database, Dataset, Edge, SecurityGraph, Tool
from lattence_ai.attacks import AttackRunner

PACK_ROOT = Path(__file__).parents[3] / "lattence-packs" / "attacks"


def _observe(rule_path: str, nodes: tuple[object, ...], edges: tuple[Edge, ...]):
    graph = SecurityGraph(
        project_id="fixture",
        nodes=list(nodes),
        edges=list(edges),
        generated_at=datetime(2026, 1, 1, tzinfo=UTC),
    )
    rule = load_rule_pack(PACK_ROOT / rule_path)
    observations = AttackRunner(graph, (rule,)).run()
    return {obs.target_node_id: obs.matched for obs in observations}


def _real_rag_path(sink_id: str) -> tuple[Agent, Tool, tuple[Edge, ...]]:
    tool = Tool(id="tool:retriever", name="retriever")
    agent = Agent(id="agent:rag", name="rag", tool_ids=[tool.id])
    edges = (
        Edge(id="e1", source_id=agent.id, target_id=tool.id, type="calls"),
        Edge(id="e2", source_id=tool.id, target_id=sink_id, type="accesses"),
    )
    return agent, tool, edges


def test_indirect_prompt_injection_requires_real_path() -> None:
    """LT-AI-002: workflow.py-style isolated node must not fire."""
    genuine = Dataset(id="dataset:rag-pipeline:app.py:15", name="rag context")
    agent, tool, edges = _real_rag_path(genuine.id)

    # Superficially resembles the same rule shape (sensitivity=unknown) but
    # is a discovery artifact with no agent ever wired to it, exactly the
    # workflow.py:208 case: an f-string mistaken for a dataset reference.
    decoy = Dataset(id="dataset:chroma:workflow.py:208", name="error message")

    matched = _observe(
        "prompt-injection/indirect.yaml",
        (genuine, agent, tool, decoy),
        edges,
    )
    assert matched[genuine.id] is True
    assert matched[decoy.id] is False


def test_untrusted_retrieved_context_requires_real_path() -> None:
    """LT-AI-008: same field shape, same fix, same regression shape."""
    genuine = Dataset(id="dataset:rag-pipeline:app.py:15", name="rag context")
    agent, tool, edges = _real_rag_path(genuine.id)
    decoy = Dataset(id="dataset:chroma:workflow.py:208", name="error message")

    matched = _observe(
        "retrieval/untrusted-context.yaml",
        (genuine, agent, tool, decoy),
        edges,
    )
    assert matched[genuine.id] is True
    assert matched[decoy.id] is False


def test_retrieval_corpus_poisoning_requires_real_path() -> None:
    """LT-AI-007: a vector-store-shaped database with no agent path is inert."""
    genuine = Database(
        id="database:chroma",
        name="chroma",
        engine="chroma",
        metadata={"vector_store": True},
    )
    agent, tool, edges = _real_rag_path(genuine.id)

    # Same vector_store metadata shape, but discovered from an unrelated
    # config file never reached by any agent's tool.
    decoy = Database(
        id="database:chroma:orphan-config",
        name="orphan chroma config",
        engine="chroma",
        metadata={"vector_store": True},
    )

    matched = _observe(
        "retrieval/poisoning.yaml",
        (genuine, agent, tool, decoy),
        edges,
    )
    assert matched[genuine.id] is True
    assert matched[decoy.id] is False
