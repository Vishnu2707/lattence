from typing import Protocol, cast, runtime_checkable

from lattence.evidence import Finding
from lattence.graph import Node, Project, SecurityGraph
from lattence_ai import RawResult, TestCase
from pydantic import TypeAdapter, ValidationError

_FINDINGS = TypeAdapter(list[Finding])
_METHODS = ("discover", "generate_tests", "execute", "normalize_results")


class ProviderValidationError(ValueError):
    """A provider or one of its results violates the frozen contract."""


@runtime_checkable
class SecurityProvider(Protocol):
    def discover(self, project: Project) -> list[Node]: ...

    def generate_tests(self, graph: SecurityGraph) -> list[TestCase]: ...

    def execute(self, test: TestCase) -> RawResult: ...

    def normalize_results(self, raw: RawResult) -> list[Finding]: ...


def validate_provider(provider: object) -> SecurityProvider:
    for method in _METHODS:
        candidate = getattr(provider, method, None)
        if not callable(candidate):
            raise ProviderValidationError(f"provider is missing method: {method}")
    return cast(SecurityProvider, provider)


def normalize_provider_result(
    provider: object, test: TestCase, raw: RawResult
) -> tuple[Finding, ...]:
    checked = validate_provider(provider)
    try:
        result = RawResult.model_validate(raw.model_dump())
    except ValidationError as error:
        raise ProviderValidationError(f"invalid raw result: {error}") from error
    if result.test_id != test.id:
        raise ProviderValidationError(
            f"provider result test id {result.test_id!r} does not match {test.id!r}"
        )
    if not result.provider:
        raise ProviderValidationError("provider result has an empty provider name")
    if result.finished_at < result.started_at:
        raise ProviderValidationError("provider result finished_at precedes started_at")
    try:
        findings = _FINDINGS.validate_python(
            checked.normalize_results(result), strict=True
        )
    except ValidationError as error:
        raise ProviderValidationError(f"invalid normalized finding: {error}") from error

    identifiers: set[str] = set()
    for finding in findings:
        if finding.id in identifiers:
            raise ProviderValidationError(f"duplicate finding id: {finding.id}")
        identifiers.add(finding.id)
        if finding.target_node_id != test.target_node_id:
            raise ProviderValidationError(
                f"finding {finding.id} targets {finding.target_node_id!r}, "
                f"expected {test.target_node_id!r}"
            )
    return tuple(findings)
