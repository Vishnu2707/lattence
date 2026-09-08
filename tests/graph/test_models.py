from datetime import UTC, datetime, timedelta, timezone

import pytest
from lattence.graph import (
    Agent,
    Application,
    Edge,
    Project,
    SecurityGraph,
    SourceRef,
)
from pydantic import ValidationError

NOW = datetime(2026, 1, 1, tzinfo=UTC)


def application() -> Application:
    return Application(
        id="application:service",
        name="service",
        source=SourceRef(path="src/service.py", line=4),
        frameworks=["example"],
        entrypoints=["src/service.py"],
        runtime="python",
    )


def test_project_round_trip_is_stable_and_utc() -> None:
    scanned_at = datetime(2026, 1, 1, tzinfo=timezone(timedelta(hours=2)))
    project = Project(
        id="project:fixture",
        name="fixture",
        root=".",
        scanned_at=scanned_at,
        nodes=[application()],
    )

    restored = Project.model_validate_json(project.model_dump_json())

    assert restored == project
    assert restored.scanned_at.utcoffset() == timedelta(0)
    assert restored.nodes[0].type == "application"


def test_nodes_reject_unknown_fields_and_absolute_sources() -> None:
    with pytest.raises(ValidationError):
        Application(
            id="application:service",
            name="service",
            unexpected=True,
        )

    with pytest.raises(ValidationError, match="project-relative"):
        SourceRef(path="/tmp/service.py")


def test_graph_allows_parallel_edges_with_distinct_ids() -> None:
    app = application()
    agent = Agent(id="agent:service/main", name="main")
    edges = [
        Edge(
            id="edge:contains:source",
            source_id=app.id,
            target_id=agent.id,
            type="contains",
            evidence_refs=["source:4"],
        ),
        Edge(
            id="edge:contains:config",
            source_id=app.id,
            target_id=agent.id,
            type="contains",
            evidence_refs=["config:2"],
        ),
    ]

    graph = SecurityGraph(
        project_id="project:fixture",
        nodes=[app, agent],
        edges=edges,
        generated_at=NOW,
    )

    assert len(graph.edges) == 2
    assert SecurityGraph.model_validate_json(graph.model_dump_json()) == graph


@pytest.mark.parametrize(
    "edges, message",
    [
        (
            [
                Edge(
                    id="edge:broken",
                    source_id="application:service",
                    target_id="agent:missing",
                    type="contains",
                )
            ],
            "unknown node",
        ),
        (
            [
                Edge(
                    id="edge:duplicate",
                    source_id="application:service",
                    target_id="agent:main",
                    type="contains",
                ),
                Edge(
                    id="edge:duplicate",
                    source_id="application:service",
                    target_id="agent:main",
                    type="delegates_to",
                ),
            ],
            "duplicate edge id",
        ),
    ],
)
def test_graph_rejects_invalid_edges(edges: list[Edge], message: str) -> None:
    nodes = [application(), Agent(id="agent:main", name="main")]

    with pytest.raises(ValidationError, match=message):
        SecurityGraph(
            project_id="project:fixture",
            nodes=nodes,
            edges=edges,
            generated_at=NOW,
        )
