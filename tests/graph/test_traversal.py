from datetime import UTC, datetime

import pytest
from lattence.graph import (
    Edge,
    SecurityGraph,
    Tool,
    find_attack_paths,
    reachable_nodes,
)


def _graph() -> SecurityGraph:
    nodes = [Tool(id=f"tool:{name}", name=name) for name in "abcd"]
    edges = [
        Edge(id="edge:ab", source_id="tool:a", target_id="tool:b", type="calls"),
        Edge(id="edge:ac", source_id="tool:a", target_id="tool:c", type="trusts"),
        Edge(id="edge:bd", source_id="tool:b", target_id="tool:d", type="calls"),
        Edge(id="edge:cd", source_id="tool:c", target_id="tool:d", type="calls"),
        Edge(id="edge:ba", source_id="tool:b", target_id="tool:a", type="calls"),
    ]
    return SecurityGraph(
        project_id="fixture",
        nodes=nodes,
        edges=edges,
        generated_at=datetime(2026, 1, 1, tzinfo=UTC),
    )


def test_reachable_nodes_respect_type_and_depth_filters() -> None:
    graph = _graph()

    assert reachable_nodes(graph, ("tool:a",)) == (
        "tool:b",
        "tool:c",
        "tool:d",
    )
    assert reachable_nodes(graph, ("tool:a",), frozenset({"calls"}), max_depth=1) == (
        "tool:b",
    )


def test_attack_paths_are_simple_bounded_and_deterministic() -> None:
    paths = find_attack_paths(_graph(), ("tool:a",), ("tool:d",), max_depth=3)

    assert [path.node_ids for path in paths] == [
        ("tool:a", "tool:b", "tool:d"),
        ("tool:a", "tool:c", "tool:d"),
    ]


def test_unknown_nodes_and_invalid_depth_are_rejected() -> None:
    graph = _graph()

    with pytest.raises(ValueError, match="unknown start node"):
        reachable_nodes(graph, ("tool:missing",))
    with pytest.raises(ValueError, match="max_depth must be positive"):
        find_attack_paths(graph, ("tool:a",), ("tool:d",), max_depth=0)
