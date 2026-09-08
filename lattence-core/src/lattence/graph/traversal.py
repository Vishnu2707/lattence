from collections import deque
from collections.abc import Iterable
from dataclasses import dataclass

from .common import NodeId
from .schema import Edge, EdgeType, SecurityGraph


@dataclass(frozen=True, order=True)
class GraphPath:
    node_ids: tuple[NodeId, ...]
    edge_ids: tuple[str, ...]


def _adjacency(
    graph: SecurityGraph, edge_types: frozenset[EdgeType] | None
) -> dict[NodeId, tuple[Edge, ...]]:
    values: dict[NodeId, list[Edge]] = {}
    for edge in graph.edges:
        if edge_types is not None and edge.type not in edge_types:
            continue
        values.setdefault(edge.source_id, []).append(edge)
    return {
        node_id: tuple(sorted(edges, key=lambda item: (item.target_id, item.id)))
        for node_id, edges in values.items()
    }


def reachable_nodes(
    graph: SecurityGraph,
    start_ids: Iterable[NodeId],
    edge_types: frozenset[EdgeType] | None = None,
    max_depth: int | None = None,
) -> tuple[NodeId, ...]:
    if max_depth is not None and max_depth < 0:
        raise ValueError("max_depth must not be negative")
    known = {node.id for node in graph.nodes}
    starts = tuple(sorted(set(start_ids)))
    unknown = next((node_id for node_id in starts if node_id not in known), None)
    if unknown is not None:
        raise ValueError(f"unknown start node: {unknown}")

    adjacency = _adjacency(graph, edge_types)
    visited = set(starts)
    queue = deque((node_id, 0) for node_id in starts)
    reached: set[NodeId] = set()
    while queue:
        node_id, depth = queue.popleft()
        if max_depth is not None and depth >= max_depth:
            continue
        for edge in adjacency.get(node_id, ()):
            if edge.target_id in visited:
                continue
            visited.add(edge.target_id)
            reached.add(edge.target_id)
            queue.append((edge.target_id, depth + 1))
    return tuple(sorted(reached))


def find_attack_paths(
    graph: SecurityGraph,
    source_ids: Iterable[NodeId],
    target_ids: Iterable[NodeId],
    max_depth: int = 8,
    edge_types: frozenset[EdgeType] | None = None,
) -> tuple[GraphPath, ...]:
    if max_depth < 1:
        raise ValueError("max_depth must be positive")
    known = {node.id for node in graph.nodes}
    sources = tuple(sorted(set(source_ids)))
    targets = frozenset(target_ids)
    unknown = next(
        (node_id for node_id in (*sources, *sorted(targets)) if node_id not in known),
        None,
    )
    if unknown is not None:
        raise ValueError(f"unknown path node: {unknown}")

    adjacency = _adjacency(graph, edge_types)
    found: list[GraphPath] = []
    queue = deque(GraphPath((source,), ()) for source in sources)
    while queue:
        path = queue.popleft()
        if len(path.edge_ids) >= max_depth:
            continue
        for edge in adjacency.get(path.node_ids[-1], ()):
            if edge.target_id in path.node_ids:
                continue
            candidate = GraphPath(
                (*path.node_ids, edge.target_id), (*path.edge_ids, edge.id)
            )
            if edge.target_id in targets:
                found.append(candidate)
            else:
                queue.append(candidate)
    return tuple(sorted(found, key=lambda item: (len(item.edge_ids), item)))
