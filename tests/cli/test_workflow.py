import json
from pathlib import Path

import pytest
from lattence.cli import app
from lattence.cli.options import SeverityGate
from lattence.cli.workflow import exceeds_gate
from lattence.evidence import ReportSummary
from typer.testing import CliRunner

runner = CliRunner()


def _summary(**counts: int) -> ReportSummary:
    base = {
        "total": 0,
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
        "info": 0,
        "pqc_readiness": 0,
    }
    base.update(counts)
    return ReportSummary(**base)


@pytest.mark.parametrize(
    ("gate", "counts", "expected"),
    [
        (SeverityGate.NONE, {"critical": 5}, False),
        (SeverityGate.HIGH, {"medium": 3}, False),
        (SeverityGate.HIGH, {"high": 1}, True),
        (SeverityGate.HIGH, {"critical": 1}, True),
        (SeverityGate.LOW, {"info": 1}, False),
        (SeverityGate.LOW, {"low": 1}, True),
        (SeverityGate.INFO, {"info": 1}, True),
    ],
)
def test_exceeds_gate(
    gate: SeverityGate, counts: dict[str, int], expected: bool
) -> None:
    assert exceeds_gate(_summary(**counts), gate) is expected


def _project(root: Path) -> None:
    (root / "app.py").write_text(
        """\
from crewai import Agent
agent = Agent()
documents = retriever.retrieve()
""",
        encoding="utf-8",
    )
    (root / "pyproject.toml").write_text(
        '[project]\nname="fixture"\nversion="1"\ndependencies=["crewai"]\n',
        encoding="utf-8",
    )
    (root / "mcp.json").write_text(
        json.dumps(
            {
                "servers": {
                    "local": {
                        "command": "fixture",
                        "tools": [{"name": "write_record", "sideEffects": True}],
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    (root / "lattence.targets.yaml").write_text(
        """\
version: "1"
authorization: owned-or-authorized
targets:
  - kind: project
    value: "."
""",
        encoding="utf-8",
    )


def test_scan_attack_graph_and_report_work_offline(tmp_path: Path) -> None:
    _project(tmp_path)

    scan = runner.invoke(
        app,
        [
            "scan",
            str(tmp_path),
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
            str(tmp_path),
            "--offline",
            "--out",
            str(tmp_path),
            "--fail-on",
            "none",
        ],
    )
    graph = runner.invoke(
        app,
        ["graph", "export", str(tmp_path), "--offline", "--out", str(tmp_path)],
    )
    report = runner.invoke(
        app, ["report", str(tmp_path), "--offline", "--out", str(tmp_path)]
    )

    assert scan.exit_code == 0, scan.output
    assert "DISCOVERY" in scan.stdout
    assert attack.exit_code == 0, attack.output
    assert "VULNERABLE" in attack.stdout
    assert "Indirect chain" in attack.stdout
    assert graph.exit_code == 0, graph.output
    assert report.exit_code == 0, report.output
    assert (tmp_path / "lattence-report.json").is_file()
    assert (tmp_path / "lattence-report.html").is_file()
    assert (tmp_path / "lattence-graph.json").is_file()


def test_scan_exits_nonzero_when_findings_meet_the_gate(tmp_path: Path) -> None:
    _project(tmp_path)

    result = runner.invoke(
        app,
        ["scan", str(tmp_path), "--offline", "--quiet", "--out", str(tmp_path)],
    )

    assert result.exit_code == 1


def test_scan_exits_zero_when_the_gate_is_disabled(tmp_path: Path) -> None:
    _project(tmp_path)

    result = runner.invoke(
        app,
        [
            "scan",
            str(tmp_path),
            "--offline",
            "--quiet",
            "--out",
            str(tmp_path),
            "--fail-on",
            "none",
        ],
    )

    assert result.exit_code == 0


def test_attack_refuses_project_without_declaration(tmp_path: Path) -> None:
    (tmp_path / "plain.py").write_text("value = 1\n", encoding="utf-8")

    result = runner.invoke(app, ["attack", str(tmp_path), "--offline"])

    assert result.exit_code == 2
    assert "attack requires lattence.targets.yaml" in result.output
