import re
from datetime import datetime
from pathlib import PurePosixPath

from .nodes import (
    API,
    Agent,
    Application,
    Certificate,
    CryptoAlgorithm,
    Database,
    Dataset,
    ExternalService,
    MCPServer,
    Node,
    Tool,
)
from .schema import Edge, EdgeType, Project, SecurityGraph


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _evidence(source: Node, target: Node) -> list[str]:
    return sorted(
        {node.source.path for node in (source, target) if node.source is not None}
    )


def _edge(source: Node, target: Node, edge_type: EdgeType) -> Edge:
    edge = Edge(
        id=f"edge:{_slug(source.id)}:{edge_type}:{_slug(target.id)}",
        source_id=source.id,
        target_id=target.id,
        type=edge_type,
        evidence_refs=_evidence(source, target),
    )
    if isinstance(target, Tool) and target.permissions:
        edge = edge.model_copy(
            update={"permission": ",".join(sorted(target.permissions))}
        )
    if isinstance(target, (API, ExternalService)):
        edge = edge.model_copy(update={"auth_method": target.auth_method})
    if isinstance(target, Database) and target.credential_id:
        edge = edge.model_copy(update={"auth_method": "credential"})
    if isinstance(target, MCPServer):
        edge = edge.model_copy(update={"transport": target.transport})
    if isinstance(target, CryptoAlgorithm):
        edge = edge.model_copy(update={"algorithm": target.algorithm})
    return edge


def _node_paths(node: Node) -> tuple[str, ...]:
    paths = [node.source.path] if node.source is not None else []
    if isinstance(node, Application):
        paths.extend(node.entrypoints)
    return tuple(sorted(set(paths)))


def _crypto_binding(source: Node, target: Node) -> tuple[str, tuple[str, ...]] | None:
    if not isinstance(source, (Application, Agent, Tool, MCPServer)):
        return None
    if not isinstance(target, (Certificate, CryptoAlgorithm)) or target.source is None:
        return None
    target_path = target.source.path
    source_paths = _node_paths(source)
    if source.source is not None and source.source.path == target_path:
        return "exact-source", (target_path,)
    if isinstance(source, Application) and target_path in source.entrypoints:
        return "application-entrypoint", (target_path,)
    referenced_by = target.metadata.get("referenced_by", [])
    if isinstance(referenced_by, list):
        matches = tuple(sorted(path for path in source_paths if path in referenced_by))
        if matches:
            return "config-reference", (*matches, target_path)
    same_module = tuple(
        path
        for path in source_paths
        if PurePosixPath(path).parent == PurePosixPath(target_path).parent
    )
    if same_module:
        return "module-proximity", (*same_module, target_path)
    return None


def _crypto_edge(source: Node, target: Certificate | CryptoAlgorithm) -> Edge | None:
    binding = _crypto_binding(source, target)
    if binding is None:
        return None
    reason, evidence_refs = binding
    edge_type: EdgeType = "protected_by"
    if isinstance(target, CryptoAlgorithm) and target.purpose in {
        "key exchange",
        "transport",
    }:
        edge_type = "key_exchange"
    return _edge(source, target, edge_type).model_copy(
        update={
            "evidence_refs": sorted(set(evidence_refs)),
            "metadata": {"binding_reason": reason},
        }
    )


def _same_source(source: Node, target: Node) -> bool:
    return bool(
        source.source and target.source and source.source.path == target.source.path
    )


def _application_owns(application: Application, node: Node) -> bool:
    if node.source is None:
        return False
    return node.source.path in {
        *application.entrypoints,
        *(tuple([application.source.path]) if application.source else ()),
    }


def _candidate_edges(nodes: tuple[Node, ...]) -> list[Edge]:
    edges: list[Edge] = []
    by_id = {node.id: node for node in nodes}
    for node in nodes:
        if isinstance(node, (Application, Agent, Tool, MCPServer)):
            for target in nodes:
                if isinstance(target, (Certificate, CryptoAlgorithm)):
                    crypto_edge = _crypto_edge(node, target)
                    if crypto_edge is not None:
                        edges.append(crypto_edge)
        if isinstance(node, Application):
            for target in nodes:
                if isinstance(target, (Agent, Tool)) and _application_owns(
                    node, target
                ):
                    edges.append(_edge(node, target, "contains"))
                elif isinstance(
                    target, (API, Database, ExternalService)
                ) and _application_owns(node, target):
                    edges.append(_edge(node, target, "calls"))
        elif isinstance(node, Agent):
            for target_id in (*node.model_ids, *node.tool_ids):
                referenced = by_id.get(target_id)
                if referenced is not None:
                    edges.append(_edge(node, referenced, "calls"))
        elif isinstance(node, MCPServer):
            for target_id in node.tool_ids:
                referenced = by_id.get(target_id)
                if isinstance(referenced, Tool):
                    edges.append(_edge(node, referenced, "contains"))
        elif isinstance(node, Tool):
            for target in nodes:
                if isinstance(
                    target, (Database, Dataset, ExternalService)
                ) and _same_source(node, target):
                    edges.append(_edge(node, target, "accesses"))
        elif isinstance(node, Database) and node.credential_id:
            referenced = by_id.get(node.credential_id)
            if referenced is not None:
                edges.append(_edge(node, referenced, "authenticated_by"))
        elif isinstance(node, Certificate):
            for target in nodes:
                if isinstance(target, CryptoAlgorithm) and _same_source(node, target):
                    edges.append(_edge(node, target, "protected_by"))
    return edges


def build_security_graph(
    project: Project, generated_at: datetime | None = None
) -> SecurityGraph:
    nodes = tuple(sorted(project.nodes, key=lambda item: item.id))
    candidates = _candidate_edges(nodes)
    unique = {edge.id: edge for edge in candidates}
    return SecurityGraph(
        version="1",
        project_id=project.id,
        nodes=list(nodes),
        edges=[unique[key] for key in sorted(unique)],
        generated_at=generated_at or project.scanned_at,
    )
