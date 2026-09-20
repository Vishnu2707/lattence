from datetime import UTC, datetime, timedelta

import pytest
from lattence.evidence import (
    EnvironmentFingerprint,
    EvidenceBundle,
    Finding,
    PolicyDecision,
    ReproductionRecipe,
)
from lattence.graph import Agent, Project, SecurityGraph
from lattence.providers import (
    ProviderValidationError,
    normalize_provider_result,
    validate_provider,
)
from lattence_ai import RawResult
from lattence_ai import TestCase as ProviderTestCase

NOW = datetime(2026, 1, 1, tzinfo=UTC)


def _finding(*, finding_id: str = "LT-AI-001", target: str = "agent:main") -> Finding:
    return Finding(
        id=finding_id,
        title="External engine finding",
        source="fixture",
        severity="high",
        confidence="high",
        target_node_id=target,
        evidence=EvidenceBundle(
            id=f"evidence:{finding_id}",
            inputs=[],
            transcript=[],
            telemetry_spans=[],
            policy_decision=PolicyDecision(
                policy_id="policy:external",
                outcome="fail",
                reason="External engine matched.",
            ),
            started_at=NOW,
            finished_at=NOW,
            environment=EnvironmentFingerprint(
                platform="test",
                python="3.12",
                lattence_version="0.0.0",
                dependency_digest="a" * 64,
                configuration_digest="b" * 64,
            ),
            replay_seed=7,
        ),
        reproduction=ReproductionRecipe(
            command=["fixture", "replay"],
            working_directory=".",
            expected="VULNERABLE",
        ),
        remediation="Apply a boundary.",
    )


class FixtureProvider:
    def __init__(self, findings: list[Finding] | None = None) -> None:
        self.findings = findings or [_finding()]

    def discover(self, project: Project) -> list[Agent]:
        return [Agent(id="agent:main", name=project.name)]

    def generate_tests(self, graph: SecurityGraph) -> list[ProviderTestCase]:
        return [
            ProviderTestCase(
                id="fixture:test",
                title="Fixture test",
                target_node_id=graph.nodes[0].id,
                timeout_seconds=1,
                replay_seed=7,
            )
        ]

    def execute(self, test: ProviderTestCase) -> RawResult:
        return RawResult(
            provider="fixture",
            test_id=test.id,
            started_at=NOW,
            finished_at=NOW,
            payload={"matched": True},
        )

    def normalize_results(self, raw: RawResult) -> list[Finding]:
        return self.findings


def _test() -> ProviderTestCase:
    return ProviderTestCase(
        id="fixture:test",
        title="Fixture test",
        target_node_id="agent:main",
        timeout_seconds=1,
        replay_seed=7,
    )


def test_provider_runtime_accepts_complete_implementation() -> None:
    assert validate_provider(FixtureProvider()) is not None


def test_provider_runtime_rejects_missing_method() -> None:
    with pytest.raises(ProviderValidationError, match="discover"):
        validate_provider(object())


def test_normalization_returns_valid_findings() -> None:
    provider = FixtureProvider()
    raw = provider.execute(_test())

    assert normalize_provider_result(provider, _test(), raw) == (_finding(),)


def test_normalization_rejects_mismatched_result_and_duplicate_findings() -> None:
    provider = FixtureProvider([_finding(), _finding()])
    raw = provider.execute(_test()).model_copy(update={"test_id": "wrong"})

    with pytest.raises(ProviderValidationError, match="test id"):
        normalize_provider_result(provider, _test(), raw)

    raw = provider.execute(_test())
    with pytest.raises(ProviderValidationError, match="duplicate finding"):
        normalize_provider_result(provider, _test(), raw)


def test_normalization_rejects_reversed_interval() -> None:
    raw = RawResult(
        provider="fixture",
        test_id="fixture:test",
        started_at=NOW,
        finished_at=NOW - timedelta(seconds=1),
        payload={},
    )

    with pytest.raises(ProviderValidationError, match="finished_at"):
        normalize_provider_result(FixtureProvider(), _test(), raw)
