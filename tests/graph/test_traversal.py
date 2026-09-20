from datetime import UTC, datetime

import pytest
from lattence.graph import (
    Edge,
    SecurityGraph,
    Tool,
    find_attack_paths,
    find_topology_paths,
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


def test_topology_paths_retain_stored_and_traversal_directions() -> None:
    graph = _graph()

    paths = find_topology_paths(graph, ("tool:d",), ("tool:c",))

    assert len(paths) == 1
    assert paths[0].node_ids == ("tool:d", "tool:c")
    assert paths[0].hops[0].edge_id == "edge:cd"
    assert paths[0].hops[0].source_id == "tool:c"
    assert paths[0].hops[0].target_id == "tool:d"
    assert paths[0].hops[0].from_node_id == "tool:d"
    assert paths[0].hops[0].to_node_id == "tool:c"
    assert paths[0].hops[0].traversal == "reverse"


def test_topology_paths_return_only_shortest_simple_paths_per_endpoint() -> None:
    graph = _graph()

    paths = find_topology_paths(graph, ("tool:d",), ("tool:a",), max_depth=4)

    assert [path.node_ids for path in paths] == [
        ("tool:d", "tool:b", "tool:a"),
        ("tool:d", "tool:b", "tool:a"),
        ("tool:d", "tool:c", "tool:a"),
    ]
    assert [tuple(hop.edge_id for hop in path.hops) for path in paths] == [
        ("edge:bd", "edge:ab"),
        ("edge:bd", "edge:ba"),
        ("edge:cd", "edge:ac"),
    ]
    assert all(len(set(path.node_ids)) == len(path.node_ids) for path in paths)


def test_topology_paths_validate_nodes_depth_and_edge_filter() -> None:
    graph = _graph()

    assert (
        find_topology_paths(
            graph,
            ("tool:d",),
            ("tool:c",),
            edge_types=frozenset({"trusts"}),
        )
        == ()
    )
    with pytest.raises(ValueError, match="unknown topology node"):
        find_topology_paths(graph, ("tool:missing",), ("tool:a",))
    with pytest.raises(ValueError, match="max_depth must be positive"):
        find_topology_paths(graph, ("tool:a",), ("tool:d",), max_depth=0)
