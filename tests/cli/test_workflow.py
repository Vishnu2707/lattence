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
from langchain.tools import tool


@tool
def retrieve(query: str) -> str:
    return query


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


def test_report_html_embeds_real_cross_layer_chain_from_vulnerable_agent(
    tmp_path: Path,
) -> None:
    example = Path(__file__).parents[2] / "examples" / "vulnerable-agent"

    chain = runner.invoke(
        app,
        ["graph", "chain", str(example), "--offline", "--out", str(tmp_path)],
    )
    scan = runner.invoke(
        app,
        [
            "scan",
            str(example),
            "--offline",
            "--out",
            str(tmp_path),
            "--fail-on",
            "none",
        ],
    )
    report = runner.invoke(
        app, ["report", str(tmp_path), "--offline", "--out", str(tmp_path)]
    )

    assert chain.exit_code == 0, chain.output
    assert scan.exit_code == 0, scan.output
    assert report.exit_code == 0, report.output
    rendered = (tmp_path / "lattence-report.html").read_text(encoding="utf-8")
    assert "32 finding correlations across 9 distinct structural paths" in rendered
    assert "LT-AI-002 -&gt; LT-PQC-203" in rendered
    assert "key_exchange" in rendered
    assert "https://" not in rendered
    assert "http://" not in rendered
    assert "fetch(" not in rendered
    assert "cdn." not in rendered


def test_scan_vulnerable_agent_graph_and_pqc_summary_stay_sane(
    tmp_path: Path,
) -> None:
    """Regression for a real bug: a stale local report artifact once showed
    2,312 graph nodes and 20,684 edges for this fixture (versus 17-24 nodes
    consistently produced by this fixture across v0.4.1 through v1.0), and a
    JSON summary with quantum_vulnerable_assets/quantum_vulnerable_paths
    hard-coded to 0 while the terminal renderer showed real vulnerable
    algorithms. Bisection at a14d7ba, b4224cb, and 34b891d found the node and
    edge counts were never actually wrong on any of those commits (a fresh
    `scan` at each reproduced the same 24 nodes and 92 edges seen here); the
    inflated artifact was a stale, gitignored leftover file, not a live
    regression. The PQC summary contradiction was real: `create_report`
    never populated the two quantum fields, so they kept their model
    defaults of 0 regardless of the graph's actual crypto topology. This
    test pins both: the node/edge counts stay in range, and the JSON summary
    is internally consistent with the terminal output for the same run.
    """
    example = Path(__file__).parents[2] / "examples" / "vulnerable-agent"

    scan = runner.invoke(
        app,
        ["scan", str(example), "--offline", "--out", str(tmp_path)],
    )
    assert scan.exit_code in (0, 1), scan.output

    report_path = tmp_path / "lattence-report.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    nodes = report["graph"]["nodes"]
    edges = report["graph"]["edges"]

    assert 17 <= len(nodes) <= 24, len(nodes)
    assert len(edges) < 200, len(edges)

    algorithms = [node for node in nodes if node["type"] == "crypto_algorithm"]
    vulnerable_count = sum(
        1 for node in algorithms if node.get("quantum_status") == "vulnerable"
    )
    assert f"Quantum vulnerable    {vulnerable_count}" in scan.stdout

    summary = report["summary"]
    # The summary must not silently default to zero when the graph actually
    # contains a reachable, quantum-vulnerable crypto asset: at least one of
    # the two fields must reflect that real exposure.
    if vulnerable_count > 0:
        assert (
            summary["quantum_vulnerable_assets"] > 0
            or summary["quantum_vulnerable_paths"] > 0
        ), summary


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


def test_verify_reports_vulnerable_and_exits_nonzero(tmp_path: Path) -> None:
    _project(tmp_path)
    runner.invoke(
        app,
        [
            "attack",
            str(tmp_path),
            "--offline",
            "--quiet",
            "--out",
            str(tmp_path),
            "--fail-on",
            "none",
        ],
    )

    result = runner.invoke(app, ["verify", "LT-AI-001", "--out", str(tmp_path)])

    assert result.exit_code == 1
    assert "VULNERABLE  LT-AI-001" in result.stdout


def test_verify_reports_blocked_for_unknown_finding(tmp_path: Path) -> None:
    _project(tmp_path)
    runner.invoke(
        app,
        [
            "attack",
            str(tmp_path),
            "--offline",
            "--quiet",
            "--out",
            str(tmp_path),
            "--fail-on",
            "none",
        ],
    )

    result = runner.invoke(app, ["verify", "LT-AI-999", "--out", str(tmp_path)])

    assert result.exit_code == 2
    assert "BLOCKED  LT-AI-999" in result.stdout


def test_verify_json_output_is_machine_readable(tmp_path: Path) -> None:
    _project(tmp_path)
    runner.invoke(
        app,
        [
            "attack",
            str(tmp_path),
            "--offline",
            "--quiet",
            "--out",
            str(tmp_path),
            "--fail-on",
            "none",
        ],
    )

    result = runner.invoke(
        app, ["verify", "LT-AI-001", "--out", str(tmp_path), "--json"]
    )

    payload = json.loads(result.stdout)
    assert payload["outcome"] == "vulnerable"
    assert payload["finding_id"] == "LT-AI-001"
