from lattence.cli.workflow import create_report, run_external_providers
from lattence.evidence import Finding
from lattence.graph import Node, Project, SecurityGraph
from lattence.providers import ProviderValidationError
from lattence_ai import RawResult
from lattence_ai import TestCase as ProviderTestCase


def _project(root) -> None:
    (root / "app.py").write_text(
        "from crewai import Agent\nagent = Agent()\n",
        encoding="utf-8",
    )
    (root / "pyproject.toml").write_text(
        '[project]\nname="fixture"\nversion="1"\ndependencies=["crewai"]\n',
        encoding="utf-8",
    )


class StaticProvider:
    def __init__(self, finding: Finding) -> None:
        self.finding = finding

    def discover(self, project: Project) -> list[Node]:
        return []

    def generate_tests(self, graph: SecurityGraph) -> list[ProviderTestCase]:
        return [
            ProviderTestCase(
                id="external:test",
                title="External test",
                target_node_id=self.finding.target_node_id,
                timeout_seconds=1,
                replay_seed=1,
            )
        ]

    def execute(self, test: ProviderTestCase) -> RawResult:
        return RawResult(
            provider="fixture",
            test_id=test.id,
            started_at=self.finding.evidence.started_at,
            finished_at=self.finding.evidence.finished_at,
            payload={},
        )

    def normalize_results(self, raw: RawResult) -> list[Finding]:
        return [self.finding]


def test_external_provider_findings_merge_into_report(tmp_path) -> None:
    _project(tmp_path)
    report = create_report(tmp_path)
    external = report.findings[0].model_copy(
        update={"id": "LT-EXT-001", "source": "fixture"}
    )

    merged = run_external_providers(report, [StaticProvider(external)])

    assert merged.summary.total == report.summary.total + 1
    assert any(item.id == "LT-EXT-001" for item in merged.findings)


def test_external_provider_rejects_duplicate_finding_id(tmp_path) -> None:
    _project(tmp_path)
    report = create_report(tmp_path)

    try:
        run_external_providers(report, [StaticProvider(report.findings[0])])
    except ProviderValidationError as error:
        assert "duplicate finding" in str(error)
    else:
        raise AssertionError("duplicate provider finding was accepted")
