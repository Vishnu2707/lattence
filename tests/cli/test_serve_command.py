import sys

import pytest
from lattence.cli import app
from typer.testing import CliRunner

runner = CliRunner()


def test_serve_help_lists_host_and_port() -> None:
    result = runner.invoke(app, ["serve", "--help"])
    assert result.exit_code == 0
    assert "--host" in result.output
    assert "--port" in result.output


def test_serve_without_api_extra_fails_clearly(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(sys.modules, "lattence_api", None)
    result = runner.invoke(app, ["serve"])
    assert result.exit_code != 0
    assert "api extra" in result.output
