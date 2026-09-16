from dataclasses import dataclass
from typing import Literal

from lattence.graph import Certificate, CryptoAlgorithm, Node, SecurityGraph

from lattence_crypto.discovery import CryptoLibrary

type CryptoNodeKind = Literal[
    "algorithm", "certificate", "component", "library", "tls_configuration"
]


@dataclass(frozen=True, order=True)
class CryptoGraphNode:
    id: str
    kind: CryptoNodeKind
    name: str
    source_path: str | None = None
    quantum_status: str | None = None
    implementation: str | None = None
    purpose: str | None = None


@dataclass(frozen=True, order=True)
class CryptoGraphEdge:
    source_id: str
    target_id: str
    relationship: str
    evidence_refs: tuple[str, ...] = ()


@dataclass(frozen=True)
class CryptoDependencyGraph:
    nodes: tuple[CryptoGraphNode, ...]
    edges: tuple[CryptoGraphEdge, ...]


def _kind(node: Node) -> CryptoNodeKind:
    if isinstance(node, CryptoAlgorithm):
        if node.purpose == "transport":
            return "tls_configuration"
        return "algorithm"
    if isinstance(node, Certificate):
        return "certificate"
    return "component"


def _project_node(node: Node) -> CryptoGraphNode:
    source_path = node.source.path if node.source is not None else None
    if isinstance(node, CryptoAlgorithm):
        return CryptoGraphNode(
            id=node.id,
            kind=_kind(node),
            name=node.name,
            source_path=source_path,
            quantum_status=node.quantum_status,
            implementation=node.implementation,
            purpose=node.purpose,
        )
    quantum_status = None
    if isinstance(node, Certificate):
        certificate_algorithms = " ".join(
            filter(None, (node.public_key_algorithm, node.signature_algorithm))
        ).lower()
        if any(
            name in certificate_algorithms
            for name in ("dsa", "ec", "ed25519", "ed448", "rsa")
        ):
            quantum_status = "vulnerable"
    return CryptoGraphNode(
        id=node.id,
        kind=_kind(node),
        name=node.name,
        source_path=source_path,
        quantum_status=quantum_status,
        purpose="signature" if isinstance(node, Certificate) else None,
    )


def _library_node(library: CryptoLibrary) -> CryptoGraphNode:
    return CryptoGraphNode(
        id=f"crypto_library:{library.ecosystem}:{library.name}:{library.source_path}",
        kind="library",
        name=library.name,
        source_path=library.source_path,
        implementation=library.ecosystem,
    )


def build_crypto_graph(
    graph: SecurityGraph,
    libraries: tuple[CryptoLibrary, ...] = (),
) -> CryptoDependencyGraph:
    """Project crypto assets and every graph ancestor that can reach them."""
    crypto_ids = {
        node.id
        for node in graph.nodes
        if isinstance(node, (Certificate, CryptoAlgorithm))
    }
    included_ids = set(crypto_ids)
    changed = True
    while changed:
        changed = False
        for edge in graph.edges:
            if edge.target_id in included_ids and edge.source_id not in included_ids:
                included_ids.add(edge.source_id)
                changed = True

    projected_nodes = [
        _project_node(node) for node in graph.nodes if node.id in included_ids
    ]
    projected_edges = [
        CryptoGraphEdge(
            source_id=edge.source_id,
            target_id=edge.target_id,
            relationship=edge.type,
            evidence_refs=tuple(sorted(edge.evidence_refs)),
        )
        for edge in graph.edges
        if edge.source_id in included_ids and edge.target_id in included_ids
    ]

    algorithms = [node for node in graph.nodes if isinstance(node, CryptoAlgorithm)]
    for library in libraries:
        library_node = _library_node(library)
        projected_nodes.append(library_node)
        for algorithm in algorithms:
            algorithm_path = algorithm.source.path if algorithm.source else None
            if algorithm.implementation == library.source_path or (
                algorithm_path is not None and algorithm_path in library.referenced_by
            ):
                evidence_refs = tuple(
                    sorted(
                        {
                            library.source_path,
                            *(path for path in (algorithm_path,) if path is not None),
                        }
                    )
                )
                projected_edges.append(
                    CryptoGraphEdge(
                        source_id=library_node.id,
                        target_id=algorithm.id,
                        relationship="implements",
                        evidence_refs=evidence_refs,
                    )
                )

    return CryptoDependencyGraph(
        nodes=tuple(sorted(set(projected_nodes))),
        edges=tuple(sorted(set(projected_edges))),
    )
