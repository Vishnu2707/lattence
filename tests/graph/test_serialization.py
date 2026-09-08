from datetime import UTC, datetime
from pathlib import Path

import pytest
from lattence.graph import (
    Edge,
    SecurityGraph,
    Tool,
    security_graph_json,
    write_security_graph,
)


def _graph(reverse: bool = False) -> SecurityGraph:
    nodes = [
        Tool(id="tool:b", name="b", tags={"two", "one"}),
        Tool(id="tool:a", name="a", permissions={"write", "read"}),
    ]
    edges = [
        Edge(
            id="edge:one",
            source_id="tool:a",
            target_id="tool:b",
            type="calls",
            evidence_refs=["z.py", "a.py"],
        )
    ]
    return SecurityGraph(
        project_id="fixture",
        nodes=list(reversed(nodes)) if reverse else nodes,
        edges=edges,
        generated_at=datetime(2026, 1, 1, tzinfo=UTC),
    )


def test_graph_json_is_deterministic_and_round_trips() -> None:
    rendered = security_graph_json(_graph())

    assert rendered == security_graph_json(_graph(reverse=True))
    parsed = SecurityGraph.model_validate_json(rendered)
    assert {node.id for node in parsed.nodes} == {"tool:a", "tool:b"}
    assert rendered.endswith("\n")


def test_writes_graph_and_rejects_negative_indent(tmp_path: Path) -> None:
    destination = tmp_path / "output" / "graph.json"

    write_security_graph(_graph(), destination)

    assert destination.read_text(encoding="utf-8") == security_graph_json(_graph())
    with pytest.raises(ValueError, match="indent must not be negative"):
        security_graph_json(_graph(), indent=-1)
