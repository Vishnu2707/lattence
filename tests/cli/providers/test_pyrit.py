import json
from datetime import UTC, datetime

from lattence.graph import Model, SecurityGraph
from lattence.providers.pyrit import PyritProvider

NOW = datetime(2026, 1, 1, tzinfo=UTC)


def _graph() -> SecurityGraph:
    return SecurityGraph(
        project_id="fixture",
        nodes=[
            Model(
                id="model:chat",
                name="registered-chat",
                provider="fixture-provider",
                model_name="fixture-model",
                metadata={
                    "pyrit_scenario": "airt.jailbreak",
                    "pyrit_target": "registered-target",
                },
            )
        ],
        edges=[],
        generated_at=NOW,
    )


def test_pyrit_generates_tests_from_registered_target_metadata() -> None:
    test = PyritProvider().generate_tests(_graph())[0]

    assert test.id == "pyrit:model:chat"
    assert test.inputs == {
        "scenario": "airt.jailbreak",
        "target": "registered-target",
    }


def test_pyrit_executes_through_optional_scanner_command() -> None:
    commands: list[list[str]] = []

    def execute(command: list[str]) -> tuple[int, str, str]:
        commands.append(command)
        return (
            0,
            json.dumps(
                {
                    "results": [
                        {
                            "objective": "override safeguards",
                            "outcome": "success",
                            "score": 0.9,
                        }
                    ]
                }
            ),
            "",
        )

    provider = PyritProvider(executor=execute)
    test = provider.generate_tests(_graph())[0]

    raw = provider.execute(test)

    assert commands == [
        [
            "pyrit_scan",
            "run",
            "airt.jailbreak",
            "--target",
            "registered-target",
            "--output-format",
            "json",
        ]
    ]
    assert raw.error is None


def test_pyrit_normalizes_successful_attacks_only() -> None:
    provider = PyritProvider()
    test = provider.generate_tests(_graph())[0]
    raw = provider.raw_result(
        test,
        {
            "results": [
                {"objective": "override safeguards", "outcome": "success"},
                {"objective": "benign request", "outcome": "failure"},
            ]
        },
    )

    findings = provider.normalize_results(raw)

    assert len(findings) == 1
    assert findings[0].source == "pyrit"
    assert findings[0].target_node_id == "model:chat"
    assert findings[0].title == "PyRIT override safeguards"


def test_pyrit_returns_provider_error_for_missing_scanner() -> None:
    provider = PyritProvider(executor=lambda command: (127, "", "not installed"))
    test = provider.generate_tests(_graph())[0]

    raw = provider.execute(test)

    assert raw.error == "not installed"
    assert provider.normalize_results(raw) == []
