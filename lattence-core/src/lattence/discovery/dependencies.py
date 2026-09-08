import json
import re
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from packaging.requirements import InvalidRequirement, Requirement

from .inventory import ProjectFile


class DependencyManifestError(ValueError):
    pass


@dataclass(frozen=True, order=True)
class Dependency:
    ecosystem: Literal["python", "node"]
    name: str
    specifier: str
    group: str
    source_path: str
    source_line: int | None = None


@dataclass(frozen=True)
class DependencyInventory:
    dependencies: tuple[Dependency, ...]
    manifests: tuple[str, ...]


def _python_requirement(
    value: str, group: str, path: str, line: int | None
) -> Dependency:
    try:
        requirement = Requirement(value)
    except InvalidRequirement as error:
        raise DependencyManifestError(
            f"invalid Python requirement in {path}"
        ) from error
    specifier = str(requirement.specifier)
    if requirement.url:
        specifier = "direct-reference"
    if requirement.marker:
        specifier = f"{specifier}; {requirement.marker}".lstrip("; ")
    return Dependency("python", requirement.name, specifier, group, path, line)


def _string_list(value: object) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        return []
    return value


def _parse_pyproject(path: Path, relative: str) -> list[Dependency]:
    try:
        document = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as error:
        raise DependencyManifestError(f"cannot parse {relative}") from error

    dependencies: list[Dependency] = []
    project = document.get("project", {})
    if isinstance(project, dict):
        for value in _string_list(project.get("dependencies")):
            dependencies.append(_python_requirement(value, "runtime", relative, None))
        optional = project.get("optional-dependencies", {})
        if isinstance(optional, dict):
            for group, values in sorted(optional.items()):
                if not isinstance(group, str):
                    continue
                for value in _string_list(values):
                    dependencies.append(
                        _python_requirement(value, f"optional:{group}", relative, None)
                    )

    groups = document.get("dependency-groups", {})
    if isinstance(groups, dict):
        for group, values in sorted(groups.items()):
            if not isinstance(group, str):
                continue
            for value in _string_list(values):
                dependencies.append(
                    _python_requirement(value, f"group:{group}", relative, None)
                )
    return dependencies


def _parse_requirements(path: Path, relative: str) -> list[Dependency]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as error:
        raise DependencyManifestError(f"cannot read {relative}") from error

    dependencies: list[Dependency] = []
    for line_number, raw_line in enumerate(lines, start=1):
        line = raw_line.split(" #", 1)[0].strip()
        if not line or line.startswith(("#", "-")):
            continue
        dependencies.append(
            _python_requirement(line, "requirements", relative, line_number)
        )
    return dependencies


def _parse_package_json(path: Path, relative: str) -> list[Dependency]:
    try:
        document: object = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise DependencyManifestError(f"cannot parse {relative}") from error
    if not isinstance(document, dict):
        raise DependencyManifestError(f"manifest {relative} must contain an object")

    dependencies: list[Dependency] = []
    sections = {
        "dependencies": "runtime",
        "devDependencies": "development",
        "optionalDependencies": "optional",
        "peerDependencies": "peer",
    }
    for section, group in sections.items():
        values: Any = document.get(section, {})
        if not isinstance(values, dict):
            continue
        for name, specifier in sorted(values.items()):
            if isinstance(name, str) and isinstance(specifier, str):
                dependencies.append(
                    Dependency("node", name, specifier, group, relative, None)
                )
    return dependencies


def discover_dependency_manifests(
    root: Path, files: tuple[ProjectFile, ...]
) -> DependencyInventory:
    dependencies: list[Dependency] = []
    manifests: list[str] = []
    for project_file in files:
        relative = project_file.path
        name = Path(relative).name
        parser = None
        if name == "pyproject.toml":
            parser = _parse_pyproject
        elif re.fullmatch(r"requirements(?:[-.][\w-]+)?\.txt", name):
            parser = _parse_requirements
        elif name == "package.json":
            parser = _parse_package_json
        if parser is None:
            continue
        manifests.append(relative)
        dependencies.extend(parser(root / relative, relative))

    unique = {dependency: None for dependency in dependencies}
    return DependencyInventory(tuple(sorted(unique)), tuple(sorted(manifests)))
