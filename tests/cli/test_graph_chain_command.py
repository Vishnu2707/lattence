import json
from pathlib import Path

from lattence.cli import app
from typer.testing import CliRunner

runner = CliRunner()
EXAMPLE = Path(__file__).parents[2] / "examples" / "vulnerable-agent"


def test_graph_chain_prints_real_edges_and_evidence(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        [
            "graph",
            "chain",
            str(EXAMPLE),
            "--offline",
            "--no-color",
            "--out",
            str(tmp_path),
        ],
    )

    assert result.exit_code == 0, result.output
    assert "LATTENCE  graph chain" in result.stdout
    assert "LT-AI-002 -> LT-PQC-203" in result.stdout
    assert "EDGE 1      accesses  reverse" in result.stdout
    assert "EDGE 2      key_exchange  forward" in result.stdout
    assert "tool:app.py:delete_customer_record" in result.stdout
    assert "EVIDENCE  app.py" in result.stdout
    assert "app.py, crypto_config.py" in result.stdout
    assert "\x1b[" not in result.stdout


def test_graph_chain_json_is_the_real_presentation(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        ["graph", "chain", str(EXAMPLE), "--json", "--out", str(tmp_path)],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.stdout)
    assert any(
        chain["source_finding_id"] == "LT-AI-002"
        and chain["crypto_finding_id"] == "LT-PQC-203"
        for chain in payload["cross_layer_chains"]
    )
    assert json.loads((tmp_path / "presentation.json").read_text()) == payload
