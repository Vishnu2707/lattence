import json
from pathlib import Path

from lattence.cli import app
from typer.testing import CliRunner

runner = CliRunner()


def _project(root: Path) -> None:
    (root / "app.py").write_text(
        "from crewai import Agent\nagent = Agent()\n",
        encoding="utf-8",
    )
    (root / "pyproject.toml").write_text(
        '[project]\nname="fixture"\nversion="1"\ndependencies=["crewai"]\n',
        encoding="utf-8",
    )


def _scan(root: Path) -> None:
    result = runner.invoke(
        app,
        ["scan", str(root), "--out", str(root), "--fail-on", "none", "--quiet"],
    )
    assert result.exit_code == 0, result.output


def test_harden_json_reads_complete_scan_result(tmp_path: Path) -> None:
    _project(tmp_path)
    _scan(tmp_path)

    result = runner.invoke(app, ["harden", str(tmp_path), "--json"])

    assert result.exit_code == 1
    plans = json.loads(result.stdout)["plans"]
    assert plans
    assert plans[0]["remediation"]
    assert plans[0]["target"]["id"].startswith("agent:")


def test_harden_finding_id_uses_report_under_out(tmp_path: Path) -> None:
    _project(tmp_path)
    _scan(tmp_path)

    result = runner.invoke(
        app,
        [
            "harden",
            "LT-AI-001",
            "--out",
            str(tmp_path),
            "--fail-on",
            "none",
        ],
    )

    assert result.exit_code == 0
    assert "REMEDIATION  LT-AI-001" in result.stdout
    assert "Target" in result.stdout
    assert "Reproduce" in result.stdout


def test_harden_unknown_finding_exits_two(tmp_path: Path) -> None:
    _project(tmp_path)
    _scan(tmp_path)

    result = runner.invoke(app, ["harden", "LT-AI-999", "--out", str(tmp_path)])

    assert result.exit_code == 2
    assert "finding not found" in result.output


def test_harden_does_not_modify_project_or_report(tmp_path: Path) -> None:
    _project(tmp_path)
    _scan(tmp_path)
    before = {
        path.relative_to(tmp_path): path.read_bytes()
        for path in tmp_path.rglob("*")
        if path.is_file()
    }

    result = runner.invoke(
        app, ["harden", str(tmp_path), "--quiet", "--fail-on", "none"]
    )

    after = {
        path.relative_to(tmp_path): path.read_bytes()
        for path in tmp_path.rglob("*")
        if path.is_file()
    }
    assert result.exit_code == 0
    assert after == before
