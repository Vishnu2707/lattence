import fnmatch
import re
from dataclasses import dataclass

from lattence.graph import Model, SourceRef

from .dependencies import DependencyInventory
from .javascript_syntax import JavaScriptSyntax
from .models import RulePack
from .python_syntax import PythonSyntax

_PROVIDER_NAMES = {
    "LT-AI-201": "".join(("Open", "AI")),
    "LT-AI-202": "".join(("Anthro", "pic")),
    "LT-AI-203": "".join(("Gemi", "ni")),
    "LT-AI-204": "Cohere",
    "LT-AI-205": "Mistral",
    "LT-AI-206": "Ollama",
}


@dataclass(frozen=True, order=True)
class _ProviderObservation:
    path: str
    line: int | None
    kind: str
    value: str
    configured_model: bool = False


def _observations(
    dependencies: DependencyInventory,
    python_files: tuple[PythonSyntax, ...],
    javascript_files: tuple[JavaScriptSyntax, ...],
) -> tuple[_ProviderObservation, ...]:
    found: list[_ProviderObservation] = []
    for dependency in dependencies.dependencies:
        found.append(
            _ProviderObservation(
                dependency.source_path,
                dependency.source_line,
                "dependency",
                dependency.name,
            )
        )
    for python_syntax in python_files:
        found.extend(
            _ProviderObservation(
                python_syntax.path, item.location.line, "import", item.module
            )
            for item in python_syntax.imports
        )
        found.extend(
            _ProviderObservation(
                python_syntax.path,
                item.location.line,
                "call",
                item.function,
                "model" in item.keyword_names,
            )
            for item in python_syntax.calls
        )
    for javascript_syntax in javascript_files:
        found.extend(
            _ProviderObservation(
                javascript_syntax.path, item.location.line, "import", item.module
            )
            for item in javascript_syntax.imports
        )
        found.extend(
            _ProviderObservation(
                javascript_syntax.path, item.location.line, "call", item.function
            )
            for item in javascript_syntax.calls
        )
    return tuple(sorted(found))


def _matches(pattern: str, observation: _ProviderObservation) -> bool:
    kind, separator, value_pattern = pattern.partition(":")
    if not separator or kind != observation.kind:
        return False
    return fnmatch.fnmatchcase(observation.value.lower(), value_pattern.lower())


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def detect_models(
    rules: tuple[RulePack, ...],
    dependencies: DependencyInventory,
    python_files: tuple[PythonSyntax, ...] = (),
    javascript_files: tuple[JavaScriptSyntax, ...] = (),
) -> tuple[Model, ...]:
    observations = _observations(dependencies, python_files, javascript_files)
    models: list[Model] = []
    for rule in sorted(rules, key=lambda item: item.id):
        provider = _PROVIDER_NAMES.get(rule.id, rule.title)
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
        calls = [item for item in matches if item.kind == "call"]
        evidence = calls or [matches[0]]
        for item in evidence:
            line = item.line or 0
            models.append(
                Model(
                    id=f"model:{_slug(provider)}:{item.path}:{line}",
                    name=f"{provider} model",
                    source=SourceRef(path=item.path, line=item.line),
                    provider=provider,
                    model_name="configured" if item.configured_model else "unspecified",
                    local=provider == "Ollama",
                    metadata={"rule_id": rule.id},
                )
            )
    unique = {model.id: model for model in models}
    return tuple(unique[key] for key in sorted(unique))
