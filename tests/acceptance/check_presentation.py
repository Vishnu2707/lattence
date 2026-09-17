import json
import sys
from pathlib import Path
from typing import Any


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _accepted_chain(presentation: dict[str, Any]) -> dict[str, Any]:
    return next(
        chain
        for chain in presentation["cross_layer_chains"]
        if chain["source_finding_id"] == "LT-AI-002"
        and chain["crypto_finding_id"] == "LT-PQC-203"
    )


def check(presentation_path: Path, dashboard_root: Path) -> None:
    presentation = _load(presentation_path)
    chain = _accepted_chain(presentation)
    assert presentation["version"] == "1"
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

    edges = {edge["id"]: edge for edge in presentation["graph"]["edges"]}
    for hop in chain["hops"]:
        stored = edges[hop["edge_id"]]
        assert (hop["source_id"], hop["target_id"], hop["edge_type"]) == (
            stored["source_id"],
            stored["target_id"],
            stored["type"],
        )

    assert {"app.py", "crypto_config.py"}.issubset(chain["evidence_refs"])
    for relative in (
        "index.html",
        "src/dashboard.mjs",
        "src/dashboard-model.mjs",
        "src/dashboard.css",
        "src/tokens.css",
        "src/visual-grammar.json",
    ):
        assert (dashboard_root / relative).is_file(), relative


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: check_presentation.py PRESENTATION DASHBOARD_ROOT")
    check(Path(sys.argv[1]), Path(sys.argv[2]))
