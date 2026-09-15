import json
from datetime import UTC, datetime
from pathlib import Path

from lattence.graph import Model, SecurityGraph
from lattence.providers.promptfoo import PromptfooProvider

NOW = datetime(2026, 1, 1, tzinfo=UTC)


def _graph() -> SecurityGraph:
    return SecurityGraph(
        project_id="fixture",
        nodes=[
            Model(
                id="model:chat",
                name="chat",
                provider="fixture-provider",
                model_name="fixture-model",
                metadata={"promptfoo_target": "http://fixture.invalid/chat"},
            )
        ],
        edges=[],
        generated_at=NOW,
    )


def test_promptfoo_generates_tests_from_target_metadata() -> None:
    test = PromptfooProvider().generate_tests(_graph())[0]

    assert test.id == "promptfoo:model:chat"
    assert test.inputs == {"target": "http://fixture.invalid/chat"}


def test_promptfoo_runs_redteam_with_json_output(tmp_path: Path) -> None:
    commands: list[list[str]] = []

    def execute(command: list[str], output_path: Path) -> tuple[int, str]:
        commands.append(command)
        output_path.write_text(
            json.dumps({"results": {"results": []}}), encoding="utf-8"
        )
        return 0, ""

    provider = PromptfooProvider(executor=execute, work_directory=tmp_path)
    raw = provider.execute(provider.generate_tests(_graph())[0])

    assert commands == [
        [
            "promptfoo",
            "redteam",
            "run",
            "--target",
            "http://fixture.invalid/chat",
            "--output",
            str(tmp_path / "promptfoo-model-chat.json"),
        ]
    ]
    assert raw.error is None


def test_promptfoo_normalizes_failed_assertions_only() -> None:
    provider = PromptfooProvider()
    test = provider.generate_tests(_graph())[0]
    raw = provider.raw_result(
        test,
        {
            "results": {
                "results": [
                    {
                        "success": False,
                        "gradingResult": {"reason": "Prompt injection succeeded"},
                    },
                    {"success": True, "gradingResult": {"reason": "Blocked"}},
                ]
            }
        },
    )

    findings = provider.normalize_results(raw)

    assert len(findings) == 1
    assert findings[0].source == "promptfoo"
    assert findings[0].target_node_id == "model:chat"
    assert findings[0].title == "Promptfoo Prompt injection succeeded"


def test_promptfoo_returns_provider_error_for_missing_command() -> None:
    provider = PromptfooProvider(executor=lambda command, output: (127, "missing"))
    test = provider.generate_tests(_graph())[0]

    raw = provider.execute(test)

    assert raw.error == "missing"
    assert provider.normalize_results(raw) == []
