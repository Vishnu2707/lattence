from datetime import UTC, datetime
from pathlib import Path

import pytest
from lattence.discovery import load_rule_pack
from lattence.graph import Database, Dataset, SecurityGraph
from lattence_ai.attacks import AttackRunner

PACK_ROOT = Path(__file__).parents[3] / "lattence-packs" / "attacks" / "retrieval"


def _matched(rule_name: str, node: Database | Dataset) -> bool:
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
            Database(
                id="database:vector",
                name="vector",
                engine="fixture",
                metadata={"vector_store": True},
            ),
            True,
        ),
        (Database(id="database:sql", name="sql", engine="sql"), False),
    ],
)
def test_retrieval_corpus_poisoning(node: Database, expected: bool) -> None:
    assert _matched("poisoning.yaml", node) is expected


@pytest.mark.parametrize(
    ("node", "expected"),
    [
        (Dataset(id="dataset:unknown", name="unknown"), True),
        (
            Dataset(id="dataset:internal", name="internal", sensitivity="internal"),
            False,
        ),
    ],
)
def test_untrusted_retrieved_context(node: Dataset, expected: bool) -> None:
    assert _matched("untrusted-context.yaml", node) is expected
