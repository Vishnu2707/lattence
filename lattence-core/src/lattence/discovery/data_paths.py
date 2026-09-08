import fnmatch
import re
from dataclasses import dataclass

from lattence.graph import Database, Dataset, Node, SourceRef

from .dependencies import DependencyInventory
from .javascript_syntax import JavaScriptSyntax
from .models import RulePack
from .python_syntax import PythonSyntax


@dataclass(frozen=True, order=True)
class _DataObservation:
    path: str
    line: int | None
    kind: str
    value: str


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _observations(
    dependencies: DependencyInventory,
    python_files: tuple[PythonSyntax, ...],
    javascript_files: tuple[JavaScriptSyntax, ...],
) -> tuple[_DataObservation, ...]:
    values = [
        _DataObservation(item.source_path, item.source_line, "dependency", item.name)
        for item in dependencies.dependencies
    ]
    for python_syntax in python_files:
        values.extend(
            _DataObservation(
                python_syntax.path, item.location.line, "import", item.module
            )
            for item in python_syntax.imports
        )
        values.extend(
            _DataObservation(
                python_syntax.path, item.location.line, "call", item.function
            )
            for item in python_syntax.calls
        )
    for javascript_syntax in javascript_files:
        values.extend(
            _DataObservation(
                javascript_syntax.path, item.location.line, "import", item.module
            )
            for item in javascript_syntax.imports
        )
        values.extend(
            _DataObservation(
                javascript_syntax.path, item.location.line, "call", item.function
            )
            for item in javascript_syntax.calls
        )
    return tuple(sorted(values))


def _matches(pattern: str, observation: _DataObservation) -> bool:
    kind, separator, expected = pattern.partition(":")
    return bool(
        separator
        and kind == observation.kind
        and fnmatch.fnmatchcase(observation.value.lower(), expected.lower())
    )


def detect_data_paths(
    rules: tuple[RulePack, ...],
    dependencies: DependencyInventory,
    python_files: tuple[PythonSyntax, ...] = (),
    javascript_files: tuple[JavaScriptSyntax, ...] = (),
) -> tuple[Node, ...]:
    observations = _observations(dependencies, python_files, javascript_files)
    nodes: list[Node] = []
    for rule in sorted(rules, key=lambda item: item.id):
        patterns = [
            *(f"dependency:{value}" for value in rule.match.dependencies or []),
            *(rule.match.syntax or []),
        ]
        matches = tuple(
            item
            for item in observations
            if any(_matches(pattern, item) for pattern in patterns)
        )
        if not matches:
            continue
        first = matches[0]
        source = SourceRef(path=first.path, line=first.line)
        slug = _slug(rule.title)
        if "database" in rule.applies_to:
            nodes.append(
                Database(
                    id=f"database:{slug}",
                    name=rule.title,
                    source=source,
                    engine=slug,
                    metadata={"rule_id": rule.id, "vector_store": True},
                )
            )
        if "dataset" not in rule.applies_to:
            continue
        calls = [item for item in matches if item.kind == "call"]
        for item in calls:
            line = item.line or 0
            nodes.append(
                Dataset(
                    id=f"dataset:{slug}:{item.path}:{line}",
                    name=f"{rule.title} data path",
                    source=SourceRef(path=item.path, line=item.line),
                    vectorized=True,
                    metadata={"rule_id": rule.id, "operation": item.value},
                )
            )
    unique = {node.id: node for node in nodes}
    return tuple(unique[key] for key in sorted(unique))
