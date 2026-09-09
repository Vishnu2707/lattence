from importlib.metadata import version

import pytest
from lattence.cli import app
from typer.testing import CliRunner

runner = CliRunner()
COMMANDS = [
    ["scan"],
    ["attack"],
    ["harden"],
    ["verify"],
    ["report"],
    ["tui"],
    ["pqc", "assess"],
    ["crypto", "chaos"],
    ["provider", "enable"],
    ["provider", "list"],
    ["graph", "export"],
    ["policy", "check"],
]
COMMON_OPTIONS = [
    "--json",
    "--out",
    "--offline",
    "--no-color",
    "--quiet",
    "--planner",
    "--fail-on",
]


def test_package_and_version_entrypoint() -> None:
    result = runner.invoke(app, ["--version"])

    assert result.exit_code == 0
    lines = result.stdout.splitlines()
    assert 1 <= len(lines) - 1 <= 6
    assert lines[-1] == f"lattence {version('lattence')}"


@pytest.mark.parametrize("command", COMMANDS)
def test_command_exposes_common_options(command: list[str]) -> None:
    result = runner.invoke(app, [*command, "--help"])

    assert result.exit_code == 0, result.output
    for option in COMMON_OPTIONS:
        assert option in result.stdout


def test_usage_errors_exit_with_two() -> None:
    result = runner.invoke(app, ["verify"])

    assert result.exit_code == 2
