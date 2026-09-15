import json
from pathlib import Path

import pytest
from lattence.cli import app
from typer.testing import CliRunner

runner = CliRunner()


def test_provider_enable_and_list_json(tmp_path: Path) -> None:
    enabled = runner.invoke(
        app, ["provider", "enable", "garak", "--out", str(tmp_path), "--json"]
    )
    listed = runner.invoke(app, ["provider", "list", "--out", str(tmp_path), "--json"])

    assert enabled.exit_code == 0, enabled.output
    assert json.loads(enabled.stdout)["enabled"] is True
    assert listed.exit_code == 0, listed.output
    providers = json.loads(listed.stdout)["providers"]
    assert next(item for item in providers if item["name"] == "garak")["enabled"]


def test_provider_enable_rejects_unknown_name(tmp_path: Path) -> None:
    result = runner.invoke(
        app, ["provider", "enable", "unknown", "--out", str(tmp_path)]
    )

    assert result.exit_code == 2
    assert "unknown provider" in result.output


def test_provider_list_plain_is_stable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("lattence.providers.registry.which", lambda name: None)
    result = runner.invoke(app, ["provider", "list", "--out", str(tmp_path)])

    assert result.exit_code == 0
    assert result.stdout.splitlines() == [
        "garak      disabled  unavailable",
        "promptfoo  disabled  unavailable",
        "pyrit      disabled  unavailable",
    ]
