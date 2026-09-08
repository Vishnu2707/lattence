import fnmatch
import re
from dataclasses import dataclass

from lattence.graph import Agent, Application, Node, SourceRef

from .dependencies import DependencyInventory
from .javascript_syntax import JavaScriptSyntax
from .models import RulePack
from .python_syntax import PythonSyntax


@dataclass(frozen=True, order=True)
class _Observation:
    path: str
    line: int | None
    runtime: str
    kind: str
    value: str


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _observations(
    dependencies: DependencyInventory,
    python_files: tuple[PythonSyntax, ...],
    javascript_files: tuple[JavaScriptSyntax, ...],
) -> tuple[_Observation, ...]:
    found: list[_Observation] = []
    for dependency in dependencies.dependencies:
        found.append(
            _Observation(
                dependency.source_path,
                dependency.source_line,
                dependency.ecosystem,
                "dependency",
                dependency.name,
            )
        )
    for python_syntax in python_files:
        for python_import in python_syntax.imports:
            found.append(
                _Observation(
                    python_syntax.path,
                    python_import.location.line,
                    "python",
                    "import",
                    python_import.module,
                )
            )
        for python_call in python_syntax.calls:
            found.append(
                _Observation(
                    python_syntax.path,
                    python_call.location.line,
                    "python",
                    "call",
                    python_call.function,
                )
            )
    for javascript_syntax in javascript_files:
        for javascript_import in javascript_syntax.imports:
            found.append(
                _Observation(
                    javascript_syntax.path,
                    javascript_import.location.line,
                    "node",
                    "import",
                    javascript_import.module,
                )
            )
        for javascript_call in javascript_syntax.calls:
            found.append(
                _Observation(
                    javascript_syntax.path,
                    javascript_call.location.line,
                    "node",
                    "call",
                    javascript_call.function,
                )
            )
    return tuple(sorted(found))


def _matches(pattern: str, observation: _Observation) -> bool:
    prefix, separator, value_pattern = pattern.partition(":")
    if not separator:
        return False
    kind = "call" if prefix in {"call", "agent-call"} else prefix
    return observation.kind == kind and fnmatch.fnmatchcase(
        observation.value.lower(), value_pattern.lower()
    )


def _rule_matches(
    rule: RulePack, observations: tuple[_Observation, ...]
) -> tuple[_Observation, ...]:
    patterns = [
        *(f"dependency:{value}" for value in rule.match.dependencies or []),
        *(rule.match.syntax or []),
    ]
    return tuple(
        observation
        for observation in observations
        if any(_matches(pattern, observation) for pattern in patterns)
    )


def detect_frameworks(
    rules: tuple[RulePack, ...],
    dependencies: DependencyInventory,
    python_files: tuple[PythonSyntax, ...] = (),
    javascript_files: tuple[JavaScriptSyntax, ...] = (),
) -> tuple[Node, ...]:
    observations = _observations(dependencies, python_files, javascript_files)
    nodes: list[Node] = []
    for rule in sorted(rules, key=lambda item: item.id):
        matches = _rule_matches(rule, observations)
        if not matches:
            continue
        first = matches[0]
        source = SourceRef(path=first.path, line=first.line)
        slug = _slug(rule.title)
        entrypoints = sorted(
            {item.path for item in matches if item.kind in {"import", "call"}}
        )
        runtime = next(
            (item.runtime for item in matches if item.runtime in {"python", "node"}),
            None,
        )
        nodes.append(
            Application(
                id=f"application:{slug}",
                name=rule.title,
                source=source,
                frameworks=[rule.title],
                entrypoints=entrypoints,
                runtime=runtime,
                metadata={"rule_id": rule.id},
            )
        )
        agent_patterns = [
            pattern
            for pattern in rule.match.syntax or []
            if pattern.startswith("agent-call:")
        ]
        for observation in matches:
            if not any(_matches(pattern, observation) for pattern in agent_patterns):
                continue
            line = observation.line or 0
            nodes.append(
                Agent(
                    id=f"agent:{slug}:{observation.path}:{line}",
                    name=observation.value.rsplit(".", 1)[-1],
                    source=SourceRef(path=observation.path, line=observation.line),
                    framework=rule.title,
                    metadata={"rule_id": rule.id},
                )
            )
    return tuple(nodes)
