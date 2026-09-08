import re
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from lattence.graph import Node, Project

from .agent_tools import detect_agents_and_tools
from .credentials import detect_identities
from .data_paths import detect_data_paths
from .dependencies import DependencyInventory, discover_dependency_manifests
from .frameworks import detect_frameworks
from .infrastructure import discover_infrastructure
from .inventory import ProjectInventory, inventory_project
from .javascript_syntax import (
    JavaScriptSyntax,
    JavaScriptSyntaxError,
    parse_javascript_file,
)
from .models import RulePack
from .providers import detect_models
from .python_syntax import PythonSyntax, PythonSyntaxError, parse_python_file
from .rules import load_rule_packs
from .services import detect_services


class DiscoveryError(ValueError):
    pass


@dataclass(frozen=True)
class DiscoveryResult:
    project: Project
    inventory: ProjectInventory
    dependencies: DependencyInventory
    errors: tuple[str, ...]


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "project"


def _syntax(
    inventory: ProjectInventory,
) -> tuple[tuple[PythonSyntax, ...], tuple[JavaScriptSyntax, ...], tuple[str, ...]]:
    python_files: list[PythonSyntax] = []
    javascript_files: list[JavaScriptSyntax] = []
    errors: list[str] = []
    for project_file in inventory.files:
        relative = project_file.path
        path = inventory.root / relative
        try:
            if path.suffix.lower() == ".py":
                python_files.append(parse_python_file(path, inventory.root))
            elif path.suffix.lower() in {".js", ".jsx", ".mjs", ".ts", ".tsx"}:
                javascript_files.append(parse_javascript_file(path, inventory.root))
        except (PythonSyntaxError, JavaScriptSyntaxError) as error:
            errors.append(str(error))
    return tuple(python_files), tuple(javascript_files), tuple(sorted(errors))


def _rules(rule_root: Path, category: str) -> tuple[RulePack, ...]:
    path = rule_root / category
    return tuple(load_rule_packs(path)) if path.is_dir() else ()


def _deduplicate(groups: Iterable[Iterable[Node]]) -> tuple[Node, ...]:
    nodes: dict[str, Node] = {}
    for group in groups:
        for node in group:
            existing = nodes.get(node.id)
            if existing is not None and existing != node:
                raise DiscoveryError(f"conflicting discovery node id: {node.id}")
            nodes[node.id] = node
    return tuple(nodes[key] for key in sorted(nodes))


def discover_project(
    root: Path,
    rule_root: Path,
    additional_nodes: Iterable[Node] = (),
    scanned_at: datetime | None = None,
) -> DiscoveryResult:
    inventory = inventory_project(root)
    dependencies = discover_dependency_manifests(inventory.root, inventory.files)
    python_files, javascript_files, errors = _syntax(inventory)

    framework_nodes = detect_frameworks(
        _rules(rule_root, "frameworks"),
        dependencies,
        python_files,
        javascript_files,
    )
    model_nodes = detect_models(
        _rules(rule_root, "providers"), dependencies, python_files, javascript_files
    )
    agent_tools = detect_agents_and_tools(
        framework_nodes, model_nodes, python_files, javascript_files
    )
    identities = detect_identities(
        inventory.root, inventory.files, python_files, javascript_files
    )
    infrastructure = discover_infrastructure(inventory.root, inventory.files)
    nodes = _deduplicate(
        (
            framework_nodes,
            model_nodes,
            agent_tools.agents,
            agent_tools.tools,
            detect_data_paths(
                _rules(rule_root, "data"),
                dependencies,
                python_files,
                javascript_files,
            ),
            detect_services(
                _rules(rule_root, "services"),
                dependencies,
                python_files,
                javascript_files,
            ),
            identities.secrets,
            identities.identities,
            infrastructure.applications,
            infrastructure.services,
            additional_nodes,
        )
    )
    project = Project(
        id=f"project:{_slug(inventory.root.name)}",
        name=inventory.root.name,
        root=".",
        scanned_at=scanned_at or datetime.now(UTC),
        nodes=list(nodes),
    )
    return DiscoveryResult(project, inventory, dependencies, errors)
