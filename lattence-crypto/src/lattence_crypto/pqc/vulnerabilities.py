from dataclasses import dataclass

from .graph import CryptoDependencyGraph, CryptoGraphEdge, CryptoGraphNode


@dataclass(frozen=True, order=True)
class QuantumVulnerablePath:
    target_id: str
    node_ids: tuple[str, ...]
    relationships: tuple[str, ...]
    source_paths: tuple[str, ...]
    transitive: bool


def _path_evidence(
    nodes: tuple[CryptoGraphNode, ...], edges: tuple[CryptoGraphEdge, ...]
) -> tuple[str, ...]:
    return tuple(
        sorted(
            {
                *(
                    node.source_path
                    for node in nodes
                    if node.source_path is not None
                ),
                *(reference for edge in edges for reference in edge.evidence_refs),
            }
        )
    )


def find_quantum_vulnerable_paths(
    graph: CryptoDependencyGraph,
) -> tuple[QuantumVulnerablePath, ...]:
    """Return every direct and transitive path into vulnerable crypto assets."""
    by_id = {node.id: node for node in graph.nodes}
    incoming: dict[str, list[CryptoGraphEdge]] = {}
    for edge in graph.edges:
        incoming.setdefault(edge.target_id, []).append(edge)
    for edges in incoming.values():
        edges.sort()

    findings: set[QuantumVulnerablePath] = set()
    vulnerable_nodes = sorted(
        (node for node in graph.nodes if node.quantum_status == "vulnerable"),
        key=lambda node: node.id,
    )
    for target in vulnerable_nodes:
        target_incoming = incoming.get(target.id, [])
        if not target_incoming:
            findings.add(
                QuantumVulnerablePath(
                    target_id=target.id,
                    node_ids=(target.id,),
                    relationships=(),
                    source_paths=_path_evidence((target,), ()),
                    transitive=False,
                )
            )
            continue

        stack: list[tuple[str, tuple[str, ...], tuple[CryptoGraphEdge, ...]]] = [
            (edge.source_id, (edge.source_id, target.id), (edge,))
            for edge in reversed(target_incoming)
        ]
        while stack:
            current_id, node_ids, path_edges = stack.pop()
            path_nodes = tuple(by_id[node_id] for node_id in node_ids)
            findings.add(
                QuantumVulnerablePath(
                    target_id=target.id,
                    node_ids=node_ids,
                    relationships=tuple(edge.relationship for edge in path_edges),
                    source_paths=_path_evidence(path_nodes, path_edges),
                    transitive=len(path_edges) > 1,
                )
            )
            for edge in reversed(incoming.get(current_id, [])):
                if edge.source_id in node_ids:
                    continue
                stack.append(
                    (
                        edge.source_id,
                        (edge.source_id, *node_ids),
                        (edge, *path_edges),
                    )
                )
    return tuple(sorted(findings))
