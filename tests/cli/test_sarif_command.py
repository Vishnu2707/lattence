import json
from pathlib import Path

from lattence.cli import app
from typer.testing import CliRunner

runner = CliRunner()


def test_sarif_writes_valid_document(tmp_path: Path) -> None:
    report_path = tmp_path / "lattence-report.json"
    runner.invoke(
        app, ["scan", "examples/vulnerable-agent", "--quiet", "--out", str(tmp_path)]
    )
    assert report_path.is_file()

    sarif_path = tmp_path / "lattence.sarif.json"
    result = runner.invoke(app, ["sarif", str(report_path), "--out", str(sarif_path)])

    assert result.exit_code == 0
    document = json.loads(sarif_path.read_text())
    assert document["version"] == "2.1.0"
    assert len(document["runs"][0]["results"]) == 13


def test_sarif_json_writes_to_stdout(tmp_path: Path) -> None:
    runner.invoke(
        app, ["scan", "examples/vulnerable-agent", "--quiet", "--out", str(tmp_path)]
    )
    report_path = tmp_path / "lattence-report.json"

    result = runner.invoke(app, ["sarif", str(report_path), "--json"])

    assert result.exit_code == 0
    document = json.loads(result.stdout)
    assert document["version"] == "2.1.0"
