import json
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


def test_vulnerable_example_crypto_assessment_is_stable_and_chaos_rolls_back(
    tmp_path: Path,
) -> None:
    assessment = [
        "pqc",
        "assess",
        str(EXAMPLE),
        "--offline",
        "--json",
        "--out",
        str(tmp_path),
        "--fail-on",
        "none",
    ]
    first = runner.invoke(app, assessment)
    second = runner.invoke(app, assessment)

    assert first.exit_code == 0, first.output
    assert second.exit_code == 0, second.output
    first_payload = json.loads(first.stdout)
    second_payload = json.loads(second.stdout)
    assert len(first_payload["crypto_graph"]["nodes"]) == len(
        second_payload["crypto_graph"]["nodes"]
    )
    assert len(first_payload["crypto_graph"]["edges"]) == len(
        second_payload["crypto_graph"]["edges"]
    )
    assert first_payload["quantum_exposure"] == second_payload["quantum_exposure"]
    assert first_payload["crypto_graph"]["edges"]

    crypto_config = EXAMPLE / "crypto_config.py"
    before = crypto_config.read_bytes()
    chaos = runner.invoke(
        app,
        [
            "crypto",
            "chaos",
            str(EXAMPLE),
            "--offline",
            "--json",
            "--out",
            str(tmp_path),
            "--fail-on",
            "none",
        ],
    )

    assert chaos.exit_code == 0, chaos.output
    assert json.loads(chaos.stdout)["downgrade"]["status"] == "resistant"
    assert crypto_config.read_bytes() == before


def test_vulnerable_example_has_real_ai_to_crypto_chain(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        [
            "tui",
            str(EXAMPLE),
            "--offline",
            "--json",
            "--out",
            str(tmp_path),
        ],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.stdout)
    chain = next(
        item
        for item in payload["cross_layer_chains"]
        if item["source_finding_id"] == "LT-AI-002"
        and item["crypto_finding_id"] == "LT-PQC-203"
    )
    assert chain["start_node_id"] == "dataset:rag-pipeline:app.py:15"
    assert chain["end_node_id"] == ("crypto_algorithm:crypto_config.py:7:tls-1-2")
    assert [hop["traversal"] for hop in chain["hops"]] == [
        "reverse",
        "forward",
    ]
    assert [hop["edge_type"] for hop in chain["hops"]] == [
        "accesses",
        "key_exchange",
    ]
    assert chain["hops"][0]["from_node_id"] == chain["start_node_id"]
    assert chain["hops"][0]["to_node_id"] == ("tool:app.py:delete_customer_record")
    assert chain["hops"][1]["from_node_id"] == ("tool:app.py:delete_customer_record")
    assert chain["hops"][1]["to_node_id"] == chain["end_node_id"]

    edges = {edge["id"]: edge for edge in payload["graph"]["edges"]}
    for hop in chain["hops"]:
        edge = edges[hop["edge_id"]]
        assert (hop["source_id"], hop["target_id"], hop["edge_type"]) == (
            edge["source_id"],
            edge["target_id"],
            edge["type"],
        )
    assert {"app.py", "crypto_config.py"}.issubset(chain["evidence_refs"])
