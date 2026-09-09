from pathlib import Path

from lattence.cli import app
from typer.testing import CliRunner

runner = CliRunner()
EXAMPLE = Path(__file__).parents[2] / "examples" / "vulnerable-agent"


def test_vulnerable_example_scans_and_attacks_offline(tmp_path: Path) -> None:
    scan = runner.invoke(
        app,
        [
            "scan",
            str(EXAMPLE),
            "--offline",
            "--no-color",
            "--out",
            str(tmp_path),
            "--fail-on",
            "none",
        ],
    )
    attack = runner.invoke(
        app,
        [
            "attack",
            str(EXAMPLE),
            "--offline",
            "--out",
            str(tmp_path),
            "--fail-on",
            "none",
        ],
    )

    assert scan.exit_code == 0, scan.output
    assert "Agents" in scan.stdout
    assert "MCP servers" in scan.stdout
    assert "PQC readiness" in scan.stdout
    assert attack.exit_code == 0, attack.output
    assert "LT-AI-002" in attack.stdout
    assert "Indirect chain" in attack.stdout
    assert "mcp_server" in attack.stdout
    assert (tmp_path / "lattence-report.json").is_file()
    assert (tmp_path / "lattence-report.html").is_file()
