from collections import deque
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Literal

from .common import NodeId
from .schema import Edge, EdgeType, SecurityGraph


@dataclass(frozen=True, order=True)
class GraphPath:
    node_ids: tuple[NodeId, ...]
    edge_ids: tuple[str, ...]


type TraversalDirection = Literal["forward", "reverse"]


@dataclass(frozen=True, order=True)
class TopologyHop:
    edge_id: str
    source_id: NodeId
    target_id: NodeId
    edge_type: EdgeType
    traversal: TraversalDirection
    from_node_id: NodeId
    to_node_id: NodeId
    evidence_refs: tuple[str, ...] = ()


@dataclass(frozen=True, order=True)
class TopologyPath:
    node_ids: tuple[NodeId, ...]
    hops: tuple[TopologyHop, ...]


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


def _topology_adjacency(
    graph: SecurityGraph, edge_types: frozenset[EdgeType] | None
) -> dict[NodeId, tuple[TopologyHop, ...]]:
    values: dict[NodeId, list[TopologyHop]] = {}
    for edge in graph.edges:
        if edge_types is not None and edge.type not in edge_types:
            continue
        values.setdefault(edge.source_id, []).append(
            TopologyHop(
                edge_id=edge.id,
                source_id=edge.source_id,
                target_id=edge.target_id,
                edge_type=edge.type,
                traversal="forward",
                from_node_id=edge.source_id,
                to_node_id=edge.target_id,
                evidence_refs=tuple(sorted(edge.evidence_refs)),
            )
        )
        values.setdefault(edge.target_id, []).append(
            TopologyHop(
                edge_id=edge.id,
                source_id=edge.source_id,
                target_id=edge.target_id,
                edge_type=edge.type,
                traversal="reverse",
                from_node_id=edge.target_id,
                to_node_id=edge.source_id,
                evidence_refs=tuple(sorted(edge.evidence_refs)),
            )
        )
    return {
        node_id: tuple(
            sorted(
                hops,
                key=lambda item: (
                    item.to_node_id,
                    item.edge_id,
                    item.traversal,
                ),
            )
        )
        for node_id, hops in values.items()
    }


def find_topology_paths(
    graph: SecurityGraph,
    source_ids: Iterable[NodeId],
    target_ids: Iterable[NodeId],
    max_depth: int = 8,
    edge_types: frozenset[EdgeType] | None = None,
) -> tuple[TopologyPath, ...]:
    """Return shortest simple topology paths while preserving edge direction."""
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
        raise ValueError(f"unknown topology node: {unknown}")

    adjacency = _topology_adjacency(graph, edge_types)
    found: list[TopologyPath] = []
    queue = deque(TopologyPath((source,), ()) for source in sources)
    while queue:
        path = queue.popleft()
        if len(path.hops) >= max_depth:
            continue
        for hop in adjacency.get(path.node_ids[-1], ()):
            if hop.to_node_id in path.node_ids:
                continue
            candidate = TopologyPath(
                (*path.node_ids, hop.to_node_id), (*path.hops, hop)
            )
            if hop.to_node_id in targets:
                found.append(candidate)
            else:
                queue.append(candidate)

    shortest: dict[tuple[NodeId, NodeId], int] = {}
    for path in found:
        key = (path.node_ids[0], path.node_ids[-1])
        shortest[key] = min(shortest.get(key, max_depth + 1), len(path.hops))
    return tuple(
        sorted(
            (
                path
                for path in found
                if len(path.hops) == shortest[(path.node_ids[0], path.node_ids[-1])]
            ),
            key=lambda item: (len(item.hops), item),
        )
    )
