import json
from datetime import UTC, datetime
from pathlib import Path

from lattence.graph import Model, Project, SecurityGraph
from lattence.providers.garak import GarakProvider

NOW = datetime(2026, 1, 1, tzinfo=UTC)


def _model() -> Model:
    return Model(
        id="model:chat",
        name="chat",
        provider="fixture-provider",
        model_name="fixture-model",
    )


def _graph() -> SecurityGraph:
    return SecurityGraph(
        project_id="fixture",
        nodes=[_model()],
        edges=[],
        generated_at=NOW,
    )


def test_garak_generates_deterministic_model_tests() -> None:
    provider = GarakProvider()

    tests = provider.generate_tests(_graph())

    assert len(tests) == 1
    assert tests[0].id == "garak:model:chat"
    assert tests[0].target_node_id == "model:chat"
    assert tests[0].inputs == {
        "target_name": "fixture-model",
        "target_type": "fixture-provider",
    }


def test_garak_discovers_no_additional_project_nodes() -> None:
    project = Project(
        id="fixture",
        name="fixture",
        root=".",
        scanned_at=NOW,
        nodes=[_model()],
    )

    assert GarakProvider().discover(project) == []


def test_garak_executes_without_importing_the_optional_package(tmp_path: Path) -> None:
    commands: list[list[str]] = []

    def execute(command: list[str], report_path: Path) -> tuple[int, str]:
        commands.append(command)
        report_path.write_text(
            json.dumps(
                {
                    "entry_type": "eval",
                    "probe": "promptinject.Hijack",
                    "detector": "mitigation.MitigationBypass",
                    "passed": 0,
                    "total": 1,
                }
            )
            + "\n",
            encoding="utf-8",
        )
        return 0, ""

    provider = GarakProvider(executor=execute, work_directory=tmp_path)
    test = provider.generate_tests(_graph())[0]

    raw = provider.execute(test)

    assert commands == [
        [
            "garak",
            "--target_type",
            "fixture-provider",
            "--target_name",
            "fixture-model",
            "--report_prefix",
            str(tmp_path / "garak-model-chat"),
            "--narrow_output",
        ]
    ]
    assert raw.error is None
    assert raw.payload["records"][0]["entry_type"] == "eval"


def test_garak_normalizes_failed_evaluations_and_ignores_passes() -> None:
    provider = GarakProvider()
    test = provider.generate_tests(_graph())[0]
    raw = provider.raw_result(
        test,
        [
            {
                "entry_type": "eval",
                "probe": "promptinject.Hijack",
                "detector": "mitigation.Bypass",
                "passed": 0,
                "total": 1,
            },
            {
                "entry_type": "eval",
                "probe": "xss.Markdown",
                "detector": "xss.MarkdownExfil",
                "passed": 1,
                "total": 1,
            },
        ],
    )

    findings = provider.normalize_results(raw)

    assert len(findings) == 1
    assert findings[0].source == "garak"
    assert findings[0].target_node_id == "model:chat"
    assert findings[0].title == "Garak promptinject.Hijack"
    assert findings[0].evidence.inputs[0].value["failed"] == 1
    assert findings[0].reproduction.command[0] == "garak"
