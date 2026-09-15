from dataclasses import dataclass
from pathlib import PurePosixPath
from urllib.parse import urlsplit

from lattence.evidence import Finding, Report
from lattence.graph import Node

from .targets import OwnedTarget, TargetDeclaration


class ScopeValidationError(ValueError):
    pass


@dataclass(frozen=True)
class ScopeCheck:
    allowed: bool
    touched_node_ids: tuple[str, ...]
    out_of_scope_node_ids: tuple[str, ...]


def _node_urls(node: Node) -> tuple[str, ...]:
    candidates: list[str | None] = []
    if node.type == "model":
        candidates.append(node.endpoint)
    elif node.type == "api":
        candidates.append(node.base_url)
    elif node.type == "mcp_server":
        candidates.append(node.url)
    elif node.type == "external_service":
        candidates.append(node.host)
    return tuple(
        candidate
        for candidate in candidates
        if candidate is not None and urlsplit(candidate).scheme in {"http", "https"}
    )


def _url_matches(actual: str, declared: str) -> bool:
    actual_parts = urlsplit(actual)
    declared_parts = urlsplit(declared)
    if (actual_parts.scheme, actual_parts.hostname, actual_parts.port) != (
        declared_parts.scheme,
        declared_parts.hostname,
        declared_parts.port,
    ):
        return False
    declared_path = declared_parts.path.rstrip("/")
    actual_path = actual_parts.path.rstrip("/")
    return not declared_path or actual_path == declared_path or actual_path.startswith(
        f"{declared_path}/"
    )


def _project_matches(node: Node, value: str) -> bool:
    if node.source is None:
        return value in {".", "./"} and not _node_urls(node)
    if value in {".", "./"}:
        return True
    source = PurePosixPath(node.source.path)
    scope = PurePosixPath(value)
    return source == scope or scope in source.parents


def _target_matches(node: Node, target: OwnedTarget) -> bool:
    if target.kind == "project":
        return _project_matches(node, target.value)
    return any(_url_matches(url, target.value) for url in _node_urls(node))


def _finding_allowed(
    finding: Finding, node: Node, declaration: TargetDeclaration
) -> bool:
    targets = declaration.targets
    node_urls = _node_urls(node)
    if not finding.reproduction.offline and node_urls:
        targets = [target for target in targets if target.kind == "url"]
    return any(_target_matches(node, target) for target in targets)


def check_report_scope(report: Report, declaration: TargetDeclaration) -> ScopeCheck:
    nodes = {node.id: node for node in report.graph.nodes}
    touched = sorted({finding.target_node_id for finding in report.findings})
    out_of_scope: list[str] = []
    for finding in report.findings:
        node = nodes.get(finding.target_node_id)
        if node is None:
            raise ScopeValidationError(
                f"finding {finding.id} references missing graph node: "
                f"{finding.target_node_id}"
            )
        if not _finding_allowed(finding, node, declaration):
            out_of_scope.append(node.id)
    denied = tuple(sorted(set(out_of_scope)))
    return ScopeCheck(
        allowed=not denied,
        touched_node_ids=tuple(touched),
        out_of_scope_node_ids=denied,
    )
